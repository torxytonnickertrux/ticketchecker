# 🎫 Sistema de Ingressos com Pagamentos Mercado Pago

## 🚀 Sistema Completo e Testado

Sistema profissional de venda de ingressos integrado com Mercado Pago, incluindo webhooks seguros, testes abrangentes e monitoramento completo.

## ✨ Funcionalidades

### 💳 Pagamentos
- **PIX**: Pagamento instantâneo
- **Cartão de Crédito**: Mastercard, Visa, American Express, Elo
- **Cartão de Débito**: Elo Débito
- **Checkout Pro**: Interface completa do Mercado Pago

### 🔗 Webhooks Avançados
- **Validação de Segurança**: HMAC SHA256 + Timestamp
- **Processamento Automático**: Atualização de status em tempo real
- **Logs Detalhados**: Rastreamento completo de eventos
- **Ambientes Separados**: Teste e Produção

### 🧪 Testes Abrangentes
- **Testes de Webhook**: Conectividade e segurança
- **Testes de Cartão**: Todos os cenários de pagamento
- **Testes de Integração**: Fluxo completo
- **Testes de Performance**: Monitoramento de sistema

### 📊 Monitoramento
- **Health Checks**: Verificação de saúde do sistema
- **Logs Estruturados**: Análise de eventos
- **Alertas**: Notificações de problemas
- **Relatórios**: Estatísticas detalhadas

## 🔧 Configuração Rápida

### 1. Instalação
```bash
# Clonar repositório
git clone <repository-url>
cd sistema_ingresso

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### 2. Configuração do Mercado Pago
```bash
# Configurar variáveis de ambiente
cp .env.example .env

# Editar .env com suas credenciais
MERCADO_PAGO_ACCESS_TOKEN=seu_access_token
MERCADO_PAGO_PUBLIC_KEY=sua_public_key
WEBHOOK_SECRET_KEY=sua_chave_secreta
```

### 3. Configuração de Produção
```bash
# Executar configuração automática
python setup_production.py

# Executar todos os testes
python run_all_tests.py

# Validar sistema
python validate_system.py
```

## 🧪 Execução de Testes

### Teste Completo
```bash
# Executar todos os testes
python run_all_tests.py
```

### Testes Individuais
```bash
# Testes de webhook
python test_webhook.py

# Testes abrangentes
python test_comprehensive_payment.py

# Testes de cartão
python test_credit_cards.py

# Monitoramento
python monitor_system.py
```

## 🔗 URLs dos Webhooks

### Teste
```
https://ingressoptga.pythonanywhere.com/comunication/build/teste
```

### Produção
```
https://ingressoptga.pythonanywhere.com/comunication/build/production
```

### Chave Secreta
```
1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
```

## 💳 Cartões de Teste

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

## 📊 Monitoramento

### Health Checks
```bash
# Status do sistema
curl https://ingressoptga.pythonanywhere.com/comunication/status/

# Teste de conectividade
curl https://ingressoptga.pythonanywhere.com/comunication/test/

# Monitoramento contínuo
python monitor_system.py --continuous --interval 5
```

### Métricas Monitoradas
- **Eventos Webhook**: Total, pendentes, processados, falharam
- **Notificações**: Aprovadas, rejeitadas, pendentes
- **Compras**: Status e volume
- **Performance**: Tempo de resposta dos endpoints
- **Logs**: Análise de erros e warnings

## 🗄️ Estrutura do Projeto

```
sistema_ingresso/
├── backend/                 # Configurações Django
├── communication/           # App de comunicação Mercado Pago
│   ├── models.py           # Modelos de webhook
│   ├── views.py            # Views de webhook
│   ├── services.py         # Serviços de processamento
│   ├── validators.py       # Validadores de segurança
│   └── test_service.py     # Serviço de testes
├── events/                 # App de eventos e ingressos
│   ├── models.py           # Modelos de evento, ticket, compra
│   ├── views.py            # Views de eventos
│   ├── simple_payment.py   # Sistema de pagamento
│   └── mercadopago_service.py  # Serviço Mercado Pago
├── docs/                   # Documentação
├── test_*.py              # Scripts de teste
├── monitor_system.py      # Monitoramento
├── setup_production.py    # Configuração de produção
├── validate_system.py     # Validação final
└── run_all_tests.py       # Executor de testes
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

## 📚 Documentação Adicional

- [Sistema de Pagamentos Completo](docs/SISTEMA_PAGAMENTOS_COMPLETO.md)
- [Webhook Mercado Pago](docs/WEBHOOK_MERCADO_PAGO.md)
- [Configuração de Produção](docs/CONFIGURACAO_PROJETO.md)

## 🏆 Status do Projeto

- **Desenvolvimento**: ✅ Concluído
- **Testes**: ✅ Concluído
- **Documentação**: ✅ Concluído
- **Produção**: ✅ Pronto
- **Monitoramento**: ✅ Ativo

**Sistema 100% funcional e testado!** 🎯