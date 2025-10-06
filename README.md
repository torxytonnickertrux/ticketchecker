# 🎫 Sistema de Ingressos - Eventos

Sistema completo de gerenciamento de eventos e venda de ingressos com integração ao Mercado Pago.

## 🚀 Funcionalidades

### 📅 **Gestão de Eventos**
- Criação e edição de eventos
- Gerenciamento de tipos de ingressos
- Controle de estoque
- Dashboard administrativo

### 💳 **Sistema de Pagamentos**
- **PIX** - Pagamento instantâneo
- **Cartão de Crédito** - Visa, Mastercard, Elo
- **Cartão de Débito** - Visa, Mastercard, Elo
- Integração completa com Mercado Pago

### 🎟️ **Validação de Ingressos**
- QR Code único por ingresso
- Validação em tempo real
- Histórico de compras
- Sistema de cupons

### 📧 **Comunicação**
- Emails de confirmação
- Notificações de pagamento
- Recuperação de senha
- Webhooks do Mercado Pago

## 🛠️ **Tecnologias**

- **Backend:** Django 5.2
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Pagamentos:** Mercado Pago API
- **Email:** SMTP / MailHog (desenvolvimento)
- **Admin:** Django Unfold

## 📁 **Estrutura do Projeto**

```
sistema_ingresso/
├── backend/                 # Configurações Django
├── events/                  # App principal de eventos
├── communication/           # App de comunicação
├── templates/               # Templates HTML
├── static/                  # Arquivos estáticos
├── media/                   # Uploads de usuários
├── scripts/                 # Scripts utilitários
│   ├── windows/            # Scripts para Windows
│   └── *.py                # Scripts Python
├── tools/                   # Ferramentas externas
│   └── mailhog/            # MailHog para email local
├── docs/                    # Documentação
│   ├── setup/              # Configuração inicial
│   ├── payments/           # Documentação de pagamentos
│   ├── deployment/         # Deploy e produção
│   └── troubleshooting/    # Solução de problemas
└── requirements.txt         # Dependências Python
```

## 🚀 **Instalação Rápida**

### **1. Clone o repositório**
```bash
git clone <repository-url>
cd sistema_ingresso
```

### **2. Crie um ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### **3. Instale as dependências**
```bash
pip install -r requirements.txt
```

### **4. Configure as variáveis de ambiente**
```bash
cp env_example.txt .env
# Edite o arquivo .env com suas configurações
```

### **5. Execute as migrações**
```bash
python manage.py migrate
```

### **6. Crie um superusuário**
```bash
python manage.py createsuperuser
```

### **7. Execute o servidor**
```bash
python manage.py runserver
```

## ⚙️ **Configuração**

### **Mercado Pago**
1. Acesse [Mercado Pago Developers](https://developers.mercadopago.com)
2. Crie uma aplicação
3. Configure as credenciais no `.env`:
```env
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-...
MERCADO_PAGO_PUBLIC_KEY=APP_USR-...
MERCADO_PAGO_SANDBOX=True
```

### **Email (Desenvolvimento)**
Para testar emails localmente:
```bash
# Windows
scripts/windows/setup_mailhog.bat

# Linux/Mac
./tools/mailhog/mailhog
```

## 📚 **Documentação**

- **[Configuração Inicial](docs/setup/)** - Guias de configuração
- **[Sistema de Pagamentos](docs/payments/)** - Documentação completa de pagamentos
- **[Deploy](docs/deployment/)** - Guias de deploy
- **[Solução de Problemas](docs/troubleshooting/)** - Troubleshooting

## 🧪 **Testes**

```bash
# Executar todos os testes
python scripts/run_all_tests.py

# Validar sistema
python scripts/validate_system.py
```

## 📱 **Scripts Úteis**

### **Windows**
```bash
# Executar servidor local
scripts/windows/run_local_server.bat

# Configurar MailHog
scripts/windows/setup_mailhog.bat
```

### **Linux/Mac**
```bash
# Monitorar sistema
python scripts/monitor_system.py

# Configurar produção
python scripts/setup_production.py
```

## 🔧 **Desenvolvimento**

### **Estrutura de Apps**
- **`events/`** - Eventos, ingressos, pagamentos
- **`communication/`** - Emails, notificações, webhooks

### **Modelos Principais**
- **`Event`** - Eventos
- **`Ticket`** - Tipos de ingressos
- **`Purchase`** - Compras
- **`Payment`** - Pagamentos
- **`QRCode`** - Códigos QR

## 🚀 **Deploy**

### **PythonAnywhere**
```bash
# Script de deploy automático
bash scripts/setup_pythonanywhere.sh
```

### **Outros Provedores**
Consulte a documentação em `docs/deployment/`

## 📞 **Suporte**

Para problemas e dúvidas:
1. Consulte `docs/troubleshooting/`
2. Verifique os logs em `logs/`
3. Execute `python scripts/validate_system.py`

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ para facilitar a gestão de eventos e vendas de ingressos.**