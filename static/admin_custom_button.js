// Adicionar botão de navegação ao site principal no admin
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
        .jazzmin-site-button i {
            font-size: 16px;
        }
    `;
    document.head.appendChild(style);
    
    // Adicionar o botão ao body
    document.body.appendChild(button);
    
    // Adicionar botão na navbar se existir
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const navItem = document.createElement('li');
        navItem.className = 'nav-item d-none d-sm-inline-block';
        navItem.innerHTML = `
            <a href="/" class="nav-link" style="background: linear-gradient(135deg, #007cba, #005a87); color: white; border-radius: 5px; margin: 0 5px;">
                <i class="fas fa-home"></i> Site Principal
            </a>
        `;
        navbar.appendChild(navItem);
    }
    
    // Adicionar botão na sidebar se existir
    const sidebar = document.querySelector('.nav-sidebar');
    if (sidebar) {
        const sidebarItem = document.createElement('li');
        sidebarItem.className = 'nav-item';
        sidebarItem.innerHTML = `
            <a href="/" class="nav-link" style="background: linear-gradient(135deg, #007cba, #005a87); color: white; margin: 5px; border-radius: 5px;">
                <i class="nav-icon fas fa-home"></i>
                <p>Site Principal</p>
            </a>
        `;
        // Inserir no início da sidebar
        sidebar.insertBefore(sidebarItem, sidebar.firstChild);
    }
});
