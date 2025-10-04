# Script PowerShell para configurar MailHog
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Configuração do MailHog Local" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar diretório para MailHog
if (!(Test-Path "mailhog")) {
    New-Item -ItemType Directory -Name "mailhog"
}
Set-Location "mailhog"

Write-Host "Baixando MailHog para Windows..." -ForegroundColor Yellow
Write-Host ""

try {
    # Baixar MailHog
    $url = "https://github.com/mailhog/MailHog/releases/latest/download/MailHog_windows_amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile "MailHog.exe"
    
    if (Test-Path "MailHog.exe") {
        Write-Host ""
        Write-Host "✅ MailHog baixado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "    Instruções de Uso:" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Execute o MailHog:" -ForegroundColor White
        Write-Host "   .\MailHog.exe" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Acesse a interface web em:" -ForegroundColor White
        Write-Host "   http://localhost:8025" -ForegroundColor Blue
        Write-Host ""
        Write-Host "3. O servidor SMTP estará rodando em:" -ForegroundColor White
        Write-Host "   localhost:1025" -ForegroundColor Gray
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        $response = Read-Host "Deseja iniciar o MailHog agora? (s/n)"
        if ($response -eq "s" -or $response -eq "S") {
            Write-Host "Iniciando MailHog..." -ForegroundColor Yellow
            Start-Process -FilePath ".\MailHog.exe" -WindowStyle Normal
            
            Write-Host ""
            Write-Host "✅ MailHog iniciado!" -ForegroundColor Green
            Write-Host "🌐 Interface web: http://localhost:8025" -ForegroundColor Blue
            Write-Host "📧 SMTP: localhost:1025" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        throw "Arquivo não foi baixado corretamente"
    }
} catch {
    Write-Host "❌ Erro ao baixar MailHog!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluções alternativas:" -ForegroundColor Yellow
    Write-Host "1. Baixe manualmente de: https://github.com/mailhog/MailHog/releases" -ForegroundColor White
    Write-Host "2. Ou use Docker: docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog" -ForegroundColor White
    Write-Host ""
}

Set-Location ".."
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")