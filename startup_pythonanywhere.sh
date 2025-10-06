#!/bin/bash
# Script de inicialização para PythonAnywhere

# Configurar variáveis de ambiente
export MERCADO_PAGO_ACCESS_TOKEN="APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812"
export MERCADO_PAGO_PUBLIC_KEY="APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71"
export MERCADO_PAGO_SANDBOX="True"
export SITE_URL="https://ingressoptga.pythonanywhere.com"
export GOOGLE_OAUTH2_CLIENT_ID="REPLACE_WITH_YOUR_GOOGLE_CLIENT_ID"
export GOOGLE_OAUTH2_SECRET="REPLACE_WITH_YOUR_GOOGLE_CLIENT_SECRET"
export EMAIL_HOST_USER="vgf.tools1@gmail.com"
export EMAIL_HOST_PASSWORD=""
export WEBHOOK_SECRET_KEY="1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d"

# Navegar para o diretório do projeto
cd /home/ingressoptga/ticketchecker

# Aplicar migrações
python3.10 manage.py migrate --settings=backend.settings_pythonanywhere

# Coletar arquivos estáticos
python3.10 manage.py collectstatic --noinput --settings=backend.settings_pythonanywhere

echo "✅ Aplicação configurada com sucesso!"
