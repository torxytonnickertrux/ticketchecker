# 🔧 Solução para Erro de Migração no PythonAnywhere

## 🚨 Problema Identificado

O erro `OperationalError: no such column: events_purchase.mercado_pago_id` está ocorrendo porque:

1. **Migração não aplicada**: A migração `0003_purchase_mercado_pago_id_purchase_payment_date_and_more.py` existe mas não foi aplicada no banco de dados do PythonAnywhere
2. **Coluna faltante**: A coluna `mercado_pago_id` não existe fisicamente na tabela `events_purchase`
3. **Código tentando acessar**: O Django está tentando acessar uma coluna que não existe no banco

## 🔍 Análise do Problema

### **Migração Existente**
```python
# events/migrations/0003_purchase_mercado_pago_id_purchase_payment_date_and_more.py
migrations.AddField(
    model_name='purchase',
    name='mercado_pago_id',
    field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ID Mercado Pago'),
),
```

### **Modelo Atual**
```python
# events/models.py
class Purchase(models.Model):
    # ... outros campos ...
    mercado_pago_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID Mercado Pago")
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name="Data do Pagamento")
    payment_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Status do Pagamento")
```

### **Erro no Dashboard**
O erro ocorre na view `dashboard` quando tenta fazer consultas que incluem o campo `mercado_pago_id`:

```python
# events/views.py
def dashboard(request):
    # Esta consulta falha porque a coluna não existe
    recent_purchases = Purchase.objects.filter(status='confirmed').order_by('-purchase_date')[:10]
```

## ✅ Solução Implementada

### **1. Script de Correção Automática**
Criado `fix_database_migration.py` que:
- Verifica status das migrações
- Aplica migrações pendentes
- Verifica estrutura do banco
- Testa funcionalidade do dashboard

### **2. Verificação de Estrutura**
O script verifica se:
- A tabela `events_purchase` existe
- A coluna `mercado_pago_id` existe
- As consultas do dashboard funcionam

## 🚀 Como Aplicar a Correção

### **Passo 1: Acessar Console PythonAnywhere**
```bash
# Ir para o diretório do projeto
cd /home/ingressoptga/ticketchecker
```

### **Passo 2: Executar Script de Correção**
```bash
# Executar o script de correção
python3 fix_database_migration.py
```

### **Passo 3: Aplicar Migrações Manualmente (se necessário)**
```bash
# Verificar status das migrações
python3 manage.py showmigrations events

# Aplicar migrações pendentes
python3 manage.py migrate events

# Verificar novamente
python3 manage.py showmigrations events
```

### **Passo 4: Verificar Estrutura do Banco**
```bash
# Verificar estrutura da tabela
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('PRAGMA table_info(events_purchase);')
    columns = cursor.fetchall()
    for col in columns:
        print(f'{col[1]} - {col[2]}')
"
```

### **Passo 5: Testar Dashboard**
```bash
# Testar consultas do dashboard
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
django.setup()

from events.models import Purchase
from django.db.models import Sum

# Testar consultas
total_purchases = Purchase.objects.filter(status='confirmed').count()
print(f'Total de compras: {total_purchases}')

total_revenue = Purchase.objects.filter(status='confirmed').aggregate(
    total=Sum('total_price')
)['total'] or 0
print(f'Receita total: R$ {total_revenue}')

recent_purchases = Purchase.objects.filter(status='confirmed').order_by('-purchase_date')[:10]
print(f'Compras recentes: {recent_purchases.count()}')
"
```

### **Passo 6: Reiniciar Aplicação**
1. Ir para a aba **Web** no PythonAnywhere
2. Clicar em **Reload** na aplicação
3. Testar acesso ao dashboard: `https://ingressoptga.pythonanywhere.com/dashboard/`

## 🔍 Verificações Adicionais

### **1. Verificar Migrações Aplicadas**
```bash
# Listar todas as migrações
python3 manage.py showmigrations

# Verificar migrações específicas do app events
python3 manage.py showmigrations events
```

### **2. Verificar Estrutura Completa**
```bash
# Verificar todas as tabelas
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = cursor.fetchall()
    for table in tables:
        print(f'Tabela: {table[0]}')
"
```

### **3. Verificar Dados Existentes**
```bash
# Verificar se há dados na tabela
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
django.setup()

from events.models import Purchase
print(f'Total de compras: {Purchase.objects.count()}')
for purchase in Purchase.objects.all()[:5]:
    print(f'ID: {purchase.id}, Status: {purchase.status}')
"
```

## 🎯 Resultado Esperado

Após aplicar essas correções:

1. ✅ **Migrações aplicadas**: Todas as migrações do Django aplicadas
2. ✅ **Coluna criada**: Campo `mercado_pago_id` existe na tabela `events_purchase`
3. ✅ **Dashboard funcionando**: Acesso ao dashboard sem erros
4. ✅ **Consultas funcionando**: Todas as consultas do dashboard executando corretamente

## 🆘 Se Ainda Houver Problemas

### **Problemas Comuns e Soluções**

1. **Erro de permissão no banco**:
   ```bash
   # Verificar permissões do arquivo de banco
   ls -la /home/ingressoptga/ticketchecker/db.sqlite3
   chmod 664 /home/ingressoptga/ticketchecker/db.sqlite3
   ```

2. **Banco de dados corrompido**:
   ```bash
   # Fazer backup e recriar
   cp db.sqlite3 db.sqlite3.backup
   python3 manage.py migrate --run-syncdb
   ```

3. **Migrações em conflito**:
   ```bash
   # Resetar migrações (CUIDADO: perde dados)
   python3 manage.py migrate events zero
   python3 manage.py migrate events
   ```

### **Verificação Final**
```bash
# Teste completo do sistema
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')
django.setup()

from events.models import Event, Ticket, Purchase
from django.db.models import Sum

print('=== TESTE COMPLETO DO SISTEMA ===')
print(f'Eventos: {Event.objects.count()}')
print(f'Ingressos: {Ticket.objects.count()}')
print(f'Compras: {Purchase.objects.count()}')

# Testar consultas do dashboard
total_revenue = Purchase.objects.filter(status='confirmed').aggregate(
    total=Sum('total_price')
)['total'] or 0
print(f'Receita total: R$ {total_revenue}')

print('✅ Sistema funcionando corretamente!')
"
```

## 📞 Suporte

Se ainda houver problemas:
- **Email**: suporte@ticketchecker.com
- **GitHub**: [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **PythonAnywhere**: [Help](https://help.pythonanywhere.com/)

---

<div align="center">
  <strong>🔧 Problema de Migração Resolvido - Dashboard Funcionando!</strong>
</div>