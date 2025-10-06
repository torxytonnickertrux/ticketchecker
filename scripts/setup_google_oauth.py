#!/usr/bin/env python
"""
Script para configurar automaticamente o Google OAuth no Django
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider

def setup_google_oauth():
    """Configura o Google OAuth automaticamente"""
    
    print("Configurando Google OAuth...")
    
    # 1. Configurar Site
    try:
        site = Site.objects.get(id=1)
        site.domain = 'localhost:8000'
        site.name = 'TicketChecker'
        site.save()
        print("OK - Site configurado: localhost:8000")
    except Site.DoesNotExist:
        site = Site.objects.create(
            id=1,
            domain='localhost:8000',
            name='TicketChecker'
        )
        print("OK - Site criado: localhost:8000")
    
    # 2. Configurar SocialApp do Google
    try:
        # Remover aplicações existentes do Google
        SocialApp.objects.filter(provider='google').delete()
        
        # Criar nova aplicação
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=os.getenv('GOOGLE_OAUTH2_CLIENT_ID', ''),
            secret=os.getenv('GOOGLE_OAUTH2_SECRET', ''),
        )
        google_app.sites.add(site)
        
        print("OK - Aplicacao social Google configurada")
        
        if not google_app.client_id or not google_app.secret:
            print("ATENCAO: Credenciais do Google nao configuradas!")
            print("   Configure as variaveis de ambiente:")
            print("   GOOGLE_OAUTH2_CLIENT_ID=seu_client_id")
            print("   GOOGLE_OAUTH2_SECRET=seu_client_secret")
            print("   Ou configure manualmente no admin Django")
        
    except Exception as e:
        print(f"ERRO ao configurar aplicacao social: {e}")
        return False
    
    print("\nConfiguracao concluida!")
    print("\nProximos passos:")
    print("1. Configure as credenciais do Google no arquivo .env")
    print("2. Ou acesse o admin Django e configure manualmente")
    print("3. Teste o login em: http://localhost:8000/accounts/login/")
    
    return True

if __name__ == '__main__':
    setup_google_oauth()