"""
Views para processamento de pagamentos
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.db import transaction
import json
import logging

from .models import Purchase, Payment, Ticket
from .mercadopago_service import MercadoPagoService
from .forms import PaymentForm

logger = logging.getLogger(__name__)

@login_required
def payment_form(request, purchase_id):
    """
    Formulário de pagamento
    """
    try:
        purchase = get_object_or_404(Purchase, pk=purchase_id, user=request.user)
        print(f"Payment form: Purchase ID={purchase.id}, Ticket ID={purchase.ticket.id if purchase.ticket else 'None'}")
        
        # Verificar se o ticket ainda existe
        if not purchase.ticket:
            messages.error(request, 'Ticket não encontrado para esta compra.')
            return redirect('event_list')
            
    except Exception as e:
        print(f"Erro ao buscar purchase {purchase_id}: {e}")
        messages.error(request, 'Compra não encontrada.')
        return redirect('event_list')
    
    # Verificar se já existe pagamento
    try:
        if hasattr(purchase, 'payment') and purchase.payment:
            if purchase.payment.is_approved:
                messages.info(request, 'Esta compra já foi paga.')
                return redirect('purchase_history')
            elif purchase.payment.is_pending:
                messages.info(request, 'Esta compra está aguardando pagamento.')
                return redirect('payment_status', payment_id=purchase.payment.id)
    except Exception as e:
        print(f"🔍 DEBUG: Erro ao verificar pagamento existente: {e}")
        # Continuar normalmente se houver erro
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        print(f"🔍 DEBUG FORM: Dados POST: {request.POST}")
        print(f"🔍 DEBUG FORM: Formulário válido: {form.is_valid()}")
        if not form.is_valid():
            print(f"🔍 DEBUG FORM: Erros do formulário: {form.errors}")
        if form.is_valid():
            try:
                # Criar pagamento
                payment_data = form.cleaned_data
                payment_data.update({
                    'payer_email': request.user.email,
                    'payer_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    'payer_document': payment_data.get('payer_document', '')
                })
                
                mp_service = MercadoPagoService()
                
                # Verificar se o ticket ainda existe
                try:
                    ticket = purchase.ticket
                    event_name = ticket.event.name
                except:
                    messages.error(request, 'Ticket não encontrado ou foi removido.')
                    return redirect('event_list')
                
                # Criar pagamento baseado no método
                if payment_data['payment_method'] == 'pix':
                    print(f"🔍 DEBUG VIEW: Criando preferência PIX para purchase {purchase.id}")
                    # PIX via preferência (compatível com sandbox)
                    preference = mp_service.create_preference(purchase, payment_data)
                    print(f"🔍 DEBUG VIEW: Resultado create_preference: {preference}")
                    
                    if preference:
                        # Salvar dados do pagamento PIX via preferência
                        payment = Payment.objects.create(
                            purchase=purchase,
                            mercado_pago_id=preference['id'],
                            payment_method='pix',
                            amount=purchase.total_price,
                            description=f"Ingresso para {event_name}",
                            payer_email=request.user.email,
                            payer_name=payment_data['payer_name'],
                            payer_document=payment_data.get('payer_document', ''),
                            mp_response=preference
                        )
                        
                        # Atualizar status da compra
                        purchase.status = 'processing'
                        purchase.mercado_pago_id = preference['id']
                        purchase.save()
                        
                        # Redirecionar para checkout (que vai mostrar PIX)
                        return redirect('payment_checkout', payment_id=payment.id)
                    else:
                        messages.error(request, 'Erro ao criar pagamento PIX. Tente novamente.')
                else:
                    # Cartão de crédito via preferência
                    preference = mp_service.create_preference(purchase, payment_data)
                    
                    if preference:
                        # Salvar dados do pagamento
                        payment = Payment.objects.create(
                            purchase=purchase,
                            mercado_pago_id=preference['id'],
                            payment_method=payment_data['payment_method'],
                            amount=purchase.total_price,
                            description=f"Ingresso para {event_name}",
                            payer_email=request.user.email,
                            payer_name=payment_data['payer_name'],
                            payer_document=payment_data.get('payer_document', ''),
                            mp_response=preference
                        )
                        
                        # Atualizar status da compra
                        purchase.status = 'processing'
                        purchase.mercado_pago_id = preference['id']
                        purchase.save()
                        
                        # Redirecionar para checkout
                        return redirect('payment_checkout', payment_id=payment.id)
                    else:
                        messages.error(request, 'Erro ao processar pagamento. Tente novamente.')
                    
            except Exception as e:
                logger.error(f"Erro no processamento do pagamento: {e}")
                messages.error(request, 'Erro interno. Tente novamente.')
    else:
        form = PaymentForm()
    
    context = {
        'purchase': purchase,
        'form': form,
    }
    return render(request, 'events/payment_form.html', context)

@login_required
def payment_checkout(request, payment_id):
    """
    Checkout do pagamento
    """
    payment = get_object_or_404(Payment, pk=payment_id, purchase__user=request.user)
    
    # Buscar dados da preferência
    preference = None
    if payment.mp_response:
        preference = payment.mp_response
    
    context = {
        'payment': payment,
        'mercadopago_public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
        'preference_id': payment.mercado_pago_id,
        'preference': preference,
    }
    return render(request, 'events/payment_checkout.html', context)

@login_required
def payment_status(request, payment_id):
    """
    Status do pagamento
    """
    payment = get_object_or_404(Payment, pk=payment_id, purchase__user=request.user)
    
    # Atualizar status do pagamento
    mp_service = MercadoPagoService()
    mp_payment = mp_service.get_payment(payment.mercado_pago_id)
    
    if mp_payment:
        payment.status = mp_payment['status']
        # Tentar definir payment_status se o campo existir
        try:
            payment.payment_status = mp_payment['status_detail']
        except:
            pass  # Campo não existe ainda
        payment.mp_response = mp_payment
        payment.save()
        
        # Atualizar status da compra
        if payment.is_approved:
            payment.purchase.status = 'approved'
            payment.paid_at = timezone.now()
            payment.save()
            
            # Atualizar quantidade de tickets
            ticket = payment.purchase.ticket
            ticket.quantity -= payment.purchase.quantity
            ticket.save()
            
            messages.success(request, 'Pagamento aprovado! Seu ingresso foi confirmado.')
        elif payment.is_rejected:
            payment.purchase.status = 'rejected'
            payment.purchase.save()
            messages.error(request, 'Pagamento rejeitado.')
    
    # Verificar se é uma requisição AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        response_data = {
            'status': payment.status,
            'is_approved': payment.is_approved,
            'is_pending': payment.is_pending,
            'is_rejected': payment.is_rejected,
            'payment_method': payment.payment_method,
            'amount': float(payment.amount),
            'mercado_pago_id': payment.mercado_pago_id
        }
        # Adicionar payment_status apenas se o campo existir
        try:
            response_data['payment_status'] = payment.payment_status or 'pending'
        except:
            response_data['payment_status'] = 'pending'
        
        return JsonResponse(response_data)
    
    context = {
        'payment': payment,
    }
    return render(request, 'events/payment_status.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def webhook_mercadopago(request):
    """
    Webhook para receber notificações do Mercado Pago
    """
    try:
        data = json.loads(request.body)
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Buscar pagamento no banco
                try:
                    payment = Payment.objects.get(mercado_pago_id=payment_id)
                    
                    # Atualizar status
                    mp_service = MercadoPagoService()
                    mp_payment = mp_service.get_payment(payment_id)
                    
                    if mp_payment:
                        payment.status = mp_payment['status']
                        payment.payment_status = mp_payment['status_detail']
                        payment.mp_response = mp_payment
                        payment.save()
                        
                        # Atualizar status da compra
                        if payment.is_approved:
                            payment.purchase.status = 'approved'
                            payment.paid_at = timezone.now()
                            payment.save()
                            
                            # Atualizar quantidade de tickets
                            with transaction.atomic():
                                ticket = payment.purchase.ticket
                                ticket.quantity -= payment.purchase.quantity
                                ticket.save()
                                
                                # Criar validação com QR code
                                from .models import TicketValidation
                                TicketValidation.objects.get_or_create(purchase=payment.purchase)
                                
                        elif payment.is_rejected:
                            payment.purchase.status = 'rejected'
                            payment.purchase.save()
                    
                    logger.info(f"Webhook processado para pagamento {payment_id}")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Pagamento {payment_id} não encontrado no banco")
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def payment_success(request):
    """
    Página de sucesso do pagamento
    """
    return render(request, 'events/payment_success.html')

@login_required
def payment_failure(request):
    """
    Página de falha do pagamento
    """
    return render(request, 'events/payment_failure.html')

@login_required
def payment_pending(request):
    """
    Página de pagamento pendente
    """
    return render(request, 'events/payment_pending.html')

@login_required
def cancel_payment(request, payment_id):
    """
    Cancelar pagamento
    """
    payment = get_object_or_404(Payment, pk=payment_id, purchase__user=request.user)
    
    if payment.is_pending:
        mp_service = MercadoPagoService()
        if mp_service.cancel_payment(payment.mercado_pago_id):
            payment.status = 'cancelled'
            payment.purchase.status = 'cancelled'
            payment.save()
            payment.purchase.save()
            
            messages.success(request, 'Pagamento cancelado com sucesso.')
        else:
            messages.error(request, 'Erro ao cancelar pagamento.')
    else:
        messages.warning(request, 'Este pagamento não pode ser cancelado.')
    
    return redirect('purchase_history')