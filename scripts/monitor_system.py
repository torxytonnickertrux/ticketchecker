#!/usr/bin/env python3
"""
Script de monitoramento do sistema de pagamentos
"""
import os
import sys
import django
from pathlib import Path
import requests
import json
import time
from datetime import datetime, timedelta

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from communication.models import WebhookEvent, WebhookLog, PaymentNotification
from events.models import Purchase
from django.utils import timezone


class SystemMonitor:
    """
    Monitor do sistema de pagamentos
    """
    
    def __init__(self):
        self.base_url = "https://ingressoptga.pythonanywhere.com"
        self.webhook_secret = "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"
    
    def check_webhook_health(self):
        """Verificar saúde dos webhooks"""
        print("🔍 Verificando saúde dos webhooks...")
        
        try:
            # Testar endpoint de teste
            response = requests.get(f"{self.base_url}/comunication/test/", timeout=30)
            if response.status_code == 200:
                print("✅ Endpoint de teste funcionando")
            else:
                print(f"❌ Endpoint de teste com problema: {response.status_code}")
                return False
            
            # Testar endpoint de status
            response = requests.get(f"{self.base_url}/comunication/status/", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint de status funcionando")
                print(f"   Total de eventos: {data['statistics']['total_events']}")
                print(f"   Eventos pendentes: {data['statistics']['pending_events']}")
                print(f"   Eventos processados: {data['statistics']['processed_events']}")
                print(f"   Eventos falharam: {data['statistics']['failed_events']}")
            else:
                print(f"❌ Endpoint de status com problema: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar saúde dos webhooks: {e}")
            return False
    
    def check_recent_events(self, hours=24):
        """Verificar eventos recentes"""
        print(f"\n📊 Verificando eventos das últimas {hours} horas...")
        
        since = timezone.now() - timedelta(hours=hours)
        
        # Eventos webhook
        webhook_events = WebhookEvent.objects.filter(received_at__gte=since)
        print(f"   Eventos webhook: {webhook_events.count()}")
        
        # Eventos por status
        for status, label in [('pending', 'Pendentes'), ('processed', 'Processados'), ('failed', 'Falharam'), ('ignored', 'Ignorados')]:
            count = webhook_events.filter(status=status).count()
            print(f"     {label}: {count}")
        
        # Eventos por tipo
        for event_type in ['payment', 'plan', 'subscription', 'invoice']:
            count = webhook_events.filter(event_type=event_type).count()
            if count > 0:
                print(f"     {event_type}: {count}")
        
        # Notificações de pagamento
        notifications = PaymentNotification.objects.filter(created_at__gte=since)
        print(f"   Notificações de pagamento: {notifications.count()}")
        
        # Notificações por tipo
        for notification_type in ['payment_approved', 'payment_rejected', 'payment_cancelled', 'payment_pending']:
            count = notifications.filter(notification_type=notification_type).count()
            if count > 0:
                print(f"     {notification_type}: {count}")
        
        # Compras recentes
        purchases = Purchase.objects.filter(purchase_date__gte=since)
        print(f"   Compras: {purchases.count()}")
        
        # Compras por status
        for status, label in [('pending', 'Pendentes'), ('processing', 'Processando'), ('approved', 'Aprovadas'), ('rejected', 'Rejeitadas')]:
            count = purchases.filter(status=status).count()
            if count > 0:
                print(f"     {label}: {count}")
        
        return True
    
    def check_failed_events(self):
        """Verificar eventos que falharam"""
        print("\n❌ Verificando eventos que falharam...")
        
        failed_events = WebhookEvent.objects.filter(status='failed').order_by('-received_at')[:10]
        
        if failed_events.count() == 0:
            print("✅ Nenhum evento falhou recentemente")
            return True
        
        print(f"⚠️ {failed_events.count()} eventos falharam recentemente:")
        
        for event in failed_events:
            print(f"   ID: {event.event_id}")
            print(f"   Tipo: {event.event_type}")
            print(f"   Recebido: {event.received_at}")
            print(f"   Erro: {event.error_message}")
            print(f"   Assinatura válida: {event.signature_valid}")
            print("   ---")
        
        return False
    
    def check_system_performance(self):
        """Verificar performance do sistema"""
        print("\n⚡ Verificando performance do sistema...")
        
        # Tempo de resposta dos endpoints
        endpoints = [
            ("/comunication/test/", "GET"),
            ("/comunication/status/", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=30)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # em ms
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: {response_time:.2f}ms")
                else:
                    print(f"❌ {endpoint}: {response.status_code} ({response_time:.2f}ms)")
                
            except Exception as e:
                print(f"❌ {endpoint}: Erro - {e}")
        
        return True
    
    def check_database_health(self):
        """Verificar saúde do banco de dados"""
        print("\n🗄️ Verificando saúde do banco de dados...")
        
        try:
            # Contar registros
            webhook_count = WebhookEvent.objects.count()
            log_count = WebhookLog.objects.count()
            notification_count = PaymentNotification.objects.count()
            purchase_count = Purchase.objects.count()
            
            print(f"   Eventos webhook: {webhook_count}")
            print(f"   Logs: {log_count}")
            print(f"   Notificações: {notification_count}")
            print(f"   Compras: {purchase_count}")
            
            # Verificar integridade
            orphaned_logs = WebhookLog.objects.filter(webhook_event__isnull=True).count()
            if orphaned_logs > 0:
                print(f"⚠️ {orphaned_logs} logs órfãos encontrados")
            else:
                print("✅ Nenhum log órfão encontrado")
            
            # Verificar eventos duplicados
            duplicate_events = WebhookEvent.objects.values('event_id').annotate(
                count=models.Count('event_id')
            ).filter(count__gt=1).count()
            
            if duplicate_events > 0:
                print(f"⚠️ {duplicate_events} eventos duplicados encontrados")
            else:
                print("✅ Nenhum evento duplicado encontrado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco de dados: {e}")
            return False
    
    def generate_report(self):
        """Gerar relatório completo"""
        print("📋 Gerando relatório completo do sistema...")
        print("=" * 60)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'webhook_health': self.check_webhook_health(),
            'recent_events': self.check_recent_events(),
            'failed_events': self.check_failed_events(),
            'performance': self.check_system_performance(),
            'database_health': self.check_database_health()
        }
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DO RELATÓRIO")
        print("=" * 60)
        
        if all(report.values()):
            print("🎉 Sistema funcionando perfeitamente!")
        else:
            print("⚠️ Alguns problemas foram detectados:")
            for key, value in report.items():
                if not value:
                    print(f"   - {key}")
        
        return report
    
    def run_continuous_monitoring(self, interval_minutes=5):
        """Executar monitoramento contínuo"""
        print(f"🔄 Iniciando monitoramento contínuo (intervalo: {interval_minutes} min)")
        print("Pressione Ctrl+C para parar")
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.generate_report()
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido pelo usuário")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor do sistema de pagamentos')
    parser.add_argument('--continuous', action='store_true', help='Executar monitoramento contínuo')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo em minutos para monitoramento contínuo')
    parser.add_argument('--hours', type=int, default=24, help='Horas para verificar eventos recentes')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.continuous:
        monitor.run_continuous_monitoring(args.interval)
    else:
        monitor.check_recent_events(args.hours)
        monitor.generate_report()


if __name__ == "__main__":
    main()