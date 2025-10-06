# Configuração de Email para Recuperação de Senha

## 📧 Resumo da Configuração

O sistema de recuperação de senha foi configurado para usar o email **vgf.tools1@gmail.com** para enviar instruções de recuperação de acesso aos usuários.

## 🔧 Configurações Implementadas

### 1. **Configurações do Django (backend/settings.py)**

```python
# Configurações de Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'vgf.tools1@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Senha de app do Gmail
DEFAULT_FROM_EMAIL = 'vgf.tools1@gmail.com'
SERVER_EMAIL = 'vgf.tools1@gmail.com'
```

### 2. **Variáveis de Ambiente (env_example.txt)**

```bash
# Configurações de email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=vgf.tools1@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app_gmail
DEFAULT_FROM_EMAIL=vgf.tools1@gmail.com
```

## 📋 Templates de Email Criados

### 1. **Email de Recuperação (password_reset_email.html)**
- ✅ Design profissional com branding TicketChecker
- ✅ Instruções claras para o usuário
- ✅ Botão de ação destacado
- ✅ Informações de segurança
- ✅ Link alternativo caso o botão não funcione
- ✅ Informações de contato

### 2. **Assunto do Email (password_reset_subject.txt)**
- ✅ Assunto claro: "Recuperação de Senha - TicketChecker"

### 3. **Páginas de Interface**
- ✅ `password_reset_form.html` - Formulário para solicitar recuperação
- ✅ `password_reset_done.html` - Confirmação de envio do email
- ✅ `password_reset_confirm.html` - Formulário para nova senha
- ✅ `password_reset_complete.html` - Confirmação de alteração

## 🔐 Configuração da Senha de App do Gmail

### Passo 1: Ativar Verificação em Duas Etapas
1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá em **Segurança** → **Verificação em duas etapas**
3. Ative a verificação em duas etapas se ainda não estiver ativa

### Passo 2: Gerar Senha de App
1. Ainda em **Segurança**, procure por **Senhas de app**
2. Clique em **Senhas de app**
3. Selecione **Email** como aplicativo
4. Selecione **Outro (nome personalizado)** como dispositivo
5. Digite: "TicketChecker Sistema"
6. Clique em **Gerar**
7. **COPIE A SENHA GERADA** (ela só aparece uma vez!)

### Passo 3: Configurar no Sistema
1. Crie um arquivo `.env` na raiz do projeto (copie do `env_example.txt`)
2. Substitua `sua_senha_de_app_gmail` pela senha gerada no passo 2
3. Salve o arquivo `.env`

**Exemplo do arquivo .env:**
```bash
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

## 🧪 Testando a Funcionalidade

### 1. **Teste Manual**
1. Acesse `/accounts/password_reset/`
2. Digite um email válido cadastrado no sistema
3. Clique em "Enviar Instruções"
4. Verifique se o email chegou na caixa de entrada
5. Siga o link no email para redefinir a senha

### 2. **Teste de Desenvolvimento**
Para testar sem enviar emails reais, altere temporariamente no `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Isso fará os emails aparecerem no console do Django.

## 📱 URLs Disponíveis

- `/accounts/password_reset/` - Solicitar recuperação
- `/accounts/password_reset/done/` - Confirmação de envio
- `/accounts/password_reset_confirm/<uidb64>/<token>/` - Redefinir senha
- `/accounts/password_reset_complete/` - Confirmação de alteração

## 🎨 Características do Email

### Design Profissional
- ✅ Logo e branding TicketChecker
- ✅ Cores consistentes com o sistema
- ✅ Layout responsivo para mobile
- ✅ Botões de ação destacados

### Conteúdo Informativo
- ✅ Instruções claras passo a passo
- ✅ Informações de segurança
- ✅ Prazo de validade do link (24 horas)
- ✅ Contato para suporte

### Elementos de Segurança
- ✅ Avisos sobre não solicitação
- ✅ Informações sobre expiração do link
- ✅ Instruções para verificar spam

## 🔧 Solução de Problemas

### Email não chega
1. ✅ Verifique a pasta de spam
2. ✅ Confirme se a senha de app está correta
3. ✅ Verifique se a verificação em duas etapas está ativa
4. ✅ Teste com `console.EmailBackend` primeiro

### Erro de autenticação
1. ✅ Confirme se a senha de app foi copiada corretamente
2. ✅ Verifique se não há espaços extras na senha
3. ✅ Confirme se o email está correto

### Link não funciona
1. ✅ Verifique se o link não expirou (24 horas)
2. ✅ Confirme se o token não foi usado anteriormente
3. ✅ Teste em modo incógnito

## 📊 Monitoramento

### Logs de Email
Os emails enviados são logados pelo Django. Para monitorar:
```python
# Em settings.py, adicione:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'email.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚀 Próximos Passos

1. ✅ **Configurar senha de app** do Gmail
2. ✅ **Testar funcionalidade** completa
3. ✅ **Monitorar logs** de email
4. ✅ **Treinar usuários** sobre o processo
5. ✅ **Documentar procedimentos** de suporte

## 📞 Suporte

Para dúvidas sobre a configuração de email:
- **Email:** vgf.tools1@gmail.com
- **Documentação:** Este arquivo
- **Logs:** Verificar arquivo de log do Django

---

**Data da Configuração:** {{ data_atual }}  
**Email Configurado:** vgf.tools1@gmail.com  
**Status:** Pronto para uso após configuração da senha de app