# 🚀 Deploy no PythonAnywhere - TicketChecker

## 📋 Pré-requisitos

1. Conta no PythonAnywhere
2. Repositório Git configurado
3. Virtual environment ativado

## 🔧 Passos para Deploy

### 1. Clone o Repositório
```bash
git clone https://github.com/torxytonnickertrux/ticketchecker.git
cd ticketchecker
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 5. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic
```

### 6. Configurar Web App

1. Acesse o **Web** tab no PythonAnywhere
2. Clique em **Add a new web app**
3. Escolha **Django**
4. Selecione a versão do Python (3.13)
5. Configure o caminho do código: `/home/ingressoptga/ticketchecker`
6. Configure o caminho do WSGI: `/home/ingressoptga/ticketchecker/ticketchecker_wsgi.py`

### 7. Configurar WSGI

O arquivo `ticketchecker_wsgi.py` já está configurado e usa `backend.settings_pythonanywhere` que detecta automaticamente se está no PythonAnywhere.

### 8. Configurar Domínio

No arquivo WSGI, ajuste:
- `ingressoptga.pythonanywhere.com` para seu domínio
- Caminhos dos arquivos conforme sua estrutura

### 9. Configurar Email (Opcional)

Para envio de emails, configure no `settings_production.py`:
- `EMAIL_HOST_USER`: Seu email Gmail
- `EMAIL_HOST_PASSWORD`: Senha de app do Gmail

### 10. Testar

1. Acesse seu domínio no PythonAnywhere
2. Verifique se o site carrega corretamente
3. Teste as funcionalidades principais

## 🔧 Comandos Úteis

### Recarregar Web App
```bash
touch /var/www/ingressoptga_pythonanywhere_com_wsgi.py
```

### Ver Logs
```bash
tail -f /var/log/ingressoptga.pythonanywhere.com.error.log
```

### Atualizar Código
```bash
git pull origin main
python manage.py collectstatic --noinput
```

## ⚠️ Problemas Comuns

### 1. Erro de Módulos (qrcode, Pillow)
```bash
pip install -r requirements.txt
```

### 2. Erro de Arquivos Estáticos
```bash
# Criar diretório static se não existir
mkdir -p /home/ingressoptga/ticketchecker/static
python manage.py collectstatic --noinput
```

### 3. Erro de STATIC_ROOT
```bash
# Usar as configurações corretas
python manage.py collectstatic --noinput --settings=backend.settings_pythonanywhere
```

### 4. Erro de Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Erro de Permissões
```bash
chmod 755 /home/ingressoptga/ticketchecker
```

### 6. Erro de Logging
O arquivo `settings_pythonanywhere.py` detecta automaticamente se está no PythonAnywhere e configura o logging apenas se necessário.

## 📁 Estrutura de Arquivos

```
ticketchecker/
├── backend/
│   ├── settings.py
│   ├── settings_production.py
│   └── ...
├── events/
├── template/
├── static/
├── staticfiles/
├── media/
├── requirements.txt
└── ticketchecker_wsgi.py
```

## 🎯 Configurações Importantes

- **STATIC_ROOT**: `/home/ingressoptga/ticketchecker/staticfiles`
- **MEDIA_ROOT**: `/home/ingressoptga/ticketchecker/media`
- **DEBUG**: `False` em produção
- **ALLOWED_HOSTS**: Seu domínio PythonAnywhere

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs de erro
2. Confirme se todas as dependências estão instaladas
3. Verifique as configurações de STATIC_ROOT e MEDIA_ROOT
4. Teste localmente antes de fazer deploy
