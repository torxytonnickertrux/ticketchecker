#!/bin/bash

# Script para instalar Django Jazzmin no PythonAnywhere
# Execute este script após fazer deploy

echo "🎨 Instalando Django Jazzmin para interface moderna..."

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

# Coletar arquivos estáticos (incluindo Django Jazzmin)
echo "📄 Coletando arquivos estáticos do Django Jazzmin..."
python manage.py collectstatic --noinput

# Verificar se os arquivos do Django Jazzmin foram coletados
echo "🔍 Verificando arquivos do Django Jazzmin..."
if [ -d "staticfiles/jazzmin" ]; then
    echo "✅ Arquivos do Django Jazzmin coletados com sucesso!"
    echo "📊 Arquivos encontrados:"
    find staticfiles/jazzmin -name "*.css" -o -name "*.js" | head -10
else
    echo "❌ Arquivos do Django Jazzmin não encontrados!"
    echo "🔧 Tentando novamente..."
    python manage.py collectstatic --noinput --clear
fi

# Configurar permissões
echo "🔐 Configurando permissões..."
chmod -R 755 staticfiles/
chmod -R 755 media/

echo "✅ Instalação do Django Jazzmin concluída!"
echo "🌐 Acesse /admin/ para ver a interface moderna"
echo "📁 Arquivos estáticos em: $(pwd)/staticfiles/"
echo "🎨 Interface moderna com Bootstrap ativada!"
echo "💡 Django Jazzmin é mais leve e compatível com PythonAnywhere!"
