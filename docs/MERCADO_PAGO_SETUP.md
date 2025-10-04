# 🚀 Configuração do Sistema de Pagamento - Mercado Pago

## 📋 Visão Geral

Sistema completo de pagamentos integrado com Mercado Pago, suportando:
- ✅ **PIX** (aprovação instantânea)
- ✅ **Cartão de Crédito** (parcelamento)
- ✅ **Webhooks** para atualizações automáticas
- ✅ **Interface responsiva** e moderna
- ✅ **Logs detalhados** para monitoramento

## 🔧 Configuração Inicial

### 1. Credenciais do Mercado Pago

1. Acesse [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Crie uma aplicação
3. Obtenha suas credenciais:
   - **Access Token** (produção)
   - **Public Key** (produção)

### 2. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=SEU_ACCESS_TOKEN_AQUI
MERCADO_PAGO_PUBLIC_KEY=SEU_PUBLIC_KEY_AQUI
MERCADO_PAGO_SANDBOX=False

# Site
SITE_URL=https://seudominio.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

### 3. Webhooks

Configure o webhook no painel do Mercado Pago:
- **URL**: `https://seudominio.com/webhook/mercadopago/`
- **Eventos**: `payment`

## 🏗️ Arquitetura do Sistema

### Modelos Principais

1. **Purchase**: Compra do ingresso
2. **Payment**: Pagamento via Mercado Pago
3. **TicketValidation**: QR Code para validação

### Fluxo de Pagamento

1. **Criação da Compra** → Status: `pending`
2. **Seleção do Método** → PIX ou Cartão
3. **Criação do Pagamento** → Mercado Pago
4. **Checkout** → Interface do MP
5. **Webhook** → Atualização automática
6. **Confirmação** → Status: `approved`

## 🎯 Funcionalidades Implementadas

### ✅ PIX
- QR Code automático
- Aprovação instantânea
- Interface nativa do MP

### ✅ Cartão de Crédito
- Tokenização segura
- Parcelamento (1-12x)
- Validação em tempo real

### ✅ Webhooks
- Atualização automática de status
- Logs detalhados
- Tratamento de erros

### ✅ Interface
- Design responsivo
- Feedback visual
- Auto-refresh para PIX

## 🔒 Segurança

- ✅ **Tokenização** de cartões
- ✅ **Webhooks** verificados
- ✅ **Logs** de auditoria
- ✅ **Validações** robustas
- ✅ **Transações** atômicas

## 📊 Monitoramento

### Logs Disponíveis
- Criação de pagamentos
- Webhooks recebidos
- Erros de processamento
- Status de transações

### Admin Django
- Visualização de pagamentos
- Status em tempo real
- Dados do Mercado Pago
- Histórico completo

## 🚀 Deploy para Produção

### 1. Configurações de Produção

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['seudominio.com']
MERCADO_PAGO_SANDBOX = False
```

### 2. SSL/HTTPS
- Obrigatório para webhooks
- Certificado válido
- Redirecionamento HTTP → HTTPS

### 3. Banco de Dados
```bash
python manage.py migrate
python manage.py collectstatic
```

## 🧪 Testes

### Ambiente de Teste
- Use credenciais de sandbox
- Teste com cartões de teste
- Verifique webhooks

### Cartões de Teste
- **Aprovado**: 4009 1750 0000 0008
- **Rejeitado**: 4000 0000 0000 0002
- **Pendente**: 4000 0000 0000 0004

## 📱 Interface do Usuário

### Páginas Implementadas
1. **Formulário de Pagamento** (`/payment/<id>/`)
2. **Checkout** (`/payment/checkout/<id>/`)
3. **Status** (`/payment/status/<id>/`)
4. **Sucesso** (`/payment/success/`)
5. **Falha** (`/payment/failure/`)

### Recursos da Interface
- ✅ Design responsivo
- ✅ Feedback visual
- ✅ Auto-refresh
- ✅ Máscaras de entrada
- ✅ Validações em tempo real

## 🔧 Manutenção

### Logs
```bash
tail -f logs/django.log
```

### Monitoramento
- Status dos pagamentos
- Webhooks recebidos
- Erros de processamento

### Backup
- Banco de dados
- Logs de transações
- Configurações

## 📞 Suporte

### Em caso de problemas:
1. Verifique os logs
2. Confirme webhooks
3. Valide credenciais
4. Teste em sandbox

### Contatos:
- **Email**: suporte@seudominio.com
- **Logs**: `logs/django.log`
- **Admin**: `/admin/`

---

## 🎉 Sistema Pronto para Produção!

O sistema está completamente configurado e pronto para processar pagamentos reais via PIX e cartão de crédito com Mercado Pago.
