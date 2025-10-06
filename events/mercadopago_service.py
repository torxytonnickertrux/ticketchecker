"""
Serviço de integração com Mercado Pago
"""
import mercadopago
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class MercadoPagoService:
    """
    Serviço para integração com Mercado Pago
    """
    
    def __init__(self):
        # Usar credenciais de teste para sandbox
        if settings.MERCADO_PAGO_SANDBOX:
            # Credenciais de teste (APP_USR- é correto para sandbox)
            test_token = "APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812"
            self.sdk = mercadopago.SDK(test_token)
            print(f"🔍 DEBUG MP: Usando credenciais de TESTE (sandbox)")
            print(f"🔍 DEBUG MP: Token usado: {test_token[:20]}...")
        else:
            self.sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            print(f"🔍 DEBUG MP: Usando credenciais de PRODUÇÃO")
            print(f"🔍 DEBUG MP: Token usado: {settings.MERCADO_PAGO_ACCESS_TOKEN[:20]}...")
    
    def create_payment(self, purchase, payment_data):
        """
        Criar pagamento no Mercado Pago
        
        Args:
            purchase: Instância do modelo Purchase
            payment_data: Dados do pagamento (método, dados do pagador, etc.)
        
        Returns:
            dict: Resposta do Mercado Pago
        """
        try:
            # Preparar dados do pagamento
            payment_request = {
                "transaction_amount": float(purchase.total_price),
                "description": f"Ingresso para {purchase.ticket.event.name}",
                "payment_method_id": payment_data.get('payment_method'),
                "payer": {
                    "email": payment_data.get('payer_email'),
                    "first_name": payment_data.get('payer_name', '').split(' ')[0] if payment_data.get('payer_name') else '',
                    "last_name": ' '.join(payment_data.get('payer_name', '').split(' ')[1:]) if payment_data.get('payer_name') and len(payment_data.get('payer_name', '').split(' ')) > 1 else '',
                    "identification": {
                        "type": "CPF",
                        "number": payment_data.get('payer_document', '')
                    }
                },
                "external_reference": str(purchase.id),
                "metadata": {
                    "purchase_id": purchase.id,
                    "ticket_id": purchase.ticket.id if purchase.ticket else None,
                    "event_id": purchase.ticket.event.id if purchase.ticket and purchase.ticket.event else None
                }
            }
            
            # Configurações específicas por método de pagamento
            if payment_data.get('payment_method') == 'pix':
                payment_request["payment_method_id"] = "pix"
                
            elif payment_data.get('payment_method') == 'credit_card':
                payment_request.update({
                    "token": payment_data.get('card_token'),
                    "installments": payment_data.get('installments', 1),
                    "payment_method_id": payment_data.get('card_payment_method_id')
                })
            
            # Criar pagamento
            result = self.sdk.payment().create(payment_request)
            
            if result["status"] == 201:
                logger.info(f"Pagamento criado com sucesso: {result['response']['id']}")
                return result["response"]
            else:
                logger.error(f"Erro ao criar pagamento: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na criação do pagamento: {e}")
            return None
    
    def get_payment(self, payment_id):
        """
        Buscar informações de um pagamento
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
        
        Returns:
            dict: Dados do pagamento
        """
        try:
            result = self.sdk.payment().get(payment_id)
            if result["status"] == 200:
                return result["response"]
            else:
                logger.error(f"Erro ao buscar pagamento {payment_id}: {result}")
                return None
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento {payment_id}: {e}")
            return None
    
    def cancel_payment(self, payment_id):
        """
        Cancelar um pagamento
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
        
        Returns:
            bool: True se cancelado com sucesso
        """
        try:
            result = self.sdk.payment().cancel(payment_id)
            if result["status"] == 200:
                logger.info(f"Pagamento {payment_id} cancelado com sucesso")
                return True
            else:
                logger.error(f"Erro ao cancelar pagamento {payment_id}: {result}")
                return False
        except Exception as e:
            logger.error(f"Erro ao cancelar pagamento {payment_id}: {e}")
            return False
    
    def refund_payment(self, payment_id, amount=None):
        """
        Reembolsar um pagamento
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
            amount: Valor do reembolso (opcional, se não informado reembolsa total)
        
        Returns:
            bool: True se reembolsado com sucesso
        """
        try:
            refund_data = {}
            if amount:
                refund_data["amount"] = float(amount)
            
            result = self.sdk.payment().refund(payment_id, refund_data)
            if result["status"] == 200:
                logger.info(f"Pagamento {payment_id} reembolsado com sucesso")
                return True
            else:
                logger.error(f"Erro ao reembolsar pagamento {payment_id}: {result}")
                return False
        except Exception as e:
            logger.error(f"Erro ao reembolsar pagamento {payment_id}: {e}")
            return False
    
    def create_preference(self, purchase, payment_data):
        """
        Criar preferência de pagamento (Checkout Pro)
        
        Args:
            purchase: Instância do modelo Purchase
            payment_data: Dados do pagamento
        
        Returns:
            dict: Resposta do Mercado Pago
        """
        try:
            # Verificar se o ticket existe
            if not purchase.ticket:
                logger.error(f"Purchase {purchase.id} não tem ticket associado")
                return None
            
            preference_data = {
                "items": [
                    {
                        "title": f"Ingresso {purchase.ticket.type} - {purchase.ticket.event.name}",
                        "quantity": purchase.quantity,
                        "unit_price": float(purchase.ticket.price),
                        "currency_id": "BRL"
                    }
                ],
                "payer": {
                    "email": payment_data.get('payer_email'),
                    "name": payment_data.get('payer_name', ''),
                    "identification": {
                        "type": "CPF",
                        "number": payment_data.get('payer_document', '')
                    }
                },
                "external_reference": str(purchase.id),
                "back_urls": {
                    "success": f"{settings.SITE_URL}/payment/success/",
                    "failure": f"{settings.SITE_URL}/payment/failure/",
                    "pending": f"{settings.SITE_URL}/payment/pending/"
                },
                "metadata": {
                    "purchase_id": purchase.id,
                    "ticket_id": purchase.ticket.id,
                    "event_id": purchase.ticket.event.id
                }
            }
            
            # Configurar métodos de pagamento permitidos
            if payment_data.get('payment_method') == 'pix':
                preference_data["payment_methods"] = {
                    "excluded_payment_methods": [
                        {"id": "credit_card"},
                        {"id": "debit_card"},
                        {"id": "bank_transfer"},
                        {"id": "atm"},
                        {"id": "bolbradesco"},
                        {"id": "pec"},
                        {"id": "pagofacil"},
                        {"id": "rapipago"}
                    ],
                    "excluded_payment_types": [
                        {"id": "credit_card"},
                        {"id": "debit_card"}
                    ],
                    "installments": 1
                }
            elif payment_data.get('payment_method') == 'credit_card':
                preference_data["payment_methods"] = {
                    "excluded_payment_methods": [
                        {"id": "pix"},
                        {"id": "debit_card"}
                    ]
                }
            
            result = self.sdk.preference().create(preference_data)
            
            if result["status"] == 201:
                logger.info(f"Preferência criada com sucesso: {result['response']['id']}")
                return result["response"]
            else:
                logger.error(f"Erro ao criar preferência: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na criação da preferência: {e}")
            return None
    
    def create_pix_payment(self, purchase, payment_data):
        """
        Criar pagamento PIX direto (não via preferência)
        
        Args:
            purchase: Instância do modelo Purchase
            payment_data: Dados do pagamento
        
        Returns:
            dict: Resposta do Mercado Pago com QR Code PIX
        """
        try:
            print(f"🔍 DEBUG PIX: Iniciando criação de pagamento PIX para purchase {purchase.id}")
            
            # Verificar se o ticket existe
            if not purchase.ticket:
                logger.error(f"Purchase {purchase.id} não tem ticket associado")
                print(f"❌ DEBUG PIX: Purchase {purchase.id} não tem ticket associado")
                return None
            
            print(f"🔍 DEBUG PIX: Ticket encontrado - {purchase.ticket.type} - R$ {purchase.total_price}")
            
            payment_request = {
                "transaction_amount": float(purchase.total_price),
                "description": f"Ingresso {purchase.ticket.type} - {purchase.ticket.event.name}",
                "payment_method_id": "pix",
                "payer": {
                    "email": payment_data.get('payer_email'),
                    "first_name": payment_data.get('payer_name', '').split(' ')[0] if payment_data.get('payer_name') else '',
                    "last_name": ' '.join(payment_data.get('payer_name', '').split(' ')[1:]) if payment_data.get('payer_name') and len(payment_data.get('payer_name', '').split(' ')) > 1 else '',
                    "identification": {
                        "type": "CPF",
                        "number": payment_data.get('payer_document', '')
                    }
                },
                "external_reference": str(purchase.id),
                "metadata": {
                    "purchase_id": purchase.id,
                    "ticket_id": purchase.ticket.id,
                    "event_id": purchase.ticket.event.id
                }
            }
            
            print(f"🔍 DEBUG PIX: Dados do pagamento: {payment_request}")
            
            # Criar pagamento PIX
            result = self.sdk.payment().create(payment_request)
            
            print(f"🔍 DEBUG PIX: Resultado do Mercado Pago: {result}")
            
            if result["status"] == 201:
                logger.info(f"Pagamento PIX criado com sucesso: {result['response']['id']}")
                print(f"✅ DEBUG PIX: Pagamento PIX criado com sucesso: {result['response']['id']}")
                return result["response"]
            else:
                logger.error(f"Erro ao criar pagamento PIX: {result}")
                print(f"❌ DEBUG PIX: Erro ao criar pagamento PIX: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na criação do pagamento PIX: {e}")
            print(f"❌ DEBUG PIX: Exceção na criação do pagamento PIX: {e}")
            return None