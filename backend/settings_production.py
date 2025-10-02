"""
Configurações de produção para PythonAnywhere
"""

from .settings import *

# Configurações de produção
DEBUG = False

# Hosts permitidos para PythonAnywhere
ALLOWED_HOSTS = [
    'ingressoptga.pythonanywhere.com',  # Substitua pelo seu domínio
    'www.ingressoptga.pythonanywhere.com',
]

# Configurações de Email para produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'  # Substitua pelo seu email
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'  # Substitua pela sua senha de app

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Configurações de sessão
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/ingressoptga/ticketchecker/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
