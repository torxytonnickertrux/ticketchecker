# Configuração de Email Local com MailHog

## 📧 Resumo

Este guia configura um ambiente de desenvolvimento local para testar emails usando o **MailHog**, um servidor SMTP local que captura todos os emails enviados durante o desenvolvimento.

## 🚀 Configuração Rápida

### 1. **Instalar MailHog**

**Opção A: Script Automático (Recomendado)**
```bash
# Execute um dos scripts:
setup_mailhog.bat        # Windows Batch
setup_mailhog.ps1         # Windows PowerShell
```

**Opção B: Download Manual**
1. Acesse: https://github.com/mailhog/MailHog/releases
2. Baixe `MailHog_windows_amd64.exe`
3. Coloque na pasta `mailhog/`
4. Execute: `.\mailhog\MailHog.exe`

**Opção C: Docker**
```bash
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

### 2. **Iniciar MailHog**
```bash
.\mailhog\MailHog.exe
```

### 3. **Verificar Funcionamento**
- **Interface Web:** http://localhost:8025
- **Servidor SMTP:** localhost:1025

## 🔧 Configurações do Django

### Arquivo: `backend/settings_local.py`
```python
# Configurações de Email para desenvolvimento local (MailHog)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@ticketchecker.local'
SERVER_EMAIL = 'noreply@ticketchecker.local'
```

### Iniciar Servidor Django Local
```bash
# Opção 1: Script automático
run_local_server.bat

# Opção 2: Comando manual
python manage.py runserver --settings=backend.settings_local
```

## 🧪 Testando o Sistema

### 1. **Teste Automático**
```bash
python test_email_local.py
```

### 2. **Teste Manual**
1. Acesse: http://localhost:8000/accounts/password_reset/
2. Digite um email qualquer (ex: test@example.com)
3. Clique em "Enviar Instruções"
4. Verifique o email em: http://localhost:8025

## 📋 Scripts Disponíveis

### `setup_mailhog.bat`
- Baixa e configura o MailHog automaticamente
- Inicia o servidor MailHog

### `setup_mailhog.ps1`
- Versão PowerShell do script de configuração
- Mais robusta para ambientes corporativos

### `test_email_local.py`
- Testa todos os tipos de email
- Verifica conexão com MailHog
- Mostra configurações atuais

### `run_local_server.bat`
- Inicia servidor Django com configurações locais
- Verifica se MailHog está rodando
- Ativa ambiente virtual automaticamente

## 🎯 Funcionalidades Testadas

### ✅ Tipos de Email
- **Email básico** - Texto simples
- **Email HTML** - Com formatação e estilos
- **Email de recuperação** - Template profissional
- **Múltiplos destinatários** - Lista de emails
- **Email com anexo** - Arquivos anexados

### ✅ Templates Testados
- `password_reset_email.html` - Recuperação de senha
- `password_reset_subject.txt` - Assunto do email
- Templates de interface atualizados

## 🔍 Verificação de Funcionamento

### 1. **Interface MailHog**
- Acesse: http://localhost:8025
- Veja todos os emails enviados
- Visualize HTML, texto e anexos
- Delete emails antigos

### 2. **Logs do Django**
- Arquivo: `email_debug.log`
- Console do servidor Django
- Informações detalhadas de debug

### 3. **Teste de Conectividade**
```python
# Verificar se MailHog está rodando
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 1025))
if result == 0:
    print("✅ MailHog está rodando!")
else:
    print("❌ MailHog não está rodando!")
```

## 🚨 Solução de Problemas

### MailHog não inicia
```bash
# Verificar se a porta está ocupada
netstat -an | findstr :1025
netstat -an | findstr :8025

# Matar processo na porta se necessário
taskkill /F /PID <PID>
```

### Django não conecta
1. Verificar se MailHog está rodando
2. Confirmar configurações em `settings_local.py`
3. Verificar logs de erro

### Emails não aparecem
1. Verificar interface MailHog: http://localhost:8025
2. Limpar cache do navegador
3. Verificar logs do Django

## 📊 Vantagens do MailHog

### ✅ Para Desenvolvimento
- **Sem configuração SMTP** - Não precisa de credenciais reais
- **Interface visual** - Veja emails como o usuário final
- **Sem spam** - Emails não saem do ambiente local
- **Teste rápido** - Instantâneo, sem delays de rede

### ✅ Para Testes
- **Múltiplos destinatários** - Teste listas de email
- **Anexos** - Verifique arquivos anexados
- **HTML** - Visualize renderização de templates
- **Debug** - Veja headers e metadados

## 🔄 Fluxo de Trabalho

### 1. **Desenvolvimento**
```bash
# Terminal 1: Iniciar MailHog
.\mailhog\MailHog.exe

# Terminal 2: Iniciar Django
python manage.py runserver --settings=backend.settings_local
```

### 2. **Teste**
```bash
# Testar emails
python test_email_local.py

# Testar recuperação de senha
# Acesse: http://localhost:8000/accounts/password_reset/
```

### 3. **Verificação**
- Interface MailHog: http://localhost:8025
- Logs Django: `email_debug.log`

## 📝 Próximos Passos

1. ✅ **Configurar MailHog** - Execute os scripts
2. ✅ **Testar emails** - Use `test_email_local.py`
3. ✅ **Testar recuperação** - Fluxo completo
4. ✅ **Verificar templates** - Visualização HTML
5. ✅ **Documentar bugs** - Se encontrar problemas

## 🎉 Resultado Esperado

Após a configuração, você deve conseguir:
- ✅ Enviar emails de recuperação de senha
- ✅ Ver emails na interface MailHog
- ✅ Testar todos os templates
- ✅ Desenvolver sem configuração SMTP real
- ✅ Debuggar problemas de email facilmente

---

**Configuração:** Ambiente Local com MailHog  
**Interface:** http://localhost:8025  
**SMTP:** localhost:1025  
**Status:** Pronto para desenvolvimento