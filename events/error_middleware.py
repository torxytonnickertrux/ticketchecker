"""
Middleware para capturar e tratar erros de ticket
"""
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from .error_logger import ErrorLogger
import logging

logger = logging.getLogger(__name__)

class TicketErrorMiddleware:
    """
    Middleware para capturar erros relacionados a tickets
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Processa exceções relacionadas a tickets
        """
        # Log do erro
        ErrorLogger.log_ticket_error(exception, {
            'user_id': request.user.id if request.user.is_authenticated else None,
            'url': request.path,
            'method': request.method,
        })
        
        # Log do estado do banco
        ErrorLogger.log_database_state()
        
        # Tratar erros específicos
        if isinstance(exception, ObjectDoesNotExist):
            if 'ticket' in str(exception).lower():
                messages.error(request, 'Ticket não encontrado. Verifique se o ingresso ainda está disponível.')
                return redirect('event_list')
            elif 'purchase' in str(exception).lower():
                messages.error(request, 'Compra não encontrada.')
                return redirect('purchase_history')
        
        elif isinstance(exception, ValidationError):
            messages.error(request, f'Erro de validação: {str(exception)}')
            return redirect('event_list')
        
        elif isinstance(exception, IntegrityError):
            messages.error(request, 'Erro de integridade do banco de dados.')
            return redirect('event_list')
        
        # Se for uma requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': str(exception),
                'type': type(exception).__name__
            }, status=500)
        
        return None
