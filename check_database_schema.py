#!/usr/bin/env python3
"""
Script para verificar e corrigir esquema do banco de dados
Execute este script no console do PythonAnywhere
"""

import os
import sys
import sqlite3

def check_database_schema():
    """Verifica e corrige o esquema do banco de dados"""
    
    print("🔍 Verificando esquema do banco de dados...")
    
    # Caminho do banco de dados
    db_path = '/home/ingressoptga/ticketchecker/db.sqlite3'
    
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
    
    # Verificar tabelas existentes
    print("\n📋 Tabelas existentes:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"  - {table[0]}")
    
    # Verificar estrutura da tabela events_purchase
    print("\n🔍 Estrutura da tabela events_purchase:")
    try:
        cursor.execute("PRAGMA table_info(events_purchase);")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ Tabela events_purchase não existe!")
            return False
        
        print("Colunas encontradas:")
        mercado_pago_exists = False
        
        for column in columns:
            col_id, col_name, col_type, not_null, default_val, pk = column
            print(f"  - {col_name} ({col_type})")
            
            if col_name == 'mercado_pago_id':
                mercado_pago_exists = True
        
        if mercado_pago_exists:
            print("✅ Coluna mercado_pago_id existe")
            return True
        else:
            print("❌ Coluna mercado_pago_id não existe!")
            return add_missing_column(cursor, conn)
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False
    finally:
        conn.close()

def add_missing_column(cursor, conn):
    """Adiciona a coluna faltante"""
    
    print("\n🔧 Adicionando coluna mercado_pago_id...")
    
    try:
        # Adicionar coluna mercado_pago_id
        cursor.execute("""
            ALTER TABLE events_purchase 
            ADD COLUMN mercado_pago_id VARCHAR(100) NULL;
        """)
        
        # Adicionar coluna payment_date
        cursor.execute("""
            ALTER TABLE events_purchase 
            ADD COLUMN payment_date DATETIME NULL;
        """)
        
        # Adicionar coluna payment_status
        cursor.execute("""
            ALTER TABLE events_purchase 
            ADD COLUMN payment_status VARCHAR(50) NULL;
        """)
        
        # Confirmar alterações
        conn.commit()
        print("✅ Colunas adicionadas com sucesso")
        
        # Verificar novamente
        print("\n🔍 Verificando estrutura após correção:")
        cursor.execute("PRAGMA table_info(events_purchase);")
        columns = cursor.fetchall()
        
        for column in columns:
            col_id, col_name, col_type, not_null, default_val, pk = column
            print(f"  - {col_name} ({col_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar colunas: {e}")
        conn.rollback()
        return False

def test_queries():
    """Testa as consultas que estavam falhando"""
    
    print("\n🧪 Testando consultas do dashboard...")
    
    try:
        # Configurar Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
        django.setup()
        
        from events.models import Purchase
        from django.db.models import Sum
        
        # Testar consulta básica
        total_purchases = Purchase.objects.count()
        print(f"✅ Total de compras: {total_purchases}")
        
        # Testar consulta com filtro
        confirmed_purchases = Purchase.objects.filter(status='confirmed').count()
        print(f"✅ Compras confirmadas: {confirmed_purchases}")
        
        # Testar consulta com Sum
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
        print(f"❌ Erro ao testar consultas: {e}")
        return False

def main():
    """Função principal"""
    
    print("🎯 Verificando e corrigindo esquema do banco de dados...")
    
    # 1. Verificar esquema
    if not check_database_schema():
        print("❌ Problemas no esquema do banco")
        return False
    
    # 2. Testar consultas
    if not test_queries():
        print("❌ Problemas nas consultas")
        return False
    
    print("\n🎉 Banco de dados corrigido e funcionando!")
    print("\n📋 Próximos passos:")
    print("1. Reinicie sua aplicação web no PythonAnywhere")
    print("2. Teste o acesso ao dashboard")
    print("3. Verifique se não há mais erros nos logs")
    
    return True

if __name__ == "__main__":
    main()