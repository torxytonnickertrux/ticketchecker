"""
Decoradores para debug e captura de erros
"""
from functools import wraps
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from .error_logger import ErrorLogger
import traceback

def debug_ticket_flow(func):
    """
    Decorador para debug do fluxo de tickets
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # Log do início da função
            ErrorLogger.log_purchase_flow(f"START_{func.__name__}", {
                'args': args,
                'kwargs': kwargs,
                'user_id': request.user.id if request.user.is_authenticated else None,
            })
            
            # Executar função
            result = func(request, *args, **kwargs)
            
            # Log do sucesso
            ErrorLogger.log_purchase_flow(f"SUCCESS_{func.__name__}", {
                'result_type': type(result).__name__,
            })
            
            return result
            
        except Exception as e:
            # Log do erro
            ErrorLogger.log_ticket_error(e, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'user_id': request.user.id if request.user.is_authenticated else None,
            })
            
            # Tratar erro
            messages.error(request, f'Erro em {func.__name__}: {str(e)}')
            return redirect('event_list')
    
    return wrapper

def safe_ticket_access(func):
    """
    Decorador para acesso seguro a tickets
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # Verificar se há ticket_id nos kwargs
            if 'ticket_id' in kwargs:
                ticket_id = kwargs['ticket_id']
                ErrorLogger.log_purchase_flow(f"ACCESSING_TICKET_{ticket_id}", {
                    'ticket_id': ticket_id,
                    'user_id': request.user.id if request.user.is_authenticated else None,
                })
            
            return func(request, *args, **kwargs)
            
        except Exception as e:
            ErrorLogger.log_ticket_error(e, {
                'function': func.__name__,
                'ticket_id': kwargs.get('ticket_id'),
                'user_id': request.user.id if request.user.is_authenticated else None,
            })
            
            messages.error(request, 'Erro ao acessar ticket. Tente novamente.')
            return redirect('event_list')
    
    return wrapper

def safe_purchase_access(func):
    """
    Decorador para acesso seguro a compras
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # Verificar se há purchase_id nos kwargs
            if 'purchase_id' in kwargs:
                purchase_id = kwargs['purchase_id']
                ErrorLogger.log_purchase_flow(f"ACCESSING_PURCHASE_{purchase_id}", {
                    'purchase_id': purchase_id,
                    'user_id': request.user.id if request.user.is_authenticated else None,
                })
            
            return func(request, *args, **kwargs)
            
        except Exception as e:
            ErrorLogger.log_ticket_error(e, {
                'function': func.__name__,
                'purchase_id': kwargs.get('purchase_id'),
                'user_id': request.user.id if request.user.is_authenticated else None,
            })
            
            messages.error(request, 'Erro ao acessar compra. Tente novamente.')
            return redirect('purchase_history')
    
    return wrapper
