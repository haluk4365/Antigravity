# HLK AI Reklam Asistani — PowerShell ile TEST BASLAT
# Kullanim: PowerShell'de bu scripti calistir
#   .\testi_baslat.ps1
# veya Claude Code'tan:
#   py main.py  (otomatik test modunda baslar, .env ENV=test)

$ErrorActionPreference = "Continue"

# Eski python process'lerini oldur
Write-Host "Eski bot process'leri kapatiliyor..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Test ortam degiskenleri
$env:ENV = "test"
$env:TEST_MODE = "true"
$env:BOT_MODE = "test"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "=====================" -ForegroundColor Green
Write-Host "TEST MODU BASLATILDI" -ForegroundColor Green
Write-Host "Bot: @hlk01_test_bot" -ForegroundColor Green
Write-Host "PID: $pid" -ForegroundColor Gray
Write-Host "=====================" -ForegroundColor Green

# Botu baslat
py main.py
