# 🎫 Sistema de Ingressos

> **Documentação completa do sistema de gestão de ingressos do TicketChecker**

## 📋 Visão Geral

O sistema de ingressos permite criar diferentes tipos de ingressos para eventos, com controle de estoque, preços e limitações por pessoa.

## 🎯 Funcionalidades Principais

### **Tipos de Ingressos**
- **VIP** - Ingressos premium
- **Standard** - Ingressos padrão
- **Estudante** - Desconto para estudantes
- **Early Bird** - Desconto por compra antecipada

### **Controle de Estoque**
- Quantidade disponível em tempo real
- Controle de vendas
- Alertas de estoque baixo
- Bloqueio automático quando esgotado

## 🛠️ Modelos de Dados

### **Ticket Model**
```python
class Ticket(models.Model):
    TICKET_TYPES = [
        ('VIP', 'VIP'),
        ('Standard', 'Padrão'),
        ('Student', 'Estudante'),
        ('Early Bird', 'Early Bird'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    type = models.CharField(max_length=255, choices=TICKET_TYPES)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    max_per_person = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
```

## 💰 Sistema de Preços

### **Configuração de Preços**
- Preço base por tipo
- Validação de valores positivos
- Formatação monetária
- Cálculo automático de totais

### **Exemplos de Preços**
```python
# VIP - R$ 299,90
ticket_vip = Ticket.objects.create(
    event=event,
    price=299.90,
    type='VIP',
    quantity=50
)

# Standard - R$ 149,90
ticket_standard = Ticket.objects.create(
    event=event,
    price=149.90,
    type='Standard',
    quantity=200
)
```

## 🛒 Sistema de Compra

### **Processo de Compra**
1. **Seleção do Evento** - Escolher evento desejado
2. **Escolha do Ingresso** - Selecionar tipo e quantidade
3. **Aplicar Cupom** - Usar código de desconto (opcional)
4. **Finalizar Compra** - Processar pagamento
5. **Confirmação** - Receber QR Code por email

### **Validações de Compra**
```python
def validate_purchase(ticket, quantity, user):
    # Verificar se o ingresso está ativo
    if not ticket.is_active:
        raise ValidationError("Ingresso não está disponível")
    
    # Verificar estoque
    if ticket.quantity < quantity:
        raise ValidationError("Quantidade insuficiente em estoque")
    
    # Verificar limite por pessoa
    if quantity > ticket.max_per_person:
        raise ValidationError(f"Máximo de {ticket.max_per_person} ingressos por pessoa")
```

## 📱 Interface do Usuário

### **Seleção de Ingressos**
- Cards com informações do ingresso
- Preço destacado
- Quantidade disponível
- Botão de compra

### **Carrinho de Compras**
- Resumo da compra
- Cálculo de totais
- Aplicação de cupons
- Finalização segura

## 🔍 Controle de Estoque

### **Atualização em Tempo Real**
```python
def update_stock(ticket, quantity):
    """Atualiza o estoque após uma compra"""
    ticket.quantity -= quantity
    ticket.save()
    
    # Verificar se esgotou
    if ticket.quantity <= 0:
        ticket.is_active = False
        ticket.save()
```

### **Alertas de Estoque**
- Notificação quando estoque < 10
- Bloqueio automático quando esgotado
- Relatórios de vendas
- Previsão de esgotamento

## 🎛️ Administração

### **Gestão de Ingressos**
- Criação de novos tipos
- Edição de preços
- Controle de estoque
- Ativação/desativação

### **Relatórios de Vendas**
- Vendas por tipo de ingresso
- Performance por evento
- Análise de preços
- Métricas de conversão

## 📊 Analytics

### **Métricas Disponíveis**
- Total de ingressos vendidos
- Receita por tipo
- Taxa de conversão
- Performance temporal

### **Relatórios**
```python
# Vendas por tipo
sales_by_type = Ticket.objects.annotate(
    total_sales=Count('purchases')
).values('type', 'total_sales')

# Receita total
total_revenue = Purchase.objects.aggregate(
    total=Sum('total_price')
)['total']
```

## 🚀 Exemplos de Uso

### **Criar Ingressos para um Evento**
```python
event = Event.objects.get(id=1)

# VIP - 50 unidades
ticket_vip = Ticket.objects.create(
    event=event,
    price=299.90,
    type='VIP',
    quantity=50,
    max_per_person=2
)

# Standard - 200 unidades
ticket_standard = Ticket.objects.create(
    event=event,
    price=149.90,
    type='Standard',
    quantity=200,
    max_per_person=5
)
```

### **Verificar Disponibilidade**
```python
def check_availability(ticket_id, quantity):
    ticket = Ticket.objects.get(id=ticket_id)
    
    if ticket.quantity >= quantity and ticket.is_active:
        return True, "Disponível"
    elif ticket.quantity < quantity:
        return False, "Estoque insuficiente"
    else:
        return False, "Ingresso esgotado"
```

## 🎯 Próximas Funcionalidades

- [ ] Ingressos com desconto progressivo
- [ ] Sistema de lista de espera
- [ ] Ingressos com data de validade
- [ ] Integração com APIs de pagamento
- [ ] Sistema de reembolsos

## 📞 Suporte

Para dúvidas sobre o sistema de ingressos:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Documentação** - [Wiki](https://github.com/seu-usuario/ticketchecker/wiki)

---

<div align="center">
  <strong>🎫 Sistema de Ingressos - Controle total sobre suas vendas!</strong>
</div>
