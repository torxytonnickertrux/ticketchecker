#!/bin/bash

# Script de setup final para PythonAnywhere
# Execute este script após clonar o repositório

echo "🚀 Configurando TicketChecker no PythonAnywhere (Versão Final)..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Configurar banco de dados
echo "🗄️ Configurando banco de dados..."
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
echo "📄 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário (opcional)
echo "👤 Para criar um superusuário, execute:"
echo "python manage.py createsuperuser"

echo "✅ Setup concluído!"
echo "🌐 Configure o WSGI com: backend.settings_pythonanywhere"
echo "📁 Certifique-se de que os diretórios existem:"
echo "   - /home/ingressoptga/ticketchecker/static"
echo "   - /home/ingressoptga/ticketchecker/staticfiles"
echo "   - /home/ingressoptga/ticketchecker/media"
echo "   - /home/ingressoptga/ticketchecker/logs"
