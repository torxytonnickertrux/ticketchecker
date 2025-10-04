# 🧪 Credenciais de Teste - Mercado Pago

> **Configuração completa para ambiente de desenvolvimento e testes**

## 🔑 Credenciais de Teste

### **Credenciais da Aplicação**
```env
# Mercado Pago - CREDENCIAIS DE TESTE
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812
MERCADO_PAGO_PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
MERCADO_PAGO_SANDBOX=True
```

### **Configuração Completa do .env**
```env
# Mercado Pago - CREDENCIAIS DE TESTE
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812
MERCADO_PAGO_PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
MERCADO_PAGO_SANDBOX=True

# Site
SITE_URL=http://127.0.0.1:8000

# Email (configurar conforme necessário)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
DEFAULT_FROM_EMAIL=noreply@ticketchecker.com

# Django
DEBUG=True
SECRET_KEY=sua_secret_key_aqui
```

## 👥 Usuários de Teste

### **Comprador (Buyer)**
- **User ID:** 2903096586
- **Usuário:** TESTUSER4303...
- **Senha:** X837SeJ4KB
- **País:** Brasil

### **Vendedor (Seller)**
- **User ID:** 2902307812
- **Usuário:** TESTUSER7042...
- **Senha:** lV7Mk0tnCD
- **País:** Brasil

## 💳 Cartões de Teste

### **Mastercard**
- **Número:** 5031 4332 1540 6351
- **CVV:** 123
- **Vencimento:** 11/30

### **Visa**
- **Número:** 4235 6477 2802 5682
- **CVV:** 123
- **Vencimento:** 11/30

### **American Express**
- **Número:** 3753 651535 56885
- **CVV:** 1234
- **Vencimento:** 11/30

### **Elo Débito**
- **Número:** 5067 7667 8388 8311
- **CVV:** 123
- **Vencimento:** 11/30

## 🎯 Testando Diferentes Status de Pagamento

Para testar diferentes resultados, use os seguintes nomes no titular do cartão:

### **Status de Pagamento**
| Status | Nome do Titular | CPF | Descrição |
|--------|----------------|-----|-----------|
| **APRO** | APRO | 12345678909 | Pagamento aprovado |
| **OTHE** | OTHE | 12345678909 | Recusado por erro geral |
| **CONT** | CONT | - | Pagamento pendente |
| **CALL** | CALL | - | Recusado com validação para autorizar |
| **FUND** | FUND | - | Recusado por quantia insuficiente |
| **SECU** | SECU | - | Recusado por código de segurança inválido |
| **EXPI** | EXPI | - | Recusado por problema com a data de vencimento |
| **FORM** | FORM | - | Recusado por erro no formulário |

## 🚀 Como Configurar

### **1. Criar arquivo .env**
```bash
# Na raiz do projeto
cp .env.example .env
```

### **2. Editar .env com as credenciais**
```env
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812
MERCADO_PAGO_PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
MERCADO_PAGO_SANDBOX=True
```

### **3. Instalar dependências**
```bash
pip install mercadopago
```

### **4. Executar migrações**
```bash
python manage.py migrate
```

### **5. Iniciar servidor**
```bash
python manage.py runserver
```

## 🧪 Cenários de Teste

### **1. Pagamento Aprovado**
- **Cartão:** 5031 4332 1540 6351
- **Nome:** APRO
- **CPF:** 12345678909
- **Resultado:** Pagamento aprovado instantaneamente

### **2. Pagamento Recusado**
- **Cartão:** 4235 6477 2802 5682
- **Nome:** FUND
- **CPF:** 12345678909
- **Resultado:** Recusado por quantia insuficiente

### **3. Pagamento Pendente**
- **Cartão:** 3753 651535 56885
- **Nome:** CONT
- **CPF:** 12345678909
- **Resultado:** Pagamento pendente de aprovação

## 🔍 Monitoramento de Testes

### **Logs de Pagamento**
```python
# Verificar logs no console
python manage.py shell
>>> from events.models import Payment
>>> Payment.objects.all()
```

### **Status dos Pagamentos**
```python
# Verificar status
>>> for payment in Payment.objects.all():
...     print(f"ID: {payment.mercado_pago_id}, Status: {payment.status}")
```

## 📱 Testando no Frontend

### **1. Acessar Site**
```
http://127.0.0.1:8000
```

### **2. Criar Evento de Teste**
- Nome: "Evento de Teste"
- Data: Data futura
- Preço: R$ 50,00

### **3. Comprar Ingresso**
- Selecionar ingresso
- Escolher método de pagamento
- Usar cartão de teste
- Testar diferentes cenários

## 🚨 Importante

### **⚠️ Avisos de Segurança**
- **NUNCA** use cartões reais em ambiente de teste
- **SEMPRE** use as credenciais de teste fornecidas
- **MANTENHA** o `MERCADO_PAGO_SANDBOX=True` em desenvolvimento

### **🔒 Dados Sensíveis**
- **NÃO** commite o arquivo `.env` no Git
- **USE** `.env.example` como template
- **CONFIGURE** variáveis de ambiente em produção

## 📞 Suporte

Para dúvidas sobre testes:
- **Mercado Pago:** [Suporte](https://www.mercadopago.com.br/developers/support)
- **Documentação:** [Guia de Testes](https://www.mercadopago.com.br/developers/pt/docs/testing)
- **GitHub:** [Issues](https://github.com/seu-usuario/ticketchecker/issues)

---

<div align="center">
  <strong>🧪 Credenciais de Teste - Configure e teste seu sistema de pagamentos!</strong>
</div>
