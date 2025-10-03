"""
Views de debug para administradores
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import connection
from .models import Ticket, Purchase, Event
from .error_logger import ErrorLogger
import json

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def debug_dashboard(request):
    """
    Dashboard de debug para administradores
    """
    try:
        # Estatísticas gerais
        stats = {
            'total_events': Event.objects.count(),
            'total_tickets': Ticket.objects.count(),
            'total_purchases': Purchase.objects.count(),
            'active_tickets': Ticket.objects.filter(is_active=True).count(),
            'pending_purchases': Purchase.objects.filter(status='pending').count(),
            'processing_purchases': Purchase.objects.filter(status='processing').count(),
            'approved_purchases': Purchase.objects.filter(status='approved').count(),
        }
        
        # Tickets com problemas
        problematic_tickets = Ticket.objects.filter(
            models.Q(quantity__lt=0) | 
            models.Q(price__lt=0) |
            models.Q(event__isnull=True)
        )
        
        # Compras com problemas
        problematic_purchases = Purchase.objects.filter(
            models.Q(ticket__isnull=True) |
            models.Q(quantity__lt=1) |
            models.Q(total_price__lt=0)
        )
        
        # Log do estado atual
        ErrorLogger.log_database_state()
        
        context = {
            'stats': stats,
            'problematic_tickets': problematic_tickets,
            'problematic_purchases': problematic_purchases,
        }
        
        return render(request, 'events/debug_dashboard.html', context)
        
    except Exception as e:
        ErrorLogger.log_ticket_error(e, {
            'user_id': request.user.id,
            'view': 'debug_dashboard',
        })
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_staff)
def debug_ticket(request, ticket_id):
    """
    Debug de um ticket específico
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        
        # Log do estado do ticket
        ErrorLogger.log_object_state(ticket, f"DEBUG_TICKET_{ticket_id}")
        
        # Compras relacionadas
        purchases = Purchase.objects.filter(ticket=ticket)
        
        # Log das compras
        for purchase in purchases:
            ErrorLogger.log_object_state(purchase, f"DEBUG_PURCHASE_{purchase.id}")
        
        context = {
            'ticket': ticket,
            'purchases': purchases,
        }
        
        return render(request, 'events/debug_ticket.html', context)
        
    except Exception as e:
        ErrorLogger.log_ticket_error(e, {
            'ticket_id': ticket_id,
            'user_id': request.user.id,
        })
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_staff)
def debug_purchase(request, purchase_id):
    """
    Debug de uma compra específica
    """
    try:
        purchase = Purchase.objects.get(pk=purchase_id)
        
        # Log do estado da compra
        ErrorLogger.log_object_state(purchase, f"DEBUG_PURCHASE_{purchase_id}")
        
        # Verificar se o ticket existe
        ticket_exists = purchase.ticket is not None
        ticket_active = purchase.ticket.is_active if ticket_exists else False
        
        context = {
            'purchase': purchase,
            'ticket_exists': ticket_exists,
            'ticket_active': ticket_active,
        }
        
        return render(request, 'events/debug_purchase.html', context)
        
    except Exception as e:
        ErrorLogger.log_ticket_error(e, {
            'purchase_id': purchase_id,
            'user_id': request.user.id,
        })
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_staff)
def debug_logs(request):
    """
    Visualizar logs de debug
    """
    try:
        # Aqui você pode implementar a leitura dos logs
        # Por simplicidade, vamos retornar uma mensagem
        context = {
            'message': 'Logs de debug disponíveis no console e arquivo de log',
        }
        
        return render(request, 'events/debug_logs.html', context)
        
    except Exception as e:
        ErrorLogger.log_ticket_error(e, {
            'user_id': request.user.id,
            'view': 'debug_logs',
        })
        return JsonResponse({'error': str(e)}, status=500)
