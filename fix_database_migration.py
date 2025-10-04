#!/usr/bin/env python3
"""
Script para corrigir problemas de migração no PythonAnywhere
Execute este script no console do PythonAnywhere
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def fix_database_migration():
    """Corrige problemas de migração no banco de dados"""
    
    print("🔧 Corrigindo problemas de migração no PythonAnywhere...")
    
    # 1. Verificar se estamos no diretório correto
    project_dir = '/home/ingressoptga/ticketchecker'
    if not os.path.exists(project_dir):
        print(f"❌ Diretório do projeto não encontrado: {project_dir}")
        return False
    
    os.chdir(project_dir)
    print(f"✅ Mudando para diretório: {project_dir}")
    
    # 2. Configurar Django
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
        django.setup()
        print("✅ Django configurado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        return False
    
    # 3. Verificar status das migrações
    print("\n📋 Verificando status das migrações...")
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capturar saída do comando showmigrations
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        call_command('showmigrations', 'events', verbosity=0)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        print("Status das migrações:")
        print(output)
        
        # Verificar se há migrações pendentes
        if '[ ]' in output:
            print("⚠️  Há migrações pendentes!")
            return apply_pending_migrations()
        else:
            print("✅ Todas as migrações foram aplicadas")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")
        return False

def apply_pending_migrations():
    """Aplica migrações pendentes"""
    
    print("\n🚀 Aplicando migrações pendentes...")
    
    try:
        from django.core.management import call_command
        
        # Aplicar migrações
        call_command('migrate', 'events', verbosity=2)
        print("✅ Migrações aplicadas com sucesso")
        
        # Verificar novamente
        print("\n📋 Verificando status após aplicação...")
        call_command('showmigrations', 'events', verbosity=1)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        return False

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    
    print("\n🔍 Verificando estrutura do banco de dados...")
    
    try:
        from django.db import connection
        from events.models import Purchase
        
        # Verificar se a tabela existe
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events_purchase';")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("❌ Tabela events_purchase não existe!")
                return False
            
            print("✅ Tabela events_purchase existe")
            
            # Verificar colunas da tabela
            cursor.execute("PRAGMA table_info(events_purchase);")
            columns = cursor.fetchall()
            
            print("\nColunas da tabela events_purchase:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
            
            # Verificar se a coluna mercado_pago_id existe
            mercado_pago_column = any(col[1] == 'mercado_pago_id' for col in columns)
            
            if mercado_pago_column:
                print("✅ Coluna mercado_pago_id existe")
                return True
            else:
                print("❌ Coluna mercado_pago_id não existe!")
                print("💡 Execute as migrações para corrigir isso")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura do banco: {e}")
        return False

def test_dashboard_access():
    """Testa o acesso ao dashboard"""
    
    print("\n🧪 Testando acesso ao dashboard...")
    
    try:
        from events.models import Purchase
        from django.db.models import Sum
        
        # Testar consulta que estava falhando
        total_purchases = Purchase.objects.filter(status='confirmed').count()
        print(f"✅ Total de compras confirmadas: {total_purchases}")
        
        # Testar consulta com Sum
        total_revenue = Purchase.objects.filter(status='confirmed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        print(f"✅ Receita total: R$ {total_revenue}")
        
        # Testar consulta de compras recentes
        recent_purchases = Purchase.objects.filter(status='confirmed').order_by('-purchase_date')[:10]
        print(f"✅ Compras recentes encontradas: {recent_purchases.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        return False

def main():
    """Função principal"""
    
    print("🎯 Iniciando correção de problemas de banco de dados...")
    
    # 1. Verificar migrações
    if not fix_database_migration():
        print("❌ Falha ao corrigir migrações")
        return False
    
    # 2. Verificar estrutura do banco
    if not check_database_structure():
        print("❌ Problemas na estrutura do banco")
        return False
    
    # 3. Testar dashboard
    if not test_dashboard_access():
        print("❌ Problemas no acesso ao dashboard")
        return False
    
    print("\n🎉 Todos os problemas foram resolvidos!")
    print("\n📋 Próximos passos:")
    print("1. Reinicie sua aplicação web no PythonAnywhere")
    print("2. Teste o acesso ao dashboard")
    print("3. Verifique se não há mais erros nos logs")
    
    return True

if __name__ == "__main__":
    main()