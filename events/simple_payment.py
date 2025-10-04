"""
Sistema de pagamento simplificado
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Purchase
from .debug_decorators import safe_purchase_access
from .error_logger import ErrorLogger
import mercadopago
import json

@login_required
def simple_payment(request, purchase_id):
    """
    Pagamento simples - apenas PIX
    """
    try:
        purchase = get_object_or_404(Purchase, pk=purchase_id, user=request.user)
        
        # Log do acesso à compra
        ErrorLogger.log_purchase_flow("PAYMENT_ACCESS", {
            'purchase_id': purchase_id,
            'user_id': request.user.id,
        })
        
        # Log do estado da compra
        ErrorLogger.log_object_state(purchase, "PURCHASE_FOR_PAYMENT")
        
        # Verificar se o ticket ainda existe
        if not purchase.ticket:
            ErrorLogger.log_ticket_error(Exception("Ticket não encontrado na compra"), {
                'purchase_id': purchase_id,
                'user_id': request.user.id,
            })
            messages.error(request, 'Ticket não encontrado para esta compra.')
            return redirect('event_list')
        
        # Verificar se o evento do ticket ainda existe
        if not purchase.ticket.event:
            ErrorLogger.log_ticket_error(Exception("Evento não encontrado para o ticket"), {
                'purchase_id': purchase_id,
                'ticket_id': purchase.ticket.id,
                'user_id': request.user.id,
            })
            messages.error(request, 'Evento não encontrado para este ingresso.')
            return redirect('event_list')
        
        # Verificar se o evento ainda está ativo
        if not purchase.ticket.event.is_active:
            ErrorLogger.log_ticket_error(Exception("Evento inativo"), {
                'purchase_id': purchase_id,
                'ticket_id': purchase.ticket.id,
                'event_id': purchase.ticket.event.id,
                'user_id': request.user.id,
            })
            messages.error(request, 'Este evento não está mais ativo.')
            return redirect('event_list')
        
        # Log do ticket da compra
        ErrorLogger.log_object_state(purchase.ticket, "TICKET_FOR_PAYMENT")
        
    except Exception as e:
        ErrorLogger.log_ticket_error(e, {
            'purchase_id': purchase_id,
            'user_id': request.user.id if request.user.is_authenticated else None,
        })
        messages.error(request, 'Erro ao acessar compra.')
        return redirect('purchase_history')
    
    if request.method == 'POST':
        try:
            # Configurar Mercado Pago
            mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            
            # Verificar novamente antes de criar a preferência
            if not purchase.ticket:
                ErrorLogger.log_ticket_error(Exception("Ticket não encontrado ao criar preferência"), {
                    'purchase_id': purchase_id,
                    'user_id': request.user.id,
                })
                messages.error(request, 'Ticket não encontrado para esta compra.')
                return redirect('event_list')
            
            if not purchase.ticket.event:
                ErrorLogger.log_ticket_error(Exception("Evento não encontrado ao criar preferência"), {
                    'purchase_id': purchase_id,
                    'ticket_id': purchase.ticket.id,
                    'user_id': request.user.id,
                })
                messages.error(request, 'Evento não encontrado para este ingresso.')
                return redirect('event_list')
            
            # Criar preferência com verificação adicional
            try:
                # Verificar se todos os objetos ainda existem
                ticket = purchase.ticket
                event = ticket.event
                
                if not ticket:
                    raise Exception("Ticket não encontrado")
                if not event:
                    raise Exception("Evento não encontrado")
                
                # Criar preferência
                preference_data = {
                    "items": [
                        {
                            "title": f"Ingresso {ticket.type} - {event.name}",
                            "quantity": purchase.quantity,
                            "unit_price": float(ticket.price),
                            "currency_id": "BRL"
                        }
                    ],
                "payer": {
                    "email": request.user.email,
                    "name": request.user.get_full_name() or request.user.username
                },
                "payment_methods": {
                    "excluded_payment_methods": [
                        {"id": "credit_card"},
                        {"id": "debit_card"},
                        {"id": "bank_transfer"},
                        {"id": "atm"},
                        {"id": "bolbradesco"},
                        {"id": "pec"},
                        {"id": "pagofacil"},
                        {"id": "rapipago"}
                    ],
                    "excluded_payment_types": [
                        {"id": "credit_card"},
                        {"id": "debit_card"}
                    ],
                    "installments": 1
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/payment/success/",
                    "failure": f"{settings.SITE_URL}/payment/failure/",
                    "pending": f"{settings.SITE_URL}/payment/pending/"
                }
                }
                
                # Criar preferência
                result = mp.preference().create(preference_data)
                
            except Exception as e:
                ErrorLogger.log_ticket_error(e, {
                    'purchase_id': purchase_id,
                    'ticket_id': purchase.ticket.id if purchase.ticket else None,
                    'event_id': purchase.ticket.event.id if purchase.ticket and purchase.ticket.event else None,
                    'user_id': request.user.id,
                    'error_location': 'preference_creation'
                })
                messages.error(request, f'Erro ao criar preferência: {str(e)}')
                return redirect('event_list')
            
            if result["status"] == 201:
                preference = result["response"]
                
                # Atualizar compra
                purchase.status = 'processing'
                purchase.mercado_pago_id = preference['id']
                purchase.save()
                
                # Redirecionar para checkout
                return redirect(preference['init_point'])
            else:
                messages.error(request, 'Erro ao processar pagamento.')
                
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
    
    context = {
        'purchase': purchase,
    }
    return render(request, 'events/simple_payment.html', context)

@login_required
def payment_success(request):
    """
    Página de sucesso
    """
    return render(request, 'events/payment_success.html')

@login_required
def payment_failure(request):
    """
    Página de falha
    """
    return render(request, 'events/payment_failure.html')

@login_required
def payment_pending(request):
    """
    Página pendente
    """
    return render(request, 'events/payment_pending.html')

@csrf_exempt
def webhook_simple(request):
    """
    Webhook simples
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                
                # Buscar compra pelo ID do Mercado Pago
                purchase = Purchase.objects.get(mercado_pago_id=payment_id)
                
                # Atualizar status
                purchase.status = 'approved'
                purchase.save()
                
                # Atualizar quantidade de tickets
                ticket = purchase.ticket
                ticket.quantity -= purchase.quantity
                ticket.save()
                
        except Exception as e:
            print(f"Erro no webhook: {e}")
    
    return JsonResponse({'status': 'ok'})
