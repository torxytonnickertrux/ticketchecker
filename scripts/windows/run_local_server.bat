@echo off
echo ========================================
echo    Servidor Django - Ambiente Local
echo ========================================
echo.

REM Verificar se MailHog está rodando
echo Verificando se MailHog está rodando...
powershell -Command "try { $tcpClient = New-Object System.Net.Sockets.TcpClient; $tcpClient.Connect('localhost', 1025); $tcpClient.Close(); Write-Host '✅ MailHog está rodando!' } catch { Write-Host '❌ MailHog não está rodando!' }"

echo.
echo Iniciando servidor Django com configurações locais...
echo.
echo 🌐 Servidor: http://localhost:8000
echo 📧 MailHog: http://localhost:8025
echo 📝 Logs: email_debug.log
echo.

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Iniciar servidor Django com configurações locais
python manage.py runserver --settings=backend.settings_local

echo.
echo Servidor Django finalizado.
pause