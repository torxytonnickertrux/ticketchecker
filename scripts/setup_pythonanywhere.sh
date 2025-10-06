#!/bin/bash

# Script de setup para PythonAnywhere
# Execute este script após clonar o repositório

echo "🚀 Configurando TicketChecker no PythonAnywhere..."

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
echo "🌐 Acesse seu domínio no PythonAnywhere para testar"
