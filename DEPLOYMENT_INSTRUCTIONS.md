# Instruções de Deployment no PythonAnywhere

## Problemas Identificados e Corrigidos

### ✅ Problemas Corrigidos

1. **Configuração do WSGI**: Corrigido para usar `backend.settings_pythonanywhere`
2. **Requirements.txt**: Removidas dependências duplicadas
3. **Configurações do Mercado Pago**: Adicionadas ao arquivo de configuração do PythonAnywhere
4. **Configurações do Google OAuth**: Adicionadas ao arquivo de configuração do PythonAnywhere
5. **Configurações de Email**: Corrigidas para usar variáveis de ambiente

## Passos para Deploy no PythonAnywhere

### 1. Upload dos Arquivos
Faça upload de todos os arquivos do projeto para o PythonAnywhere, incluindo:
- Todos os arquivos Python
- Arquivo `requirements.txt` corrigido
- Arquivo `.env` com as variáveis de ambiente
- Banco de dados `db.sqlite3`

### 2. Instalar Dependências
No console do PythonAnywhere, execute:
```bash
pip3.10 install --user -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

**IMPORTANTE**: As credenciais sensíveis foram removidas dos arquivos por segurança. Você precisa configurar suas próprias credenciais.

#### Opção 1: Usar arquivo .env (Recomendado)
1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com suas credenciais reais:
```bash
nano .env
```

#### Opção 2: Configurar variáveis de ambiente diretamente
No console do PythonAnywhere, configure as variáveis de ambiente:
```bash
export MERCADO_PAGO_ACCESS_TOKEN="sua_credencial_do_mercado_pago"
export MERCADO_PAGO_PUBLIC_KEY="sua_chave_publica_do_mercado_pago"
export MERCADO_PAGO_SANDBOX="True"
export SITE_URL="https://ingressoptga.pythonanywhere.com"
export GOOGLE_OAUTH2_CLIENT_ID="REPLACE_WITH_YOUR_GOOGLE_CLIENT_ID"
export GOOGLE_OAUTH2_SECRET="REPLACE_WITH_YOUR_GOOGLE_CLIENT_SECRET"
export EMAIL_HOST_USER="seu_email@gmail.com"
export EMAIL_HOST_PASSWORD="sua_senha_de_app"
export WEBHOOK_SECRET_KEY="sua_chave_secreta_do_webhook"
```

#### Como obter as credenciais:

**Google OAuth2:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione um existente
3. Ative a API do Google+ e OAuth2
4. Crie credenciais OAuth2
5. Configure as URLs de redirecionamento

**Mercado Pago:**
1. Acesse [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Crie uma aplicação
3. Obtenha o Access Token e Public Key
4. Configure as URLs de callback

**Email (Gmail):**
1. Ative a verificação em 2 etapas
2. Gere uma senha de app específica
3. Use essa senha no EMAIL_HOST_PASSWORD

### 4. Aplicar Migrações
```bash
python3.10 manage.py migrate --settings=backend.settings_pythonanywhere
```

### 5. Coletar Arquivos Estáticos
```bash
python3.10 manage.py collectstatic --noinput --settings=backend.settings_pythonanywhere
```

### 6. Criar Superusuário (se necessário)
```bash
python3.10 manage.py createsuperuser --settings=backend.settings_pythonanywhere
```

### 7. Configurar WSGI
No arquivo WSGI do PythonAnywhere, use:
```python
import os
import sys

# Adicionar o diretório do projeto ao path
path = '/home/ingressoptga/ticketchecker'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_pythonanywhere')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 8. Configurar Web Server
No painel do PythonAnywhere:
1. Vá para a aba "Web"
2. Configure o domínio para `ingressoptga.pythonanywhere.com`
3. Use o arquivo WSGI configurado acima
4. Configure os arquivos estáticos para `/home/ingressoptga/ticketchecker/staticfiles/`

## Verificações Pós-Deploy

### 1. Testar Aplicação
Acesse `https://ingressoptga.pythonanywhere.com` e verifique se:
- A página inicial carrega
- Os arquivos estáticos (CSS/JS) carregam
- O admin funciona em `/admin/`
- O login com Google funciona

### 2. Verificar Logs
Monitore os logs de erro em:
- Error log: `/var/log/ingressoptga.pythonanywhere.com.error.log`
- Access log: `/var/log/ingressoptga.pythonanywhere.com.access.log`
- Server log: `/var/log/ingressoptga.pythonanywhere.com.server.log`

### 3. Testar Funcionalidades
- Criação de eventos
- Compra de ingressos
- Pagamentos via Mercado Pago
- Validação de QR codes
- Envio de emails

## Problemas Comuns e Soluções

### Erro 500 - Internal Server Error
1. Verifique os logs de erro
2. Confirme se todas as dependências estão instaladas
3. Verifique se as variáveis de ambiente estão configuradas
4. Confirme se o banco de dados está acessível

### Arquivos Estáticos Não Carregam
1. Execute `collectstatic` novamente
2. Verifique as configurações de STATIC_ROOT e STATIC_URL
3. Confirme se o diretório staticfiles tem as permissões corretas

### Erro de Banco de Dados
1. Verifique se o arquivo db.sqlite3 existe e tem permissões de leitura/escrita
2. Execute as migrações: `python3.10 manage.py migrate`
3. Verifique se o usuário tem permissões no diretório do banco

### Erro de Mercado Pago
1. Verifique se as credenciais estão corretas
2. Confirme se está usando o ambiente de sandbox em desenvolvimento
3. Verifique se as URLs de callback estão configuradas corretamente

## Monitoramento Contínuo

1. **Logs**: Monitore regularmente os logs de erro
2. **Performance**: Verifique o tempo de resposta da aplicação
3. **Banco de Dados**: Monitore o tamanho e performance do banco
4. **Arquivos Estáticos**: Verifique se os arquivos estão sendo servidos corretamente

## Backup e Manutenção

### Backup Regular
1. Faça backup do banco de dados SQLite
2. Faça backup dos arquivos de mídia
3. Mantenha backup das configurações

### Atualizações
1. Teste atualizações em ambiente local primeiro
2. Faça backup antes de atualizar em produção
3. Monitore os logs após atualizações

## Contato e Suporte

Para problemas específicos:
1. Verifique os logs de erro
2. Consulte a documentação do Django
3. Verifique a documentação do PythonAnywhere
4. Consulte a documentação do Mercado Pago