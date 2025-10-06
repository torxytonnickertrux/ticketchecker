#!/usr/bin/env python3
"""
Script de configuração para produção
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
import subprocess
import shutil


class ProductionSetup:
    """
    Configuração para ambiente de produção
    """
    
    def __init__(self):
        self.base_dir = BASE_DIR
        self.static_root = self.base_dir / 'staticfiles'
        self.media_root = self.base_dir / 'media'
        self.logs_dir = self.base_dir / 'logs'
    
    def create_directories(self):
        """Criar diretórios necessários"""
        print("📁 Criando diretórios necessários...")
        
        directories = [
            self.static_root,
            self.media_root,
            self.logs_dir,
            self.base_dir / 'communication' / 'migrations',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")
    
    def collect_static_files(self):
        """Coletar arquivos estáticos"""
        print("\n📦 Coletando arquivos estáticos...")
        
        try:
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            print("✅ Arquivos estáticos coletados com sucesso")
        except Exception as e:
            print(f"❌ Erro ao coletar arquivos estáticos: {e}")
            return False
        
        return True
    
    def run_migrations(self):
        """Executar migrações"""
        print("\n🗄️ Executando migrações...")
        
        try:
            execute_from_command_line(['manage.py', 'makemigrations'])
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Migrações executadas com sucesso")
        except Exception as e:
            print(f"❌ Erro ao executar migrações: {e}")
            return False
        
        return True
    
    def create_superuser(self):
        """Criar superusuário"""
        print("\n👤 Criando superusuário...")
        
        try:
            from django.contrib.auth.models import User
            
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@ingressoptga.com',
                    password='admin123456'
                )
                print("✅ Superusuário criado: admin/admin123456")
            else:
                print("✅ Superusuário já existe")
        except Exception as e:
            print(f"❌ Erro ao criar superusuário: {e}")
            return False
        
        return True
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        print("\n📝 Configurando sistema de logging...")
        
        try:
            # Criar arquivo de log
            log_file = self.logs_dir / 'django.log'
            log_file.touch()
            
            # Configurar permissões
            os.chmod(log_file, 0o666)
            
            print(f"✅ Log configurado: {log_file}")
        except Exception as e:
            print(f"❌ Erro ao configurar logging: {e}")
            return False
        
        return True
    
    def setup_webhook_config(self):
        """Configurar webhooks"""
        print("\n🔗 Configurando webhooks...")
        
        webhook_config = {
            'test_url': 'https://ingressoptga.pythonanywhere.com/comunication/build/teste',
            'production_url': 'https://ingressoptga.pythonanywhere.com/comunication/build/production',
            'secret_key': '1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d',
            'events': ['payment', 'plan', 'subscription', 'invoice']
        }
        
        config_file = self.base_dir / 'webhook_config.json'
        
        try:
            import json
            with open(config_file, 'w') as f:
                json.dump(webhook_config, f, indent=2)
            
            print(f"✅ Configuração de webhook salva: {config_file}")
        except Exception as e:
            print(f"❌ Erro ao configurar webhook: {e}")
            return False
        
        return True
    
    def setup_environment_variables(self):
        """Configurar variáveis de ambiente"""
        print("\n🌍 Configurando variáveis de ambiente...")
        
        env_content = """# Configurações de Produção
SECRET_KEY=django-insecure-pm@#jrz=x#5ln7+r#9&)@&ezet-#292bjrf)^fqh110#$zrbq7
DEBUG=False
ALLOWED_HOSTS=ingressoptga.pythonanywhere.com,localhost,127.0.0.1

# Configurações do Banco de Dados
DATABASE_URL=sqlite:///db.sqlite3

# Configurações do Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812
MERCADO_PAGO_PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
MERCADO_PAGO_SANDBOX=True

# URLs do Sistema
SITE_URL=https://ingressoptga.pythonanywhere.com

# Configurações de Webhook
WEBHOOK_SECRET_KEY=1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
WEBHOOK_TIMEOUT=300

# Configurações de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=vgf.tools1@gmail.com
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=vgf.tools1@gmail.com

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/django.log

# Configurações de Produção
PRODUCTION=True
PYTHONANYWHERE=True
"""
        
        env_file = self.base_dir / '.env.production'
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print(f"✅ Variáveis de ambiente salvas: {env_file}")
        except Exception as e:
            print(f"❌ Erro ao configurar variáveis de ambiente: {e}")
            return False
        
        return True
    
    def test_system(self):
        """Testar sistema"""
        print("\n🧪 Testando sistema...")
        
        try:
            # Testar importações
            from communication.models import WebhookEvent, WebhookLog, PaymentNotification
            from events.models import Event, Ticket, Purchase
            print("✅ Modelos importados com sucesso")
            
            # Testar configurações
            print(f"✅ DEBUG: {settings.DEBUG}")
            print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
            print(f"✅ MERCADO_PAGO_ACCESS_TOKEN: {settings.MERCADO_PAGO_ACCESS_TOKEN[:20]}...")
            print(f"✅ WEBHOOK_SECRET_KEY: {settings.WEBHOOK_SECRET_KEY[:20]}...")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao testar sistema: {e}")
            return False
    
    def create_startup_script(self):
        """Criar script de inicialização"""
        print("\n🚀 Criando script de inicialização...")
        
        startup_script = """#!/bin/bash
# Script de inicialização para produção

echo "🚀 Iniciando sistema de ingressos..."

# Ativar ambiente virtual (se existir)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
"""
        
        script_file = self.base_dir / 'start_production.sh'
        
        try:
            with open(script_file, 'w') as f:
                f.write(startup_script)
            
            # Tornar executável
            os.chmod(script_file, 0o755)
            
            print(f"✅ Script de inicialização criado: {script_file}")
        except Exception as e:
            print(f"❌ Erro ao criar script de inicialização: {e}")
            return False
        
        return True
    
    def create_wsgi_config(self):
        """Criar configuração WSGI para PythonAnywhere"""
        print("\n⚙️ Criando configuração WSGI...")
        
        wsgi_content = """import os
import sys

# Adicionar o diretório do projeto ao Python path
path = '/mnt/d/Documentos/projetos/python/bot_analise_marketing/sistema_ingresso'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Importar aplicação WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""
        
        wsgi_file = self.base_dir / 'ticketchecker_wsgi.py'
        
        try:
            with open(wsgi_file, 'w') as f:
                f.write(wsgi_content)
            
            print(f"✅ Configuração WSGI criada: {wsgi_file}")
        except Exception as e:
            print(f"❌ Erro ao criar configuração WSGI: {e}")
            return False
        
        return True
    
    def run_setup(self):
        """Executar configuração completa"""
        print("🚀 Iniciando configuração para produção")
        print("=" * 50)
        
        steps = [
            ("Criar diretórios", self.create_directories),
            ("Executar migrações", self.run_migrations),
            ("Coletar arquivos estáticos", self.collect_static_files),
            ("Criar superusuário", self.create_superuser),
            ("Configurar logging", self.setup_logging),
            ("Configurar webhooks", self.setup_webhook_config),
            ("Configurar variáveis de ambiente", self.setup_environment_variables),
            ("Criar script de inicialização", self.create_startup_script),
            ("Criar configuração WSGI", self.create_wsgi_config),
            ("Testar sistema", self.test_system),
        ]
        
        results = []
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                result = step_func()
                results.append((step_name, result))
                if result:
                    print(f"✅ {step_name} concluído com sucesso")
                else:
                    print(f"❌ {step_name} falhou")
            except Exception as e:
                print(f"❌ {step_name} falhou com erro: {e}")
                results.append((step_name, False))
        
        # Resumo
        print("\n" + "=" * 50)
        print("📊 RESUMO DA CONFIGURAÇÃO")
        print("=" * 50)
        
        successful = sum(1 for _, result in results if result)
        total = len(results)
        
        for step_name, result in results:
            status = "✅" if result else "❌"
            print(f"{status} {step_name}")
        
        print(f"\nTotal: {successful}/{total} etapas concluídas com sucesso")
        
        if successful == total:
            print("🎉 Configuração para produção concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Configurar webhooks no Mercado Pago")
            print("2. Testar endpoints de webhook")
            print("3. Monitorar logs do sistema")
            print("4. Executar testes de integração")
        else:
            print("⚠️ Algumas etapas falharam. Verifique os erros acima.")
        
        return successful == total


def main():
    """Função principal"""
    setup = ProductionSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()