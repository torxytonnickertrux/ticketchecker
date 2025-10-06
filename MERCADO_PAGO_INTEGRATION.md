# Integração com Mercado Pago - TicketChecker

## 📋 Visão Geral

Este documento descreve a integração completa com o Mercado Pago implementada no sistema TicketChecker, seguindo as melhores práticas de desenvolvimento Django e integração de pagamentos.

## 🏗️ Arquitetura da Integração

### Fluxo de Pagamento

1. **Usuário clica em "Pagar com Mercado Pago"** no evento
2. **Sistema cria preferência** no Mercado Pago
3. **Usuário é redirecionado** para o checkout do MP
4. **Callbacks processam** o resultado do pagamento
5. **Webhook atualiza** o status automaticamente

### Componentes Principais

- **Views**: `events/mercadopago_views.py`
- **Templates**: `templates/events/pagamento_*.html`
- **URLs**: Configuradas em `events/urls.py`
- **Modelos**: Campos adicionados em `Purchase`

## ⚙️ Configurações

### Variáveis de Ambiente

```bash
# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=seu_access_token_aqui
MERCADO_PAGO_PUBLIC_KEY=sua_public_key_aqui
MERCADO_PAGO_SANDBOX=True  # False para produção

# URLs do Sistema
SITE_URL=http://localhost:8000  # Ajustar para produção

# Webhook
WEBHOOK_SECRET_KEY=sua_chave_secreta_aqui
```

### Configurações por Ambiente

#### Desenvolvimento Local
```bash
# Usar .env.local
DEBUG=True
SITE_URL=http://127.0.0.1:8000
MERCADO_PAGO_SANDBOX=True
```

#### Produção (PythonAnywhere)
```bash
# Usar .env.pythonanywhere
DEBUG=False
SITE_URL=https://ingressoptga.pythonanywhere.com
MERCADO_PAGO_SANDBOX=False
```

## 🔧 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env.local

# Editar com suas credenciais
nano .env.local
```

### 3. Executar Migrações

```bash
python manage.py makemigrations events
python manage.py migrate
```

### 4. Testar Integração

```bash
python test_mercadopago_integration.py
```

## 🚀 Uso da Integração

### 1. Criar Preferência de Pagamento

```python
# A view criar_preferencia_pagamento é chamada automaticamente
# quando o usuário clica em "Pagar com Mercado Pago"
```

### 2. Processar Callbacks

```python
# Sucesso: /events/pagamento/sucesso/
# Falha: /events/pagamento/falha/
# Pendente: /events/pagamento/pendente/
```

### 3. Webhook para Atualizações

```python
# URL: /events/webhook/mercadopago/
# Processa notificações automáticas do MP
```

## 📊 Modelos de Dados

### Purchase (Atualizado)

```python
class Purchase(models.Model):
    # ... campos existentes ...
    preference_id = models.CharField(max_length=100, blank=True, null=True)
    mp_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ], default='pending')
    # ... outros campos ...
```

## 🧪 Testes

### Executar Testes Unitários

```bash
python manage.py test events.tests_mercadopago
```

### Executar Teste de Integração

```bash
python test_mercadopago_integration.py
```

### Testes Disponíveis

- ✅ Criação de preferência de pagamento
- ✅ Callbacks de sucesso/falha/pendente
- ✅ Webhook de notificações
- ✅ Validação de dados
- ✅ Tratamento de erros

## 🔒 Segurança

### Validações Implementadas

- ✅ Verificação de usuário autenticado
- ✅ Validação de evento ativo
- ✅ Verificação de tickets disponíveis
- ✅ Validação de content-type no webhook
- ✅ Tratamento de erros robusto

### Configurações de Segurança

```python
# HTTPS obrigatório em produção
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 📱 Templates

### Páginas de Pagamento

- **Sucesso**: `templates/events/pagamento_sucesso.html`
- **Falha**: `templates/events/pagamento_falha.html`
- **Pendente**: `templates/events/pagamento_pendente.html`

### Botão de Compra

```html
<!-- Em templates/events/event_detail.html -->
<a href="{% url 'comprar_ingresso' event.id %}" class="btn btn-success btn-sm">
    <i class="fas fa-credit-card me-1"></i>Pagar com Mercado Pago
</a>
```

## 🚀 Deploy

### PythonAnywhere

1. **Configurar variáveis de ambiente**:
   ```bash
   # No console do PythonAnywhere
   export MERCADO_PAGO_ACCESS_TOKEN="seu_token"
   export MERCADO_PAGO_PUBLIC_KEY="sua_key"
   export MERCADO_PAGO_SANDBOX="False"
   ```

2. **Atualizar WSGI**:
   ```python
   # Em wsgi.py
   import mercadopago  # Adicionar esta linha
   ```

3. **Executar comandos**:
   ```bash
   python manage.py collectstatic
   python manage.py migrate
   ```

4. **Recarregar aplicação** no painel do PythonAnywhere

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Token Inválido
```
Solução: Verificar se MERCADO_PAGO_ACCESS_TOKEN está correto
```

#### 2. Callback não funciona
```
Solução: Verificar se SITE_URL está configurado corretamente
```

#### 3. Webhook não recebe notificações
```
Solução: Verificar se a URL está acessível publicamente
```

### Logs de Debug

```python
# Verificar logs do Django
python manage.py runserver --verbosity=2

# Verificar logs específicos do MP
tail -f logs/django.log | grep "mercadopago"
```

## 📚 Referências

- [Documentação Oficial Mercado Pago](https://www.mercadopago.com.br/developers)
- [SDK Python Mercado Pago](https://github.com/mercadopago/sdk-python)
- [Django Documentation](https://docs.djangoproject.com/)

## 🤝 Suporte

Para dúvidas ou problemas:

1. Verificar logs de erro
2. Executar testes de integração
3. Consultar documentação do Mercado Pago
4. Abrir issue no repositório

---

**Desenvolvido com ❤️ para o TicketChecker**