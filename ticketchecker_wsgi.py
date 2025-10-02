"""
WSGI config for ticketchecker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Adicionar o caminho do projeto ao Python path
path = '/home/ingressoptga/ticketchecker'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
