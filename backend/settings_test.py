"""
Configurações específicas para testes
"""
from .settings import *
import os

# Configurações de teste
DEBUG = True
TESTING = True

# Banco de dados em memória para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Configurações do Mercado Pago para teste
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812'
MERCADO_PAGO_PUBLIC_KEY = 'APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71'
MERCADO_PAGO_SANDBOX = True

# URLs para teste
SITE_URL = 'http://localhost:8000'

# Configurações de webhook para teste
WEBHOOK_SECRET_KEY = "1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"

# Desabilitar logging durante testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Configurações de email para teste
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Configurações de cache para teste
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Configurações de sessão para teste
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Configurações de arquivos estáticos para teste
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configurações de mídia para teste
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Configurações de segurança para teste
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Configurações de CSRF para teste
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

# Configurações de CORS para teste
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configurações de rate limiting para teste
RATELIMIT_ENABLE = False

# Configurações de cache para teste
CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = 'test'

# Configurações de logging para teste
LOGGING_CONFIG = None