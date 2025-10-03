#!/usr/bin/env python
"""
Teste de acesso concorrente para identificar o erro real
"""
import os
import sys
import django
import threading
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from events.models import Event, Ticket, Purchase
from events.error_logger import ErrorLogger
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def simulate_concurrent_access():
    """
    Simular acesso concorrente que pode causar o erro
    """
    print("🔄 TESTE DE ACESSO CONCORRENTE")
    print("=" * 60)
    
    try:
        # 1. Criar uma compra
        User = get_user_model()
        user = User.objects.get(username='testuser')
        ticket = Ticket.objects.filter(is_active=True).first()
        
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=1,
            total_price=ticket.price,
            status='pending'
        )
        
        print(f"✅ Compra criada: ID {purchase.id}")
        
        # 2. Simular múltiplos acessos simultâneos
        def access_purchase(purchase_id, thread_id):
            try:
                print(f"   Thread {thread_id}: Acessando compra {purchase_id}")
                
                # Simular o que acontece no simple_payment
                purchase = Purchase.objects.get(id=purchase_id)
                
                if not purchase.ticket:
                    print(f"   Thread {thread_id}: ❌ PROBLEMA - Compra sem ticket!")
                    return
                
                # Verificar se o ticket ainda existe
                try:
                    ticket = Ticket.objects.get(id=purchase.ticket.id)
                    print(f"   Thread {thread_id}: ✅ Ticket existe: {ticket.type}")
                except Ticket.DoesNotExist:
                    print(f"   Thread {thread_id}: ❌ PROBLEMA - Ticket {purchase.ticket.id} não existe!")
                    return
                
                # Verificar se o evento existe
                if ticket.event:
                    print(f"   Thread {thread_id}: ✅ Evento existe: {ticket.event.name}")
                else:
                    print(f"   Thread {thread_id}: ❌ PROBLEMA - Ticket sem evento!")
                    return
                
                print(f"   Thread {thread_id}: ✅ Todos os checks passaram!")
                
            except Exception as e:
                print(f"   Thread {thread_id}: ❌ ERRO: {e}")
                ErrorLogger.log_ticket_error(e, {
                    'thread_id': thread_id,
                    'purchase_id': purchase_id,
                })
        
        # 3. Executar múltiplos threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=access_purchase, args=(purchase.id, i))
            threads.append(thread)
            thread.start()
        
        # Aguardar todos os threads
        for thread in threads:
            thread.join()
        
        # 4. Limpar
        purchase.delete()
        print(f"\n🧹 Compra de teste removida")
        
    except Exception as e:
        print(f"❌ Erro no teste concorrente: {e}")
        ErrorLogger.log_ticket_error(e, {'test': 'concurrent_access'})

def test_timing_issues():
    """
    Testar problemas de timing
    """
    print(f"\n⏰ TESTE DE PROBLEMAS DE TIMING")
    print("=" * 60)
    
    try:
        # 1. Criar uma compra
        User = get_user_model()
        user = User.objects.get(username='testuser')
        ticket = Ticket.objects.filter(is_active=True).first()
        
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=1,
            total_price=ticket.price,
            status='pending'
        )
        
        print(f"✅ Compra criada: ID {purchase.id}")
        
        # 2. Simular delay entre criação e acesso
        print(f"⏳ Aguardando 2 segundos...")
        time.sleep(2)
        
        # 3. Tentar acessar a compra
        try:
            purchase = Purchase.objects.get(id=purchase.id)
            print(f"✅ Compra acessada: {purchase.id}")
            
            if purchase.ticket:
                print(f"✅ Ticket existe: {purchase.ticket.type}")
            else:
                print(f"❌ PROBLEMA: Compra sem ticket!")
                return
            
            # 4. Simular o que acontece no simple_payment
            print(f"🔄 Simulando simple_payment...")
            
            # Verificar se o ticket ainda existe
            try:
                ticket = Ticket.objects.get(id=purchase.ticket.id)
                print(f"✅ Ticket encontrado: {ticket.type}")
            except Ticket.DoesNotExist:
                print(f"❌ PROBLEMA: Ticket {purchase.ticket.id} não existe!")
                return
            
            # Verificar se o evento existe
            if ticket.event:
                print(f"✅ Evento existe: {ticket.event.name}")
            else:
                print(f"❌ PROBLEMA: Ticket sem evento!")
                return
            
            print(f"✅ Todos os checks passaram!")
            
        except Exception as e:
            print(f"❌ ERRO ao acessar compra: {e}")
            ErrorLogger.log_ticket_error(e, {
                'purchase_id': purchase.id,
                'test': 'timing_issues'
            })
        
        # 5. Limpar
        purchase.delete()
        print(f"\n🧹 Compra de teste removida")
        
    except Exception as e:
        print(f"❌ Erro no teste de timing: {e}")
        ErrorLogger.log_ticket_error(e, {'test': 'timing_issues'})

if __name__ == "__main__":
    simulate_concurrent_access()
    test_timing_issues()
