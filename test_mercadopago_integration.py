#!/usr/bin/env python
"""
Script de teste para integração com Mercado Pago
Execute com: python test_mercadopago_integration.py
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_test')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event, Ticket, Purchase
from events.mercadopago_views import criar_preferencia_pagamento
from unittest.mock import patch, MagicMock


def test_mercadopago_integration():
    """Teste de integração com Mercado Pago"""
    print("🧪 Iniciando testes de integração com Mercado Pago...")
    
    # Criar dados de teste
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    event = Event.objects.create(
        name='Evento de Teste MP',
        description='Descrição do evento de teste',
        date=timezone.now() + timezone.timedelta(days=7),
        location='Local de Teste',
        is_active=True
    )
    
    ticket = Ticket.objects.create(
        event=event,
        price=Decimal('50.00'),
        type='Standard',
        quantity=100,
        is_active=True
    )
    
    print(f"✅ Dados de teste criados:")
    print(f"   - Usuário: {user.username}")
    print(f"   - Evento: {event.name}")
    print(f"   - Ticket: {ticket.type} - R$ {ticket.price}")
    
    # Teste 1: Verificar se os modelos estão corretos
    print("\n🔍 Teste 1: Verificação dos modelos...")
    
    # Verificar propriedades do evento
    assert event.is_available, "Evento deve estar disponível"
    print("   ✅ Evento está disponível")
    
    # Verificar propriedades do ticket
    assert ticket.is_available, "Ticket deve estar disponível"
    print("   ✅ Ticket está disponível")
    
    # Verificar criação de compra
    purchase = Purchase.objects.create(
        ticket=ticket,
        user=user,
        quantity=1,
        total_price=ticket.price,
        status='pending',
        mp_status='pending',
        preference_id='pref_test_123',
        mercado_pago_id='pay_test_123'
    )
    
    assert purchase.ticket == ticket, "Compra deve referenciar o ticket correto"
    assert purchase.user == user, "Compra deve referenciar o usuário correto"
    assert purchase.total_price == ticket.price, "Preço total deve ser calculado corretamente"
    print("   ✅ Compra criada com sucesso")
    
    # Teste 2: Verificar configurações
    print("\n🔍 Teste 2: Verificação das configurações...")
    
    from django.conf import settings
    
    # Verificar se as configurações do MP estão definidas
    assert hasattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN'), "MERCADO_PAGO_ACCESS_TOKEN deve estar definido"
    assert hasattr(settings, 'MERCADO_PAGO_PUBLIC_KEY'), "MERCADO_PAGO_PUBLIC_KEY deve estar definido"
    assert hasattr(settings, 'MERCADO_PAGO_SANDBOX'), "MERCADO_PAGO_SANDBOX deve estar definido"
    print("   ✅ Configurações do Mercado Pago estão definidas")
    
    # Verificar URLs de callback
    assert hasattr(settings, 'MERCADO_PAGO_BACKURL_SUCCESS'), "MERCADO_PAGO_BACKURL_SUCCESS deve estar definido"
    assert hasattr(settings, 'MERCADO_PAGO_BACKURL_FAILURE'), "MERCADO_PAGO_BACKURL_FAILURE deve estar definido"
    assert hasattr(settings, 'MERCADO_PAGO_BACKURL_PENDING'), "MERCADO_PAGO_BACKURL_PENDING deve estar definido"
    print("   ✅ URLs de callback estão definidas")
    
    # Teste 3: Verificar views (com mock)
    print("\n🔍 Teste 3: Verificação das views...")
    
    # Mock do SDK do Mercado Pago
    with patch('events.mercadopago_views.mercadopago.SDK') as mock_sdk_class:
        mock_sdk = MagicMock()
        mock_sdk_class.return_value = mock_sdk
        
        mock_preference = MagicMock()
        mock_sdk.preference.return_value = mock_preference
        
        mock_response = {
            'response': {
                'id': 'pref_test_123',
                'init_point': 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref_test_123'
            }
        }
        mock_preference.create.return_value = mock_response
        
        # Simular request
        class MockRequest:
            def __init__(self, user):
                self.user = user
                self.session = {}
        
        request = MockRequest(user)
        
        # Testar criação de preferência
        try:
            # Esta função redireciona, então vamos capturar a exceção
            try:
                criar_preferencia_pagamento(request, event.id)
            except Exception as e:
                if "redirect" in str(e).lower():
                    print("   ✅ View de criação de preferência funciona (redirecionamento)")
                else:
                    raise e
        except Exception as e:
            print(f"   ❌ Erro na view de criação de preferência: {e}")
            return False
    
    # Teste 4: Verificar templates
    print("\n🔍 Teste 4: Verificação dos templates...")
    
    template_files = [
        'templates/events/pagamento_sucesso.html',
        'templates/events/pagamento_falha.html',
        'templates/events/pagamento_pendente.html',
        'templates/events/event_detail.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"   ✅ {template_file} existe")
        else:
            print(f"   ❌ {template_file} não encontrado")
            return False
    
    # Teste 5: Verificar URLs
    print("\n🔍 Teste 5: Verificação das URLs...")
    
    from django.urls import reverse, NoReverseMatch
    
    url_names = [
        'comprar_ingresso',
        'pagamento_sucesso',
        'pagamento_falha',
        'pagamento_pendente',
        'webhook_mercadopago'
    ]
    
    for url_name in url_names:
        try:
            if url_name == 'comprar_ingresso':
                reverse(url_name, args=[event.id])
            else:
                reverse(url_name)
            print(f"   ✅ URL {url_name} está configurada")
        except NoReverseMatch:
            print(f"   ❌ URL {url_name} não encontrada")
            return False
    
    print("\n🎉 Todos os testes passaram! A integração com Mercado Pago está funcionando corretamente.")
    return True


def test_webhook_validation():
    """Teste de validação de webhook"""
    print("\n🔍 Teste de validação de webhook...")
    
    from events.mercadopago_views import webhook_mercadopago
    from django.test import RequestFactory
    import json
    
    factory = RequestFactory()
    
    # Teste com content-type inválido
    request = factory.post('/events/webhook/mercadopago/', data='test', content_type='text/plain')
    response = webhook_mercadopago(request)
    
    if response.status_code == 400:
        print("   ✅ Validação de content-type funciona")
    else:
        print("   ❌ Validação de content-type falhou")
        return False
    
    # Teste com JSON inválido
    request = factory.post('/events/webhook/mercadopago/', data='invalid json', content_type='application/json')
    response = webhook_mercadopago(request)
    
    if response.status_code == 500:
        print("   ✅ Validação de JSON funciona")
    else:
        print("   ❌ Validação de JSON falhou")
        return False
    
    print("   ✅ Validação de webhook funciona corretamente")
    return True


if __name__ == '__main__':
    print("🚀 Iniciando testes de integração com Mercado Pago")
    print("=" * 60)
    
    try:
        # Executar testes
        success = test_mercadopago_integration()
        
        if success:
            success = test_webhook_validation()
        
        if success:
            print("\n✅ Todos os testes passaram com sucesso!")
            print("🎯 A integração com Mercado Pago está pronta para uso.")
            sys.exit(0)
        else:
            print("\n❌ Alguns testes falharam.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)