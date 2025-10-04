#!/usr/bin/env python3
"""
Script para corrigir configuração do WSGI no PythonAnywhere
Execute este script no console do PythonAnywhere
"""

import os
import sys

def fix_wsgi_configuration():
    """Corrige configuração do WSGI no PythonAnywhere"""
    
    print("🔧 Corrigendo configuração do WSGI no PythonAnywhere...")
    
    # Caminho do arquivo WSGI no PythonAnywhere
    wsgi_file = '/var/www/ingressoptga_pythonanywhere_com_wsgi.py'
    
    # Conteúdo correto do WSGI
    correct_wsgi_content = '''"""
WSGI config for ingressoptga project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Adicionar o caminho do projeto ao Python path
path = '/home/ingressoptga/ticketchecker'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''
    
    try:
        # Verificar se o arquivo existe
        if os.path.exists(wsgi_file):
            print(f"✅ Arquivo WSGI encontrado: {wsgi_file}")
            
            # Ler conteúdo atual
            with open(wsgi_file, 'r') as f:
                current_content = f.read()
            
            # Verificar se precisa de correção
            needs_fix = False
            
            if 'backend.settings_pythonanywhere' not in current_content:
                print("⚠️  WSGI não está usando settings_pythonanywhere")
                needs_fix = True
            
            if '/home/ingressoptga/ticketchecker' not in current_content:
                print("⚠️  Caminho do projeto incorreto no WSGI")
                needs_fix = True
            
            if needs_fix:
                print("🔧 Corrigindo arquivo WSGI...")
                
                # Fazer backup
                backup_file = wsgi_file + '.backup'
                with open(backup_file, 'w') as f:
                    f.write(current_content)
                print(f"✅ Backup criado: {backup_file}")
                
                # Escrever conteúdo correto
                with open(wsgi_file, 'w') as f:
                    f.write(correct_wsgi_content)
                print("✅ Arquivo WSGI corrigido")
            else:
                print("✅ Arquivo WSGI já está correto")
        else:
            print(f"❌ Arquivo WSGI não encontrado: {wsgi_file}")
            print("   Você precisa criar este arquivo no painel do PythonAnywhere")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir WSGI: {e}")
        return False

def verify_wsgi_configuration():
    """Verifica configuração do WSGI"""
    
    print("\n🔍 Verificando configuração do WSGI...")
    
    wsgi_file = '/var/www/ingressoptga_pythonanywhere_com_wsgi.py'
    
    if not os.path.exists(wsgi_file):
        print(f"❌ Arquivo WSGI não encontrado: {wsgi_file}")
        return False
    
    try:
        with open(wsgi_file, 'r') as f:
            content = f.read()
        
        print("Conteúdo do arquivo WSGI:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        
        # Verificações
        checks = [
            ('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere' in content),
            ('Caminho do projeto', '/home/ingressoptga/ticketchecker' in content),
            ('Import get_wsgi_application', 'get_wsgi_application' in content),
            ('Variável application', 'application = get_wsgi_application()' in content),
        ]
        
        print("\nVerificações:")
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Erro ao verificar WSGI: {e}")
        return False

def test_django_setup():
    """Testa configuração do Django"""
    
    print("\n🧪 Testando configuração do Django...")
    
    try:
        # Adicionar caminho do projeto
        project_path = '/home/ingressoptga/ticketchecker'
        if project_path not in sys.path:
            sys.path.append(project_path)
        
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
        
        import django
        django.setup()
        
        print("✅ Django configurado com sucesso")
        
        # Testar importação de modelos
        from events.models import Event, Ticket, Purchase
        print("✅ Modelos importados com sucesso")
        
        # Testar configuração de logging
        import logging
        logger = logging.getLogger('django')
        logger.info("Teste de logging - Django funcionando")
        print("✅ Sistema de logging funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Django: {e}")
        return False

def main():
    """Função principal"""
    
    print("🎯 Corrigindo configuração do WSGI no PythonAnywhere...")
    
    # 1. Verificar configuração atual
    if not verify_wsgi_configuration():
        print("❌ Configuração do WSGI tem problemas")
    
    # 2. Corrigir configuração
    if not fix_wsgi_configuration():
        print("❌ Falha ao corrigir WSGI")
        return False
    
    # 3. Verificar novamente
    if not verify_wsgi_configuration():
        print("❌ Configuração do WSGI ainda tem problemas")
        return False
    
    # 4. Testar Django
    if not test_django_setup():
        print("❌ Falha ao testar Django")
        return False
    
    print("\n🎉 Configuração do WSGI corrigida com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Reinicie sua aplicação web no PythonAnywhere")
    print("2. Verifique se não há mais erros nos logs")
    print("3. Teste o acesso ao site")
    
    return True

if __name__ == "__main__":
    main()