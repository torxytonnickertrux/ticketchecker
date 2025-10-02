#!/bin/bash

# Script para corrigir arquivos estáticos do Django Jazzmin no PythonAnywhere
# Execute este script após fazer deploy

echo "🎨 Corrigindo arquivos estáticos do Django Jazzmin..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Limpar arquivos estáticos antigos
echo "🧹 Limpando arquivos estáticos antigos..."
rm -rf staticfiles/*

# Coletar arquivos estáticos (incluindo Django Jazzmin)
echo "📄 Coletando arquivos estáticos do Django Jazzmin..."
python manage.py collectstatic --noinput --clear

# Verificar se os arquivos do Django Jazzmin foram coletados
echo "🔍 Verificando arquivos do Django Jazzmin..."
if [ -d "staticfiles/jazzmin" ]; then
    echo "✅ Arquivos do Django Jazzmin coletados com sucesso!"
    echo "📊 Arquivos encontrados:"
    find staticfiles/jazzmin -name "*.css" -o -name "*.js" | head -10
    echo ""
    echo "📁 Estrutura de arquivos:"
    ls -la staticfiles/jazzmin/
else
    echo "❌ Arquivos do Django Jazzmin não encontrados!"
    echo "🔧 Tentando novamente..."
    python manage.py collectstatic --noinput --clear
fi

# Verificar arquivos do admin Django
echo "🔍 Verificando arquivos do admin Django..."
if [ -d "staticfiles/admin" ]; then
    echo "✅ Arquivos do admin Django encontrados!"
    echo "📊 Arquivos CSS:"
    find staticfiles/admin -name "*.css" | head -5
    echo "📊 Arquivos JS:"
    find staticfiles/admin -name "*.js" | head -5
else
    echo "❌ Arquivos do admin Django não encontrados!"
fi

# Configurar permissões
echo "🔐 Configurando permissões..."
chmod -R 755 staticfiles/
chmod -R 755 media/

# Verificar tamanho dos arquivos
echo "📊 Tamanho dos arquivos estáticos:"
du -sh staticfiles/

echo "✅ Correção dos arquivos estáticos concluída!"
echo "🌐 Acesse /admin/ para ver a interface estilizada"
echo "📁 Arquivos estáticos em: $(pwd)/staticfiles/"
echo "🎨 Interface Django Jazzmin ativada!"
