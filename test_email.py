#!/usr/bin/env python
"""
Script para testar a configuração de email do Django
Execute: python test_email.py
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

def test_basic_email():
    """Testa envio básico de email"""
    print("🧪 Testando envio básico de email...")
    
    try:
        send_mail(
            subject='Teste de Email - TicketChecker',
            message='Este é um teste de configuração de email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['vgf.tools1@gmail.com'],
            fail_silently=False,
        )
        print("✅ Email básico enviado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email básico: {e}")
        return False

def test_html_email():
    """Testa envio de email HTML"""
    print("🧪 Testando envio de email HTML...")
    
    try:
        # Renderizar template HTML
        html_content = """
        <html>
        <body>
            <h2>Teste de Email HTML</h2>
            <p>Este é um teste de email HTML do sistema TicketChecker.</p>
            <p><strong>Configuração:</strong></p>
            <ul>
                <li>Host: {EMAIL_HOST}</li>
                <li>Porta: {EMAIL_PORT}</li>
                <li>TLS: {EMAIL_USE_TLS}</li>
                <li>Usuário: {EMAIL_HOST_USER}</li>
            </ul>
        </body>
        </html>
        """.format(
            EMAIL_HOST=settings.EMAIL_HOST,
            EMAIL_PORT=settings.EMAIL_PORT,
            EMAIL_USE_TLS=settings.EMAIL_USE_TLS,
            EMAIL_HOST_USER=settings.EMAIL_HOST_USER
        )
        
        email = EmailMultiAlternatives(
            subject='Teste HTML - TicketChecker',
            body='Versão texto do email',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['vgf.tools1@gmail.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print("✅ Email HTML enviado com sucesso!")
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
            'uid': 'test_uid',
            'token': 'test_token'
        }
        
        html_content = render_to_string('registration/password_reset_email.html', context)
        
        email = EmailMultiAlternatives(
            subject='Teste de Recuperação - TicketChecker',
            body='Versão texto do email de recuperação',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['vgf.tools1@gmail.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        print("✅ Email de recuperação enviado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email de recuperação: {e}")
        return False

def check_email_settings():
    """Verifica configurações de email"""
    print("🔍 Verificando configurações de email...")
    
    settings_to_check = [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_HOST_USER',
        'DEFAULT_FROM_EMAIL',
        'SERVER_EMAIL'
    ]
    
    for setting in settings_to_check:
        value = getattr(settings, setting, 'NÃO CONFIGURADO')
        print(f"  {setting}: {value}")
    
    # Verificar se EMAIL_HOST_PASSWORD está configurado
    password = os.getenv('EMAIL_HOST_PASSWORD', '')
    if password:
        print(f"  EMAIL_HOST_PASSWORD: {'*' * len(password)} (configurado)")
    else:
        print("  EMAIL_HOST_PASSWORD: NÃO CONFIGURADO")
        print("  ⚠️  Configure a senha de app do Gmail no arquivo .env")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de configuração de email...")
    print("=" * 50)
    
    # Verificar configurações
    check_email_settings()
    print()
    
    # Verificar se EMAIL_HOST_PASSWORD está configurado
    password = os.getenv('EMAIL_HOST_PASSWORD', '')
    if not password:
        print("❌ EMAIL_HOST_PASSWORD não está configurado!")
        print("📝 Configure a senha de app do Gmail no arquivo .env")
        print("📖 Consulte docs/CONFIGURACAO_EMAIL_RECUPERACAO.md para instruções")
        return
    
    # Executar testes
    tests = [
        test_basic_email,
        test_html_email,
        test_password_reset_email
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
        print("-" * 30)
    
    # Resumo dos resultados
    print("\n📊 Resumo dos Testes:")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes aprovados: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! A configuração de email está funcionando.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as configurações.")
        print("📖 Consulte docs/CONFIGURACAO_EMAIL_RECUPERACAO.md para solução de problemas.")

if __name__ == '__main__':
    main()