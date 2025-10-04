# 🚀 Configuração de Email Local - TicketChecker

## ⚡ Início Rápido

### 1. **Configurar MailHog**
```bash
# Execute um dos scripts:
setup_mailhog.bat        # Windows Batch
setup_mailhog.ps1         # Windows PowerShell
```

### 2. **Iniciar Servidor Django**
```bash
run_local_server.bat      # Script automático
# OU
python manage.py runserver --settings=backend.settings_local
```

### 3. **Testar Sistema**
```bash
python test_email_local.py      # Testes básicos
python test_complete_flow.py    # Fluxo completo
```

## 📧 Acesso aos Emails

- **Interface MailHog:** http://localhost:8025
- **Servidor Django:** http://localhost:8000
- **Recuperação de Senha:** http://localhost:8000/accounts/password_reset/

## 🧪 Testes Disponíveis

### `test_email_local.py`
- ✅ Verifica conexão com MailHog
- ✅ Testa email básico
- ✅ Testa email HTML
- ✅ Testa template de recuperação
- ✅ Testa múltiplos destinatários
- ✅ Testa email com anexo

### `test_complete_flow.py`
- ✅ Cria usuário de teste
- ✅ Solicita recuperação de senha
- ✅ Envia email de recuperação
- ✅ Confirma token
- ✅ Altera senha
- ✅ Testa login com nova senha

## 📁 Arquivos Criados

### Scripts de Configuração
- `setup_mailhog.bat` - Configuração automática MailHog
- `setup_mailhog.ps1` - Versão PowerShell
- `run_local_server.bat` - Inicia Django local

### Configurações Django
- `backend/settings_local.py` - Configurações para desenvolvimento

### Scripts de Teste
- `test_email_local.py` - Testes básicos de email
- `test_complete_flow.py` - Fluxo completo de recuperação

### Documentação
- `docs/CONFIGURACAO_EMAIL_LOCAL.md` - Guia completo
- `README_EMAIL_LOCAL.md` - Este arquivo

## 🔧 Configurações

### MailHog
- **SMTP:** localhost:1025
- **Interface Web:** http://localhost:8025
- **Sem TLS/SSL:** Configurado para desenvolvimento

### Django Local
- **Settings:** `backend.settings_local`
- **Email Backend:** SMTP local
- **Logging:** Ativado para debug
- **From Email:** noreply@ticketchecker.local

## 🎯 Funcionalidades Testadas

### ✅ Recuperação de Senha
- Formulário de solicitação
- Envio de email HTML
- Confirmação de token
- Alteração de senha
- Login com nova senha

### ✅ Templates de Email
- Design profissional
- Responsivo para mobile
- Informações de segurança
- Instruções claras
- Contato para suporte

### ✅ Tipos de Email
- Texto simples
- HTML formatado
- Múltiplos destinatários
- Anexos
- Headers personalizados

## 🚨 Solução de Problemas

### MailHog não inicia
```bash
# Verificar portas ocupadas
netstat -an | findstr :1025
netstat -an | findstr :8025

# Matar processo se necessário
taskkill /F /PID <PID>
```

### Django não conecta
1. Verificar se MailHog está rodando
2. Confirmar `settings_local.py`
3. Verificar logs de erro

### Emails não aparecem
1. Limpar cache do navegador
2. Verificar interface MailHog
3. Verificar logs Django

## 📊 Vantagens do Ambiente Local

### ✅ Desenvolvimento
- **Sem configuração SMTP** real
- **Teste instantâneo** de emails
- **Interface visual** para debug
- **Sem spam** ou emails reais

### ✅ Testes
- **Múltiplos cenários** facilmente
- **Templates visuais** completos
- **Debug detalhado** de problemas
- **Isolamento** do ambiente

## 🔄 Fluxo de Trabalho

### 1. **Desenvolvimento Diário**
```bash
# Terminal 1: MailHog
.\mailhog\MailHog.exe

# Terminal 2: Django
python manage.py runserver --settings=backend.settings_local
```

### 2. **Teste de Funcionalidades**
```bash
# Teste rápido
python test_email_local.py

# Teste completo
python test_complete_flow.py
```

### 3. **Verificação Visual**
- Acesse http://localhost:8025
- Veja emails como usuário final
- Verifique HTML renderizado
- Teste em diferentes dispositivos

## 🎉 Resultado Esperado

Após seguir este guia, você terá:
- ✅ Servidor de email local funcionando
- ✅ Django configurado para desenvolvimento
- ✅ Sistema de recuperação de senha testado
- ✅ Templates profissionais de email
- ✅ Ambiente isolado para desenvolvimento

## 📞 Suporte

Para dúvidas ou problemas:
- **Documentação:** `docs/CONFIGURACAO_EMAIL_LOCAL.md`
- **Logs:** `email_debug.log`
- **Interface:** http://localhost:8025
- **Testes:** Execute os scripts de teste

---

**Status:** ✅ Pronto para desenvolvimento local  
**Ambiente:** Windows + MailHog + Django  
**Última atualização:** Configuração completa implementada