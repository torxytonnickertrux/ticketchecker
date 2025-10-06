"""
Configurações específicas para desenvolvimento local com MailHog
"""

from .settings import *

# Configurações de Email para desenvolvimento local (MailHog)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@ticketchecker.local'
SERVER_EMAIL = 'noreply@ticketchecker.local'

# Configurações de debug
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Logging para emails
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'email_debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'events': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

print("🔧 Configurações de desenvolvimento local carregadas!")
print("📧 Email configurado para MailHog (localhost:1025)")
print("🌐 Interface web do MailHog: http://localhost:8025")