#!/usr/bin/env python
"""
Script para testar o fluxo completo de recuperação de senha
Execute: python test_complete_flow.py
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

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.urls import reverse

def create_test_user():
    """Cria um usuário de teste"""
    print("👤 Criando usuário de teste...")
    
    username = 'testuser'
    email = 'test@example.com'
    
    # Deletar usuário existente se houver
    try:
        user = User.objects.get(username=username)
        user.delete()
        print(f"   Usuário '{username}' existente removido")
    except User.DoesNotExist:
        pass
    
    # Criar novo usuário
    user = User.objects.create_user(
        username=username,
        email=email,
        password='testpassword123',
        first_name='Usuário',
        last_name='Teste'
    )
    
    print(f"✅ Usuário criado: {user.username} ({user.email})")
    return user

def test_password_reset_request(user):
    """Testa solicitação de recuperação de senha"""
    print("📧 Testando solicitação de recuperação de senha...")
    
    try:
        # Gerar token de recuperação
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Contexto para o template
        context = {
            'user': user,
            'protocol': 'http',
            'domain': 'localhost:8000',
            'uid': uid,
            'token': token,
        }
        
        # Renderizar template HTML
        html_content = render_to_string('registration/password_reset_email.html', context)
        
        # Enviar email
        send_mail(
            subject='Recuperação de Senha - TicketChecker',
            message='Versão texto do email de recuperação',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False,
        )
        
        print("✅ Email de recuperação enviado!")
        print(f"   Destinatário: {user.email}")
        print(f"   Token: {token[:10]}...")
        print("   📧 Verifique no MailHog: http://localhost:8025")
        
        return uid, token
        
    except Exception as e:
        print(f"❌ Erro ao enviar email de recuperação: {e}")
        return None, None

def test_password_reset_confirm(uid, token):
    """Testa confirmação de recuperação de senha"""
    print("🔐 Testando confirmação de recuperação...")
    
    try:
        from django.utils.http import urlsafe_base64_decode
        from django.contrib.auth.tokens import default_token_generator
        
        # Decodificar UID
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
        
        # Verificar token
        if default_token_generator.check_token(user, token):
            print("✅ Token válido!")
            print(f"   Usuário: {user.username}")
            print(f"   Email: {user.email}")
            
            # Simular alteração de senha
            new_password = 'newpassword123'
            user.set_password(new_password)
            user.save()
            
            print("✅ Senha alterada com sucesso!")
            print(f"   Nova senha: {new_password}")
            
            return True
        else:
            print("❌ Token inválido!")
            return False
            
    except Exception as e:
        print(f"❌ Erro na confirmação: {e}")
        return False

def test_login_with_new_password(user, new_password):
    """Testa login com nova senha"""
    print("🔑 Testando login com nova senha...")
    
    try:
        from django.contrib.auth import authenticate
        
        # Tentar autenticar com nova senha
        authenticated_user = authenticate(
            username=user.username,
            password=new_password
        )
        
        if authenticated_user:
            print("✅ Login com nova senha bem-sucedido!")
            print(f"   Usuário autenticado: {authenticated_user.username}")
            return True
        else:
            print("❌ Falha na autenticação com nova senha!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

def test_email_templates():
    """Testa todos os templates de email"""
    print("📄 Testando templates de email...")
    
    templates_to_test = [
        'registration/password_reset_email.html',
        'registration/password_reset_subject.txt',
    ]
    
    success_count = 0
    
    for template in templates_to_test:
        try:
            # Contexto de teste
            context = {
                'user': type('User', (), {
                    'username': 'testuser',
                    'get_full_name': lambda: 'Usuário Teste',
                    'email': 'test@example.com'
                })(),
                'protocol': 'http',
                'domain': 'localhost:8000',
                'uid': 'test_uid',
                'token': 'test_token'
            }
            
            # Renderizar template
            content = render_to_string(template, context)
            
            if content and len(content.strip()) > 0:
                print(f"✅ Template '{template}' renderizado com sucesso")
                success_count += 1
            else:
                print(f"❌ Template '{template}' está vazio")
                
        except Exception as e:
            print(f"❌ Erro no template '{template}': {e}")
    
    print(f"📊 Templates testados: {success_count}/{len(templates_to_test)}")
    return success_count == len(templates_to_test)

def cleanup_test_data():
    """Limpa dados de teste"""
    print("🧹 Limpando dados de teste...")
    
    try:
        # Remover usuário de teste
        test_user = User.objects.filter(username='testuser').first()
        if test_user:
            test_user.delete()
            print("✅ Usuário de teste removido")
        
        # Limpar logs se necessário
        log_file = 'email_debug.log'
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write('')
            print("✅ Log de email limpo")
            
    except Exception as e:
        print(f"⚠️  Erro na limpeza: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Teste Completo do Fluxo de Recuperação de Senha")
    print("=" * 60)
    
    # Verificar configurações
    print("🔍 Verificando configurações...")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Testar templates
    templates_ok = test_email_templates()
    print()
    
    if not templates_ok:
        print("❌ Problemas com templates. Verifique os arquivos.")
        return
    
    # Criar usuário de teste
    user = create_test_user()
    print()
    
    # Testar solicitação de recuperação
    uid, token = test_password_reset_request(user)
    print()
    
    if not uid or not token:
        print("❌ Falha na solicitação de recuperação")
        cleanup_test_data()
        return
    
    # Testar confirmação
    confirm_ok = test_password_reset_confirm(uid, token)
    print()
    
    if not confirm_ok:
        print("❌ Falha na confirmação de recuperação")
        cleanup_test_data()
        return
    
    # Testar login com nova senha
    login_ok = test_login_with_new_password(user, 'newpassword123')
    print()
    
    # Resumo final
    print("📊 Resumo do Teste Completo:")
    print("=" * 60)
    
    if templates_ok and uid and token and confirm_ok and login_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Fluxo completo de recuperação de senha funcionando")
        print("✅ Templates de email funcionando")
        print("✅ Envio de email funcionando")
        print("✅ Confirmação de token funcionando")
        print("✅ Alteração de senha funcionando")
        print("✅ Login com nova senha funcionando")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("❌ Verifique os logs para mais detalhes")
    
    print()
    print("💡 Próximos passos:")
    print("   1. Acesse http://localhost:8025 para ver os emails")
    print("   2. Teste manualmente em http://localhost:8000/accounts/password_reset/")
    print("   3. Verifique os logs em email_debug.log")
    
    # Limpeza
    cleanup_test_data()

if __name__ == '__main__':
    main()