#!/usr/bin/env python
"""
Script de análise para identificar o erro "Ticket não encontrado"
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from events.models import Event, Ticket, Purchase
from events.error_logger import ErrorLogger
from django.db import connection

def analyze_database_state():
    """
    Analisar o estado atual do banco de dados
    """
    print("🔍 ANÁLISE COMPLETA DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # 1. Verificar eventos
        events = Event.objects.all()
        print(f"📅 Total de eventos: {events.count()}")
        for event in events:
            print(f"   - Evento {event.id}: {event.name} (Ativo: {event.is_active})")
        
        # 2. Verificar tickets
        tickets = Ticket.objects.all()
        print(f"\n🎫 Total de tickets: {tickets.count()}")
        for ticket in tickets:
            print(f"   - Ticket {ticket.id}: {ticket.type} (Ativo: {ticket.is_active}, Qtd: {ticket.quantity})")
            if ticket.event:
                print(f"     Evento: {ticket.event.name} (ID: {ticket.event.id})")
            else:
                print(f"     ⚠️  PROBLEMA: Ticket sem evento!")
        
        # 3. Verificar compras
        purchases = Purchase.objects.all()
        print(f"\n🛒 Total de compras: {purchases.count()}")
        for purchase in purchases:
            print(f"   - Compra {purchase.id}: Status {purchase.status}")
            if purchase.ticket:
                print(f"     Ticket: {purchase.ticket.type} (ID: {purchase.ticket.id})")
            else:
                print(f"     ⚠️  PROBLEMA: Compra sem ticket!")
            
            if purchase.user:
                print(f"     Usuário: {purchase.user.username}")
            else:
                print(f"     ⚠️  PROBLEMA: Compra sem usuário!")
        
        # 4. Verificar relacionamentos problemáticos
        print(f"\n🚨 ANÁLISE DE PROBLEMAS:")
        
        # Tickets sem evento
        tickets_without_event = Ticket.objects.filter(event__isnull=True)
        print(f"   - Tickets sem evento: {tickets_without_event.count()}")
        
        # Compras sem ticket
        purchases_without_ticket = Purchase.objects.filter(ticket__isnull=True)
        print(f"   - Compras sem ticket: {purchases_without_ticket.count()}")
        
        # Compras sem usuário
        purchases_without_user = Purchase.objects.filter(user__isnull=True)
        print(f"   - Compras sem usuário: {purchases_without_user.count()}")
        
        # 5. Verificar SQL direto
        print(f"\n🗄️ VERIFICAÇÃO SQL DIRETA:")
        with connection.cursor() as cursor:
            # Verificar tabela events_ticket
            cursor.execute("SELECT id, type, quantity, is_active, event_id FROM events_ticket")
            ticket_rows = cursor.fetchall()
            print(f"   - Registros na tabela events_ticket: {len(ticket_rows)}")
            for row in ticket_rows:
                print(f"     ID: {row[0]}, Tipo: {row[1]}, Qtd: {row[2]}, Ativo: {row[3]}, Evento: {row[4]}")
            
            # Verificar tabela events_purchase
            cursor.execute("SELECT id, ticket_id, user_id, status, total_price FROM events_purchase")
            purchase_rows = cursor.fetchall()
            print(f"   - Registros na tabela events_purchase: {len(purchase_rows)}")
            for row in purchase_rows:
                print(f"     ID: {row[0]}, Ticket: {row[1]}, Usuário: {row[2]}, Status: {row[3]}, Total: {row[4]}")
        
        # 6. Log do estado para o sistema de debug
        ErrorLogger.log_database_state()
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        ErrorLogger.log_ticket_error(e, {'analysis': 'database_state'})

def analyze_specific_error():
    """
    Analisar o erro específico "Ticket não encontrado"
    """
    print("\n🎯 ANÁLISE DO ERRO ESPECÍFICO")
    print("=" * 50)
    
    try:
        # Simular o fluxo que causa o erro
        print("1. Verificando tickets ativos...")
        active_tickets = Ticket.objects.filter(is_active=True)
        print(f"   Tickets ativos: {active_tickets.count()}")
        
        if active_tickets.exists():
            ticket = active_tickets.first()
            print(f"   Primeiro ticket ativo: ID {ticket.id}, Tipo: {ticket.type}")
            
            # Verificar se o evento existe
            if ticket.event:
                print(f"   Evento do ticket: {ticket.event.name} (ID: {ticket.event.id})")
            else:
                print("   ⚠️  PROBLEMA: Ticket sem evento!")
            
            # Verificar se o ticket tem quantidade
            print(f"   Quantidade disponível: {ticket.quantity}")
            
            # Verificar se o ticket está disponível
            print(f"   Ticket disponível: {ticket.is_available}")
        
        # Verificar compras recentes
        print("\n2. Verificando compras recentes...")
        recent_purchases = Purchase.objects.order_by('-id')[:5]
        for purchase in recent_purchases:
            print(f"   Compra {purchase.id}:")
            print(f"     Status: {purchase.status}")
            print(f"     Ticket: {purchase.ticket.id if purchase.ticket else 'NONE'}")
            print(f"     Usuário: {purchase.user.username if purchase.user else 'NONE'}")
            
            # Verificar se o ticket da compra ainda existe
            if purchase.ticket:
                try:
                    ticket = Ticket.objects.get(id=purchase.ticket.id)
                    print(f"     ✅ Ticket existe: {ticket.type}")
                except Ticket.DoesNotExist:
                    print(f"     ❌ PROBLEMA: Ticket {purchase.ticket.id} não existe mais!")
            else:
                print(f"     ❌ PROBLEMA: Compra sem ticket!")
        
    except Exception as e:
        print(f"❌ Erro na análise específica: {e}")
        ErrorLogger.log_ticket_error(e, {'analysis': 'specific_error'})

if __name__ == "__main__":
    analyze_database_state()
    analyze_specific_error()
