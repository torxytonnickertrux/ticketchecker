"""
Serviços para processamento de webhooks do Mercado Pago
"""
import logging
from django.utils import timezone
from django.conf import settings
from .models import WebhookEvent, WebhookLog, PaymentNotification
from events.models import Purchase, Payment
import mercadopago

logger = logging.getLogger(__name__)


class WebhookService:
    """
    Serviço principal para processamento de webhooks
    """
    
    def __init__(self):
        self.mp_sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    
    def process_event(self, webhook_event, environment):
        """
        Processar evento do webhook
        
        Args:
            webhook_event: Instância de WebhookEvent
            environment: 'test' ou 'production'
        
        Returns:
            dict: Resultado do processamento
        """
        try:
            event_type = webhook_event.event_type
            raw_data = webhook_event.raw_data
            
            # Log do início do processamento
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='INFO',
                message=f'Iniciando processamento do evento {event_type}',
                details={'environment': environment}
            )
            
            # Processar baseado no tipo de evento
            if event_type == 'payment':
                return self._process_payment_event(webhook_event, environment)
            elif event_type == 'plan':
                return self._process_plan_event(webhook_event, environment)
            elif event_type == 'subscription':
                return self._process_subscription_event(webhook_event, environment)
            elif event_type == 'invoice':
                return self._process_invoice_event(webhook_event, environment)
            else:
                # Evento não suportado
                WebhookLog.objects.create(
                    webhook_event=webhook_event,
                    level='WARNING',
                    message=f'Tipo de evento não suportado: {event_type}',
                    details={'event_type': event_type}
                )
                
                webhook_event.status = 'ignored'
                webhook_event.save()
                
                return {
                    'success': True,
                    'message': f'Evento {event_type} ignorado (não suportado)',
                    'processed_data': {}
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar evento {webhook_event.event_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'details': {'event_id': webhook_event.event_id}
            }
    
    def _process_payment_event(self, webhook_event, environment):
        """
        Processar evento de pagamento
        """
        try:
            raw_data = webhook_event.raw_data
            payment_id = raw_data.get('data', {}).get('id')
            
            if not payment_id:
                return {
                    'success': False,
                    'error': 'ID do pagamento não encontrado no evento'
                }
            
            # Buscar dados do pagamento no Mercado Pago
            payment_data = self._get_payment_from_mp(payment_id)
            
            if not payment_data:
                return {
                    'success': False,
                    'error': f'Não foi possível obter dados do pagamento {payment_id}'
                }
            
            # Processar pagamento
            processor = PaymentProcessor()
            result = processor.process_payment(payment_data, webhook_event, environment)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar evento de pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_plan_event(self, webhook_event, environment):
        """
        Processar evento de plano (não implementado)
        """
        WebhookLog.objects.create(
            webhook_event=webhook_event,
            level='INFO',
            message='Evento de plano recebido (não processado)',
            details={'environment': environment}
        )
        
        return {
            'success': True,
            'message': 'Evento de plano ignorado',
            'processed_data': {}
        }
    
    def _process_subscription_event(self, webhook_event, environment):
        """
        Processar evento de assinatura (não implementado)
        """
        WebhookLog.objects.create(
            webhook_event=webhook_event,
            level='INFO',
            message='Evento de assinatura recebido (não processado)',
            details={'environment': environment}
        )
        
        return {
            'success': True,
            'message': 'Evento de assinatura ignorado',
            'processed_data': {}
        }
    
    def _process_invoice_event(self, webhook_event, environment):
        """
        Processar evento de fatura (não implementado)
        """
        WebhookLog.objects.create(
            webhook_event=webhook_event,
            level='INFO',
            message='Evento de fatura recebido (não processado)',
            details={'environment': environment}
        )
        
        return {
            'success': True,
            'message': 'Evento de fatura ignorado',
            'processed_data': {}
        }
    
    def _get_payment_from_mp(self, payment_id):
        """
        Buscar dados do pagamento no Mercado Pago
        """
        try:
            result = self.mp_sdk.payment().get(payment_id)
            
            if result["status"] == 200:
                return result["response"]
            else:
                logger.error(f"Erro ao buscar pagamento {payment_id}: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento {payment_id}: {e}")
            return None


class PaymentProcessor:
    """
    Processador de pagamentos
    """
    
    def process_payment(self, payment_data, webhook_event, environment):
        """
        Processar dados de pagamento
        
        Args:
            payment_data: Dados do pagamento do Mercado Pago
            webhook_event: Evento webhook
            environment: Ambiente (test/production)
        
        Returns:
            dict: Resultado do processamento
        """
        try:
            payment_id = payment_data.get('id')
            external_reference = payment_data.get('external_reference')
            status = payment_data.get('status')
            
            # Log do processamento
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='INFO',
                message=f'Processando pagamento {payment_id}',
                details={
                    'payment_id': payment_id,
                    'external_reference': external_reference,
                    'status': status,
                    'environment': environment
                }
            )
            
            # Buscar compra pela referência externa
            if not external_reference:
                return {
                    'success': False,
                    'error': 'Referência externa não encontrada no pagamento'
                }
            
            try:
                purchase = Purchase.objects.get(id=external_reference)
            except Purchase.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Compra {external_reference} não encontrada'
                }
            
            # Atualizar compra
            purchase.mercado_pago_id = payment_id
            purchase.payment_status = status
            
            # Mapear status do Mercado Pago para status interno
            if status == 'approved':
                purchase.status = 'approved'
                purchase.payment_date = timezone.now()
                
                # Atualizar quantidade de tickets
                if purchase.ticket:
                    purchase.ticket.quantity -= purchase.quantity
                    purchase.ticket.save()
                    
            elif status == 'rejected':
                purchase.status = 'rejected'
            elif status == 'cancelled':
                purchase.status = 'cancelled'
            elif status == 'pending':
                purchase.status = 'processing'
            
            purchase.save()
            
            # Criar notificação de pagamento
            notification_type = self._get_notification_type(status)
            PaymentNotification.objects.create(
                webhook_event=webhook_event,
                notification_type=notification_type,
                payment_id=payment_id,
                external_reference=external_reference,
                amount=payment_data.get('transaction_amount', 0),
                currency=payment_data.get('currency_id', 'BRL'),
                payment_status=status,
                payment_method=payment_data.get('payment_method_id'),
                payment_date=timezone.now() if status == 'approved' else None
            )
            
            # Log de sucesso
            WebhookLog.objects.create(
                webhook_event=webhook_event,
                level='INFO',
                message=f'Pagamento {payment_id} processado com sucesso',
                details={
                    'purchase_id': purchase.id,
                    'status': status,
                    'notification_type': notification_type
                }
            )
            
            return {
                'success': True,
                'message': f'Pagamento {payment_id} processado com sucesso',
                'processed_data': {
                    'purchase_id': purchase.id,
                    'payment_id': payment_id,
                    'status': status,
                    'notification_type': notification_type
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_notification_type(self, status):
        """
        Mapear status do Mercado Pago para tipo de notificação
        """
        mapping = {
            'approved': 'payment_approved',
            'rejected': 'payment_rejected',
            'cancelled': 'payment_cancelled',
            'pending': 'payment_pending',
        }
        
        return mapping.get(status, 'payment_pending')