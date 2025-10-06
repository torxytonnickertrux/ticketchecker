#!/usr/bin/env python
"""
Script de deploy para integração com Mercado Pago
Execute com: python deploy_mercadopago.py
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso!")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro!")
        print(f"   Erro: {e.stderr.strip()}")
        return False


def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("🔍 Verificando ambiente...")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Execute este script no diretório raiz do projeto Django")
        return False
    
    # Verificar se requirements.txt existe
    if not os.path.exists('requirements.txt'):
        print("❌ Arquivo requirements.txt não encontrado")
        return False
    
    # Verificar se o arquivo de configuração existe
    if not os.path.exists('backend/settings.py'):
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    print("✅ Ambiente verificado com sucesso!")
    return True


def install_dependencies():
    """Instala as dependências necessárias"""
    print("\n📦 Instalando dependências...")
    
    # Verificar se pip está disponível
    if not run_command("pip --version", "Verificando pip"):
        print("❌ pip não está disponível. Instale o Python e pip primeiro.")
        return False
    
    # Instalar dependências
    if not run_command("pip install -r requirements.txt", "Instalando dependências do requirements.txt"):
        return False
    
    return True


def setup_environment_files():
    """Configura os arquivos de ambiente"""
    print("\n⚙️ Configurando arquivos de ambiente...")
    
    # Verificar se .env.local existe
    if not os.path.exists('.env.local'):
        print("📝 Criando .env.local...")
        with open('.env.local', 'w') as f:
            f.write("""# Configurações locais de desenvolvimento
DEBUG=True
SITE_URL=http://127.0.0.1:8000

# Mercado Pago - Sandbox (teste)
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-2943803310877194-100314-299157cd680f0367d0c7e1a21233a9a5-2902307812
MERCADO_PAGO_PUBLIC_KEY=APP_USR-3bd9ca6a-9418-4549-89ce-07698d75fa71
MERCADO_PAGO_SANDBOX=True

# Email para desenvolvimento
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST_USER=vgf.tools1@gmail.com
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=vgf.tools1@gmail.com

# Google OAuth (se necessário)
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_SECRET=

# Webhook
WEBHOOK_SECRET_KEY=1780494c4a6fdde056486e2f07b041cda3b81c6def03e746eae273bb830c784d
""")
        print("✅ .env.local criado com configurações padrão")
    else:
        print("✅ .env.local já existe")
    
    return True


def run_migrations():
    """Executa as migrações do banco de dados"""
    print("\n🗄️ Executando migrações...")
    
    # Fazer migrações
    if not run_command("python manage.py makemigrations events", "Criando migrações"):
        return False
    
    # Aplicar migrações
    if not run_command("python manage.py migrate", "Aplicando migrações"):
        return False
    
    return True


def run_tests():
    """Executa os testes de integração"""
    print("\n🧪 Executando testes...")
    
    # Executar teste de integração
    if not run_command("python test_mercadopago_integration.py", "Teste de integração com Mercado Pago"):
        print("⚠️ Alguns testes falharam, mas a instalação pode estar correta")
        print("   Verifique os logs acima para mais detalhes")
    
    return True


def create_superuser():
    """Cria um superusuário para testes"""
    print("\n👤 Criando superusuário...")
    
    # Verificar se já existe um superusuário
    try:
        result = subprocess.run(
            "python manage.py shell -c \"from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')\"",
            shell=True, capture_output=True, text=True
        )
        
        if "Superuser exists" in result.stdout:
            print("✅ Superusuário já existe")
            return True
    except:
        pass
    
    # Criar superusuário
    print("📝 Criando superusuário (use: admin/admin123 para teste)")
    try:
        subprocess.run(
            "python manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')\"",
            shell=True, check=True
        )
        print("✅ Superusuário criado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Erro ao criar superusuário (pode já existir)")
        return True


def show_next_steps():
    """Mostra os próximos passos"""
    print("\n" + "="*60)
    print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print("="*60)
    
    print("\n📋 Próximos passos:")
    print("1. Configure suas credenciais do Mercado Pago em .env.local")
    print("2. Execute o servidor: python manage.py runserver")
    print("3. Acesse: http://127.0.0.1:8000")
    print("4. Faça login com: admin/admin123")
    print("5. Crie um evento e teste a compra com Mercado Pago")
    
    print("\n🔧 Para produção:")
    print("1. Configure as variáveis de ambiente no servidor")
    print("2. Execute: python manage.py collectstatic")
    print("3. Configure o webhook no painel do Mercado Pago")
    print("4. Teste com cartões de teste do MP")
    
    print("\n📚 Documentação:")
    print("- Consulte: MERCADO_PAGO_INTEGRATION.md")
    print("- Testes: python test_mercadopago_integration.py")
    print("- Logs: tail -f logs/django.log")


def main():
    """Função principal"""
    print("🚀 Iniciando deploy da integração com Mercado Pago")
    print("="*60)
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Instalar dependências
    if not install_dependencies():
        print("❌ Falha na instalação de dependências")
        sys.exit(1)
    
    # Configurar arquivos de ambiente
    if not setup_environment_files():
        print("❌ Falha na configuração de ambiente")
        sys.exit(1)
    
    # Executar migrações
    if not run_migrations():
        print("❌ Falha nas migrações")
        sys.exit(1)
    
    # Criar superusuário
    create_superuser()
    
    # Executar testes
    run_tests()
    
    # Mostrar próximos passos
    show_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Deploy interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)