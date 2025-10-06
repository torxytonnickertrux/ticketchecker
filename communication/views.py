"""
Views para comunicação com Mercado Pago
"""
import json
import hashlib
import hmac
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import WebhookEvent, WebhookLog, PaymentNotification
from .services import WebhookService, PaymentProcessor
from .validators import WebhookValidator

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_test(request):
    """
    Webhook para ambiente de teste
    URL: https://ingressoptga.pythonanywhere.com/comunication/build/teste
    """
    return _process_webhook(request, environment='test')


@csrf_exempt
@require_http_methods(["POST"])
def webhook_production(request):
    """
    Webhook para ambiente de produção
    URL: https://ingressoptga.pythonanywhere.com/comunication/build/production
    """
    return _process_webhook(request, environment='production')


def _process_webhook(request, environment):
    """
    Processar webhook do Mercado Pago
    """
    try:
        # Obter dados do request
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        
        # Obter headers importantes
        signature = request.META.get('HTTP_X_SIGNATURE', '')
        signature_ts = request.META.get('HTTP_X_SIGNATURE_TS', '')
        source_ip = _get_client_ip(request)
        
        # Criar evento webhook
        webhook_event = WebhookEvent.objects.create(
            event_id=data.get('id', ''),
            event_type=data.get('type', ''),
            raw_data=data,
            source_ip=source_ip,
            signature_valid=False  # Será validado abaixo
        )
        
        # Log do evento recebido
        WebhookLog.objects.create(
            webhook_event=webhook_event,
            level='INFO',
            message=f'Webhook {environment} recebido',
            details={
                'event_type': data.get('type'),
                'event_id': data.get('id'),
                'source_ip': source_ip,
                'environment': environment
            }
        )
        
        # Validar assinatura
        validator = WebhookValidator()
        is_valid = validator.validate_signature(
            raw_data, 
            signature, 
            signature_ts,
            environment
        )
        
        webhook_event.signature_valid = is_valid
        
        if not is_valid:
            webhook_event.status = 'failed'
            webhook_event.error_message = 'Assinatura inválida'
            webhook_event.save()
            
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='ERROR',
                message='Assinatura do webhook inválida',
                details={
                    'signature': signature,
                    'signature_ts': signature_ts,
                    'environment': environment
                }
            )
            
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)
        
        # Processar evento
        webhook_service = WebhookService()
        result = webhook_service.process_event(webhook_event, environment)
        
        if result['success']:
            webhook_event.mark_processed()
            webhook_event.processed_data = result.get('processed_data', {})
            webhook_event.save()
            
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='INFO',
                message='Evento processado com sucesso',
                details=result.get('details', {})
            )
            
            return JsonResponse({'status': 'ok'})
        else:
            webhook_event.mark_failed(result.get('error', 'Erro desconhecido'))
            
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='ERROR',
                message='Erro ao processar evento',
                details={
                    'error': result.get('error'),
                    'details': result.get('details', {})
                }
            )
            
            return JsonResponse({'status': 'error', 'message': result.get('error')}, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do webhook: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f"Erro inesperado no webhook: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


def _get_client_ip(request):
    """
    Obter IP do cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["GET"])
def webhook_status(request):
    """
    Endpoint para verificar status do webhook
    """
    try:
        # Estatísticas básicas
        total_events = WebhookEvent.objects.count()
        pending_events = WebhookEvent.objects.filter(status='pending').count()
        processed_events = WebhookEvent.objects.filter(status='processed').count()
        failed_events = WebhookEvent.objects.filter(status='failed').count()
        
        # Eventos recentes
        recent_events = WebhookEvent.objects.order_by('-received_at')[:10]
        recent_events_data = []
        
        for event in recent_events:
            recent_events_data.append({
                'id': event.id,
                'event_type': event.event_type,
                'event_id': event.event_id,
                'status': event.status,
                'received_at': event.received_at.isoformat(),
                'signature_valid': event.signature_valid
            })
        
        return JsonResponse({
            'status': 'ok',
            'statistics': {
                'total_events': total_events,
                'pending_events': pending_events,
                'processed_events': processed_events,
                'failed_events': failed_events
            },
            'recent_events': recent_events_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do webhook: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def webhook_test_endpoint(request):
    """
    Endpoint para testar conectividade do webhook
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'Webhook endpoint is working',
        'timestamp': timezone.now().isoformat(),
        'environment': 'test'
    })