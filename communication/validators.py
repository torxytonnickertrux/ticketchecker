"""
Validadores para webhooks do Mercado Pago
"""
import hashlib
import hmac
import time
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class WebhookValidator:
    """
    Validador de webhooks do Mercado Pago
    """
    
    # Chave secreta fornecida pelo usuário
    WEBHOOK_SECRET_KEY = "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"
    
    def validate_signature(self, payload, signature, timestamp, environment):
        """
        Validar assinatura do webhook
        
        Args:
            payload: Payload bruto do webhook
            signature: Assinatura do header X-Signature
            timestamp: Timestamp do header X-Signature-Ts
            environment: Ambiente (test/production)
        
        Returns:
            bool: True se a assinatura for válida
        """
        try:
            # Verificar se os parâmetros necessários estão presentes
            if not all([payload, signature, timestamp]):
                logger.warning("Parâmetros de validação incompletos")
                return False
            
            # Verificar se o timestamp não é muito antigo (máximo 5 minutos)
            try:
                ts = int(timestamp)
                current_ts = int(time.time())
                
                if abs(current_ts - ts) > 300:  # 5 minutos
                    logger.warning(f"Timestamp muito antigo: {ts}, atual: {current_ts}")
                    return False
                    
            except ValueError:
                logger.warning(f"Timestamp inválido: {timestamp}")
                return False
            
            # Construir string para validação
            # Formato: timestamp + payload
            validation_string = f"{timestamp}{payload}"
            
            # Calcular HMAC SHA256
            expected_signature = hmac.new(
                self.WEBHOOK_SECRET_KEY.encode('utf-8'),
                validation_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Comparar assinaturas de forma segura
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                logger.info(f"Assinatura válida para ambiente {environment}")
            else:
                logger.warning(f"Assinatura inválida para ambiente {environment}")
                logger.debug(f"Esperado: {expected_signature}")
                logger.debug(f"Recebido: {signature}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erro ao validar assinatura: {e}")
            return False
    
    def validate_payload(self, payload_data):
        """
        Validar estrutura do payload
        
        Args:
            payload_data: Dados do payload (dict)
        
        Returns:
            dict: Resultado da validação
        """
        try:
            errors = []
            
            # Verificar campos obrigatórios
            required_fields = ['id', 'type', 'data']
            for field in required_fields:
                if field not in payload_data:
                    errors.append(f"Campo obrigatório '{field}' não encontrado")
            
            # Verificar tipo de evento
            if 'type' in payload_data:
                valid_types = ['payment', 'plan', 'subscription', 'invoice', 'point_integration_whitelist']
                if payload_data['type'] not in valid_types:
                    errors.append(f"Tipo de evento inválido: {payload_data['type']}")
            
            # Verificar dados específicos para pagamento
            if payload_data.get('type') == 'payment':
                if 'data' not in payload_data or 'id' not in payload_data['data']:
                    errors.append("ID do pagamento não encontrado nos dados")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar payload: {e}")
            return {
                'valid': False,
                'errors': [f"Erro na validação: {str(e)}"]
            }
    
    def validate_environment(self, environment):
        """
        Validar se o ambiente é suportado
        
        Args:
            environment: Ambiente (test/production)
        
        Returns:
            bool: True se o ambiente for válido
        """
        valid_environments = ['test', 'production']
        return environment in valid_environments