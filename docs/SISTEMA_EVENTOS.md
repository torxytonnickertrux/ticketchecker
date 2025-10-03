# 🎪 Sistema de Eventos

> **Documentação completa do sistema de gestão de eventos do TicketChecker**

## 📋 Visão Geral

O sistema de eventos permite criar, gerenciar e exibir eventos com funcionalidades avançadas de busca, filtros e controle de status.

## 🎯 Funcionalidades Principais

### **Criação de Eventos**
- Nome e descrição do evento
- Data e hora específicas
- Localização completa
- Upload de imagem
- Status ativo/inativo

### **Gestão de Eventos**
- Edição de eventos existentes
- Controle de visibilidade
- Validação de datas futuras
- Sistema de busca avançada

## 🛠️ Modelos de Dados

### **Event Model**
```python
class Event(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome do Evento")
    description = models.TextField(verbose_name="Descrição")
    date = models.DateTimeField(verbose_name="Data e Hora")
    location = models.CharField(max_length=255, verbose_name="Local")
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🎨 Interface do Usuário

### **Lista de Eventos**
- Cards responsivos com informações
- Filtros por data, local e busca
- Paginação automática
- Status visual dos eventos

### **Detalhes do Evento**
- Informações completas
- Galeria de imagens
- Lista de ingressos disponíveis
- Botões de ação

## 🔍 Sistema de Busca

### **Filtros Disponíveis**
- **Busca por texto** - Nome e descrição
- **Filtro por data** - Data inicial e final
- **Filtro por local** - Localização específica
- **Status** - Eventos ativos/inativos

### **Implementação**
```python
def event_list(request):
    form = EventSearchForm(request.GET)
    events = Event.objects.filter(is_active=True)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        location = form.cleaned_data.get('location')
        
        if search:
            events = events.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        # ... outros filtros
```

## 📱 Responsividade

### **Breakpoints**
- **Mobile** - < 768px
- **Tablet** - 768px - 1024px
- **Desktop** - > 1024px

### **Layout Responsivo**
- Grid adaptativo
- Cards empilhados em mobile
- Navegação otimizada
- Imagens responsivas

## 🎛️ Administração

### **Interface Jazzmin**
- Lista de eventos com filtros
- Ações em massa
- Busca rápida
- Estatísticas visuais

### **Campos Editáveis**
- Informações básicas
- Data e hora
- Localização
- Status ativo/inativo
- Upload de imagem

## 🔧 Configurações

### **Validações**
- Data deve ser futura
- Nome obrigatório
- Localização obrigatória
- Imagem opcional

### **Permissões**
- Criação - Staff users
- Edição - Staff users
- Visualização - Todos
- Exclusão - Superusers

## 📊 Analytics

### **Métricas Disponíveis**
- Total de eventos
- Eventos ativos/inativos
- Eventos por mês
- Eventos por localização

### **Relatórios**
- Eventos mais populares
- Vendas por evento
- Performance temporal
- Análise geográfica

## 🚀 Exemplos de Uso

### **Criar Evento**
```python
# Via Django Admin
event = Event.objects.create(
    name="Festa de Aniversário",
    description="Uma festa incrível!",
    date=timezone.now() + timedelta(days=30),
    location="Salão de Festas",
    is_active=True
)
```

### **Buscar Eventos**
```python
# Busca por nome
events = Event.objects.filter(name__icontains="festa")

# Eventos futuros
events = Event.objects.filter(date__gt=timezone.now())

# Eventos ativos
events = Event.objects.filter(is_active=True)
```

## 🎯 Próximas Funcionalidades

- [ ] Sistema de categorias
- [ ] Eventos recorrentes
- [ ] Integração com calendário
- [ ] Notificações automáticas
- [ ] Sistema de favoritos

## 📞 Suporte

Para dúvidas sobre o sistema de eventos:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Documentação** - [Wiki](https://github.com/seu-usuario/ticketchecker/wiki)

---

<div align="center">
  <strong>🎪 Sistema de Eventos - Organize seus eventos com facilidade!</strong>
</div>
