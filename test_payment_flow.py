#!/usr/bin/env python
"""
Teste do fluxo completo de pagamento para identificar o erro
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from events.models import Event, Ticket, Purchase
from events.error_logger import ErrorLogger
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_complete_payment_flow():
    """
    Testar o fluxo completo de pagamento
    """
    print("🧪 TESTE DO FLUXO COMPLETO DE PAGAMENTO")
    print("=" * 60)
    
    try:
        # 1. Simular usuário
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        print(f"✅ Usuário: {user.username} (ID: {user.id})")
        
        # 2. Pegar um ticket válido
        ticket = Ticket.objects.filter(is_active=True).first()
        if not ticket:
            print("❌ Nenhum ticket ativo encontrado!")
            return
        
        print(f"✅ Ticket selecionado: {ticket.type} (ID: {ticket.id})")
        print(f"   Evento: {ticket.event.name}")
        print(f"   Quantidade disponível: {ticket.quantity}")
        
        # 3. Simular a criação de uma compra
        print(f"\n🛒 CRIANDO COMPRA...")
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=1,
            total_price=ticket.price,
            status='pending'
        )
        print(f"✅ Compra criada: ID {purchase.id}")
        
        # 4. Verificar o estado da compra
        print(f"\n🔍 VERIFICANDO ESTADO DA COMPRA...")
        print(f"   Compra ID: {purchase.id}")
        print(f"   Ticket: {purchase.ticket.type if purchase.ticket else 'NONE'}")
        print(f"   Usuário: {purchase.user.username if purchase.user else 'NONE'}")
        print(f"   Status: {purchase.status}")
        
        # 5. Simular o acesso ao pagamento
        print(f"\n💳 SIMULANDO ACESSO AO PAGAMENTO...")
        try:
            # Verificar se o ticket ainda existe
            if purchase.ticket:
                print(f"   ✅ Ticket existe: {purchase.ticket.type}")
                print(f"   ✅ Evento do ticket: {purchase.ticket.event.name}")
            else:
                print(f"   ❌ PROBLEMA: Compra sem ticket!")
                return
            
            # Verificar se o evento ainda existe
            if purchase.ticket.event:
                print(f"   ✅ Evento existe: {purchase.ticket.event.name}")
            else:
                print(f"   ❌ PROBLEMA: Ticket sem evento!")
                return
            
            # Simular o que acontece no simple_payment
            print(f"\n🔄 SIMULANDO SIMPLE_PAYMENT...")
            
            # Verificar se o ticket ainda está ativo
            if purchase.ticket.is_active:
                print(f"   ✅ Ticket ativo: {purchase.ticket.is_active}")
            else:
                print(f"   ❌ PROBLEMA: Ticket inativo!")
                return
            
            # Verificar se o evento ainda está ativo
            if purchase.ticket.event.is_active:
                print(f"   ✅ Evento ativo: {purchase.ticket.event.is_active}")
            else:
                print(f"   ❌ PROBLEMA: Evento inativo!")
                return
            
            print(f"   ✅ Todos os checks passaram!")
            
        except Exception as e:
            print(f"   ❌ ERRO durante verificação: {e}")
            ErrorLogger.log_ticket_error(e, {
                'purchase_id': purchase.id,
                'ticket_id': purchase.ticket.id if purchase.ticket else None,
                'user_id': purchase.user.id if purchase.user else None,
            })
            return
        
        # 6. Limpar a compra de teste
        purchase.delete()
        print(f"\n🧹 Compra de teste removida")
        
        print(f"\n✅ TESTE CONCLUÍDO - NENHUM ERRO DETECTADO!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        ErrorLogger.log_ticket_error(e, {'test': 'payment_flow'})

def test_specific_scenarios():
    """
    Testar cenários específicos que podem causar o erro
    """
    print(f"\n🎯 TESTANDO CENÁRIOS ESPECÍFICOS")
    print("=" * 60)
    
    try:
        # Cenário 1: Compra com ticket que foi deletado
        print("1. Testando compra com ticket deletado...")
        ticket = Ticket.objects.filter(is_active=True).first()
        if ticket:
            # Criar compra
            User = get_user_model()
            user = User.objects.get(username='testuser')
            purchase = Purchase.objects.create(
                ticket=ticket,
                user=user,
                quantity=1,
                total_price=ticket.price,
                status='pending'
            )
            
            # Deletar o ticket
            ticket_id = ticket.id
            ticket.delete()
            
            # Tentar acessar a compra
            try:
                purchase = Purchase.objects.get(id=purchase.id)
                if purchase.ticket:
                    print(f"   ❌ PROBLEMA: Ticket {ticket_id} foi deletado mas ainda está na compra!")
                else:
                    print(f"   ✅ Ticket foi removido da compra corretamente")
            except Exception as e:
                print(f"   ❌ ERRO ao acessar compra: {e}")
            
            # Limpar
            purchase.delete()
        
        # Cenário 2: Compra com evento inativo
        print("\n2. Testando compra com evento inativo...")
        ticket = Ticket.objects.filter(is_active=True).first()
        if ticket:
            # Criar compra
            User = get_user_model()
            user = User.objects.get(username='testuser')
            purchase = Purchase.objects.create(
                ticket=ticket,
                user=user,
                quantity=1,
                total_price=ticket.price,
                status='pending'
            )
            
            # Desativar o evento
            ticket.event.is_active = False
            ticket.event.save()
            
            # Tentar acessar a compra
            try:
                purchase = Purchase.objects.get(id=purchase.id)
                if purchase.ticket.event.is_active:
                    print(f"   ❌ PROBLEMA: Evento está inativo mas ainda aparece como ativo!")
                else:
                    print(f"   ✅ Evento foi desativado corretamente")
            except Exception as e:
                print(f"   ❌ ERRO ao acessar compra: {e}")
            
            # Reativar o evento
            ticket.event.is_active = True
            ticket.event.save()
            
            # Limpar
            purchase.delete()
        
        print(f"\n✅ TESTES DE CENÁRIOS CONCLUÍDOS!")
        
    except Exception as e:
        print(f"❌ Erro nos testes de cenários: {e}")
        ErrorLogger.log_ticket_error(e, {'test': 'specific_scenarios'})

if __name__ == "__main__":
    test_complete_payment_flow()
    test_specific_scenarios()
