# Sistema de Pagamentos Completo - Mercado Pago

## 🎯 Visão Geral

Sistema completo de pagamentos integrado com Mercado Pago, incluindo webhooks, testes abrangentes, monitoramento e configuração para produção.

## 🚀 Funcionalidades Implementadas

### ✅ Sistema de Pagamentos
- **PIX**: Pagamento instantâneo via PIX
- **Cartão de Crédito**: Mastercard, Visa, American Express, Elo
- **Cartão de Débito**: Elo Débito
- **Checkout Pro**: Interface completa do Mercado Pago

### ✅ Webhooks Avançados
- **Validação de Segurança**: HMAC SHA256 + Timestamp
- **Processamento Automático**: Atualização de status em tempo real
- **Logs Detalhados**: Rastreamento completo de eventos
- **Ambientes Separados**: Teste e Produção

### ✅ Testes Abrangentes
- **Testes de Webhook**: Conectividade e segurança
- **Testes de Cartão**: Todos os cenários de pagamento
- **Testes de Integração**: Fluxo completo
- **Testes de Performance**: Monitoramento de sistema

### ✅ Monitoramento
- **Health Checks**: Verificação de saúde do sistema
- **Logs Estruturados**: Análise de eventos
- **Alertas**: Notificações de problemas
- **Relatórios**: Estatísticas detalhadas

## 🔧 Configuração

### Credenciais do Mercado Pago

```bash
# Credenciais de Teste
PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812

# Usuários de Teste
BUYER_USER_ID=2903096586
SELLER_USER_ID=2902307812
BUYER_USERNAME=TESTUSER4303730899806321523
SELLER_USERNAME=TESTUSER7042493348957069718
```

### URLs dos Webhooks

```bash
# Teste
https://ingressoptga.pythonanywhere.com/comunication/build/teste

# Produção
https://ingressoptga.pythonanywhere.com/comunication/build/production

# Chave Secreta
1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
```

## 🧪 Cartões de Teste

### Cartões Aprovados
```bash
# Mastercard
5031 4332 1540 6351
123
11/30

# Visa
4235 6477 2802 5682
123
11/30

# American Express
3753 651535 56885
1234
11/30

# Elo Débito
5067 7667 8388 8311
123
11/30
```

### Cenários de Teste
```bash
# Aprovado
Nome: APRO Test User
CPF: 12345678909

# Rejeitado - Erro Geral
Nome: OTHE Test User
CPF: 12345678909

# Pendente
Nome: CONT Test User
CPF: 12345678909

# Fundos Insuficientes
Nome: FUND Test User
CPF: 12345678909

# Código de Segurança Inválido
Nome: SECU Test User
CPF: 12345678909

# Cartão Expirado
Nome: EXPI Test User
CPF: 12345678909

# Erro de Formulário
Nome: FORM Test User
CPF: 12345678909
```

## 🚀 Execução de Testes

### Teste Completo
```bash
python run_all_tests.py
```

### Testes Individuais
```bash
# Testes de Webhook
python test_webhook.py

# Testes Abrangentes
python test_comprehensive_payment.py

# Testes de Cartão
python test_credit_cards.py

# Monitoramento
python monitor_system.py

# Configuração de Produção
python setup_production.py
```

## 📊 Estrutura do Sistema

### Apps Django
```
communication/          # App de comunicação com Mercado Pago
├── models.py          # Modelos de webhook e notificações
├── views.py           # Views de webhook
├── services.py        # Serviços de processamento
├── validators.py      # Validadores de segurança
├── test_service.py    # Serviço de testes
└── admin.py           # Interface administrativa

events/                # App de eventos e ingressos
├── models.py          # Modelos de evento, ticket, compra
├── views.py           # Views de eventos
├── simple_payment.py  # Sistema de pagamento simples
└── mercadopago_service.py  # Serviço Mercado Pago
```

### Scripts de Teste
```
test_webhook.py              # Testes de conectividade
test_comprehensive_payment.py # Testes abrangentes
test_credit_cards.py         # Testes de cartão
run_all_tests.py            # Executor de todos os testes
monitor_system.py           # Monitoramento
setup_production.py         # Configuração de produção
```

## 🔒 Segurança

### Validação de Webhook
- **HMAC SHA256**: Assinatura criptográfica
- **Timestamp**: Prevenção de ataques de replay
- **Validação de Payload**: Estrutura correta dos dados
- **Rate Limiting**: Proteção contra spam

### Configurações de Segurança
```python
# Timeout de webhook (5 minutos)
WEBHOOK_TIMEOUT = 300

# Validação de timestamp
if abs(current_ts - ts) > 300:
    return False

# Validação de assinatura
hmac.compare_digest(signature, expected_signature)
```

## 📈 Monitoramento

### Health Checks
```bash
# Status do sistema
GET /comunication/status/

# Teste de conectividade
GET /comunication/test/

# Monitoramento contínuo
python monitor_system.py --continuous --interval 5
```

### Métricas Monitoradas
- **Eventos Webhook**: Total, pendentes, processados, falharam
- **Notificações**: Aprovadas, rejeitadas, pendentes
- **Compras**: Status e volume
- **Performance**: Tempo de resposta dos endpoints
- **Logs**: Análise de erros e warnings

## 🗄️ Banco de Dados

### Modelos Principais
```python
# WebhookEvent - Eventos recebidos
- event_id: ID único do evento
- event_type: Tipo (payment, plan, etc.)
- status: Status do processamento
- raw_data: Dados brutos do webhook
- signature_valid: Validação de assinatura

# WebhookLog - Logs detalhados
- webhook_event: Referência ao evento
- level: Nível do log (DEBUG, INFO, WARNING, ERROR)
- message: Mensagem do log
- details: Detalhes adicionais

# PaymentNotification - Notificações de pagamento
- webhook_event: Referência ao evento
- notification_type: Tipo de notificação
- payment_id: ID do pagamento
- amount: Valor do pagamento
- payment_status: Status do pagamento
```

## 🔄 Fluxo de Pagamento

### 1. Criação da Compra
```python
# Usuário seleciona ingresso
purchase = Purchase.objects.create(
    ticket=ticket,
    user=user,
    quantity=quantity,
    total_price=total_price,
    status='pending'
)
```

### 2. Criação da Preferência
```python
# Sistema cria preferência no Mercado Pago
preference_data = {
    "items": [{
        "title": f"Ingresso {ticket.type} - {event.name}",
        "quantity": quantity,
        "unit_price": float(ticket.price),
        "currency_id": "BRL"
    }],
    "external_reference": str(purchase.id),
    "back_urls": {
        "success": f"{SITE_URL}/payment/success/",
        "failure": f"{SITE_URL}/payment/failure/",
        "pending": f"{SITE_URL}/payment/pending/"
    }
}
```

### 3. Processamento do Webhook
```python
# Mercado Pago envia webhook
# Sistema valida assinatura
# Sistema processa pagamento
# Sistema atualiza compra
# Sistema cria notificação
```

## 🚀 Deploy para Produção

### 1. Configuração Inicial
```bash
# Executar configuração
python setup_production.py

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 2. Configuração do Mercado Pago
1. Acesse o [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Configure as URLs dos webhooks
3. Configure a chave secreta
4. Selecione os eventos desejados

### 3. Monitoramento
```bash
# Monitoramento contínuo
python monitor_system.py --continuous

# Verificação manual
python monitor_system.py --hours 24
```

## 📋 Checklist de Produção

### ✅ Configuração
- [ ] Credenciais do Mercado Pago configuradas
- [ ] URLs de webhook configuradas
- [ ] Chave secreta configurada
- [ ] Ambiente de produção configurado

### ✅ Testes
- [ ] Testes de webhook executados
- [ ] Testes de cartão executados
- [ ] Testes de integração executados
- [ ] Monitoramento configurado

### ✅ Segurança
- [ ] Validação de assinatura funcionando
- [ ] Timeout de webhook configurado
- [ ] Logs de segurança ativados
- [ ] Rate limiting configurado

### ✅ Monitoramento
- [ ] Health checks funcionando
- [ ] Logs estruturados ativados
- [ ] Alertas configurados
- [ ] Relatórios gerados

## 🆘 Troubleshooting

### Problemas Comuns

#### Webhook não recebido
```bash
# Verificar conectividade
curl https://ingressoptga.pythonanywhere.com/comunication/test/

# Verificar logs
python monitor_system.py
```

#### Assinatura inválida
```bash
# Verificar chave secreta
echo "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"

# Verificar timestamp
# Deve estar dentro de 5 minutos
```

#### Compra não encontrada
```bash
# Verificar external_reference
# Deve corresponder ao ID da compra
```

### Logs de Debug
```bash
# Verificar logs do Django
tail -f logs/django.log

# Verificar logs de webhook
python manage.py shell
>>> from communication.models import WebhookEvent
>>> WebhookEvent.objects.filter(status='failed')
```

## 📞 Suporte

### Documentação
- [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
- [Django Documentation](https://docs.djangoproject.com/)
- [Webhook Security](https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks)

### Contato
- **Email**: vgf.tools1@gmail.com
- **Sistema**: https://ingressoptga.pythonanywhere.com
- **Admin**: https://ingressoptga.pythonanywhere.com/admin/

## 🎉 Conclusão

Sistema completo de pagamentos implementado com:
- ✅ Integração completa com Mercado Pago
- ✅ Webhooks seguros e confiáveis
- ✅ Testes abrangentes para todos os cenários
- ✅ Monitoramento e alertas
- ✅ Configuração para produção
- ✅ Documentação completa

**O sistema está pronto para produção!** 🚀