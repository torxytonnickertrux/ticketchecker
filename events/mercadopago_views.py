"""
Views para integração com Mercado Pago
"""
import mercadopago
import logging
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.mail import send_mail
from .models import Event, Ticket, Purchase

logger = logging.getLogger('events')


@login_required
def criar_preferencia_pagamento(request, event_id):
    """
    Cria uma preferência de pagamento no Mercado Pago e redireciona o usuário
    """
    try:
        # Buscar o evento
        event = get_object_or_404(Event, id=event_id, is_active=True)
        
        # Verificar se o evento ainda está no futuro
        if event.date <= timezone.now():
            messages.error(request, 'Este evento já ocorreu.')
            return redirect('event_detail', event_id=event_id)
        
        # Buscar o primeiro ticket disponível do evento
        ticket = event.tickets.filter(is_active=True, quantity__gt=0).first()
        if not ticket:
            messages.error(request, 'Não há ingressos disponíveis para este evento.')
            return redirect('event_detail', event_id=event_id)
        
        # Inicializar SDK do Mercado Pago
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        
        # Dados do item para pagamento
        items = [{
            "id": str(event.id),
            "title": event.name,
            "description": f"Ingresso para {event.name} - {event.date.strftime('%d/%m/%Y %H:%M')}",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": float(Decimal(str(ticket.price)))
        }]
        
        # Dados do pagador
        payer = {
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
        }
        
        # Configuração da preferência
        preference_data = {
            "items": items,
            "payer": payer,
            "back_urls": {
                "success": settings.MERCADO_PAGO_BACKURL_SUCCESS,
                "failure": settings.MERCADO_PAGO_BACKURL_FAILURE,
                "pending": settings.MERCADO_PAGO_BACKURL_PENDING
            },
            "auto_return": "all",
            "external_reference": f"event_{event_id}_user_{request.user.id}",
            "notification_url": f"{settings.SITE_URL}/events/webhook/mercadopago/",
            "statement_descriptor": "TICKETCHECKER",
            "additional_info": f"Compra de ingresso para {event.name}",
            "metadata": {
                "event_id": event_id,
                "user_id": request.user.id,
                "ticket_id": ticket.id
            }
        }
        
        # Criar preferência
        result = sdk.preference().create(preference_data)
        
        if 'error' in result:
            logger.error(f"Erro ao criar preferência MP: {result['error']}")
            messages.error(request, 'Erro ao processar pagamento. Tente novamente.')
            return redirect('event_detail', event_id=event_id)
        
        # Salvar dados da preferência na sessão para uso posterior
        request.session['mp_preference_id'] = result['response']['id']
        request.session['mp_event_id'] = event_id
        request.session['mp_ticket_id'] = ticket.id
        
        # Redirecionar para o Mercado Pago
        init_point = result['response']['init_point']
        logger.info(f"Preferência criada com sucesso: {result['response']['id']}")
        
        return redirect(init_point)
        
    except Exception as e:
        logger.error(f"Erro ao criar preferência de pagamento: {e}")
        messages.error(request, 'Erro inesperado ao processar pagamento.')
        return redirect('event_detail', event_id=event_id)


def pagamento_sucesso(request):
    """
    Callback de sucesso do Mercado Pago
    """
    try:
        preference_id = request.GET.get('preference_id')
        payment_id = request.GET.get('payment_id')
        
        if not preference_id:
            messages.error(request, 'Dados de pagamento inválidos.')
            return redirect('event_list')
        
        # Buscar dados da sessão
        event_id = request.session.get('mp_event_id')
        ticket_id = request.session.get('mp_ticket_id')
        
        if not event_id or not ticket_id:
            messages.error(request, 'Sessão expirada. Tente novamente.')
            return redirect('event_list')
        
        # Buscar objetos
        event = get_object_or_404(Event, id=event_id)
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Criar ou atualizar compra
        purchase, created = Purchase.objects.get_or_create(
            ticket=ticket,
            user=request.user,
            defaults={
                'quantity': 1,
                'total_price': ticket.price,
                'status': 'approved',
                'mp_status': 'approved',
                'preference_id': preference_id,
                'mercado_pago_id': payment_id,
                'payment_status': 'approved',
                'payment_date': timezone.now()
            }
        )
        
        if not created:
            # Atualizar compra existente
            purchase.status = 'approved'
            purchase.mp_status = 'approved'
            purchase.preference_id = preference_id
            purchase.mercado_pago_id = payment_id
            purchase.payment_status = 'approved'
            purchase.payment_date = timezone.now()
            purchase.save()
        
        # Atualizar quantidade disponível
        if created:
            ticket.quantity -= 1
            ticket.save()
        
        # Enviar email de confirmação
        try:
            send_confirmation_email(request.user, purchase)
        except Exception as e:
            logger.error(f"Erro ao enviar email de confirmação: {e}")
        
        # Limpar sessão
        request.session.pop('mp_preference_id', None)
        request.session.pop('mp_event_id', None)
        request.session.pop('mp_ticket_id', None)
        
        logger.info(f"Pagamento aprovado: {preference_id} - Compra: {purchase.id}")
        messages.success(request, 'Pagamento aprovado! Seu ingresso foi enviado por email.')
        
        return render(request, 'events/pagamento_sucesso.html', {
            'purchase': purchase,
            'event': event
        })
        
    except Exception as e:
        logger.error(f"Erro no callback de sucesso: {e}")
        messages.error(request, 'Erro ao processar confirmação de pagamento.')
        return redirect('event_list')


def pagamento_falha(request):
    """
    Callback de falha do Mercado Pago
    """
    try:
        preference_id = request.GET.get('preference_id')
        
        # Buscar dados da sessão
        event_id = request.session.get('mp_event_id')
        
        if event_id:
            event = get_object_or_404(Event, id=event_id)
        else:
            event = None
        
        # Limpar sessão
        request.session.pop('mp_preference_id', None)
        request.session.pop('mp_event_id', None)
        request.session.pop('mp_ticket_id', None)
        
        logger.info(f"Pagamento falhou: {preference_id}")
        messages.error(request, 'Pagamento não foi aprovado. Tente novamente.')
        
        return render(request, 'events/pagamento_falha.html', {
            'event': event,
            'preference_id': preference_id
        })
        
    except Exception as e:
        logger.error(f"Erro no callback de falha: {e}")
        messages.error(request, 'Erro ao processar pagamento.')
        return redirect('event_list')


def pagamento_pendente(request):
    """
    Callback de pagamento pendente do Mercado Pago
    """
    try:
        preference_id = request.GET.get('preference_id')
        payment_id = request.GET.get('payment_id')
        
        # Buscar dados da sessão
        event_id = request.session.get('mp_event_id')
        ticket_id = request.session.get('mp_ticket_id')
        
        if event_id and ticket_id:
            event = get_object_or_404(Event, id=event_id)
            ticket = get_object_or_404(Ticket, id=ticket_id)
            
            # Criar compra pendente
            purchase, created = Purchase.objects.get_or_create(
                ticket=ticket,
                user=request.user,
                defaults={
                    'quantity': 1,
                    'total_price': ticket.price,
                    'status': 'pending',
                    'mp_status': 'pending',
                    'preference_id': preference_id,
                    'mercado_pago_id': payment_id,
                    'payment_status': 'pending'
                }
            )
            
            if not created:
                purchase.status = 'pending'
                purchase.mp_status = 'pending'
                purchase.preference_id = preference_id
                purchase.mercado_pago_id = payment_id
                purchase.payment_status = 'pending'
                purchase.save()
        else:
            event = None
            purchase = None
        
        # Limpar sessão
        request.session.pop('mp_preference_id', None)
        request.session.pop('mp_event_id', None)
        request.session.pop('mp_ticket_id', None)
        
        logger.info(f"Pagamento pendente: {preference_id}")
        messages.warning(request, 'Pagamento pendente. Aguarde aprovação.')
        
        return render(request, 'events/pagamento_pendente.html', {
            'event': event,
            'purchase': purchase,
            'preference_id': preference_id
        })
        
    except Exception as e:
        logger.error(f"Erro no callback de pendente: {e}")
        messages.error(request, 'Erro ao processar pagamento.')
        return redirect('event_list')


@csrf_exempt
@require_http_methods(["POST"])
def webhook_mercadopago(request):
    """
    Webhook para receber notificações do Mercado Pago
    """
    try:
        # Verificar se é uma notificação válida
        if request.content_type != 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Content-Type deve ser application/json'}, status=400)
        
        # Processar notificação
        data = request.json() if hasattr(request, 'json') else None
        if not data:
            import json
            data = json.loads(request.body.decode('utf-8'))
        
        # Verificar tipo de notificação
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            if payment_id:
                # Buscar informações do pagamento no Mercado Pago
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                payment_info = sdk.payment().get(payment_id)
                
                if 'error' not in payment_info:
                    # Processar atualização do status
                    process_payment_notification(payment_info['response'])
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Erro no webhook do Mercado Pago: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def process_payment_notification(payment_data):
    """
    Processa notificação de pagamento do Mercado Pago
    """
    try:
        payment_id = payment_data.get('id')
        status = payment_data.get('status')
        external_reference = payment_data.get('external_reference', '')
        
        # Extrair dados da referência externa
        if external_reference.startswith('event_'):
            parts = external_reference.split('_')
            if len(parts) >= 3:
                event_id = parts[1]
                user_id = parts[3]
                
                # Buscar compra
                purchase = Purchase.objects.filter(
                    ticket__event_id=event_id,
                    user_id=user_id,
                    mercado_pago_id=payment_id
                ).first()
                
                if purchase:
                    # Atualizar status
                    if status == 'approved':
                        purchase.status = 'approved'
                        purchase.mp_status = 'approved'
                        purchase.payment_status = 'approved'
                        purchase.payment_date = timezone.now()
                        
                        # Enviar email de confirmação
                        send_confirmation_email(purchase.user, purchase)
                        
                    elif status == 'rejected':
                        purchase.status = 'rejected'
                        purchase.mp_status = 'rejected'
                        purchase.payment_status = 'rejected'
                        
                    elif status == 'cancelled':
                        purchase.status = 'cancelled'
                        purchase.mp_status = 'cancelled'
                        purchase.payment_status = 'cancelled'
                    
                    purchase.save()
                    logger.info(f"Status atualizado para compra {purchase.id}: {status}")
        
    except Exception as e:
        logger.error(f"Erro ao processar notificação de pagamento: {e}")


def send_confirmation_email(user, purchase):
    """
    Envia email de confirmação de compra
    """
    try:
        subject = f'Confirmação de Compra - {purchase.ticket.event.name}'
        message = f'''
        Olá {user.get_full_name() or user.username},
        
        Sua compra foi confirmada com sucesso!
        
        Evento: {purchase.ticket.event.name}
        Data: {purchase.ticket.event.date.strftime("%d/%m/%Y %H:%M")}
        Local: {purchase.ticket.event.location}
        Ingresso: {purchase.ticket.get_type_display()}
        Quantidade: {purchase.quantity}
        Total: R$ {purchase.total_price:.2f}
        
        Seu QR Code será enviado em breve.
        
        Obrigado por escolher nosso sistema!
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email de confirmação enviado para {user.email}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmação: {e}")
