# 🧭 Navegação Inteligente

> **Sistema de navegação contextual entre admin e site principal**

## 📋 Visão Geral

O sistema de navegação inteligente permite transição fluida entre o painel administrativo e o site principal, com botões contextuais e navegação adaptativa.

## 🎯 Funcionalidades Principais

### **Botão Site Principal**
- Botão fixo no canto superior direito do admin
- Design moderno com gradiente azul
- Efeitos hover suaves
- Ícone Font Awesome

### **Navegação Rápida**
- Links para todas as seções principais
- Dashboard do usuário
- Sistema de validação
- Gerenciamento de cupons

## 🛠️ Implementação Técnica

### **JavaScript Customizado**
```javascript
// static/admin_custom_button.js
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o botão já existe
    if (document.querySelector('.jazzmin-site-button')) {
        return;
    }
    
    // Criar o botão fixo
    const button = document.createElement('a');
    button.href = '/';
    button.className = 'jazzmin-site-button';
    button.title = 'Ir para o Site Principal';
    button.innerHTML = '<i class="fas fa-home"></i> Site Principal';
    
    // Adicionar estilos
    const style = document.createElement('style');
    style.textContent = `
        .jazzmin-site-button {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: linear-gradient(135deg, #007cba, #005a87);
            color: white;
            padding: 12px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 2px solid transparent;
        }
        .jazzmin-site-button:hover {
            background: linear-gradient(135deg, #005a87, #003d5c);
            color: white;
            text-decoration: none;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            border-color: rgba(255,255,255,0.3);
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(button);
});
```

### **Configuração Jazzmin**
```python
# backend/settings.py
JAZZMIN_SETTINGS = {
    "custom_js": "admin_custom_button.js",
    # ... outras configurações
}
```

## 🎨 Design e Interface

### **Botão Principal**
- **Posição** - Canto superior direito (fixed)
- **Cores** - Gradiente azul (#007cba → #005a87)
- **Efeitos** - Hover com elevação
- **Ícone** - Font Awesome home
- **Responsivo** - Adapta-se a diferentes telas

### **Navegação Rápida**
- **Localização** - Barra de navegação do admin
- **Links** - Site, Eventos, Dashboard, Validação
- **Estilo** - Consistente com Jazzmin
- **Acessibilidade** - Títulos e ARIA labels

## 📱 Templates Personalizados

### **Admin Base Template**
```html
<!-- template/admin/base.html -->
{% extends "admin/base.html" %}
{% load static %}

{% block extrahead %}
{{ block.super }}
<style>
    .admin-site-nav {
        background: linear-gradient(135deg, #007cba, #005a87);
        color: white;
        padding: 15px 20px;
        margin-bottom: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .admin-site-nav .nav-links {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .admin-site-nav .nav-link {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .admin-site-nav .nav-link:hover {
        background: rgba(255,255,255,0.3);
        color: white;
        text-decoration: none;
        transform: translateY(-2px);
    }
</style>
{% endblock %}

{% block content %}
<div class="admin-site-nav">
    <h3><i class="fas fa-rocket"></i> Navegação Rápida para o Site</h3>
    <div class="nav-links">
        <a href="/" class="nav-link primary">Site Principal</a>
        <a href="/events/" class="nav-link">Eventos</a>
        <a href="/dashboard/" class="nav-link">Dashboard</a>
        <a href="/validate/" class="nav-link">Validar</a>
        <a href="/coupons/" class="nav-link">Cupons</a>
        <a href="/history/" class="nav-link">Histórico</a>
    </div>
</div>
{{ block.super }}
{% endblock %}
```

## 🔧 Configuração

### **Arquivos Necessários**
```
static/
└── admin_custom_button.js    # JavaScript principal

template/
├── admin/
│   ├── base.html            # Template base admin
│   ├── base_site.html       # Template site admin
│   └── index.html           # Página principal admin
└── jazzmin/
    ├── base.html            # Template base Jazzmin
    ├── base_site.html       # Template site Jazzmin
    ├── index.html           # Página principal Jazzmin
    └── includes/
        └── header.html      # Header customizado
```

### **Configuração Settings**
```python
# backend/settings.py
JAZZMIN_SETTINGS = {
    "site_title": "TicketChecker Admin",
    "site_header": "🎫 TicketChecker",
    "site_brand": "Sistema de Ingressos",
    "welcome_sign": "Bem-vindo ao TicketChecker",
    "custom_css": None,
    "custom_js": "admin_custom_button.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
}
```

## 🎯 Funcionalidades Contextuais

### **Navegação por Contexto**
- **Admin → Site** - Botão sempre visível
- **Site → Admin** - Link no menu do usuário
- **Contextual** - Botões adaptam-se à página atual
- **Histórico** - Lembra última página visitada

### **Links Inteligentes**
```javascript
// Adicionar botão na navbar
const navbar = document.querySelector('.navbar-nav');
if (navbar) {
    const navItem = document.createElement('li');
    navItem.className = 'nav-item d-none d-sm-inline-block';
    navItem.innerHTML = `
        <a href="/" class="nav-link" style="background: linear-gradient(135deg, #007cba, #005a87); color: white; border-radius: 5px;">
            <i class="fas fa-home"></i> Site Principal
        </a>
    `;
    navbar.appendChild(navItem);
}
```

## 📊 Analytics de Navegação

### **Métricas Disponíveis**
- Páginas mais visitadas
- Tempo de navegação
- Transições admin ↔ site
- Botões mais clicados

### **Relatórios**
- Padrões de uso
- Eficiência da navegação
- Pontos de melhoria
- Feedback dos usuários

## 🚀 Exemplos de Uso

### **Adicionar Novo Link**
```javascript
// Adicionar link personalizado
const customLink = document.createElement('a');
customLink.href = '/custom-page/';
customLink.className = 'nav-link';
customLink.innerHTML = '<i class="fas fa-star"></i> Página Customizada';
```

### **Personalizar Estilo**
```css
/* Estilo personalizado para botão */
.jazzmin-site-button {
    background: linear-gradient(135deg, #your-color-1, #your-color-2);
    border-radius: 12px;
    font-size: 16px;
    padding: 15px 25px;
}
```

## 🎯 Próximas Funcionalidades

- [ ] Navegação por breadcrumbs
- [ ] Histórico de navegação
- [ ] Favoritos personalizados
- [ ] Atalhos de teclado
- [ ] Navegação por voz

## 📞 Suporte

Para dúvidas sobre navegação inteligente:
- **Email** - suporte@ticketchecker.com
- **GitHub** - [Issues](https://github.com/seu-usuario/ticketchecker/issues)
- **Documentação** - [Wiki](https://github.com/seu-usuario/ticketchecker/wiki)

---

<div align="center">
  <strong>🧭 Navegação Inteligente - Navegue com facilidade entre admin e site!</strong>
</div>
