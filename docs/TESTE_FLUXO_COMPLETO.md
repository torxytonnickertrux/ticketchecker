# 🧪 Teste do Fluxo Completo de Compra

> **Guia para testar todo o processo de compra após as correções**

## 🔧 **Correções Implementadas**

### **1. Sistema de Pagamento Simples (`simple_payment.py`)**
- ✅ **Removido** `auto_return: "approved"` problemático
- ✅ **Mantidas** apenas as `back_urls` essenciais
- ✅ **Configuração** limpa e funcional

### **2. Serviço Mercado Pago (`mercadopago_service.py`)**
- ✅ **Removido** `auto_return` da configuração
- ✅ **Removido** `notification_url` problemática
- ✅ **Preferências** sendo criadas com sucesso

### **3. Views de Pagamento (`payment_views.py`)**
- ✅ **Já usa** `MercadoPagoService` corrigido
- ✅ **Fluxo** de pagamento complexo funcional

## 🎯 **Fluxo Completo de Teste**

### **Passo 1: Acessar o Site**
```
http://127.0.0.1:8000
```

### **Passo 2: Navegar para Eventos**
1. **Clicar** em "Eventos"
2. **Selecionar** um evento
3. **Verificar** detalhes do evento

### **Passo 3: Comprar Ingresso**
1. **Clicar** em "Comprar Ingresso"
2. **Preencher** formulário de compra:
   - Quantidade: 1
   - Cupom (opcional)
3. **Clicar** em "Finalizar Compra"

### **Passo 4: Processar Pagamento**
1. **Será redirecionado** para `/pay/<purchase_id>/`
2. **Verificar** resumo da compra
3. **Clicar** em "Pagar com PIX"
4. **Será redirecionado** para Mercado Pago

### **Passo 5: Testar Pagamento**
1. **Usar cartão de teste:**
   - **Número:** 5031 4332 1540 6351
   - **Nome:** APRO
   - **CPF:** 12345678909
   - **CVV:** 123
   - **Vencimento:** 11/30

2. **Resultado esperado:**
   - ✅ **Pagamento aprovado** instantaneamente
   - ✅ **Redirecionamento** para página de sucesso
   - ✅ **Status da compra** atualizado para `approved`

## 🔍 **Verificações Importantes**

### **1. Logs do Console**
```bash
# Verificar logs de pagamento
python manage.py shell
>>> from events.models import Purchase
>>> Purchase.objects.filter(status='processing')
>>> Purchase.objects.filter(status='approved')
```

### **2. Status das Compras**
```python
# Verificar compras por status
>>> for purchase in Purchase.objects.all():
...     print(f"ID: {purchase.id}, Status: {purchase.status}, MP ID: {purchase.mercado_pago_id}")
```

### **3. Quantidade de Tickets**
```python
# Verificar se a quantidade foi atualizada
>>> from events.models import Ticket
>>> ticket = Ticket.objects.get(id=21)  # Substitua pelo ID correto
>>> print(f"Quantidade disponível: {ticket.quantity}")
```

## 🚨 **Cenários de Teste**

### **Cenário 1: Pagamento Aprovado**
- **Cartão:** 5031 4332 1540 6351
- **Nome:** APRO
- **Resultado:** ✅ Aprovado instantaneamente

### **Cenário 2: Pagamento Recusado**
- **Cartão:** 4235 6477 2802 5682
- **Nome:** FUND
- **Resultado:** ❌ Recusado por quantia insuficiente

### **Cenário 3: Pagamento Pendente**
- **Cartão:** 3753 651535 56885
- **Nome:** CONT
- **Resultado:** ⏳ Pendente de aprovação

## 📊 **Métricas de Sucesso**

### **✅ Indicadores de Funcionamento:**
1. **Preferência criada** com sucesso
2. **Redirecionamento** para Mercado Pago
3. **Processamento** do pagamento
4. **Atualização** do status da compra
5. **Redução** da quantidade de tickets
6. **Geração** de QR Code para validação

### **❌ Problemas a Verificar:**
1. **Erro** na criação de preferência
2. **Falha** no redirecionamento
3. **Problema** no webhook
4. **Status** não atualizado
5. **Quantidade** não reduzida

## 🔧 **Solução de Problemas**

### **Erro: "Preferência não criada"**
```python
# Verificar credenciais
from django.conf import settings
print("Access Token:", settings.MERCADO_PAGO_ACCESS_TOKEN[:20] + "...")
print("Public Key:", settings.MERCADO_PAGO_PUBLIC_KEY[:20] + "...")
print("Sandbox:", settings.MERCADO_PAGO_SANDBOX)
```

### **Erro: "Webhook não funciona"**
```python
# Verificar webhook
from events.models import Purchase
purchases = Purchase.objects.filter(status='processing')
print(f"Compras processando: {purchases.count()}")
```

### **Erro: "Status não atualiza"**
```python
# Verificar status manualmente
purchase = Purchase.objects.get(id=15)  # Substitua pelo ID
purchase.status = 'approved'
purchase.save()
```

## 📱 **Teste no Frontend**

### **1. Interface do Usuário**
- ✅ **Navegação** fluida entre páginas
- ✅ **Formulários** funcionando
- ✅ **Validações** em tempo real
- ✅ **Mensagens** de erro/sucesso

### **2. Processo de Pagamento**
- ✅ **Resumo** da compra correto
- ✅ **Botão** de pagamento funcional
- ✅ **Redirecionamento** para MP
- ✅ **Retorno** após pagamento

### **3. Histórico de Compras**
- ✅ **Lista** de compras
- ✅ **Status** atualizado
- ✅ **QR Code** gerado
- ✅ **Detalhes** da compra

## 🎉 **Resultado Esperado**

### **✅ Fluxo Completo Funcionando:**
1. **Usuário** acessa o site
2. **Navega** pelos eventos
3. **Seleciona** um ingresso
4. **Preenche** dados da compra
5. **É redirecionado** para pagamento
6. **Processa** pagamento no Mercado Pago
7. **Retorna** com status atualizado
8. **Recebe** confirmação e QR Code

### **📊 Métricas de Sucesso:**
- **Tempo de resposta:** < 3 segundos
- **Taxa de sucesso:** > 95%
- **Experiência do usuário:** Fluida
- **Processamento:** Automático

---

<div align="center">
  <strong>🧪 Teste Completo - Verifique todo o fluxo de compra!</strong>
</div>
