#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Auditoria de Segurança para o Sistema de Ingressos
Realiza verificações de segurança no sistema Django, incluindo:
- Configurações de segurança no settings.py
- Vulnerabilidades comuns em views e models
- Permissões e autenticação
- Proteção contra ataques comuns (CSRF, XSS, SQL Injection)
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para importar módulos do Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.contrib.auth.models import User, Permission
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    print("Erro ao importar Django. Verifique se o ambiente virtual está ativado.")
    sys.exit(1)

class SecurityAuditor:
    """Classe para auditoria de segurança do sistema"""
    
    def __init__(self, output_file=None):
        """Inicializa o auditor de segurança"""
        self.issues = []
        self.output_file = output_file or os.path.join(
            Path(__file__).resolve().parent.parent, 
            'relatorios', 
            f'security_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        self.severity_levels = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
    
    def add_issue(self, title, description, severity, recommendation=None):
        """Adiciona um problema de segurança encontrado"""
        issue = {
            'title': title,
            'description': description,
            'severity': severity,
            'recommendation': recommendation or "Nenhuma recomendação disponível"
        }
        self.issues.append(issue)
        self.severity_levels[severity] += 1
        
    def check_debug_mode(self):
        """Verifica se o DEBUG está ativado em produção"""
        if settings.DEBUG:
            self.add_issue(
                title="DEBUG ativado",
                description="O modo DEBUG está ativado, o que pode expor informações sensíveis em produção.",
                severity="critical",
                recommendation="Desative o DEBUG em ambientes de produção definindo DEBUG = False no settings.py"
            )
    
    def check_secret_key(self):
        """Verifica se a SECRET_KEY está exposta ou é fraca"""
        if not hasattr(settings, 'SECRET_KEY'):
            self.add_issue(
                title="SECRET_KEY não definida",
                description="A SECRET_KEY não está definida nas configurações.",
                severity="critical",
                recommendation="Defina uma SECRET_KEY forte e única no settings.py"
            )
        elif settings.SECRET_KEY == 'your-secret-key-here' or len(settings.SECRET_KEY) < 32:
            self.add_issue(
                title="SECRET_KEY fraca ou padrão",
                description="A SECRET_KEY parece ser fraca ou um valor padrão.",
                severity="high",
                recommendation="Gere uma nova SECRET_KEY forte e aleatória"
            )
    
    def check_middleware(self):
        """Verifica se os middlewares de segurança estão configurados"""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware'
        ]
        
        for middleware in required_middleware:
            if middleware not in settings.MIDDLEWARE:
                self.add_issue(
                    title=f"Middleware ausente: {middleware}",
                    description=f"O middleware de segurança {middleware} não está configurado.",
                    severity="high",
                    recommendation=f"Adicione '{middleware}' à lista MIDDLEWARE no settings.py"
                )
    
    def check_https_settings(self):
        """Verifica configurações relacionadas a HTTPS"""
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            self.add_issue(
                title="Redirecionamento SSL não ativado",
                description="SECURE_SSL_REDIRECT não está ativado, permitindo conexões não-HTTPS.",
                severity="medium",
                recommendation="Defina SECURE_SSL_REDIRECT = True no settings.py para produção"
            )
        
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            self.add_issue(
                title="Cookies de sessão inseguros",
                description="SESSION_COOKIE_SECURE não está ativado, permitindo transmissão de cookies de sessão em conexões não-HTTPS.",
                severity="medium",
                recommendation="Defina SESSION_COOKIE_SECURE = True no settings.py para produção"
            )
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            self.add_issue(
                title="Cookies CSRF inseguros",
                description="CSRF_COOKIE_SECURE não está ativado, permitindo transmissão de tokens CSRF em conexões não-HTTPS.",
                severity="medium",
                recommendation="Defina CSRF_COOKIE_SECURE = True no settings.py para produção"
            )
    
    def check_admin_url(self):
        """Verifica se a URL do admin é padrão"""
        from django.urls import URLPattern, URLResolver
        
        def find_admin_url(urlpatterns, base=''):
            for pattern in urlpatterns:
                if isinstance(pattern, URLResolver):
                    # É um include, verifica recursivamente
                    yield from find_admin_url(pattern.url_patterns, base + str(pattern.pattern))
                elif isinstance(pattern, URLPattern):
                    if 'admin' in str(pattern.callback):
                        yield base + str(pattern.pattern)
        
        try:
            from backend.urls import urlpatterns
            admin_urls = list(find_admin_url(urlpatterns))
            
            if any('admin/' in url for url in admin_urls):
                self.add_issue(
                    title="URL de admin padrão",
                    description="A URL do painel de administração está usando o caminho padrão 'admin/'.",
                    severity="low",
                    recommendation="Altere a URL do admin para um caminho personalizado para dificultar ataques automatizados"
                )
        except (ImportError, AttributeError):
            self.add_issue(
                title="Não foi possível verificar URL do admin",
                description="Não foi possível verificar se a URL do admin é padrão devido a um erro de importação.",
                severity="info",
                recommendation="Verifique manualmente se a URL do admin foi personalizada"
            )
    
    def check_user_permissions(self):
        """Verifica permissões de usuários e superusuários"""
        try:
            superusers_count = User.objects.filter(is_superuser=True).count()
            if superusers_count > 2:
                self.add_issue(
                    title="Múltiplos superusuários",
                    description=f"Existem {superusers_count} superusuários no sistema.",
                    severity="medium",
                    recommendation="Limite o número de superusuários e use permissões granulares quando possível"
                )
                
            # Verifica usuários com permissões elevadas mas sem autenticação de dois fatores
            # Nota: Isso assume que você tem um campo para 2FA no modelo de usuário
            # Adapte conforme necessário
            try:
                users_with_high_permissions = User.objects.filter(
                    is_staff=True, 
                    two_factor_enabled=False
                ).count()
                if users_with_high_permissions > 0:
                    self.add_issue(
                        title="Usuários com privilégios sem 2FA",
                        description=f"{users_with_high_permissions} usuários com privilégios não têm autenticação de dois fatores ativada.",
                        severity="high",
                        recommendation="Exija autenticação de dois fatores para todos os usuários com privilégios administrativos"
                    )
            except Exception:
                # O campo two_factor_enabled provavelmente não existe
                self.add_issue(
                    title="Autenticação de dois fatores não implementada",
                    description="O sistema não parece ter implementado autenticação de dois fatores.",
                    severity="medium",
                    recommendation="Implemente autenticação de dois fatores para contas com privilégios"
                )
                
        except Exception as e:
            self.add_issue(
                title="Erro ao verificar permissões de usuários",
                description=f"Não foi possível verificar permissões de usuários: {str(e)}",
                severity="info",
                recommendation="Verifique manualmente as permissões de usuários"
            )
    
    def check_installed_apps(self):
        """Verifica aplicativos instalados para identificar problemas de segurança"""
        required_apps = [
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.messages',
        ]
        
        for app in required_apps:
            if app not in settings.INSTALLED_APPS:
                self.add_issue(
                    title=f"Aplicativo ausente: {app}",
                    description=f"O aplicativo {app} não está instalado.",
                    severity="high",
                    recommendation=f"Adicione '{app}' à lista INSTALLED_APPS no settings.py"
                )
        
        # Verifica se django-debug-toolbar está ativado em produção
        if 'debug_toolbar' in settings.INSTALLED_APPS and not settings.DEBUG:
            self.add_issue(
                title="Debug Toolbar em produção",
                description="Django Debug Toolbar está ativado em ambiente de produção.",
                severity="medium",
                recommendation="Remova 'debug_toolbar' de INSTALLED_APPS em produção ou condicione à DEBUG=True"
            )
    
    def check_database_settings(self):
        """Verifica configurações de segurança do banco de dados"""
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            self.add_issue(
                title="SQLite em uso",
                description="SQLite está sendo usado como banco de dados, o que pode não ser adequado para produção.",
                severity="medium",
                recommendation="Considere usar PostgreSQL ou MySQL para ambientes de produção"
            )
        
        # Verifica se as credenciais do banco estão expostas no settings
        if 'PASSWORD' in settings.DATABASES['default'] and settings.DATABASES['default']['PASSWORD']:
            if not os.environ.get('DATABASE_PASSWORD'):
                self.add_issue(
                    title="Senha do banco de dados exposta",
                    description="A senha do banco de dados está diretamente no arquivo settings.py.",
                    severity="high",
                    recommendation="Use variáveis de ambiente ou um arquivo .env para armazenar credenciais"
                )
    
    def check_file_upload_settings(self):
        """Verifica configurações de upload de arquivos"""
        if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
            self.add_issue(
                title="MEDIA_ROOT não configurado",
                description="MEDIA_ROOT não está configurado para uploads de arquivos.",
                severity="medium",
                recommendation="Configure MEDIA_ROOT no settings.py"
            )
        
        # Verifica se há restrições de tipo de arquivo
        # Isso é uma verificação simplificada, adapte conforme necessário
        has_file_validation = False
        
        # Procura por validação de arquivos em apps comuns
        try:
            import events.models
            import users.models
            
            # Verifica se há validadores de arquivo em algum FileField
            for app_models in [events.models, users.models]:
                for name in dir(app_models):
                    obj = getattr(app_models, name)
                    if hasattr(obj, '_meta') and hasattr(obj._meta, 'fields'):
                        for field in obj._meta.fields:
                            if field.__class__.__name__ == 'FileField' and hasattr(field, 'validators') and field.validators:
                                has_file_validation = True
                                break
        except (ImportError, AttributeError):
            pass
        
        if not has_file_validation:
            self.add_issue(
                title="Validação de uploads de arquivos ausente",
                description="Não foi encontrada validação para uploads de arquivos.",
                severity="medium",
                recommendation="Implemente validadores para restringir tipos e tamanhos de arquivos permitidos"
            )
    
    def run_all_checks(self):
        """Executa todas as verificações de segurança"""
        print("Iniciando auditoria de segurança...")
        
        checks = [
            self.check_debug_mode,
            self.check_secret_key,
            self.check_middleware,
            self.check_https_settings,
            self.check_admin_url,
            self.check_user_permissions,
            self.check_installed_apps,
            self.check_database_settings,
            self.check_file_upload_settings
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.add_issue(
                    title=f"Erro ao executar {check.__name__}",
                    description=f"Ocorreu um erro durante a verificação: {str(e)}",
                    severity="info",
                    recommendation="Verifique manualmente este aspecto de segurança"
                )
        
        return self.generate_report()
    
    def generate_report(self):
        """Gera um relatório com os problemas encontrados"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.issues),
                'severity_counts': self.severity_levels
            },
            'issues': self.issues
        }
        
        # Cria o diretório de relatórios se não existir
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Salva o relatório em um arquivo JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"Relatório de segurança gerado: {self.output_file}")
        print(f"Total de problemas encontrados: {len(self.issues)}")
        for severity, count in self.severity_levels.items():
            if count > 0:
                print(f"- {severity.upper()}: {count}")
        
        return report

if __name__ == "__main__":
    auditor = SecurityAuditor()
    auditor.run_all_checks()