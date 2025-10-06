#!/usr/bin/env python3
"""
Script de validação final do sistema de pagamentos
"""
import os
import sys
import django
from pathlib import Path
import requests
import json
import time
import hmac
import hashlib

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from communication.models import WebhookEvent, WebhookLog, PaymentNotification
from events.models import Event, Ticket, Purchase, User
from django.utils import timezone


class SystemValidator:
    """
    Validador final do sistema de pagamentos
    """
    
    def __init__(self):
        self.base_url = "https://ingressoptga.pythonanywhere.com"
        self.webhook_secret = "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"
        self.validation_results = []
    
    def validate_configuration(self):
        """Validar configurações do sistema"""
        print("🔧 Validando configurações...")
        
        checks = [
            ("SECRET_KEY", settings.SECRET_KEY, "Configurado"),
            ("DEBUG", settings.DEBUG, "Configurado"),
            ("ALLOWED_HOSTS", settings.ALLOWED_HOSTS, "Configurado"),
            ("MERCADO_PAGO_ACCESS_TOKEN", settings.MERCADO_PAGO_ACCESS_TOKEN, "Configurado"),
            ("MERCADO_PAGO_PUBLIC_KEY", settings.MERCADO_PAGO_PUBLIC_KEY, "Configurado"),
            ("WEBHOOK_SECRET_KEY", settings.WEBHOOK_SECRET_KEY, "Configurado"),
            ("SITE_URL", settings.SITE_URL, "Configurado"),
        ]
        
        for name, value, expected in checks:
            if value:
                print(f"  ✅ {name}: {expected}")
                self.validation_results.append((name, True, "OK"))
            else:
                print(f"  ❌ {name}: Não configurado")
                self.validation_results.append((name, False, "Não configurado"))
    
    def validate_database(self):
        """Validar banco de dados"""
        print("\n🗄️ Validando banco de dados...")
        
        try:
            # Verificar se as tabelas existem
            webhook_count = WebhookEvent.objects.count()
            log_count = WebhookLog.objects.count()
            notification_count = PaymentNotification.objects.count()
            purchase_count = Purchase.objects.count()
            event_count = Event.objects.count()
            ticket_count = Ticket.objects.count()
            user_count = User.objects.count()
            
            print(f"  ✅ WebhookEvent: {webhook_count} registros")
            print(f"  ✅ WebhookLog: {log_count} registros")
            print(f"  ✅ PaymentNotification: {notification_count} registros")
            print(f"  ✅ Purchase: {purchase_count} registros")
            print(f"  ✅ Event: {event_count} registros")
            print(f"  ✅ Ticket: {ticket_count} registros")
            print(f"  ✅ User: {user_count} registros")
            
            self.validation_results.append(("Database", True, "OK"))
            
        except Exception as e:
            print(f"  ❌ Erro no banco de dados: {e}")
            self.validation_results.append(("Database", False, str(e)))
    
    def validate_webhook_endpoints(self):
        """Validar endpoints de webhook"""
        print("\n🔗 Validando endpoints de webhook...")
        
        endpoints = [
            ("/comunication/test/", "GET", "Teste de conectividade"),
            ("/comunication/status/", "GET", "Status do sistema"),
        ]
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=30)
                else:
                    response = requests.post(url, timeout=30)
                
                if response.status_code == 200:
                    print(f"  ✅ {endpoint}: {description} - OK")
                    self.validation_results.append((endpoint, True, "OK"))
                else:
                    print(f"  ❌ {endpoint}: {description} - Erro {response.status_code}")
                    self.validation_results.append((endpoint, False, f"Erro {response.status_code}"))
                    
            except Exception as e:
                print(f"  ❌ {endpoint}: {description} - Erro: {e}")
                self.validation_results.append((endpoint, False, str(e)))
    
    def validate_webhook_security(self):
        """Validar segurança dos webhooks"""
        print("\n🔒 Validando segurança dos webhooks...")
        
        # Teste com assinatura inválida
        payload = json.dumps({
            "id": "test_security_validation",
            "type": "payment",
            "data": {"id": "test_payment"}
        })
        
        timestamp = str(int(time.time()))
        invalid_signature = "invalid_signature"
        
        try:
            response = requests.post(
                f"{self.base_url}/comunication/build/teste",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Signature': invalid_signature,
                    'X-Signature-Ts': timestamp
                },
                timeout=30
            )
            
            if response.status_code == 400:
                print("  ✅ Assinatura inválida rejeitada corretamente")
                self.validation_results.append(("Webhook Security", True, "OK"))
            else:
                print(f"  ❌ Assinatura inválida aceita incorretamente: {response.status_code}")
                self.validation_results.append(("Webhook Security", False, "Falha na validação"))
                
        except Exception as e:
            print(f"  ❌ Erro ao testar segurança: {e}")
            self.validation_results.append(("Webhook Security", False, str(e)))
    
    def validate_webhook_processing(self):
        """Validar processamento de webhook"""
        print("\n⚙️ Validando processamento de webhook...")
        
        # Criar dados de teste
        user, created = User.objects.get_or_create(
            username='test_validation',
            defaults={
                'email': 'test@validation.com',
                'first_name': 'Test',
                'last_name': 'Validation'
            }
        )
        
        event, created = Event.objects.get_or_create(
            name='Evento Validação',
            defaults={
                'description': 'Evento para validação',
                'date': timezone.now() + timezone.timedelta(days=30),
                'location': 'Local Validação',
                'is_active': True
            }
        )
        
        ticket, created = Ticket.objects.get_or_create(
            event=event,
            type='Standard',
            defaults={
                'price': 50.00,
                'quantity': 100,
                'is_active': True
            }
        )
        
        purchase = Purchase.objects.create(
            ticket=ticket,
            user=user,
            quantity=1,
            total_price=50.00,
            status='pending'
        )
        
        # Dados do webhook
        payload = json.dumps({
            "id": "test_validation_processing",
            "type": "payment",
            "data": {"id": "test_payment_validation"}
        })
        
        timestamp = str(int(time.time()))
        signature = self._create_signature(payload, timestamp)
        
        try:
            response = requests.post(
                f"{self.base_url}/comunication/build/teste",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Signature': signature,
                    'X-Signature-Ts': timestamp
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print("  ✅ Webhook processado com sucesso")
                
                # Verificar se o evento foi criado
                webhook_event = WebhookEvent.objects.filter(event_id="test_validation_processing").first()
                if webhook_event:
                    print("  ✅ Evento webhook criado")
                    self.validation_results.append(("Webhook Processing", True, "OK"))
                else:
                    print("  ❌ Evento webhook não criado")
                    self.validation_results.append(("Webhook Processing", False, "Evento não criado"))
            else:
                print(f"  ❌ Erro no processamento: {response.status_code}")
                self.validation_results.append(("Webhook Processing", False, f"Erro {response.status_code}"))
                
        except Exception as e:
            print(f"  ❌ Erro ao processar webhook: {e}")
            self.validation_results.append(("Webhook Processing", False, str(e)))
    
    def validate_mercado_pago_integration(self):
        """Validar integração com Mercado Pago"""
        print("\n💳 Validando integração com Mercado Pago...")
        
        try:
            import mercadopago
            
            # Testar SDK
            mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            
            # Testar criação de preferência
            preference_data = {
                "items": [
                    {
                        "title": "Teste de Validação",
                        "quantity": 1,
                        "unit_price": 10.00,
                        "currency_id": "BRL"
                    }
                ],
                "external_reference": "test_validation"
            }
            
            result = mp.preference().create(preference_data)
            
            if result["status"] == 201:
                print("  ✅ SDK do Mercado Pago funcionando")
                print("  ✅ Criação de preferência funcionando")
                self.validation_results.append(("Mercado Pago Integration", True, "OK"))
            else:
                print(f"  ❌ Erro na criação de preferência: {result}")
                self.validation_results.append(("Mercado Pago Integration", False, "Erro na criação de preferência"))
                
        except Exception as e:
            print(f"  ❌ Erro na integração com Mercado Pago: {e}")
            self.validation_results.append(("Mercado Pago Integration", False, str(e)))
    
    def validate_system_performance(self):
        """Validar performance do sistema"""
        print("\n⚡ Validando performance do sistema...")
        
        endpoints = [
            ("/comunication/test/", "GET"),
            ("/comunication/status/", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(url, timeout=30)
                else:
                    response = requests.post(url, timeout=30)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # em ms
                
                if response.status_code == 200 and response_time < 5000:  # 5 segundos
                    print(f"  ✅ {endpoint}: {response_time:.2f}ms - OK")
                    self.validation_results.append((f"Performance {endpoint}", True, f"{response_time:.2f}ms"))
                else:
                    print(f"  ❌ {endpoint}: {response_time:.2f}ms - Lento ou erro")
                    self.validation_results.append((f"Performance {endpoint}", False, f"{response_time:.2f}ms"))
                    
            except Exception as e:
                print(f"  ❌ {endpoint}: Erro - {e}")
                self.validation_results.append((f"Performance {endpoint}", False, str(e)))
    
    def _create_signature(self, payload, timestamp):
        """Criar assinatura válida para teste"""
        validation_string = f"{timestamp}{payload}"
        return hmac.new(
            self.webhook_secret.encode('utf-8'),
            validation_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def generate_validation_report(self):
        """Gerar relatório de validação"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE VALIDAÇÃO FINAL")
        print("=" * 60)
        
        # Estatísticas
        total_checks = len(self.validation_results)
        successful_checks = sum(1 for _, success, _ in self.validation_results if success)
        failed_checks = total_checks - successful_checks
        
        print(f"Total de verificações: {total_checks}")
        print(f"Verificações bem-sucedidas: {successful_checks}")
        print(f"Verificações falharam: {failed_checks}")
        print(f"Taxa de sucesso: {(successful_checks/total_checks)*100:.1f}%")
        
        # Detalhes por verificação
        print(f"\n📋 DETALHES POR VERIFICAÇÃO:")
        print("-" * 60)
        
        for name, success, message in self.validation_results:
            status = "✅" if success else "❌"
            print(f"{status} {name}: {message}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        print("-" * 60)
        
        if successful_checks == total_checks:
            print("🎉 Sistema validado com sucesso! Pronto para produção.")
            print("📋 Próximos passos:")
            print("   1. Configurar webhooks no Mercado Pago")
            print("   2. Executar testes de integração")
            print("   3. Monitorar logs em produção")
            print("   4. Configurar alertas de monitoramento")
        else:
            print("⚠️ Algumas verificações falharam. Ações recomendadas:")
            print("   1. Revisar verificações que falharam")
            print("   2. Corrigir problemas identificados")
            print("   3. Executar validação novamente")
            print("   4. Verificar configurações do sistema")
        
        # Salvar relatório
        self.save_validation_report()
        
        return successful_checks == total_checks
    
    def save_validation_report(self):
        """Salvar relatório de validação"""
        report_file = Path(__file__).parent / 'validation_report.txt'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE VALIDAÇÃO DO SISTEMA DE PAGAMENTOS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de verificações: {len(self.validation_results)}\n")
                f.write(f"Verificações bem-sucedidas: {sum(1 for _, success, _ in self.validation_results if success)}\n")
                f.write(f"Verificações falharam: {sum(1 for _, success, _ in self.validation_results if not success)}\n\n")
                
                f.write("DETALHES POR VERIFICAÇÃO:\n")
                f.write("-" * 30 + "\n")
                
                for name, success, message in self.validation_results:
                    status = "SUCESSO" if success else "FALHOU"
                    f.write(f"{name}: {status} - {message}\n")
            
            print(f"\n📄 Relatório salvo em: {report_file}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
    
    def run_validation(self):
        """Executar validação completa"""
        print("🚀 Iniciando validação final do sistema de pagamentos")
        print("=" * 60)
        
        # Executar todas as validações
        self.validate_configuration()
        self.validate_database()
        self.validate_webhook_endpoints()
        self.validate_webhook_security()
        self.validate_webhook_processing()
        self.validate_mercado_pago_integration()
        self.validate_system_performance()
        
        # Gerar relatório
        return self.generate_validation_report()


def main():
    """Função principal"""
    validator = SystemValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 Sistema validado com sucesso!")
        sys.exit(0)
    else:
        print("\n⚠️ Sistema com problemas. Verifique o relatório.")
        sys.exit(1)


if __name__ == "__main__":
    main()