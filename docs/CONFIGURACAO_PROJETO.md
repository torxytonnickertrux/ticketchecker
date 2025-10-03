# ⚙️ Configuração do Projeto

> **Guia completo de configuração do TicketChecker**

## 📋 Pré-requisitos

### **Sistema Operacional**
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+
- CentOS 7+

### **Software Necessário**
- Python 3.13+
- Django 5.2.7
- PostgreSQL 12+ (opcional)
- Git 2.30+

## 🚀 Instalação Rápida

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/ticketchecker.git
cd ticketchecker
```

### **2. Ambiente Virtual**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configurar Banco de Dados**
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

## 🔧 Configuração Detalhada

### **Variáveis de Ambiente**
```bash
# .env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### **Configuração do Django**
```python
# backend/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações básicas
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configurações de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### **Configuração do Jazzmin**
```python
# backend/settings.py
JAZZMIN_SETTINGS = {
    "site_title": "TicketChecker Admin",
    "site_header": "🎫 TicketChecker",
    "site_brand": "Sistema de Ingressos",
    "welcome_sign": "Bem-vindo ao TicketChecker",
    "custom_css": None,
    "custom_js": "admin_custom_button.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}
```

## 🗄️ Configuração do Banco de Dados

### **SQLite (Desenvolvimento)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### **PostgreSQL (Produção)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ticketchecker',
        'USER': 'postgres',
        'PASSWORD': 'sua-senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📧 Configuração de Email

### **Gmail SMTP**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'TicketChecker <noreply@ticketchecker.com>'
```

### **Outros Provedores**
```python
# Outlook
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587

# Yahoo
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587

# SendGrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
```

## 🎨 Configuração de Interface

### **Templates Personalizados**
```
template/
├── admin/              # Templates do admin
├── jazzmin/           # Templates do Jazzmin
├── events/            # Templates do app
└── base.html          # Template base
```

### **Arquivos Estáticos**
```
static/
├── css/               # Estilos CSS
├── js/                # JavaScript
├── images/            # Imagens
└── admin_custom_button.js  # Botão de navegação
```

## 🔐 Configuração de Segurança

### **Configurações de Produção**
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com', 'www.seu-dominio.com']

# Segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS (produção)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### **Configuração de CORS**
```python
# Se necessário para APIs
CORS_ALLOWED_ORIGINS = [
    "https://seu-dominio.com",
    "https://www.seu-dominio.com",
]
```

## 📊 Configuração de Logs

### **Configuração de Logging**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 Configuração de Deploy

### **PythonAnywhere**
```bash
# Instalar dependências
pip3.10 install --user django
pip3.10 install --user django-jazzmin
pip3.10 install --user python-dotenv

# Configurar WSGI
# Ver docs/DEPLOY_PYTHONANYWHERE.md
```

### **Heroku**
```bash
# Criar app
heroku create ticketchecker-app

# Configurar variáveis
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set DEBUG=False

# Deploy
git push heroku main
```

## 🔧 Troubleshooting

### **Problemas Comuns**

#### **Erro de Migração**
```bash
# Resetar migrações
python manage.py migrate --fake-initial
```

#### **Erro de Estáticos**
```bash
# Coletar estáticos
python manage.py collectstatic
```

#### **Erro de Permissões**
```bash
# Linux/Mac
chmod +x manage.py
```

### **Logs de Debug**
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## 📞 Suporte

Para problemas de configuração:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Documentação** - [Wiki](https://github.com/seu-usuario/ticketchecker/wiki)

---

<div align="center">
  <strong>⚙️ Configuração do Projeto - Configure seu TicketChecker!</strong>
</div>
