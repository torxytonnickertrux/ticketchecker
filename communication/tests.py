"""
Testes para comunicação com Mercado Pago
"""
import json
import time
import hmac
import hashlib
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from .models import WebhookEvent, WebhookLog, PaymentNotification
from events.models import Event, Ticket, Purchase, User


class WebhookTestCase(TestCase):
    """
    Testes para webhooks do Mercado Pago
    """
    
    def setUp(self):
        """Configurar dados de teste"""
        self.client = Client()
        
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar evento de teste
        self.event = Event.objects.create(
            name='Evento Teste',
            description='Descrição do evento teste',
            date=timezone.now() + timezone.timedelta(days=30),
            location='Local Teste',
            is_active=True
        )
        
        # Criar ticket de teste
        self.ticket = Ticket.objects.create(
            event=self.event,
            price=50.00,
            type='Standard',
            quantity=100,
            is_active=True
        )
        
        # Criar compra de teste
        self.purchase = Purchase.objects.create(
            ticket=self.ticket,
            user=self.user,
            quantity=2,
            total_price=100.00,
            status='pending'
        )
    
    def _create_signature(self, payload, timestamp):
        """Criar assinatura válida para teste"""
        secret_key = "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"
        validation_string = f"{timestamp}{payload}"
        return hmac.new(
            secret_key.encode('utf-8'),
            validation_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def test_webhook_test_endpoint(self):
        """Testar endpoint de teste"""
        response = self.client.get('/comunication/test/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['environment'], 'test')
    
    def test_webhook_status_endpoint(self):
        """Testar endpoint de status"""
        response = self.client.get('/comunication/status/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('statistics', data)
        self.assertIn('recent_events', data)
    
    def test_webhook_payment_approved(self):
        """Testar webhook de pagamento aprovado"""
        # Dados do webhook
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'payment',
            'data': {
                'id': 'test_payment_456'
            }
        })
        
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp)
        
        # Mock da resposta do Mercado Pago
        mock_payment_data = {
            'id': 'test_payment_456',
            'external_reference': str(self.purchase.id),
            'status': 'approved',
            'transaction_amount': 100.00,
            'currency_id': 'BRL',
            'payment_method_id': 'pix',
            'date_approved': timezone.now().isoformat()
        }
        
        with patch('communication.services.mercadopago.SDK') as mock_sdk:
            mock_instance = MagicMock()
            mock_instance.payment().get.return_value = {
                'status': 200,
                'response': mock_payment_data
            }
            mock_sdk.return_value = mock_instance
            
            # Fazer requisição
            response = self.client.post(
                '/comunication/build/teste',
                data=payload,
                content_type='application/json',
                HTTP_X_SIGNATURE=signature,
                HTTP_X_SIGNATURE_TS=timestamp
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Verificar se o evento foi criado
            webhook_event = WebhookEvent.objects.get(event_id='test_event_123')
            self.assertEqual(webhook_event.event_type, 'payment')
            self.assertEqual(webhook_event.status, 'processed')
            self.assertTrue(webhook_event.signature_valid)
            
            # Verificar se a compra foi atualizada
            self.purchase.refresh_from_db()
            self.assertEqual(self.purchase.status, 'approved')
            self.assertEqual(self.purchase.mercado_pago_id, 'test_payment_456')
            
            # Verificar se a notificação foi criada
            notification = PaymentNotification.objects.get(payment_id='test_payment_456')
            self.assertEqual(notification.notification_type, 'payment_approved')
    
    def test_webhook_invalid_signature(self):
        """Testar webhook com assinatura inválida"""
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'payment',
            'data': {'id': 'test_payment_456'}
        })
        
        timestamp = str(int(time.time()))
        invalid_signature = 'invalid_signature'
        
        response = self.client.post(
            '/comunication/build/teste',
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE=invalid_signature,
            HTTP_X_SIGNATURE_TS=timestamp
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Verificar se o evento foi criado mas marcado como falhou
        webhook_event = WebhookEvent.objects.get(event_id='test_event_123')
        self.assertFalse(webhook_event.signature_valid)
        self.assertEqual(webhook_event.status, 'failed')
    
    def test_webhook_old_timestamp(self):
        """Testar webhook com timestamp muito antigo"""
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'payment',
            'data': {'id': 'test_payment_456'}
        })
        
        # Timestamp de 10 minutos atrás
        old_timestamp = str(int(time.time()) - 600)
        signature = self._create_signature(payload, old_timestamp)
        
        response = self.client.post(
            '/comunication/build/teste',
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE=signature,
            HTTP_X_SIGNATURE_TS=old_timestamp
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_webhook_payment_rejected(self):
        """Testar webhook de pagamento rejeitado"""
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'payment',
            'data': {'id': 'test_payment_456'}
        })
        
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp)
        
        # Mock da resposta do Mercado Pago
        mock_payment_data = {
            'id': 'test_payment_456',
            'external_reference': str(self.purchase.id),
            'status': 'rejected',
            'transaction_amount': 100.00,
            'currency_id': 'BRL',
            'payment_method_id': 'pix'
        }
        
        with patch('communication.services.mercadopago.SDK') as mock_sdk:
            mock_instance = MagicMock()
            mock_instance.payment().get.return_value = {
                'status': 200,
                'response': mock_payment_data
            }
            mock_sdk.return_value = mock_instance
            
            response = self.client.post(
                '/comunication/build/teste',
                data=payload,
                content_type='application/json',
                HTTP_X_SIGNATURE=signature,
                HTTP_X_SIGNATURE_TS=timestamp
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Verificar se a compra foi atualizada
            self.purchase.refresh_from_db()
            self.assertEqual(self.purchase.status, 'rejected')
            
            # Verificar se a notificação foi criada
            notification = PaymentNotification.objects.get(payment_id='test_payment_456')
            self.assertEqual(notification.notification_type, 'payment_rejected')
    
    def test_webhook_unsupported_event_type(self):
        """Testar webhook com tipo de evento não suportado"""
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'plan',
            'data': {'id': 'test_plan_456'}
        })
        
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp)
        
        response = self.client.post(
            '/comunication/build/teste',
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE=signature,
            HTTP_X_SIGNATURE_TS=timestamp
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o evento foi marcado como ignorado
        webhook_event = WebhookEvent.objects.get(event_id='test_event_123')
        self.assertEqual(webhook_event.status, 'ignored')
    
    def test_webhook_missing_purchase(self):
        """Testar webhook com compra inexistente"""
        payload = json.dumps({
            'id': 'test_event_123',
            'type': 'payment',
            'data': {'id': 'test_payment_456'}
        })
        
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp)
        
        # Mock da resposta do Mercado Pago com referência externa inexistente
        mock_payment_data = {
            'id': 'test_payment_456',
            'external_reference': '999999',  # ID inexistente
            'status': 'approved',
            'transaction_amount': 100.00,
            'currency_id': 'BRL'
        }
        
        with patch('communication.services.mercadopago.SDK') as mock_sdk:
            mock_instance = MagicMock()
            mock_instance.payment().get.return_value = {
                'status': 200,
                'response': mock_payment_data
            }
            mock_sdk.return_value = mock_instance
            
            response = self.client.post(
                '/comunication/build/teste',
                data=payload,
                content_type='application/json',
                HTTP_X_SIGNATURE=signature,
                HTTP_X_SIGNATURE_TS=timestamp
            )
            
            self.assertEqual(response.status_code, 500)
            
            # Verificar se o evento foi marcado como falhou
            webhook_event = WebhookEvent.objects.get(event_id='test_event_123')
            self.assertEqual(webhook_event.status, 'failed')