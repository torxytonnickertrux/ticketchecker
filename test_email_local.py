#!/usr/bin/env python
"""
Script para testar emails no ambiente local com MailHog
Execute: python test_email_local.py
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django para ambiente local
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_local')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from events.models import Event, Ticket, Purchase

def check_mailhog_connection():
    """Verifica se o MailHog está rodando"""
    print("🔍 Verificando conexão com MailHog...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 1025))
        sock.close()
        
        if result == 0:
            print("✅ MailHog está rodando na porta 1025")
            return True
        else:
            print("❌ MailHog não está rodando na porta 1025")
            print("💡 Execute: .\\mailhog\\MailHog.exe")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar MailHog: {e}")
        return False

def test_basic_email():
    """Testa envio básico de email"""
    print("🧪 Testando envio básico de email...")
    
    try:
        send_mail(
            subject='Teste Local - TicketChecker',
            message='Este é um teste de email local usando MailHog.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print("✅ Email básico enviado com sucesso!")
        print("📧 Verifique no MailHog: http://localhost:8025")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email básico: {e}")
        return False

def test_html_email():
    """Testa envio de email HTML"""
    print("🧪 Testando envio de email HTML...")
    
    try:
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .footer { background: #f3f4f6; padding: 10px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎫 TicketChecker</h1>
                <h2>Teste de Email HTML</h2>
            </div>
            <div class="content">
                <p>Este é um teste de email HTML do sistema TicketChecker.</p>
                <p><strong>Configuração Local:</strong></p>
                <ul>
                    <li>Servidor: MailHog (localhost:1025)</li>
                    <li>Interface Web: http://localhost:8025</li>
                    <li>Ambiente: Desenvolvimento Local</li>
                </ul>
                <p>✅ Se você está vendo este email, a configuração está funcionando!</p>
            </div>
            <div class="footer">
                <p>TicketChecker - Sistema de Gestão de Ingressos</p>
                <p>Desenvolvimento Local com MailHog</p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject='Teste HTML Local - TicketChecker',
            body='Versão texto do email HTML',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['test@example.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print("✅ Email HTML enviado com sucesso!")
        print("📧 Verifique no MailHog: http://localhost:8025")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email HTML: {e}")
        return False

def test_password_reset_email():
    """Testa template de recuperação de senha"""
    print("🧪 Testando template de recuperação de senha...")
    
    try:
        # Simular dados do template
        context = {
            'user': type('User', (), {
                'username': 'testuser',
                'get_full_name': lambda: 'Usuário Teste'
            })(),
            'protocol': 'http',
            'domain': 'localhost:8000',
            'uid': 'test_uid_123',
            'token': 'test_token_456'
        }
        
        html_content = render_to_string('registration/password_reset_email.html', context)
        
        email = EmailMultiAlternatives(
            subject='Teste de Recuperação Local - TicketChecker',
            body='Versão texto do email de recuperação',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['test@example.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print("✅ Email de recuperação enviado com sucesso!")
        print("📧 Verifique no MailHog: http://localhost:8025")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email de recuperação: {e}")
        return False

def test_multiple_recipients():
    """Testa envio para múltiplos destinatários"""
    print("🧪 Testando envio para múltiplos destinatários...")
    
    try:
        recipients = [
            'user1@example.com',
            'user2@example.com',
            'admin@example.com'
        ]
        
        send_mail(
            subject='Teste Múltiplos Destinatários - TicketChecker',
            message='Este email foi enviado para múltiplos destinatários.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        print(f"✅ Email enviado para {len(recipients)} destinatários!")
        print("📧 Verifique no MailHog: http://localhost:8025")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar para múltiplos destinatários: {e}")
        return False

def test_email_with_attachment():
    """Testa email com anexo"""
    print("🧪 Testando email com anexo...")
    
    try:
        from io import BytesIO
        
        # Criar um arquivo de teste
        test_content = "Este é um arquivo de teste para anexo.\nTicketChecker - Sistema de Gestão de Ingressos"
        test_file = BytesIO(test_content.encode('utf-8'))
        
        email = EmailMultiAlternatives(
            subject='Teste com Anexo - TicketChecker',
            body='Este email contém um anexo de teste.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['test@example.com']
        )
        
        email.attach('teste.txt', test_file.getvalue(), 'text/plain')
        email.send()
        
        print("✅ Email com anexo enviado com sucesso!")
        print("📧 Verifique no MailHog: http://localhost:8025")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email com anexo: {e}")
        return False

def show_email_settings():
    """Mostra configurações de email"""
    print("🔍 Configurações de Email Local:")
    print("=" * 50)
    
    settings_to_show = [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_USE_SSL',
        'EMAIL_HOST_USER',
        'DEFAULT_FROM_EMAIL',
        'SERVER_EMAIL'
    ]
    
    for setting in settings_to_show:
        value = getattr(settings, setting, 'NÃO CONFIGURADO')
        print(f"  {setting}: {value}")
    
    print("=" * 50)

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de email local com MailHog...")
    print("=" * 60)
    
    # Verificar conexão com MailHog
    if not check_mailhog_connection():
        print("\n❌ MailHog não está rodando!")
        print("💡 Para iniciar o MailHog:")
        print("   1. Execute: .\\setup_mailhog.bat")
        print("   2. Ou baixe manualmente de: https://github.com/mailhog/MailHog/releases")
        print("   3. Execute: .\\mailhog\\MailHog.exe")
        return
    
    print()
    
    # Mostrar configurações
    show_email_settings()
    print()
    
    # Executar testes
    tests = [
        test_basic_email,
        test_html_email,
        test_password_reset_email,
        test_multiple_recipients,
        test_email_with_attachment
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
        print("-" * 40)
    
    # Resumo dos resultados
    print("\n📊 Resumo dos Testes:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes aprovados: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram!")
        print("📧 Verifique os emails no MailHog: http://localhost:8025")
        print("🔧 A configuração de email local está funcionando perfeitamente!")
    else:
        print("\n⚠️  Alguns testes falharam.")
        print("🔍 Verifique os logs para mais detalhes.")
    
    print("\n💡 Próximos passos:")
    print("   1. Acesse http://localhost:8025 para ver os emails")
    print("   2. Teste o fluxo completo de recuperação de senha")
    print("   3. Configure o Django para usar settings_local.py")

if __name__ == '__main__':
    main()