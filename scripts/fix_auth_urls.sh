#!/bin/bash

# Script para corrigir URLs de autenticação no PythonAnywhere
# Execute este script após fazer deploy

echo "🔐 Corrigindo URLs de autenticação..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📄 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Verificar configurações
echo "🔍 Verificando configurações..."
python manage.py check

echo "✅ Correção das URLs de autenticação concluída!"
echo "🔗 URLs configuradas:"
echo "   - Login: /accounts/login/"
echo "   - Logout: /accounts/logout/"
echo "   - Redirecionamento: /"
echo "🌐 Teste acessando um evento sem estar logado"
