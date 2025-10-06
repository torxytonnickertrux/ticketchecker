"""
Testes para integração com Mercado Pago
"""
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .models import Event, Ticket, Purchase


class MercadoPagoIntegrationTest(TestCase):
    """Testes para integração com Mercado Pago"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = Client()
        
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar evento de teste
        self.event = Event.objects.create(
            name='Evento de Teste',
            description='Descrição do evento de teste',
            date=timezone.now() + timezone.timedelta(days=7),
            location='Local de Teste',
            is_active=True
        )
        
        # Criar ticket de teste
        self.ticket = Ticket.objects.create(
            event=self.event,
            price=Decimal('50.00'),
            type='Standard',
            quantity=100,
            is_active=True
        )
        
        # Mock do SDK do Mercado Pago
        self.mock_sdk = MagicMock()
        self.mock_preference = MagicMock()
        self.mock_sdk.preference.return_value = self.mock_preference
        
    @patch('events.mercadopago_views.mercadopago.SDK')
    def test_criar_preferencia_pagamento_success(self, mock_sdk_class):
        """Teste de criação de preferência de pagamento com sucesso"""
        # Configurar mock
        mock_sdk_class.return_value = self.mock_sdk
        mock_response = {
            'response': {
                'id': 'pref_123456789',
                'init_point': 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref_123456789'
            }
        }
        self.mock_preference.create.return_value = mock_response
        
        # Fazer login
        self.client.force_login(self.user)
        
        # Fazer requisição
        response = self.client.get(reverse('comprar_ingresso', args=[self.event.id]))
        
        # Verificar redirecionamento
        self.assertEqual(response.status_code, 302)
        self.assertIn('mercadopago.com.br', response.url)
        
        # Verificar se o SDK foi chamado corretamente
        mock_sdk_class.assert_called_once_with(settings.MERCADO_PAGO_ACCESS_TOKEN)
        self.mock_preference.create.assert_called_once()
        
        # Verificar dados da preferência
        call_args = self.mock_preference.create.call_args[0][0]
        self.assertEqual(call_args['items'][0]['title'], self.event.name)
        self.assertEqual(call_args['items'][0]['unit_price'], 50.0)
        self.assertEqual(call_args['payer']['email'], self.user.email)
        
    @patch('events.mercadopago_views.mercadopago.SDK')
    def test_criar_preferencia_pagamento_error(self, mock_sdk_class):
        """Teste de criação de preferência com erro"""
        # Configurar mock para retornar erro
        mock_sdk_class.return_value = self.mock_sdk
        mock_response = {
            'error': 'Invalid access token'
        }
        self.mock_preference.create.return_value = mock_response
        
        # Fazer login
        self.client.force_login(self.user)
        
        # Fazer requisição
        response = self.client.get(reverse('comprar_ingresso', args=[self.event.id]))
        
        # Verificar redirecionamento de volta para o evento
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('event_detail', args=[self.event.id]))
        
    def test_criar_preferencia_pagamento_event_not_found(self):
        """Teste com evento não encontrado"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('comprar_ingresso', args=[999]))
        
        self.assertEqual(response.status_code, 404)
        
    def test_criar_preferencia_pagamento_event_past(self):
        """Teste com evento no passado"""
        # Criar evento no passado
        past_event = Event.objects.create(
            name='Evento Passado',
            description='Evento no passado',
            date=timezone.now() - timezone.timedelta(days=1),
            location='Local',
            is_active=True
        )
        
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('comprar_ingresso', args=[past_event.id]))
        
        # Deve redirecionar de volta para o evento
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('event_detail', args=[past_event.id]))
        
    def test_criar_preferencia_pagamento_no_tickets(self):
        """Teste sem tickets disponíveis"""
        # Criar evento sem tickets
        event_no_tickets = Event.objects.create(
            name='Evento Sem Tickets',
            description='Evento sem tickets',
            date=timezone.now() + timezone.timedelta(days=7),
            location='Local',
            is_active=True
        )
        
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('comprar_ingresso', args=[event_no_tickets.id]))
        
        # Deve redirecionar de volta para o evento
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('event_detail', args=[event_no_tickets.id]))
        
    def test_pagamento_sucesso(self):
        """Teste de callback de sucesso"""
        # Configurar sessão
        session = self.client.session
        session['mp_event_id'] = self.event.id
        session['mp_ticket_id'] = self.ticket.id
        session.save()
        
        self.client.force_login(self.user)
        
        # Fazer requisição de sucesso
        response = self.client.get(reverse('pagamento_sucesso'), {
            'preference_id': 'pref_123456789',
            'payment_id': 'pay_123456789'
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pagamento Aprovado')
        
        # Verificar se a compra foi criada
        purchase = Purchase.objects.filter(
            ticket=self.ticket,
            user=self.user
        ).first()
        
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.status, 'approved')
        self.assertEqual(purchase.mp_status, 'approved')
        self.assertEqual(purchase.preference_id, 'pref_123456789')
        
    def test_pagamento_falha(self):
        """Teste de callback de falha"""
        # Configurar sessão
        session = self.client.session
        session['mp_event_id'] = self.event.id
        session.save()
        
        self.client.force_login(self.user)
        
        # Fazer requisição de falha
        response = self.client.get(reverse('pagamento_falha'), {
            'preference_id': 'pref_123456789'
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pagamento Não Aprovado')
        
    def test_pagamento_pendente(self):
        """Teste de callback de pendente"""
        # Configurar sessão
        session = self.client.session
        session['mp_event_id'] = self.event.id
        session['mp_ticket_id'] = self.ticket.id
        session.save()
        
        self.client.force_login(self.user)
        
        # Fazer requisição de pendente
        response = self.client.get(reverse('pagamento_pendente'), {
            'preference_id': 'pref_123456789',
            'payment_id': 'pay_123456789'
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pagamento Pendente')
        
        # Verificar se a compra foi criada com status pendente
        purchase = Purchase.objects.filter(
            ticket=self.ticket,
            user=self.user
        ).first()
        
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.status, 'pending')
        self.assertEqual(purchase.mp_status, 'pending')
        
    @patch('events.mercadopago_views.mercadopago.SDK')
    def test_webhook_mercadopago(self, mock_sdk_class):
        """Teste de webhook do Mercado Pago"""
        # Configurar mock
        mock_sdk_class.return_value = self.mock_sdk
        mock_payment_info = {
            'response': {
                'id': 'pay_123456789',
                'status': 'approved',
                'external_reference': f'event_{self.event.id}_user_{self.user.id}'
            }
        }
        self.mock_sdk.payment.return_value.get.return_value = mock_payment_info
        
        # Criar compra existente
        purchase = Purchase.objects.create(
            ticket=self.ticket,
            user=self.user,
            quantity=1,
            total_price=self.ticket.price,
            status='pending',
            mp_status='pending',
            preference_id='pref_123456789',
            mercado_pago_id='pay_123456789'
        )
        
        # Dados do webhook
        webhook_data = {
            'type': 'payment',
            'data': {
                'id': 'pay_123456789'
            }
        }
        
        # Fazer requisição POST para webhook
        response = self.client.post(
            reverse('webhook_mercadopago'),
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'ok')
        
        # Verificar se a compra foi atualizada
        purchase.refresh_from_db()
        self.assertEqual(purchase.status, 'approved')
        self.assertEqual(purchase.mp_status, 'approved')
        
    def test_webhook_invalid_content_type(self):
        """Teste de webhook com content-type inválido"""
        response = self.client.post(
            reverse('webhook_mercadopago'),
            data='invalid data',
            content_type='text/plain'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('Content-Type deve ser application/json', response_data['message'])
        
    def test_webhook_invalid_json(self):
        """Teste de webhook com JSON inválido"""
        response = self.client.post(
            reverse('webhook_mercadopago'),
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')


class MercadoPagoModelTest(TestCase):
    """Testes para modelos relacionados ao Mercado Pago"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            name='Evento de Teste',
            description='Descrição do evento de teste',
            date=timezone.now() + timezone.timedelta(days=7),
            location='Local de Teste',
            is_active=True
        )
        
        self.ticket = Ticket.objects.create(
            event=self.event,
            price=Decimal('50.00'),
            type='Standard',
            quantity=100,
            is_active=True
        )
        
    def test_purchase_creation(self):
        """Teste de criação de compra"""
        purchase = Purchase.objects.create(
            ticket=self.ticket,
            user=self.user,
            quantity=1,
            total_price=self.ticket.price,
            status='approved',
            mp_status='approved',
            preference_id='pref_123456789',
            mercado_pago_id='pay_123456789',
            payment_status='approved',
            payment_date=timezone.now()
        )
        
        self.assertEqual(purchase.ticket, self.ticket)
        self.assertEqual(purchase.user, self.user)
        self.assertEqual(purchase.quantity, 1)
        self.assertEqual(purchase.total_price, Decimal('50.00'))
        self.assertEqual(purchase.status, 'approved')
        self.assertEqual(purchase.mp_status, 'approved')
        self.assertEqual(purchase.preference_id, 'pref_123456789')
        self.assertEqual(purchase.mercado_pago_id, 'pay_123456789')
        
    def test_purchase_str(self):
        """Teste do método __str__ da compra"""
        purchase = Purchase.objects.create(
            ticket=self.ticket,
            user=self.user,
            quantity=2,
            total_price=Decimal('100.00')
        )
        
        expected_str = f"2 x {self.ticket.type} para {self.user.username}"
        self.assertEqual(str(purchase), expected_str)
        
    def test_purchase_clean(self):
        """Teste do método clean da compra"""
        # Teste com quantidade inválida
        purchase = Purchase(
            ticket=self.ticket,
            user=self.user,
            quantity=0,
            total_price=Decimal('0.00')
        )
        
        with self.assertRaises(Exception):  # ValidationError
            purchase.clean()
            
    def test_ticket_is_available(self):
        """Teste da propriedade is_available do ticket"""
        # Ticket disponível
        self.assertTrue(self.ticket.is_available)
        
        # Ticket com quantidade zero
        self.ticket.quantity = 0
        self.ticket.save()
        self.assertFalse(self.ticket.is_available)
        
        # Ticket inativo
        self.ticket.quantity = 10
        self.ticket.is_active = False
        self.ticket.save()
        self.assertFalse(self.ticket.is_available)
        
    def test_event_is_available(self):
        """Teste da propriedade is_available do evento"""
        # Evento futuro
        self.assertTrue(self.event.is_available)
        
        # Evento no passado
        self.event.date = timezone.now() - timezone.timedelta(days=1)
        self.event.save()
        self.assertFalse(self.event.is_available)
        
        # Evento inativo
        self.event.date = timezone.now() + timezone.timedelta(days=7)
        self.event.is_active = False
        self.event.save()
        self.assertFalse(self.event.is_available)