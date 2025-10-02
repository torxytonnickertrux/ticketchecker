"""
Configurações específicas para resolver problemas do admin Django no PythonAnywhere
"""

from .settings import *
import os

# Detectar se estamos no PythonAnywhere
IS_PYTHONANYWHERE = 'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')

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
    EMAIL_HOST_USER = 'seu-email@gmail.com'  # Substitua pelo seu email
    EMAIL_HOST_PASSWORD = 'sua-senha-de-app'  # Substitua pela sua senha de app
    
    # Configurações de segurança
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Configurações de sessão
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Logging apenas se o diretório existir
    if os.path.exists('/home/ingressoptga/ticketchecker/logs/'):
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
    
    # Email para desenvolvimento (console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
