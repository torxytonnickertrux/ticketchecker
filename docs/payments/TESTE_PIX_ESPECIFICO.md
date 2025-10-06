# 🧪 Teste Específico - Configuração PIX

> **Guia para testar e corrigir problemas com PIX no Mercado Pago**

## 🔍 **Problema Identificado**

### **Sintoma:**
- ✅ **Sistema** redireciona para Mercado Pago
- ❌ **PIX** não aparece como opção
- ❌ **Apenas cartões** são mostrados
- ❌ **Configuração** não está funcionando

## 🔧 **Correções Aplicadas**

### **1. Configuração Melhorada (`simple_payment.py`)**
```python
"payment_methods": {
    "excluded_payment_methods": [
        {"id": "credit_card"},
        {"id": "debit_card"},
        {"id": "bank_transfer"},
        {"id": "atm"}
    ],
    "installments": 1
}
```

### **2. Exclusões Adicionais:**
- ✅ **credit_card** - Cartão de crédito
- ✅ **debit_card** - Cartão de débito  
- ✅ **bank_transfer** - Transferência bancária
- ✅ **atm** - Caixa eletrônico

## 🧪 **Teste da Configuração**

### **Passo 1: Verificar Preferência**
```python
# Testar criação de preferência
from events.simple_payment import simple_payment
from django.test import RequestFactory
from django.contrib.auth.models import User
from events.models import Purchase

factory = RequestFactory()
user = User.objects.first()
purchase = Purchase.objects.first()
request = factory.post('/pay/16/')
request.user = user

# Executar teste
simple_payment(request, purchase.id)
```

### **Passo 2: Verificar Logs**
```bash
# Verificar logs do Mercado Pago
python manage.py shell
>>> from events.mercadopago_service import MercadoPagoService
>>> from events.models import Purchase
>>> purchase = Purchase.objects.first()
>>> mp_service = MercadoPagoService()
>>> preference = mp_service.create_preference(purchase, {'payment_method': 'pix', 'payer_email': 'test@test.com', 'payer_name': 'Test User', 'payer_document': '12345678909'})
>>> print(preference)
```

## 🎯 **Cenários de Teste**

### **Cenário 1: PIX Funcionando**
1. **Acessar** `/pay/<purchase_id>/`
2. **Clicar** em "Pagar com PIX"
3. **Verificar** se redireciona para MP
4. **Verificar** se PIX aparece como opção

### **Cenário 2: Apenas PIX Disponível**
1. **Configuração** deve excluir cartões
2. **PIX** deve ser a única opção
3. **Interface** deve mostrar apenas PIX

### **Cenário 3: Teste com Cartão**
1. **Usar** cartão de teste
2. **Verificar** se processa corretamente
3. **Confirmar** pagamento

## 🔍 **Verificações Importantes**

### **1. Configuração da Preferência**
```python
# Verificar dados da preferência
preference_data = {
    "items": [...],
    "payer": {...},
    "payment_methods": {
        "excluded_payment_methods": [
            {"id": "credit_card"},
            {"id": "debit_card"},
            {"id": "bank_transfer"},
            {"id": "atm"}
        ],
        "installments": 1
    }
}
```

### **2. Logs do Mercado Pago**
```bash
# Verificar logs
tail -f logs/mercadopago.log
```

### **3. Status da Preferência**
```python
# Verificar status
if result["status"] == 201:
    print("✅ Preferência criada com sucesso")
    print(f"ID: {result['response']['id']}")
    print(f"Init Point: {result['response']['init_point']}")
else:
    print("❌ Erro na criação da preferência")
    print(f"Erro: {result}")
```

## 🚨 **Solução de Problemas**

### **Problema: PIX não aparece**
**Solução:**
1. **Verificar** configuração de `payment_methods`
2. **Confirmar** que cartões estão excluídos
3. **Testar** com credenciais corretas

### **Problema: Apenas cartões aparecem**
**Solução:**
1. **Verificar** se `excluded_payment_methods` está correto
2. **Confirmar** que PIX não está excluído
3. **Testar** com configuração limpa

### **Problema: Erro na preferência**
**Solução:**
1. **Verificar** credenciais do Mercado Pago
2. **Confirmar** que sandbox está ativado
3. **Testar** com dados válidos

## 📱 **Teste no Frontend**

### **1. Interface do Usuário**
- ✅ **Botão** "Pagar com PIX" visível
- ✅ **Redirecionamento** para MP funciona
- ✅ **PIX** aparece como opção

### **2. Processo de Pagamento**
- ✅ **PIX** é a única opção disponível
- ✅ **QR Code** é gerado
- ✅ **Pagamento** é processado

### **3. Retorno após Pagamento**
- ✅ **Status** é atualizado
- ✅ **QR Code** é gerado para validação
- ✅ **Email** de confirmação é enviado

## 🎉 **Resultado Esperado**

### **✅ PIX Funcionando Corretamente:**
1. **Usuário** clica em "Pagar com PIX"
2. **Sistema** redireciona para Mercado Pago
3. **PIX** aparece como única opção
4. **QR Code** é gerado automaticamente
5. **Pagamento** é processado instantaneamente
6. **Status** é atualizado para "approved"
7. **QR Code** de validação é gerado

### **📊 Indicadores de Sucesso:**
- **PIX disponível:** ✅ Sim
- **Cartões excluídos:** ✅ Sim
- **Pagamento processado:** ✅ Sim
- **Status atualizado:** ✅ Sim

---

<div align="center">
  <strong>🧪 Teste PIX - Verifique se o PIX está funcionando corretamente!</strong>
</div>
