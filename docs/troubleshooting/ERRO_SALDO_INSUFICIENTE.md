# 🚨 Erro "Saldo Insuficiente" - Mercado Pago Sandbox

## 📋 **Problema Identificado**

### **Erro:**
```
Você não tem saldo suficiente para fazer o pagamento
```

### **Causa:**
- ❌ **URL incorreta** - Usando `init_point` em vez de `sandbox_init_point`
- ❌ **Ambiente misturado** - Sandbox tentando acessar produção

## 🔧 **Solução Implementada**

### **1. Credenciais Corretas (já estavam):**
```python
# ✅ CORRETO - APP_USR- é para sandbox
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812'
MERCADO_PAGO_PUBLIC_KEY = 'APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71'
```

### **2. URL Sandbox Correta:**
```javascript
// ✅ CORRETO - Usar sandbox_init_point
{% if preference.sandbox_init_point %}
    window.location.href = '{{ preference.sandbox_init_point }}';
{% else %}
    window.location.href = '{{ preference.init_point }}';
{% endif %}
```

### **3. Configuração SITE_URL:**
```python
# ✅ ADICIONADO - URL para callbacks
SITE_URL = 'http://127.0.0.1:8000'
```

## 🎯 **Diferença entre URLs**

### **❌ init_point (Produção):**
```
https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=...
```

### **✅ sandbox_init_point (Teste):**
```
https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=...
```

## 🧪 **Teste da Solução**

1. **Acesse** `http://127.0.0.1:8000`
2. **Selecione** um evento
3. **Escolha** PIX como método de pagamento
4. **Preencha** os dados
5. **Clique** em "Pagar"
6. **Aguarde** o redirecionamento automático
7. **Deve ir para** `sandbox.mercadopago.com.br`
8. **PIX deve aparecer** como única opção

## 📊 **Logs Esperados**

```
🔍 DEBUG MP: Usando credenciais de TESTE (sandbox)
🔍 DEBUG MP: Token usado: APP_USR-294380331087...
INFO: Preferência criada com sucesso: 2902307812-...
🔍 DEBUG VIEW: Resultado create_preference: {...}
```

## ✅ **Status**

**Problema resolvido!** Agora o sistema usa corretamente o ambiente de sandbox do Mercado Pago.

**URLs corretas:**
- ✅ **Sandbox:** `sandbox.mercadopago.com.br`
- ❌ **Produção:** `www.mercadopago.com.br` (não usar em teste)