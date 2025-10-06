"""
Serviço avançado de testes para Mercado Pago
"""
import json
import time
import hmac
import hashlib
import requests
from django.conf import settings
from django.utils import timezone
from .models import WebhookEvent, WebhookLog, PaymentNotification
from events.models import Event, Ticket, Purchase, User
import mercadopago


class MercadoPagoTestService:
    """
    Serviço para testes abrangentes do Mercado Pago
    """
    
    def __init__(self):
        self.mp_sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        self.base_url = settings.SITE_URL
        self.webhook_secret = settings.WEBHOOK_SECRET_KEY
        
        # Cartões de teste
        self.test_cards = {
            'mastercard_approved': {
                'number': '5031433215406351',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'APRO Test User',
                'cardholder_document': '12345678909'
            },
            'visa_approved': {
                'number': '4235647728025682',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'APRO Test User',
                'cardholder_document': '12345678909'
            },
            'amex_approved': {
                'number': '375365153556885',
                'security_code': '1234',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'APRO Test User',
                'cardholder_document': '12345678909'
            },
            'elo_debit': {
                'number': '5067766783888311',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'APRO Test User',
                'cardholder_document': '12345678909'
            },
            'mastercard_rejected': {
                'number': '5031433215406351',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'OTHE Test User',
                'cardholder_document': '12345678909'
            },
            'visa_pending': {
                'number': '4235647728025682',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'CONT Test User',
                'cardholder_document': '12345678909'
            },
            'amex_insufficient_funds': {
                'number': '375365153556885',
                'security_code': '1234',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'FUND Test User',
                'cardholder_document': '12345678909'
            },
            'elo_security_code': {
                'number': '5067766783888311',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'SECU Test User',
                'cardholder_document': '12345678909'
            },
            'visa_expired': {
                'number': '4235647728025682',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'EXPI Test User',
                'cardholder_document': '12345678909'
            },
            'mastercard_form_error': {
                'number': '5031433215406351',
                'security_code': '123',
                'expiration_month': '11',
                'expiration_year': '30',
                'cardholder_name': 'FORM Test User',
                'cardholder_document': '12345678909'
            }
        }
    
    def create_test_data(self):
        """Criar dados de teste"""
        # Criar usuário de teste
        user, created = User.objects.get_or_create(
            username='testuser_mp',
            defaults={
                'email': 'test@mercadopago.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Criar evento de teste
        event, created = Event.objects.get_or_create(
            name='Evento Teste Mercado Pago',
            defaults={
                'description': 'Evento para testes do Mercado Pago',
                'date': timezone.now() + timezone.timedelta(days=30),
                'location': 'Local Teste',
                'is_active': True
            }
        )
        
        # Criar tickets de teste
        tickets = []
        for ticket_type, price in [('VIP', 100.00), ('Standard', 50.00), ('Student', 25.00)]:
            ticket, created = Ticket.objects.get_or_create(
                event=event,
                type=ticket_type,
                defaults={
                    'price': price,
                    'quantity': 100,
                    'is_active': True
                }
            )
            tickets.append(ticket)
        
        return user, event, tickets
    
    def create_test_purchase(self, user, ticket, quantity=1):
        """Criar compra de teste"""
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=quantity,
            total_price=ticket.price * quantity,
            status='pending'
        )
        return purchase
    
    def create_webhook_signature(self, payload, timestamp):
        """Criar assinatura do webhook"""
        validation_string = f"{timestamp}{payload}"
        return hmac.new(
            self.webhook_secret.encode('utf-8'),
            validation_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def send_webhook(self, payload, environment='test'):
        """Enviar webhook de teste"""
        url = f"{self.base_url}/comunication/build/{environment}"
        timestamp = str(int(time.time()))
        signature = self.create_webhook_signature(payload, timestamp)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Signature': signature,
            'X-Signature-Ts': timestamp
        }
        
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        return response
    
    def test_card_payment(self, card_name, user, ticket, quantity=1):
        """Testar pagamento com cartão"""
        print(f"\n🧪 Testando pagamento com {card_name}")
        
        # Criar compra
        purchase = self.create_test_purchase(user, ticket, quantity)
        
        # Obter dados do cartão
        card_data = self.test_cards[card_name]
        
        # Criar preferência
        preference_data = {
            "items": [
                {
                    "title": f"Ingresso {ticket.type} - {ticket.event.name}",
                    "quantity": quantity,
                    "unit_price": float(ticket.price),
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "identification": {
                    "type": "CPF",
                    "number": card_data['cardholder_document']
                }
            },
            "payment_methods": {
                "excluded_payment_methods": [
                    {"id": "pix"},
                    {"id": "debit_card"}
                ]
            },
            "back_urls": {
                "success": f"{settings.SITE_URL}/payment/success/",
                "failure": f"{settings.SITE_URL}/payment/failure/",
                "pending": f"{settings.SITE_URL}/payment/pending/"
            },
            "external_reference": str(purchase.id)
        }
        
        try:
            # Criar preferência
            result = self.mp_sdk.preference().create(preference_data)
            
            if result["status"] == 201:
                preference = result["response"]
                print(f"✅ Preferência criada: {preference['id']}")
                
                # Simular webhook de pagamento
                webhook_payload = json.dumps({
                    "id": f"test_event_{card_name}_{int(time.time())}",
                    "type": "payment",
                    "data": {"id": preference['id']}
                })
                
                # Enviar webhook
                response = self.send_webhook(webhook_payload)
                
                if response.status_code == 200:
                    print(f"✅ Webhook enviado com sucesso")
                    
                    # Verificar se a compra foi atualizada
                    purchase.refresh_from_db()
                    print(f"📊 Status da compra: {purchase.status}")
                    print(f"📊 ID Mercado Pago: {purchase.mercado_pago_id}")
                    
                    return True
                else:
                    print(f"❌ Erro no webhook: {response.status_code} - {response.text}")
                    return False
            else:
                print(f"❌ Erro ao criar preferência: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def test_pix_payment(self, user, ticket, quantity=1):
        """Testar pagamento PIX"""
        print(f"\n🧪 Testando pagamento PIX")
        
        # Criar compra
        purchase = self.create_test_purchase(user, ticket, quantity)
        
        # Criar preferência PIX
        preference_data = {
            "items": [
                {
                    "title": f"Ingresso {ticket.type} - {ticket.event.name}",
                    "quantity": quantity,
                    "unit_price": float(ticket.price),
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username
            },
            "payment_methods": {
                "excluded_payment_methods": [
                    {"id": "credit_card"},
                    {"id": "debit_card"},
                    {"id": "bank_transfer"},
                    {"id": "atm"}
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
            },
            "external_reference": str(purchase.id)
        }
        
        try:
            # Criar preferência
            result = self.mp_sdk.preference().create(preference_data)
            
            if result["status"] == 201:
                preference = result["response"]
                print(f"✅ Preferência PIX criada: {preference['id']}")
                
                # Simular webhook de pagamento
                webhook_payload = json.dumps({
                    "id": f"test_event_pix_{int(time.time())}",
                    "type": "payment",
                    "data": {"id": preference['id']}
                })
                
                # Enviar webhook
                response = self.send_webhook(webhook_payload)
                
                if response.status_code == 200:
                    print(f"✅ Webhook PIX enviado com sucesso")
                    
                    # Verificar se a compra foi atualizada
                    purchase.refresh_from_db()
                    print(f"📊 Status da compra: {purchase.status}")
                    
                    return True
                else:
                    print(f"❌ Erro no webhook PIX: {response.status_code} - {response.text}")
                    return False
            else:
                print(f"❌ Erro ao criar preferência PIX: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste PIX: {e}")
            return False
    
    def test_webhook_security(self):
        """Testar segurança do webhook"""
        print(f"\n🔒 Testando segurança do webhook")
        
        # Teste com assinatura inválida
        payload = json.dumps({
            "id": "test_security_invalid",
            "type": "payment",
            "data": {"id": "test_payment"}
        })
        
        timestamp = str(int(time.time()))
        invalid_signature = "invalid_signature"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Signature': invalid_signature,
            'X-Signature-Ts': timestamp
        }
        
        response = requests.post(
            f"{self.base_url}/comunication/build/teste",
            data=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Assinatura inválida rejeitada corretamente")
        else:
            print(f"❌ Assinatura inválida aceita incorretamente: {response.status_code}")
        
        # Teste com timestamp antigo
        old_timestamp = str(int(time.time()) - 600)  # 10 minutos atrás
        valid_signature = self.create_webhook_signature(payload, old_timestamp)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Signature': valid_signature,
            'X-Signature-Ts': old_timestamp
        }
        
        response = requests.post(
            f"{self.base_url}/comunication/build/teste",
            data=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Timestamp antigo rejeitado corretamente")
        else:
            print(f"❌ Timestamp antigo aceito incorretamente: {response.status_code}")
        
        return True
    
    def test_webhook_events(self):
        """Testar diferentes tipos de eventos"""
        print(f"\n📡 Testando diferentes tipos de eventos")
        
        events = [
            {"id": "test_payment", "type": "payment", "data": {"id": "test_payment"}},
            {"id": "test_plan", "type": "plan", "data": {"id": "test_plan"}},
            {"id": "test_subscription", "type": "subscription", "data": {"id": "test_subscription"}},
            {"id": "test_invoice", "type": "invoice", "data": {"id": "test_invoice"}},
        ]
        
        results = []
        
        for event in events:
            payload = json.dumps(event)
            response = self.send_webhook(payload)
            
            if response.status_code == 200:
                print(f"✅ Evento {event['type']} processado com sucesso")
                results.append(True)
            else:
                print(f"❌ Erro no evento {event['type']}: {response.status_code}")
                results.append(False)
        
        return all(results)
    
    def run_comprehensive_tests(self):
        """Executar todos os testes"""
        print("🚀 Iniciando testes abrangentes do Mercado Pago")
        print("=" * 60)
        
        # Criar dados de teste
        user, event, tickets = self.create_test_data()
        
        results = []
        
        # Testar segurança do webhook
        results.append(self.test_webhook_security())
        
        # Testar diferentes tipos de eventos
        results.append(self.test_webhook_events())
        
        # Testar pagamento PIX
        results.append(self.test_pix_payment(user, tickets[0]))
        
        # Testar pagamentos com cartão
        for card_name in self.test_cards.keys():
            results.append(self.test_card_payment(card_name, user, tickets[0]))
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results)
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("🎉 Todos os testes passaram!")
        else:
            print(f"⚠️ {failed_tests} testes falharam")
        
        return results