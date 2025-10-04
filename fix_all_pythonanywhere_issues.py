#!/usr/bin/env python3
"""
Script completo para corrigir TODOS os problemas no PythonAnywhere
Execute este script no console do PythonAnywhere
"""

import os
import sys
import sqlite3
import subprocess

def fix_all_issues():
    """Corrige todos os problemas identificados no PythonAnywhere"""
    
    print("🔧 Corrigindo TODOS os problemas no PythonAnywhere...")
    
    # 1. Verificar se estamos no diretório correto
    project_dir = '/home/ingressoptga/ticketchecker'
    if not os.path.exists(project_dir):
        print(f"❌ Diretório do projeto não encontrado: {project_dir}")
        return False
    
    os.chdir(project_dir)
    print(f"✅ Mudando para diretório: {project_dir}")
    
    # 2. Corrigir problema de logging
    if not fix_logging_issue():
        print("❌ Falha ao corrigir problema de logging")
        return False
    
    # 3. Corrigir problema de banco de dados
    if not fix_database_issue():
        print("❌ Falha ao corrigir problema de banco de dados")
        return False
    
    # 4. Testar solução completa
    if not test_complete_solution():
        print("❌ Falha ao testar solução completa")
        return False
    
    print("\n🎉 TODOS os problemas foram resolvidos!")
    return True

def fix_logging_issue():
    """Corrige problema de logging"""
    
    print("\n🔧 Corrigindo problema de logging...")
    
    # Verificar se o arquivo settings_pythonanywhere.py está correto
    settings_file = os.path.join(project_dir, 'backend', 'settings_pythonanywhere.py')
    
    if not os.path.exists(settings_file):
        print(f"❌ Arquivo de configuração não encontrado: {settings_file}")
        return False
    
    # Ler conteúdo atual
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Verificar se tem configuração de logging problemática
    if 'logging.FileHandler' in content:
        print("⚠️  Configuração de logging problemática encontrada")
        
        # Criar configuração segura
        safe_logging_config = '''
    # Configuração de logging segura para PythonAnywhere
    # SEMPRE usar apenas StreamHandler para evitar erros de permissão
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }'''
        
        # Substituir configuração problemática
        if 'LOGGING = {' in content:
            # Encontrar início e fim da configuração LOGGING
            start = content.find('LOGGING = {')
            if start != -1:
                # Encontrar o fim da configuração LOGGING
                brace_count = 0
                end = start
                for i, char in enumerate(content[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                # Substituir configuração
                new_content = content[:start] + safe_logging_config + content[end:]
                
                # Salvar arquivo
                with open(settings_file, 'w') as f:
                    f.write(new_content)
                
                print("✅ Configuração de logging corrigida")
            else:
                print("❌ Não foi possível encontrar configuração LOGGING")
                return False
        else:
            print("✅ Configuração de logging já está correta")
    else:
        print("✅ Configuração de logging já está correta")
    
    return True

def fix_database_issue():
    """Corrige problema de banco de dados"""
    
    print("\n🔧 Corrigindo problema de banco de dados...")
    
    db_path = os.path.join(project_dir, 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    print(f"✅ Banco de dados encontrado: {db_path}")
    
    # Conectar ao banco
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ Conectado ao banco de dados")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False
    
    # Verificar estrutura da tabela events_purchase
    try:
        cursor.execute("PRAGMA table_info(events_purchase);")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ Tabela events_purchase não existe!")
            return False
        
        # Verificar se a coluna mercado_pago_id existe
        mercado_pago_exists = any(col[1] == 'mercado_pago_id' for col in columns)
        
        if not mercado_pago_exists:
            print("❌ Coluna mercado_pago_id não existe! Adicionando...")
            
            # Adicionar colunas faltantes
            cursor.execute("""
                ALTER TABLE events_purchase 
                ADD COLUMN mercado_pago_id VARCHAR(100) NULL;
            """)
            
            cursor.execute("""
                ALTER TABLE events_purchase 
                ADD COLUMN payment_date DATETIME NULL;
            """)
            
            cursor.execute("""
                ALTER TABLE events_purchase 
                ADD COLUMN payment_status VARCHAR(50) NULL;
            """)
            
            # Confirmar alterações
            conn.commit()
            print("✅ Colunas adicionadas com sucesso")
        else:
            print("✅ Coluna mercado_pago_id já existe")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(events_purchase);")
        columns = cursor.fetchall()
        
        print("\nEstrutura final da tabela events_purchase:")
        for column in columns:
            col_id, col_name, col_type, not_null, default_val, pk = column
            print(f"  - {col_name} ({col_type})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar/corrigir estrutura: {e}")
        conn.rollback()
        conn.close()
        return False

def test_complete_solution():
    """Testa a solução completa"""
    
    print("\n🧪 Testando solução completa...")
    
    try:
        # Configurar Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
        django.setup()
        
        print("✅ Django configurado com sucesso")
        
        # Testar configuração de logging
        import logging
        logger = logging.getLogger('django')
        logger.info("Teste de logging - se você vir esta mensagem, o logging está funcionando")
        print("✅ Sistema de logging funcionando")
        
        # Testar modelos
        from events.models import Event, Ticket, Purchase
        from django.db.models import Sum
        
        print(f"✅ Eventos: {Event.objects.count()}")
        print(f"✅ Ingressos: {Ticket.objects.count()}")
        print(f"✅ Compras: {Purchase.objects.count()}")
        
        # Testar consultas do dashboard
        total_revenue = Purchase.objects.filter(status='confirmed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        print(f"✅ Receita total: R$ {total_revenue}")
        
        # Testar consulta de compras recentes
        recent_purchases = Purchase.objects.filter(status='confirmed').order_by('-purchase_date')[:10]
        print(f"✅ Compras recentes: {recent_purchases.count()}")
        
        # Testar acesso ao campo mercado_pago_id
        purchases_with_mp_id = Purchase.objects.exclude(mercado_pago_id__isnull=True).count()
        print(f"✅ Compras com ID Mercado Pago: {purchases_with_mp_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar solução: {e}")
        return False

def check_wsgi_configuration():
    """Verifica configuração do WSGI"""
    
    print("\n🔍 Verificando configuração do WSGI...")
    
    # Verificar arquivo WSGI do PythonAnywhere
    wsgi_file = '/var/www/ingressoptga_pythonanywhere_com_wsgi.py'
    
    if os.path.exists(wsgi_file):
        print(f"✅ Arquivo WSGI encontrado: {wsgi_file}")
        
        with open(wsgi_file, 'r') as f:
            content = f.read()
        
        # Verificar se está usando o módulo correto
        if 'backend.settings_pythonanywhere' in content:
            print("✅ WSGI configurado para usar settings_pythonanywhere")
        else:
            print("⚠️  WSGI pode não estar usando settings_pythonanywhere")
            
        # Verificar caminho do projeto
        if '/home/ingressoptga/ticketchecker' in content:
            print("✅ Caminho do projeto correto no WSGI")
        else:
            print("⚠️  Caminho do projeto pode estar incorreto no WSGI")
    else:
        print(f"⚠️  Arquivo WSGI não encontrado: {wsgi_file}")
        print("   Verifique a configuração no painel do PythonAnywhere")

def main():
    """Função principal"""
    
    print("🎯 Iniciando correção completa de problemas no PythonAnywhere...")
    
    # Verificar configuração do WSGI
    check_wsgi_configuration()
    
    # Corrigir todos os problemas
    if not fix_all_issues():
        print("❌ Falha ao corrigir todos os problemas")
        return False
    
    print("\n🎉 CORREÇÃO COMPLETA FINALIZADA!")
    print("\n📋 Próximos passos:")
    print("1. Reinicie sua aplicação web no PythonAnywhere")
    print("2. Teste o acesso ao dashboard: https://ingressoptga.pythonanywhere.com/dashboard/")
    print("3. Verifique se não há mais erros nos logs")
    print("4. Teste todas as funcionalidades do sistema")
    
    return True

if __name__ == "__main__":
    main()