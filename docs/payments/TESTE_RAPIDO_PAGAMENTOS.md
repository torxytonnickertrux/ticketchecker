# 🚀 Teste Rápido - Sistema de Pagamentos

> **Guia para testar o sistema de pagamentos com credenciais de teste**

## ✅ Status da Configuração

### **Credenciais Configuradas:**
- ✅ **Access Token:** APP_USR-294380331087...
- ✅ **Public Key:** APP_USR-3bd9ca6a-941...
- ✅ **Sandbox:** Ativado
- ✅ **Arquivo .env:** Criado

## 🧪 Teste Rápido

### **1. Iniciar Servidor**
```bash
python manage.py runserver
```

### **2. Acessar Site**
```
http://127.0.0.1:8000
```

### **3. Criar Evento de Teste**
1. **Login** no admin: `/admin/`
2. **Criar evento** com:
   - Nome: "Evento de Teste"
   - Data: Data futura
   - Preço: R$ 50,00

### **4. Comprar Ingresso**
1. **Acessar** evento
2. **Selecionar** ingresso
3. **Escolher** método de pagamento
4. **Usar** cartão de teste

## 💳 Cartões de Teste

### **Pagamento Aprovado**
- **Cartão:** 5031 4332 1540 6351
- **Nome:** APRO
- **CPF:** 12345678909
- **CVV:** 123
- **Vencimento:** 11/30

### **Pagamento Recusado**
- **Cartão:** 4235 6477 2802 5682
- **Nome:** FUND
- **CPF:** 12345678909
- **CVV:** 123
- **Vencimento:** 11/30

### **Pagamento Pendente**
- **Cartão:** 3753 651535 56885
- **Nome:** CONT
- **CPF:** 12345678909
- **CVV:** 1234
- **Vencimento:** 11/30

## 🔍 Verificar Resultados

### **1. Logs do Console**
```bash
# Verificar logs de pagamento
python manage.py shell
>>> from events.models import Payment
>>> Payment.objects.all()
```

### **2. Status dos Pagamentos**
```python
# Verificar status
>>> for payment in Payment.objects.all():
...     print(f"ID: {payment.mercado_pago_id}, Status: {payment.status}")
```

### **3. Compras Realizadas**
```python
# Verificar compras
>>> from events.models import Purchase
>>> Purchase.objects.all()
```

## 🎯 Cenários de Teste

### **Cenário 1: Pagamento Aprovado**
1. **Usar cartão:** 5031 4332 1540 6351
2. **Nome:** APRO
3. **Resultado:** Pagamento aprovado instantaneamente
4. **Status:** `approved`

### **Cenário 2: Pagamento Recusado**
1. **Usar cartão:** 4235 6477 2802 5682
2. **Nome:** FUND
3. **Resultado:** Recusado por quantia insuficiente
4. **Status:** `rejected`

### **Cenário 3: Pagamento Pendente**
1. **Usar cartão:** 3753 651535 56885
2. **Nome:** CONT
3. **Resultado:** Pendente de aprovação
4. **Status:** `pending`

## 🚨 Solução de Problemas

### **Erro: "Credenciais inválidas"**
```bash
# Verificar se .env existe
dir .env

# Recriar .env
python setup_credentials.py
```

### **Erro: "Módulo não encontrado"**
```bash
# Instalar dependências
pip install mercadopago python-dotenv
```

### **Erro: "Pagamento não processado"**
1. **Verificar** se sandbox está ativado
2. **Usar** cartões de teste fornecidos
3. **Verificar** logs do console

## 📊 Monitoramento

### **1. Logs de Pagamento**
```python
# Verificar logs
import logging
logger = logging.getLogger('payments')
```

### **2. Status dos Pagamentos**
- **approved:** Pagamento aprovado
- **rejected:** Pagamento recusado
- **pending:** Pagamento pendente
- **cancelled:** Pagamento cancelado

### **3. Métricas de Teste**
- **Total de pagamentos:** `Payment.objects.count()`
- **Pagamentos aprovados:** `Payment.objects.filter(status='approved').count()`
- **Pagamentos recusados:** `Payment.objects.filter(status='rejected').count()`

## 🎉 Próximos Passos

### **1. Teste Completo**
- ✅ Criar evento
- ✅ Comprar ingresso
- ✅ Testar pagamento
- ✅ Verificar status

### **2. Configuração de Produção**
- 🔄 Obter credenciais de produção
- 🔄 Configurar webhooks
- 🔄 Testar em ambiente real

### **3. Deploy**
- 🚀 Configurar PythonAnywhere
- 🚀 Aplicar correções
- 🚀 Testar em produção

---

<div align="center">
  <strong>🚀 Teste Rápido - Configure e teste seu sistema de pagamentos!</strong>
</div>
