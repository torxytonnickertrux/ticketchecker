# 🎫 TicketChecker - Sistema de Ingressos Inteligente

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org/)
[![Jazzmin](https://img.shields.io/badge/Jazzmin-3.0.1-purple.svg)](https://github.com/farridav/django-jazzmin)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Sistema completo de venda e gestão de ingressos online com interface moderna, validação QR Code e administração inteligente.**

## 🚀 Funcionalidades Principais

### 🎪 **Gestão de Eventos**
- ✅ Criação e edição de eventos
- ✅ Upload de imagens para eventos
- ✅ Sistema de localização e data/hora
- ✅ Filtros avançados (data, local, busca)
- ✅ Status ativo/inativo para eventos

### 🎫 **Sistema de Ingressos**
- ✅ Múltiplos tipos de ingressos (VIP, Standard, Estudante, Early Bird)
- ✅ Controle de estoque em tempo real
- ✅ Limite de compra por pessoa
- ✅ Preços dinâmicos por tipo
- ✅ Geração automática de QR Codes

### 💳 **Sistema de Pagamento**
- ✅ Processo de compra simplificado
- ✅ Integração com múltiplos métodos de pagamento
- ✅ Confirmação automática de pagamento
- ✅ Sistema de cupons de desconto
- ✅ Histórico completo de compras

### 🔍 **Validação de Ingressos**
- ✅ Validação via QR Code
- ✅ Interface de validação para organizadores
- ✅ Controle de ingressos já validados
- ✅ Prevenção de uso duplicado

### 👥 **Gestão de Usuários**
- ✅ Sistema de registro e login
- ✅ Perfis de usuário personalizados
- ✅ Histórico de compras individual
- ✅ Dashboard personalizado

### 🎛️ **Administração Inteligente**
- ✅ Interface Jazzmin moderna
- ✅ Navegação inteligente entre admin e site
- ✅ Dashboard administrativo completo
- ✅ Analytics de eventos
- ✅ Gestão de cupons e validações

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Django 5.2.7** - Framework web robusto
- **Python 3.13+** - Linguagem de programação
- **PostgreSQL/SQLite** - Banco de dados
- **Django Jazzmin** - Interface admin moderna

### **Frontend**
- **Bootstrap 5.3.2** - Framework CSS
- **Font Awesome 6.4.0** - Ícones
- **JavaScript ES6+** - Interatividade
- **QR Code Generation** - Geração de códigos QR

### **Recursos Avançados**
- **Sistema de Email** - Notificações automáticas
- **Upload de Arquivos** - Imagens e documentos
- **Sistema de Filtros** - Busca avançada
- **Responsive Design** - Mobile-first

## 📦 Instalação

### **Pré-requisitos**
```bash
Python 3.13+
Django 5.2.7
PostgreSQL (opcional)
```

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/ticketchecker.git
cd ticketchecker
```

### **2. Ambiente Virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configuração do Banco**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Criar Superusuário**
```bash
python manage.py createsuperuser
```

### **6. Executar Servidor**
```bash
python manage.py runserver
```

## 🎯 Uso do Sistema

### **Para Usuários Finais**
1. **Navegar pelos Eventos** - Visualizar eventos disponíveis
2. **Selecionar Ingressos** - Escolher tipo e quantidade
3. **Aplicar Cupons** - Usar códigos de desconto
4. **Finalizar Compra** - Processar pagamento
5. **Receber QR Code** - Ingresso digital via email

### **Para Organizadores**
1. **Criar Eventos** - Definir detalhes e configurações
2. **Configurar Ingressos** - Tipos, preços e quantidades
3. **Gerenciar Vendas** - Acompanhar vendas em tempo real
4. **Validar Ingressos** - Usar QR Code scanner
5. **Analisar Dados** - Relatórios e estatísticas

### **Para Administradores**
1. **Acesso ao Admin** - Interface Jazzmin moderna
2. **Gestão Completa** - Usuários, eventos, vendas
3. **Navegação Inteligente** - Botões para site principal
4. **Analytics Avançados** - Métricas detalhadas
5. **Configurações** - Sistema personalizável

## 📁 Estrutura do Projeto

```
ticketchecker/
├── 📁 backend/              # Configurações Django
│   ├── settings.py         # Configurações principais
│   ├── urls.py            # URLs do projeto
│   └── wsgi.py            # WSGI configuration
├── 📁 events/              # App principal
│   ├── models.py          # Modelos de dados
│   ├── views.py           # Views e lógica
│   ├── forms.py           # Formulários
│   ├── admin.py           # Configuração admin
│   └── templatetags/      # Template tags customizados
├── 📁 template/           # Templates HTML
│   ├── admin/             # Templates do admin
│   ├── jazzmin/          # Templates Jazzmin
│   └── events/            # Templates do app
├── 📁 static/             # Arquivos estáticos
│   ├── css/              # Estilos CSS
│   ├── js/               # JavaScript
│   └── images/            # Imagens
├── 📁 docs/               # Documentação
└── 📄 requirements.txt    # Dependências Python
```

## 🔧 Configuração

### **Variáveis de Ambiente**
```bash
# .env
SECRET_KEY=sua-chave-secreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### **Configurações do Jazzmin**
```python
JAZZMIN_SETTINGS = {
    "site_title": "TicketChecker Admin",
    "site_header": "🎫 TicketChecker",
    "site_brand": "Sistema de Ingressos",
    "welcome_sign": "Bem-vindo ao TicketChecker",
    "custom_css": None,
    "custom_js": "admin_custom_button.js",
}
```

## 🚀 Deploy

### **PythonAnywhere**
```bash
# Configurar ambiente
pip3.10 install --user django
pip3.10 install --user django-jazzmin
pip3.10 install --user python-dotenv

# Configurar WSGI
# Ver docs/DEPLOY_PYTHONANYWHERE.md
```

### **Heroku**
```bash
# Instalar Heroku CLI
heroku create ticketchecker-app
git push heroku main
heroku run python manage.py migrate
```

## 📊 Funcionalidades Avançadas

### **Sistema de Cupons**
- Códigos de desconto personalizados
- Percentual ou valor fixo
- Limite de uso por cupom
- Controle de validade

### **Analytics de Eventos**
- Vendas por evento
- Métricas de conversão
- Relatórios de performance
- Gráficos interativos

### **Validação QR Code**
- Geração automática de QR Codes
- Validação em tempo real
- Prevenção de fraudes
- Histórico de validações

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Equipe

- **Desenvolvedor Principal** - [Seu Nome](https://github.com/seu-usuario)
- **Contribuidores** - Veja [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 📞 Suporte

- **Email** - suporte@ticketchecker.com
- **Issues** - [GitHub Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Documentação** - [Wiki](https://github.com/seu-usuario/ticketchecker/wiki)

## 🎉 Agradecimentos

- Django Community
- Jazzmin Contributors
- Bootstrap Team
- Font Awesome Team

---

<div align="center">
  <strong>🎫 TicketChecker - Transformando a forma como você vende ingressos!</strong>
</div>
