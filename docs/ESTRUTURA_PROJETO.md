# 📁 Estrutura do Projeto - Sistema de Ingressos

## 🎯 **Organização Final**

### **📂 Estrutura Principal**
```
sistema_ingresso/
├── 📁 backend/                 # Configurações Django
│   ├── settings.py            # Configurações principais
│   ├── settings_local.py      # Configurações locais
│   ├── settings_test.py       # Configurações de teste
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # WSGI para produção
│
├── 📁 events/                  # App principal de eventos
│   ├── models.py              # Modelos de dados
│   ├── views.py               # Views principais
│   ├── payment_views.py       # Views de pagamento
│   ├── mercadopago_service.py # Serviço Mercado Pago
│   ├── forms.py               # Formulários
│   ├── urls.py                # URLs do app
│   └── migrations/            # Migrações do banco
│
├── 📁 communication/           # App de comunicação
│   ├── models.py              # Modelos de comunicação
│   ├── views.py               # Views de comunicação
│   ├── services.py            # Serviços de email
│   └── test_service.py        # Testes de comunicação
│
├── 📁 templates/               # Templates HTML
│   ├── base.html              # Template base
│   ├── events/                # Templates de eventos
│   ├── admin/                 # Templates do admin
│   ├── registration/          # Templates de autenticação
│   └── jazzmin/               # Templates do Jazzmin
│
├── 📁 static/                  # Arquivos estáticos
│   └── js/                    # JavaScript
│
├── 📁 media/                   # Uploads de usuários
│   └── qr_codes/              # QR Codes gerados
│
├── 📁 scripts/                 # Scripts utilitários
│   ├── windows/               # Scripts para Windows
│   │   ├── run_local_server.bat
│   │   ├── setup_mailhog.bat
│   │   └── setup_mailhog.ps1
│   ├── monitor_system.py      # Monitor do sistema
│   ├── run_all_tests.py       # Executar testes
│   ├── setup_production.py    # Setup de produção
│   ├── validate_system.py     # Validar sistema
│   └── *.sh                   # Scripts shell
│
├── 📁 tools/                   # Ferramentas externas
│   └── mailhog/               # MailHog para email local
│
├── 📁 docs/                    # Documentação
│   ├── setup/                 # Configuração inicial
│   │   ├── CONFIGURACAO_EMAIL_LOCAL.md
│   │   ├── CONFIGURACAO_PAGAMENTOS.md
│   │   └── CONFIGURACAO_PROJETO.md
│   ├── payments/              # Documentação de pagamentos
│   │   ├── SISTEMA_PAGAMENTOS_COMPLETO.md
│   │   ├── SOLUCAO_PIX_DEFINITIVA_2024.md
│   │   └── WEBHOOK_MERCADO_PAGO.md
│   ├── deployment/            # Deploy e produção
│   │   └── DEPLOY_PYTHONANYWHERE.md
│   └── troubleshooting/       # Solução de problemas
│       ├── ERRO_SALDO_INSUFICIENTE.md
│       └── SOLUCAO_*.md
│
├── 📄 requirements.txt         # Dependências Python
├── 📄 README.md               # Documentação principal
├── 📄 .gitignore              # Arquivos ignorados pelo Git
└── 📄 manage.py               # Script de gerenciamento Django
```

## 🧹 **Limpeza Realizada**

### **❌ Arquivos Removidos**
- `test_complete_flow.py` - Teste obsoleto
- `test_comprehensive_payment.py` - Teste obsoleto
- `test_credit_cards.py` - Teste obsoleto
- `test_email_local.py` - Teste obsoleto
- `test_email.py` - Teste obsoleto
- `test_webhook.py` - Teste obsoleto
- `fix_all_pythonanywhere_issues.py` - Script obsoleto
- `fix_database_migration.py` - Script obsoleto
- `fix_logging_pythonanywhere.py` - Script obsoleto
- `fix_wsgi_pythonanywhere.py` - Script obsoleto
- `check_database_schema.py` - Script obsoleto
- `ticketchecker_wsgi.py` - Arquivo duplicado
- `email_debug.log` - Log temporário

### **📁 Reorganizações**
- **Templates:** `template/` → `templates/`
- **Scripts:** Movidos para `scripts/`
- **Documentação:** Organizada em subpastas
- **Ferramentas:** Movidas para `tools/`

## 🎯 **Benefícios da Organização**

### **✅ Estrutura Clara**
- Separação lógica de responsabilidades
- Fácil navegação e manutenção
- Padrões Django respeitados

### **✅ Documentação Organizada**
- Guias por categoria
- Fácil localização de informações
- Troubleshooting separado

### **✅ Scripts Centralizados**
- Todos os utilitários em `scripts/`
- Separação por plataforma (Windows/Linux)
- Fácil execução e manutenção

### **✅ Limpeza Completa**
- Arquivos obsoletos removidos
- Logs temporários ignorados
- Estrutura otimizada

## 🚀 **Próximos Passos**

1. **Testar** a estrutura reorganizada
2. **Atualizar** documentação conforme necessário
3. **Manter** a organização em futuras modificações
4. **Documentar** novas funcionalidades adequadamente

---

**Projeto organizado e pronto para desenvolvimento! 🎉**