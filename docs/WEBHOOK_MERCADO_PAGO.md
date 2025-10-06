# Sistema de Webhooks - Mercado Pago

## Visão Geral

Este sistema implementa webhooks para comunicação com o Mercado Pago, permitindo receber notificações em tempo real sobre o status dos pagamentos.

## URLs dos Webhooks

### Ambiente de Teste
```
URL: https://ingressoptga.pythonanywhere.com/comunication/build/teste
```

### Ambiente de Produção
```
URL: https://ingressoptga.pythonanywhere.com/comunication/build/production
```

## Configuração

### Chave Secreta
```
KEY: 1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
```

### Eventos Suportados

O sistema processa os seguintes tipos de eventos do Mercado Pago:

- **payment**: Notificações de pagamento (aprovado, rejeitado, cancelado, pendente)
- **plan**: Planos de assinatura (não processado)
- **subscription**: Assinaturas (não processado)
- **invoice**: Faturas (não processado)
- **point_integration_whitelist**: Integração Ponto (não processado)

## Funcionamento

### 1. Recebimento do Webhook

Quando o Mercado Pago envia uma notificação:

1. O sistema valida a assinatura usando HMAC SHA256
2. Verifica se o timestamp não é muito antigo (máximo 5 minutos)
3. Cria um registro de `WebhookEvent`
4. Processa o evento baseado no tipo

### 2. Processamento de Pagamentos

Para eventos do tipo `payment`:

1. Busca os dados completos do pagamento no Mercado Pago
2. Localiza a compra usando a `external_reference`
3. Atualiza o status da compra:
   - `approved` → `approved` (atualiza quantidade de tickets)
   - `rejected` → `rejected`
   - `cancelled` → `cancelled`
   - `pending` → `processing`
4. Cria uma notificação de pagamento
5. Registra logs detalhados

### 3. Logs e Monitoramento

O sistema mantém logs detalhados de todas as operações:

- **WebhookEvent**: Eventos recebidos
- **WebhookLog**: Logs detalhados de processamento
- **PaymentNotification**: Notificações de pagamento processadas

## Endpoints de Monitoramento

### Status do Sistema
```
GET /comunication/status/
```

Retorna estatísticas e eventos recentes.

### Teste de Conectividade
```
GET /comunication/test/
```

Verifica se o endpoint está funcionando.

## Segurança

### Validação de Assinatura

O sistema valida cada webhook usando:

1. **HMAC SHA256** com a chave secreta
2. **Timestamp** para prevenir ataques de replay
3. **Validação de payload** para garantir estrutura correta

### Headers Obrigatórios

- `X-Signature`: Assinatura HMAC SHA256
- `X-Signature-Ts`: Timestamp Unix

## Configuração no Mercado Pago

### 1. Acessar Configurações

1. Faça login no [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Acesse sua aplicação
3. Vá em "Notificações Webhook"

### 2. Configurar URLs

- **URL de Produção**: `https://ingressoptga.pythonanywhere.com/comunication/build/production`
- **URL de Teste**: `https://ingressoptga.pythonanywhere.com/comunication/build/teste`

### 3. Configurar Eventos

Selecione os eventos que deseja receber:

- ✅ payment.created
- ✅ payment.updated
- ✅ payment.approved
- ✅ payment.rejected
- ✅ payment.cancelled

### 4. Configurar Chave Secreta

Use a chave fornecida:
```
1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
```

## Troubleshooting

### Problemas Comuns

#### 1. Webhook não recebido
- Verificar se a URL está correta
- Verificar se o servidor está online
- Verificar logs do Mercado Pago

#### 2. Assinatura inválida
- Verificar se a chave secreta está correta
- Verificar se o timestamp está dentro do limite (5 minutos)
- Verificar se o payload está sendo enviado corretamente

#### 3. Compra não encontrada
- Verificar se a `external_reference` está sendo enviada
- Verificar se a compra existe no sistema
- Verificar logs de erro

### Logs de Debug

Para debugar problemas:

1. Acesse o admin Django: `/admin/`
2. Vá em "Comunicação Mercado Pago" → "Eventos Webhook"
3. Verifique os eventos com status "failed"
4. Consulte os logs detalhados

### Monitoramento

Use o endpoint de status para monitorar:

```bash
curl https://ingressoptga.pythonanywhere.com/comunication/status/
```

## Estrutura do Banco de Dados

### WebhookEvent
- Armazena eventos recebidos
- Status: pending, processed, failed, ignored
- Validação de assinatura

### WebhookLog
- Logs detalhados de processamento
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL

### PaymentNotification
- Notificações de pagamento processadas
- Tipos: approved, rejected, cancelled, refunded, pending

## Exemplo de Payload

```json
{
  "id": "1234567890",
  "type": "payment",
  "data": {
    "id": "1234567890"
  },
  "date_created": "2024-01-01T00:00:00Z",
  "user_id": "123456789",
  "api_version": "v1",
  "action": "payment.created"
}
```

## Exemplo de Resposta

```json
{
  "status": "ok",
  "message": "Evento processado com sucesso"
}
```

## Considerações de Produção

1. **Monitoramento**: Configure alertas para eventos falhados
2. **Backup**: Mantenha backup dos logs importantes
3. **Performance**: Monitore o tempo de resposta dos webhooks
4. **Segurança**: Mantenha a chave secreta segura
5. **Escalabilidade**: Considere processamento assíncrono para alto volume