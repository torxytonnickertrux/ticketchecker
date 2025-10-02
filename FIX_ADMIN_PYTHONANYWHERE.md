# 🔧 Corrigir Admin Django no PythonAnywhere

## 🚨 Problema
O admin Django no PythonAnywhere não carrega os estilos CSS/JS, ficando sem formatação.

## ✅ Solução

### 1. **Configurações Corretas**

O projeto já foi configurado com as correções necessárias:

- ✅ `STATICFILES_FINDERS` configurado
- ✅ `STATIC_ROOT` e `STATICFILES_DIRS` corretos
- ✅ URLs para servir arquivos estáticos
- ✅ Configurações específicas para PythonAnywhere

### 2. **Deploy no PythonAnywhere**

#### **Passo 1: Clone e Configure**
```bash
git clone https://github.com/torxytonnickertrux/ticketchecker.git
cd ticketchecker
pip install -r requirements.txt
```

#### **Passo 2: Execute o Script de Correção**
```bash
bash fix_admin_pythonanywhere.sh
```

#### **Passo 3: Configure WSGI**
No PythonAnywhere, configure o WSGI para usar:
```
backend.settings_admin_fix
```

### 3. **Verificações Importantes**

#### **Verificar se os arquivos foram coletados:**
```bash
ls staticfiles/admin/
# Deve mostrar: css/, img/, js/
```

#### **Verificar se o collectstatic funcionou:**
```bash
python manage.py collectstatic --noinput
# Deve coletar arquivos do admin
```

#### **Verificar permissões:**
```bash
chmod -R 755 staticfiles/
```

### 4. **Configurações do Web App**

No PythonAnywhere Web tab:

1. **Source code**: `/home/ingressoptga/ticketchecker`
2. **WSGI file**: `/home/ingressoptga/ticketchecker/ticketchecker_wsgi.py`
3. **Static files**: 
   - URL: `/static/`
   - Directory: `/home/ingressoptga/ticketchecker/staticfiles`

### 5. **Teste do Admin**

1. Acesse: `https://ingressoptga.pythonanywhere.com/admin/`
2. Verifique se o CSS está carregando
3. Teste o login do admin

### 6. **Troubleshooting**

#### **Se o admin ainda não carregar:**

1. **Verificar arquivos estáticos:**
```bash
find staticfiles/admin -name "*.css" | head -5
```

2. **Recolher arquivos estáticos:**
```bash
python manage.py collectstatic --noinput --clear
```

3. **Verificar configurações:**
```bash
python manage.py check --settings=backend.settings_admin_fix
```

4. **Verificar logs:**
```bash
tail -f /var/log/ingressoptga.pythonanywhere.com.error.log
```

### 7. **Configurações Finais**

#### **No PythonAnywhere Web tab:**

- **Static files URL**: `/static/`
- **Static files directory**: `/home/ingressoptga/ticketchecker/staticfiles`

#### **Verificar se está funcionando:**
- Admin deve ter estilo CSS
- Botões e formulários formatados
- Ícones e cores do Django admin

### 8. **Comandos Úteis**

```bash
# Recarregar web app
touch /var/www/ingressoptga_pythonanywhere_com_wsgi.py

# Ver logs de erro
tail -f /var/log/ingressoptga.pythonanywhere.com.error.log

# Verificar arquivos estáticos
ls -la staticfiles/admin/css/
```

## 🎯 **Resultado Esperado**

Após aplicar essas correções:

- ✅ Admin Django com estilo completo
- ✅ CSS e JS carregando corretamente
- ✅ Interface formatada como esperado
- ✅ Funcionalidades do admin funcionando

## 📞 **Se Ainda Não Funcionar**

1. Verifique se o `collectstatic` foi executado
2. Confirme se os arquivos estão em `staticfiles/admin/`
3. Verifique as configurações de Static files no Web tab
4. Teste acessando diretamente: `https://ingressoptga.pythonanywhere.com/static/admin/css/base.css`
