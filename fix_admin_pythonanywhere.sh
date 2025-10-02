#!/bin/bash

# Script para corrigir problemas do admin Django no PythonAnywhere
# Execute este script após fazer deploy

echo "🔧 Corrigindo problemas do admin Django no PythonAnywhere..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Coletar arquivos estáticos (incluindo admin)
echo "📄 Coletando arquivos estáticos do admin..."
python manage.py collectstatic --noinput

# Verificar se os arquivos do admin foram coletados
echo "🔍 Verificando arquivos do admin..."
if [ -d "staticfiles/admin" ]; then
    echo "✅ Arquivos do admin coletados com sucesso!"
    echo "📊 Arquivos encontrados:"
    find staticfiles/admin -name "*.css" -o -name "*.js" | head -10
else
    echo "❌ Arquivos do admin não encontrados!"
    echo "🔧 Tentando novamente..."
    python manage.py collectstatic --noinput --clear
fi

# Configurar permissões
echo "🔐 Configurando permissões..."
chmod -R 755 staticfiles/
chmod -R 755 media/

echo "✅ Configuração do admin concluída!"
echo "🌐 Acesse /admin/ para testar o admin Django"
echo "📁 Arquivos estáticos em: $(pwd)/staticfiles/"
