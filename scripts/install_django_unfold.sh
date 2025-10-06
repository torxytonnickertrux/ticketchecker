#!/bin/bash

# Script para instalar Django Unfold no PythonAnywhere
# Execute este script após fazer deploy

echo "🚀 Instalando Django Unfold para interface futurista..."

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

# Coletar arquivos estáticos (incluindo Django Unfold)
echo "📄 Coletando arquivos estáticos do Django Unfold..."
python manage.py collectstatic --noinput

# Verificar se os arquivos do Django Unfold foram coletados
echo "🔍 Verificando arquivos do Django Unfold..."
if [ -d "staticfiles/unfold" ]; then
    echo "✅ Arquivos do Django Unfold coletados com sucesso!"
    echo "📊 Arquivos encontrados:"
    find staticfiles/unfold -name "*.css" -o -name "*.js" | head -10
else
    echo "❌ Arquivos do Django Unfold não encontrados!"
    echo "🔧 Tentando novamente..."
    python manage.py collectstatic --noinput --clear
fi

# Configurar permissões
echo "🔐 Configurando permissões..."
chmod -R 755 staticfiles/
chmod -R 755 media/

echo "✅ Instalação do Django Unfold concluída!"
echo "🌐 Acesse /admin/ para ver a interface futurista"
echo "📁 Arquivos estáticos em: $(pwd)/staticfiles/"
echo "🎨 Interface moderna com Tailwind CSS ativada!"
