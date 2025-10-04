#!/usr/bin/env python3
"""
Script para corrigir problemas de logging no PythonAnywhere
Execute este script no console do PythonAnywhere
"""

import os
import sys

def fix_logging_issues():
    """Corrige problemas de logging no PythonAnywhere"""
    
    print("🔧 Corrigindo problemas de logging no PythonAnywhere...")
    
    # 1. Verificar se estamos no diretório correto
    project_dir = '/home/ingressoptga/ticketchecker'
    if not os.path.exists(project_dir):
        print(f"❌ Diretório do projeto não encontrado: {project_dir}")
        return False
    
    os.chdir(project_dir)
    print(f"✅ Mudando para diretório: {project_dir}")
    
    # 2. Verificar se o arquivo settings_pythonanywhere.py existe
    settings_file = os.path.join(project_dir, 'backend', 'settings_pythonanywhere.py')
    if not os.path.exists(settings_file):
        print(f"❌ Arquivo de configuração não encontrado: {settings_file}")
        return False
    
    print("✅ Arquivo de configuração encontrado")
    
    # 3. Verificar configuração de logging no settings_pythonanywhere.py
    with open(settings_file, 'r') as f:
        content = f.read()
        
    if 'logging.FileHandler' in content:
        print("⚠️  Configuração de logging com FileHandler encontrada - pode causar problemas")
        print("   Recomendação: Use apenas StreamHandler para PythonAnywhere")
    else:
        print("✅ Configuração de logging parece estar correta")
    
    # 4. Testar importação do Django
    try:
        sys.path.insert(0, project_dir)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
        
        import django
        django.setup()
        print("✅ Django configurado com sucesso")
        
        # Testar configuração de logging
        import logging
        logger = logging.getLogger('django')
        logger.info("Teste de logging - se você vir esta mensagem, o logging está funcionando")
        print("✅ Sistema de logging funcionando")
        
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        return False
    
    # 5. Verificar permissões de diretórios
    directories_to_check = [
        '/home/ingressoptga/ticketchecker',
        '/home/ingressoptga/ticketchecker/staticfiles',
        '/home/ingressoptga/ticketchecker/media',
    ]
    
    for directory in directories_to_check:
        if os.path.exists(directory):
            if os.access(directory, os.W_OK):
                print(f"✅ Diretório com permissão de escrita: {directory}")
            else:
                print(f"⚠️  Diretório sem permissão de escrita: {directory}")
        else:
            print(f"⚠️  Diretório não existe: {directory}")
    
    print("\n🎉 Verificação concluída!")
    print("\n📋 Próximos passos:")
    print("1. Reinicie sua aplicação web no PythonAnywhere")
    print("2. Verifique os logs de erro")
    print("3. Teste o acesso ao site")
    
    return True

if __name__ == "__main__":
    fix_logging_issues()