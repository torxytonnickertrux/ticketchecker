# 💳 Configuração de Autenticação com Métodos de Pagamento

> **Guia completo para configurar autenticação com Mercado Pago no TicketChecker**

## 🎯 Onde Configurar a Autenticação

### **1. Arquivo de Configuração Principal**
**Localização:** `backend/settings.py`

```python
# Configurações do Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', '')
MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY', '')
MERCADO_PAGO_SANDBOX = os.getenv('MERCADO_PAGO_SANDBOX', 'True').lower() == 'true'
```

### **2. Arquivo de Variáveis de Ambiente**
**Localização:** `.env` (raiz do projeto)

```env
# Mercado Pago - Credenciais de Produção
MERCADO_PAGO_ACCESS_TOKEN=APP_USR_1234567890abcdef...
MERCADO_PAGO_PUBLIC_KEY=APP_USR_1234567890abcdef...
MERCADO_PAGO_SANDBOX=False

# Site
SITE_URL=https://seudominio.com

# Email (para notificações)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

## 🔑 Como Obter as Credenciais

### **1. Acessar Mercado Pago Developers**
```
URL: https://www.mercadopago.com.br/developers
```

### **2. Criar Aplicação**
1. **Login** na conta Mercado Pago
2. **Criar aplicação** nova
3. **Selecionar** "Marketplace" ou "E-commerce"
4. **Configurar** dados da aplicação

### **3. Obter Credenciais**
- **Access Token** (Produção)
- **Public Key** (Produção)
- **Webhook URL** (configurar depois)

## ⚙️ Configuração por Ambiente

### **Desenvolvimento (Sandbox)**
```env
# .env para desenvolvimento
MERCADO_PAGO_ACCESS_TOKEN=TEST_1234567890abcdef...
MERCADO_PAGO_PUBLIC_KEY=TEST_1234567890abcdef...
MERCADO_PAGO_SANDBOX=True
SITE_URL=http://127.0.0.1:8000
```

### **Produção (Real)**
```env
# .env para produção
MERCADO_PAGO_ACCESS_TOKEN=APP_USR_1234567890abcdef...
MERCADO_PAGO_PUBLIC_KEY=APP_USR_1234567890abcdef...
MERCADO_PAGO_SANDBOX=False
SITE_URL=https://seudominio.com
```

## 🏗️ Arquitetura do Sistema de Pagamento

### **Modelos de Dados**
```python
# events/models.py

class Purchase(models.Model):
    """Compra do ingresso"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')

class Payment(models.Model):
    """Pagamento via Mercado Pago"""
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE)
    mercado_pago_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payer_email = models.EmailField()
    payer_name = models.CharField(max_length=255)
    payer_document = models.CharField(max_length=20)
```

### **Serviço de Integração**
```python
# events/mercadopago_service.py

import mercadopago

class MercadoPagoService:
    def __init__(self):
        self.mp = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    
    def create_preference(self, purchase):
        """Criar preferência de pagamento"""
        preference_data = {
            "items": [
                {
                    "title": f"Ingresso {purchase.ticket.type}",
                    "quantity": purchase.quantity,
                    "unit_price": float(purchase.ticket.price),
                    "currency_id": "BRL"
                }
            ],
            "payer": {
                "email": purchase.user.email,
                "name": purchase.user.get_full_name()
            },
            "back_urls": {
                "success": f"{settings.SITE_URL}/payment/success/",
                "failure": f"{settings.SITE_URL}/payment/failure/",
                "pending": f"{settings.SITE_URL}/payment/pending/"
            }
        }
        return self.mp.preference().create(preference_data)
```

## 🎨 Interface de Pagamento

### **Formulário de Pagamento**
```html
<!-- template/events/payment_form.html -->
<form method="post">
    {% csrf_token %}
    
    <!-- Método de Pagamento -->
    <div class="form-group">
        <label>Método de Pagamento</label>
        <div class="form-check">
            <input type="radio" name="payment_method" value="pix" id="pix">
            <label for="pix">PIX</label>
        </div>
        <div class="form-check">
            <input type="radio" name="payment_method" value="credit_card" id="card">
            <label for="card">Cartão de Crédito</label>
        </div>
    </div>
    
    <!-- Dados do Pagador -->
    <div class="form-group">
        <label for="payer_document">CPF</label>
        <input type="text" name="payer_document" class="form-control" required>
    </div>
    
    <!-- Parcelas (apenas cartão) -->
    <div class="form-group" id="installments-group" style="display: none;">
        <label for="installments">Parcelas</label>
        <select name="installments" class="form-control">
            <option value="1">1x</option>
            <option value="2">2x</option>
            <!-- ... até 12x -->
        </select>
    </div>
</form>
```

## 🔄 Fluxo de Pagamento

### **1. Criação da Compra**
```python
# events/views.py
@login_required
def purchase_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Criar compra
    purchase = Purchase.objects.create(
        user=request.user,
        ticket=ticket,
        quantity=1,
        total_price=ticket.price
    )
    
    return redirect('payment_form', purchase_id=purchase.id)
```

### **2. Seleção do Método**
```python
@login_required
def payment_form(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Processar pagamento
            return redirect('process_payment', purchase_id=purchase.id)
    
    return render(request, 'events/payment_form.html', {
        'purchase': purchase,
        'form': PaymentForm()
    })
```

### **3. Processamento do Pagamento**
```python
@login_required
def process_payment(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Criar preferência no Mercado Pago
    mp_service = MercadoPagoService()
    preference = mp_service.create_preference(purchase)
    
    # Salvar dados do pagamento
    Payment.objects.create(
        purchase=purchase,
        mercado_pago_id=preference['response']['id'],
        payment_method=request.POST.get('payment_method'),
        amount=purchase.total_price,
        payer_email=request.user.email,
        payer_name=request.user.get_full_name(),
        payer_document=request.POST.get('payer_document')
    )
    
    # Redirecionar para Mercado Pago
    return redirect(preference['response']['init_point'])
```

## 🔔 Configuração de Webhooks

### **1. URL do Webhook**
```
https://seudominio.com/webhook/mercadopago/
```

### **2. Configuração no Mercado Pago**
1. **Acessar** painel de desenvolvedores
2. **Selecionar** aplicação
3. **Configurar** webhook:
   - **URL**: `https://seudominio.com/webhook/mercadopago/`
   - **Eventos**: `payment`

### **3. Implementação do Webhook**
```python
# events/webhook_views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mercadopago_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Processar notificação
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            # Atualizar status do pagamento
            try:
                payment = Payment.objects.get(mercado_pago_id=payment_id)
                # Atualizar status baseado na notificação
                payment.status = 'approved'  # ou outro status
                payment.save()
                
                # Atualizar compra
                payment.purchase.status = 'confirmed'
                payment.purchase.save()
                
            except Payment.DoesNotExist:
                pass
    
    return HttpResponse(status=200)
```

## 🚀 Configuração para Produção

### **1. PythonAnywhere**
```bash
# Instalar dependências
pip3.10 install --user mercadopago

# Configurar variáveis de ambiente
# No console PythonAnywhere
export MERCADO_PAGO_ACCESS_TOKEN="APP_USR_..."
export MERCADO_PAGO_PUBLIC_KEY="APP_USR_..."
export MERCADO_PAGO_SANDBOX="False"
```

### **2. Heroku**
```bash
# Configurar variáveis
heroku config:set MERCADO_PAGO_ACCESS_TOKEN="APP_USR_..."
heroku config:set MERCADO_PAGO_PUBLIC_KEY="APP_USR_..."
heroku config:set MERCADO_PAGO_SANDBOX="False"
```

## 🔐 Segurança

### **1. Validação de Webhooks**
```python
import hmac
import hashlib

def verify_webhook_signature(request):
    """Verificar assinatura do webhook"""
    signature = request.headers.get('X-Signature')
    if not signature:
        return False
    
    # Verificar assinatura
    expected_signature = hmac.new(
        settings.MERCADO_PAGO_WEBHOOK_SECRET.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### **2. Configurações de Segurança**
```python
# backend/settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 📊 Monitoramento

### **1. Logs de Pagamento**
```python
import logging

logger = logging.getLogger('payments')

def log_payment_event(event, data):
    """Registrar evento de pagamento"""
    logger.info(f"Payment Event: {event}", extra={
        'payment_id': data.get('id'),
        'status': data.get('status'),
        'amount': data.get('amount')
    })
```

### **2. Dashboard de Pagamentos**
- **Status** dos pagamentos
- **Métricas** de conversão
- **Relatórios** de vendas
- **Alertas** de falhas

## 📞 Suporte

Para dúvidas sobre configuração de pagamentos:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Mercado Pago** - [Suporte](https://www.mercadopago.com.br/developers/support)

---

<div align="center">
  <strong>💳 Configuração de Pagamentos - Configure sua autenticação com Mercado Pago!</strong>
</div>
