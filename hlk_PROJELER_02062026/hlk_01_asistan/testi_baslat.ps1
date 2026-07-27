# HLK AI Reklam Asistani — PowerShell ile TEST BASLAT
# Kullanim: .\testi_baslat.ps1

$ErrorActionPreference = "Continue"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# Eski python process'lerini oldur
Write-Host "Eski bot process'leri kapatiliyor..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Python bul: .venv oncelikli, yoksa py launcher
$pythonExe = "py"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonExe = ".\.venv\Scripts\python.exe"
    Write-Host "[OK] .venv Python kullaniliyor: $pythonExe" -ForegroundColor Green
}
else {
    Write-Host "[UYARI] .venv bulunamadi, py launcher kullaniliyor" -ForegroundColor Yellow
    Write-Host "[BILGI] .venv olusturmak icin: py -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Gray
}

# .venv varsa ama bagimliliklar eksikse kur
if (Test-Path ".\.venv\Scripts\python.exe") {
    $testImport = & .\.venv\Scripts\python.exe -c "import telegram; import fastapi" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[HATA] .venv var ama bagimliliklar eksik! Kuruluyor..." -ForegroundColor Red
        & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[KRITIK HATA] Bagimliliklar kurulamadi!" -ForegroundColor Red
            pause
            exit 1
        }
        Write-Host "[OK] Bagimliliklar kuruldu" -ForegroundColor Green
    }
}

# Test ortam degiskenleri
$env:ENV = "test"
$env:TEST_MODE = "true"
$env:BOT_MODE = "test"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "=====================" -ForegroundColor Green
Write-Host "TEST MODU BASLATILIYOR" -ForegroundColor Green
Write-Host "Python: $pythonExe" -ForegroundColor Gray
Write-Host "Bot: @hlk01_test_bot" -ForegroundColor Green
Write-Host "PID: $pid" -ForegroundColor Gray
Write-Host "=====================" -ForegroundColor Green

# Botu baslat
& $pythonExe main.py
