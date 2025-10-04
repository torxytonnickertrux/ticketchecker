"""
Sistema de logs de erro para capturar e resolver problemas
"""
import logging
import traceback
from django.conf import settings
from django.utils import timezone
from django.db import connection
import json

# Configurar logger específico para erros
logger = logging.getLogger('ticket_errors')

class ErrorLogger:
    """
    Classe para capturar e logar erros detalhados
    """
    
    @staticmethod
    def log_ticket_error(error, context=None):
        """
        Log específico para erros de ticket
        """
        error_data = {
            'timestamp': timezone.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc(),
            'user_id': context.get('user_id') if context else None,
            'ticket_id': context.get('ticket_id') if context else None,
            'purchase_id': context.get('purchase_id') if context else None,
        }
        
        logger.error(f"TICKET ERROR: {json.dumps(error_data, indent=2)}")
        
        # Log adicional para debug
        print(f"🔴 TICKET ERROR: {error}")
        print(f"📍 Context: {context}")
        print(f"📊 Traceback: {traceback.format_exc()}")
    
    @staticmethod
    def log_purchase_flow(step, data):
        """
        Log do fluxo de compra para debug
        """
        # Converter Decimal para float para evitar erro de serialização
        serializable_data = {}
        for key, value in data.items():
            if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                serializable_data[key] = float(value)
            else:
                serializable_data[key] = value
        
        flow_data = {
            'timestamp': timezone.now().isoformat(),
            'step': step,
            'data': serializable_data,
        }
        
        logger.info(f"PURCHASE FLOW: {json.dumps(flow_data, indent=2)}")
        print(f"🔄 PURCHASE FLOW - {step}: {serializable_data}")
    
    @staticmethod
    def log_database_state():
        """
        Log do estado atual do banco de dados
        """
        try:
            with connection.cursor() as cursor:
                # Verificar tickets
                cursor.execute("SELECT id, type, quantity, is_active FROM events_ticket LIMIT 5")
                tickets = cursor.fetchall()
                
                # Verificar compras
                cursor.execute("SELECT id, ticket_id, user_id, status FROM events_purchase ORDER BY id DESC LIMIT 5")
                purchases = cursor.fetchall()
                
                db_state = {
                    'tickets': tickets,
                    'purchases': purchases,
                }
                
                logger.info(f"DATABASE STATE: {json.dumps(db_state, indent=2)}")
                print(f"🗄️ DATABASE STATE: {db_state}")
                
        except Exception as e:
            logger.error(f"Error logging database state: {e}")
    
    @staticmethod
    def log_object_state(obj, obj_name):
        """
        Log do estado de um objeto específico
        """
        try:
            obj_data = {
                'object_name': obj_name,
                'object_type': type(obj).__name__,
                'object_id': getattr(obj, 'id', None),
                'object_attrs': {}
            }
            
            # Capturar atributos importantes
            important_attrs = ['id', 'ticket', 'user', 'status', 'quantity', 'total_price']
            for attr in important_attrs:
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    if hasattr(value, 'id'):
                        obj_data['object_attrs'][attr] = f"{type(value).__name__}(id={value.id})"
                    else:
                        obj_data['object_attrs'][attr] = str(value)
            
            logger.info(f"OBJECT STATE - {obj_name}: {json.dumps(obj_data, indent=2)}")
            print(f"🔍 OBJECT STATE - {obj_name}: {obj_data}")
            
        except Exception as e:
            logger.error(f"Error logging object state: {e}")
