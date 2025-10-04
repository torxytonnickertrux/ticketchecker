@echo off
echo ========================================
echo    Configuracao do MailHog Local
echo ========================================
echo.

REM Criar diretorio para MailHog
if not exist "mailhog" mkdir mailhog
cd mailhog

echo Baixando MailHog para Windows...
echo.

REM Baixar MailHog (versao mais recente)
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/mailhog/MailHog/releases/latest/download/MailHog_windows_amd64.exe' -OutFile 'MailHog.exe'}"

if exist "MailHog.exe" (
    echo.
    echo ✅ MailHog baixado com sucesso!
    echo.
    echo ========================================
    echo    Instrucoes de Uso:
    echo ========================================
    echo.
    echo 1. Execute o MailHog:
    echo    .\MailHog.exe
    echo.
    echo 2. Acesse a interface web em:
    echo    http://localhost:8025
    echo.
    echo 3. O servidor SMTP estara rodando em:
    echo    localhost:1025
    echo.
    echo ========================================
    echo.
    echo Pressione qualquer tecla para iniciar o MailHog...
    pause >nul
    
    echo Iniciando MailHog...
    start "MailHog" .\MailHog.exe
    
    echo.
    echo ✅ MailHog iniciado!
    echo 🌐 Interface web: http://localhost:8025
    echo 📧 SMTP: localhost:1025
    echo.
    echo Pressione qualquer tecla para continuar...
    pause >nul
) else (
    echo ❌ Erro ao baixar MailHog!
    echo.
    echo Solucoes alternativas:
    echo 1. Baixe manualmente de: https://github.com/mailhog/MailHog/releases
    echo 2. Ou use Docker: docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
    echo.
    pause
)

cd ..