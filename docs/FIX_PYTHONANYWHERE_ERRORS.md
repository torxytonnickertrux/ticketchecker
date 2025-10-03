# 🔧 Correção de Erros PythonAnywhere

> **Guia para corrigir erros comuns no PythonAnywhere**

## 🚨 Erros Identificados

### **1. ModuleNotFoundError: No module named 'dotenv'**
```
ModuleNotFoundError: No module named 'dotenv'
```

### **2. ValueError: Unable to configure handler 'file'**
```
ValueError: Unable to configure handler 'file'
```

### **3. TypeError: '<' not supported between instances of 'NoneType' and 'int'**
```
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

## 🛠️ Soluções

### **1. Instalar Dependências Faltantes**

#### **Via Console PythonAnywhere**
```bash
# Acessar o console
cd /home/ingressoptga/ticketchecker

# Ativar ambiente virtual
source /home/ingressoptga/.virtualenvs/venv0/bin/activate

# Instalar dependências
pip3.10 install --user python-dotenv
pip3.10 install --user django-jazzmin
pip3.10 install --user pillow
pip3.10 install --user qrcode
```

#### **Via requirements.txt**
```bash
# Criar requirements.txt
echo "Django==5.2.7" > requirements.txt
echo "python-dotenv==1.0.0" >> requirements.txt
echo "django-jazzmin==3.0.1" >> requirements.txt
echo "Pillow==10.0.0" >> requirements.txt
echo "qrcode==7.4.2" >> requirements.txt

# Instalar
pip3.10 install --user -r requirements.txt
```

### **2. Corrigir Configuração de Logs**

#### **Problema no settings.py**
```python
# REMOVER ou COMENTAR esta configuração problemática
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',  # ← PROBLEMA: pasta não existe
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

#### **Solução: Configuração Simples**
```python
# backend/settings.py
# REMOVER a configuração de LOGGING problemática
# ou usar configuração mais simples:

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
        'level': 'INFO',
    },
}
```

### **3. Corrigir Erro de Comparação None**

#### **Problema no models.py**
```python
# ERRO: Comparação com None
def clean(self):
    if self.date and self.date <= timezone.now():  # ← PROBLEMA
        raise ValidationError("A data do evento deve ser no futuro.")
```

#### **Solução: Verificação de None**
```python
# backend/settings.py ou models.py
def clean(self):
    if self.date is not None and self.date <= timezone.now():
        raise ValidationError("A data do evento deve ser no futuro.")
```

### **4. Configuração de Produção PythonAnywhere**

#### **settings.py para Produção**
```python
# backend/settings.py
import os
from pathlib import Path

# Configurações básicas
SECRET_KEY = 'sua-chave-secreta-aqui'  # Usar chave fixa para produção
DEBUG = False
ALLOWED_HOSTS = ['ingressoptga.pythonanywhere.com']

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configurações de email (opcional)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = '/home/ingressoptga/ticketchecker/static'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/ingressoptga/ticketchecker/media'

# REMOVER configuração de LOGGING problemática
# LOGGING = { ... }  # COMENTAR ou REMOVER
```

### **5. Configurar WSGI**

#### **Arquivo WSGI Correto**
```python
# /var/www/ingressoptga_pythonanywhere_com_wsgi.py
import os
import sys

# Adicionar o diretório do projeto ao path
path = '/home/ingressoptga/ticketchecker'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 🚀 Passos para Correção

### **1. Acessar Console PythonAnywhere**
```bash
# Ir para o diretório do projeto
cd /home/ingressoptga/ticketchecker

# Ativar ambiente virtual
source /home/ingressoptga/.virtualenvs/venv0/bin/activate
```

### **2. Instalar Dependências**
```bash
# Instalar python-dotenv
pip3.10 install --user python-dotenv

# Instalar outras dependências
pip3.10 install --user django-jazzmin
pip3.10 install --user pillow
pip3.10 install --user qrcode
```

### **3. Corrigir settings.py**
```bash
# Editar arquivo de configuração
nano backend/settings.py
```

**Remover ou comentar:**
```python
# COMENTAR estas linhas:
# from dotenv import load_dotenv
# load_dotenv()

# COMENTAR configuração de LOGGING problemática:
# LOGGING = { ... }
```

### **4. Configurar Variáveis de Ambiente**
```python
# Usar valores fixos em vez de dotenv
SECRET_KEY = 'sua-chave-secreta-aqui'
DEBUG = False
ALLOWED_HOSTS = ['ingressoptga.pythonanywhere.com']
```

### **5. Executar Migrações**
```bash
# Executar migrações
python3.10 manage.py migrate

# Criar superusuário
python3.10 manage.py createsuperuser

# Coletar arquivos estáticos
python3.10 manage.py collectstatic
```

### **6. Reiniciar Aplicação**
- Ir para **Web** no PythonAnywhere
- Clicar em **Reload** na aplicação

## 🔍 Verificação

### **Testar se Funcionou**
1. Acessar: `https://ingressoptga.pythonanywhere.com`
2. Verificar se carrega sem erros
3. Testar admin: `https://ingressoptga.pythonanywhere.com/admin/`

### **Logs de Erro**
- Verificar **Error log** no PythonAnywhere
- Deve estar vazio ou sem erros críticos

## 📞 Suporte

Se ainda houver problemas:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **PythonAnywhere** - [Help](https://help.pythonanywhere.com/)

---

<div align="center">
  <strong>🔧 Correção de Erros - Resolva os problemas do PythonAnywhere!</strong>
</div>
