# 🔐 Configuração do Google OAuth - TicketChecker

## 📋 Visão Geral

Este documento explica como configurar o login com Google OAuth no sistema TicketChecker usando django-allauth.

## 🚀 Configuração do Google Cloud Console

### 1. Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google+ API** e **Google OAuth2 API**

### 2. Configurar OAuth Consent Screen

1. Vá para **APIs & Services** > **OAuth consent screen**
2. Escolha **External** (para usuários externos)
3. Preencha as informações obrigatórias:
   - **App name**: TicketChecker
   - **User support email**: seu-email@exemplo.com
   - **Developer contact information**: seu-email@exemplo.com

### 3. Criar Credenciais OAuth 2.0

1. Vá para **APIs & Services** > **Credentials**
2. Clique em **Create Credentials** > **OAuth 2.0 Client IDs**
3. Configure:
   - **Application type**: Web application
   - **Name**: TicketChecker Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:8000` (desenvolvimento)
     - `https://seudominio.com` (produção)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/accounts/google/login/callback/` (desenvolvimento)
     - `https://seudominio.com/accounts/google/login/callback/` (produção)

### 4. Obter Credenciais

Após criar, você receberá:
- **Client ID**: `123456789-abcdefg.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

## ⚙️ Configuração no Django

### 1. Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Google OAuth
GOOGLE_OAUTH2_CLIENT_ID=seu_client_id_aqui
GOOGLE_OAUTH2_SECRET=seu_client_secret_aqui
```

### 2. Configuração no Admin Django

1. Acesse o admin: `http://localhost:8000/admin/`
2. Vá para **Sites** e configure:
   - **Domain name**: `localhost:8000` (desenvolvimento)
   - **Display name**: `TicketChecker`

3. Vá para **Social Applications** e adicione:
   - **Provider**: Google
   - **Name**: Google
   - **Client id**: Seu Client ID do Google
   - **Secret key**: Seu Client Secret do Google
   - **Sites**: Selecione o site configurado

## 🔧 Configurações Avançadas

### URLs Disponíveis

Após a configuração, as seguintes URLs estarão disponíveis:

- `/accounts/google/login/` - Iniciar login com Google
- `/accounts/google/login/callback/` - Callback do Google
- `/accounts/login/` - Login tradicional + Google
- `/accounts/logout/` - Logout
- `/accounts/signup/` - Cadastro

### Personalização do Template

O template de login foi atualizado para incluir o botão do Google:

```html
<!-- Login com Google -->
<div class="d-grid gap-3 mb-4">
    <a href="{% url 'google_login' %}" class="btn btn-outline-danger btn-lg">
        <i class="fab fa-google me-2"></i>Entrar com Google
    </a>
</div>
```

## 🧪 Testando a Integração

### 1. Desenvolvimento Local

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Executar servidor
python manage.py runserver

# Acessar: http://localhost:8000/accounts/login/
```

### 2. Verificar Funcionamento

1. Acesse a página de login
2. Clique em "Entrar com Google"
3. Faça login com sua conta Google
4. Verifique se foi redirecionado corretamente

## 🚨 Solução de Problemas

### Erro: "Invalid redirect_uri"

- Verifique se a URI de redirecionamento está correta no Google Cloud Console
- Certifique-se de que não há barra final desnecessária

### Erro: "Client ID not found"

- Verifique se as credenciais estão corretas no arquivo `.env`
- Confirme se a aplicação social foi criada no admin Django

### Erro: "Site not found"

- Configure o site no admin Django
- Verifique se o `SITE_ID = 1` está correto no settings.py

## 🔒 Segurança

### Produção

1. **HTTPS obrigatório**: Configure SSL/TLS
2. **Domínios específicos**: Use apenas domínios autorizados
3. **Credenciais seguras**: Nunca commite credenciais no código
4. **Rate limiting**: Configure limites de requisições

### Desenvolvimento

1. Use credenciais de teste
2. Configure domínios locais apropriados
3. Mantenha logs de debug ativados

## 📚 Recursos Adicionais

- [Documentação django-allauth](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)

## ✅ Checklist de Implementação

- [x] Instalar django-allauth
- [x] Configurar settings.py
- [x] Atualizar URLs
- [x] Modificar templates
- [x] Executar migrações
- [ ] Configurar Google Cloud Console
- [ ] Adicionar credenciais ao .env
- [ ] Configurar aplicação social no admin
- [ ] Testar integração completa