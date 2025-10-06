"""
Configurações específicas para PythonAnywhere
"""

from .settings import *
import os

# Detectar se estamos no PythonAnywhere
# Verificar múltiplas formas de detectar o ambiente PythonAnywhere
IS_PYTHONANYWHERE = (
    'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or
    'pythonanywhere.com' in os.environ.get('SERVER_NAME', '') or
    '/home/ingressoptga/' in os.path.abspath(__file__) or
    os.path.exists('/home/ingressoptga/ticketchecker')
)

if IS_PYTHONANYWHERE:
    # Configurações de produção para PythonAnywhere
    DEBUG = False
    
    # Hosts permitidos para PythonAnywhere
    ALLOWED_HOSTS = [
        'ingressoptga.pythonanywhere.com',
        'www.ingressoptga.pythonanywhere.com',
    ]
    
    # Configurações de arquivos estáticos para PythonAnywhere
    STATIC_ROOT = '/home/ingressoptga/ticketchecker/staticfiles'
    STATICFILES_DIRS = [
        '/home/ingressoptga/ticketchecker/static',
    ]
    
    # Configurações para arquivos estáticos do admin
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
    
    # Configurações de media para PythonAnywhere
    MEDIA_ROOT = '/home/ingressoptga/ticketchecker/media'
    
    # Configurações de Email para produção
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'vgf.tools1@gmail.com')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'vgf.tools1@gmail.com')
    SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'vgf.tools1@gmail.com')
    
    # Configurações de segurança
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Configurações de sessão
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Configurações do Mercado Pago para produção
    MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', 'APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812')
    MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY', 'APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71')
    MERCADO_PAGO_SANDBOX = os.getenv('MERCADO_PAGO_SANDBOX', 'True').lower() == 'true'
    
    # URL do site para callbacks do Mercado Pago
    SITE_URL = os.getenv('SITE_URL', 'https://ingressoptga.pythonanywhere.com')
    
    # URLs de callback do Mercado Pago para produção
    MERCADO_PAGO_BACKURL_SUCCESS = f"{SITE_URL}/events/pagamento/sucesso/"
    MERCADO_PAGO_BACKURL_FAILURE = f"{SITE_URL}/events/pagamento/falha/"
    MERCADO_PAGO_BACKURL_PENDING = f"{SITE_URL}/events/pagamento/pendente/"
    
    # Configuração de produção - desabilitar sandbox se PRODUCTION=True
    if os.getenv('PRODUCTION', 'False').lower() == 'true':
        MERCADO_PAGO_SANDBOX = False
    
    # Configurações de Webhook
    WEBHOOK_SECRET_KEY = os.getenv('WEBHOOK_SECRET_KEY', '1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d')
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', '300'))
    
    # Configuração de logging segura para PythonAnywhere
    # Sempre usar configuração simples para evitar erros de permissão
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
else:
    # Configurações de desenvolvimento local
    DEBUG = True
    ALLOWED_HOSTS = ['*']
    
    # Configurações de arquivos estáticos para desenvolvimento
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    
    # Configurações para arquivos estáticos do admin
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
    
    # Configurações de media para desenvolvimento
    MEDIA_ROOT = BASE_DIR / 'media'
    
    # Configurações do Mercado Pago para desenvolvimento
    MERCADO_PAGO_ACCESS_TOKEN = os.getenv('MERCADO_PAGO_ACCESS_TOKEN', 'APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812')
    MERCADO_PAGO_PUBLIC_KEY = os.getenv('MERCADO_PAGO_PUBLIC_KEY', 'APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71')
    MERCADO_PAGO_SANDBOX = os.getenv('MERCADO_PAGO_SANDBOX', 'True').lower() == 'true'
    
    # URL do site para callbacks do Mercado Pago
    SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
    
    # Configurações de Webhook
    WEBHOOK_SECRET_KEY = os.getenv('WEBHOOK_SECRET_KEY', '1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d')
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', '300'))
    
    # Email para desenvolvimento (console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# CONFIGURAÇÕES DO DJANGO-ALLAUTH (GOOGLE OAUTH)
# =============================================================================

# ID do site (necessário para django-allauth)
SITE_ID = 1

# Configurações de autenticação
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Backend padrão do Django
    'allauth.account.auth_backends.AuthenticationBackend',  # Backend do allauth
]

# Configurações do allauth
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

# URLs de redirecionamento
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Configurações do Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Configurações de credenciais do Google (serão definidas via variáveis de ambiente)
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET', '')

# Configurações de segurança
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if not DEBUG else 'http'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 dias