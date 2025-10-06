"""
Configurações específicas para testes de integração com Mercado Pago
"""
from .settings_test import *

# Configurações específicas do Mercado Pago para testes
MERCADO_PAGO_ACCESS_TOKEN = 'TEST-ACCESS-TOKEN'
MERCADO_PAGO_PUBLIC_KEY = 'TEST-PUBLIC-KEY'
MERCADO_PAGO_SANDBOX = True

# URLs para testes
SITE_URL = 'http://localhost:8000'
MERCADO_PAGO_BACKURL_SUCCESS = f"{SITE_URL}/events/pagamento/sucesso/"
MERCADO_PAGO_BACKURL_FAILURE = f"{SITE_URL}/events/pagamento/falha/"
MERCADO_PAGO_BACKURL_PENDING = f"{SITE_URL}/events/pagamento/pendente/"

# Configurações de webhook para teste
WEBHOOK_SECRET_KEY = "test-webhook-secret-key"
WEBHOOK_TIMEOUT = 300

# Configurações de email para teste
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'test@example.com'

# Configurações de logging para teste
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'events': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}