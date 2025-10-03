#!/bin/bash

# Script para corrigir erros no PythonAnywhere
# Execute este script no console do PythonAnywhere

echo "🔧 Iniciando correção de erros PythonAnywhere..."

# 1. Navegar para o diretório do projeto
cd /home/ingressoptga/ticketchecker

# 2. Ativar ambiente virtual
source /home/ingressoptga/.virtualenvs/venv0/bin/activate

# 3. Instalar dependências faltantes
echo "📦 Instalando dependências..."
pip3.10 install --user python-dotenv
pip3.10 install --user django-jazzmin
pip3.10 install --user pillow
pip3.10 install --user qrcode

# 4. Criar backup do settings.py
echo "💾 Criando backup do settings.py..."
cp backend/settings.py backend/settings.py.backup

# 5. Corrigir settings.py
echo "🔧 Corrigindo settings.py..."

# Remover import do dotenv
sed -i 's/from dotenv import load_dotenv/# from dotenv import load_dotenv/' backend/settings.py
sed -i 's/load_dotenv()/# load_dotenv()/' backend/settings.py

# Adicionar configurações de produção
cat >> backend/settings.py << 'EOF'

# Configurações de produção para PythonAnywhere
SECRET_KEY = 'django-insecure-production-key-change-this'
DEBUG = False
ALLOWED_HOSTS = ['ingressoptga.pythonanywhere.com']

# Configurações de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = '/home/ingressoptga/ticketchecker/static'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/ingressoptga/ticketchecker/media'

# Configuração de logging simples
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
EOF

# 6. Executar migrações
echo "🗄️ Executando migrações..."
python3.10 manage.py migrate

# 7. Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python3.10 manage.py collectstatic --noinput

# 8. Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python3.10 manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superusuário 'admin' criado com senha 'admin123'")
else:
    print("Superusuário já existe")
EOF

# 9. Verificar se tudo está funcionando
echo "✅ Verificando configuração..."
python3.10 manage.py check

echo "🎉 Correção concluída!"
echo "📝 Próximos passos:"
echo "1. Acesse https://ingressoptga.pythonanywhere.com"
echo "2. Teste o admin: https://ingressoptga.pythonanywhere.com/admin/"
echo "3. Login: admin / admin123"
echo "4. Se houver problemas, verifique o Error log no PythonAnywhere"
