from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class PurchaseErrorMiddleware:
    """
    Middleware para capturar e tratar erros relacionados a compras
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Processa exceções relacionadas a compras
        """
        # Log do erro para debug
        logger.error(f"Erro capturado pelo middleware: {exception}", exc_info=True)
        
        # Tratar erros de integridade referencial
        if isinstance(exception, ObjectDoesNotExist):
            if 'ticket' in str(exception).lower():
                messages.error(request, 'Ticket não encontrado ou foi removido.')
                return redirect('event_list')
            elif 'purchase' in str(exception).lower():
                messages.error(request, 'Compra não encontrada.')
                return redirect('purchase_history')
        
        # Tratar erros de validação
        if isinstance(exception, ValidationError):
            messages.error(request, f'Erro de validação: {str(exception)}')
            return redirect('event_list')
        
        # Tratar erros de integridade do banco
        if isinstance(exception, IntegrityError):
            if 'ticket' in str(exception).lower():
                messages.error(request, 'Erro de integridade: Ticket não encontrado.')
                return redirect('event_list')
            else:
                messages.error(request, 'Erro de integridade do banco de dados.')
                return redirect('event_list')
        
        # Se for uma requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': str(exception)
            }, status=400)
        
        return None
