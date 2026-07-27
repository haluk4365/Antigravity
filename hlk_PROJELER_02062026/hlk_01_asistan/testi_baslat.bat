@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
:: HLK AI Reklam Asistani — TEST BASLAT (HLK_01_asistan surumu)
:: Windows 11 uyumlu — .venv oncelikli, py launcher yedek

:: Proje dizinine gec
cd /d "%~dp0"

:: Eski python process'lerini oldur
echo Eski bot process'leri kapatiliyor...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Eski HLK TEST MODU pencerelerini kapat
taskkill /F /FI "WINDOWTITLE eq HLK TEST MODU" >nul 2>&1
timeout /t 1 /nobreak >nul

:: Python bul: .venv oncelikli, yoksa py launcher
set PYTHON_EXE=py
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo [OK] .venv Python kullaniliyor
) else (
    echo [UYARI] .venv bulunamadi, py launcher kullaniliyor
    echo [UYARI] Bagimliliklar sistem Python'unda kurulu olmayabilir!
    echo [BILGI] .venv olusturmak icin: py -m venv .venv ^&^& .venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: .venv varsa ama requirements kurulu degilse kontrol et
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import telegram; import fastapi" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [HATA] .venv var ama bagimliliklar eksik! Kuruluyor...
        .venv\Scripts\python.exe -m pip install -r requirements.txt
        if !errorlevel! neq 0 (
            echo [KRITIK HATA] Bagimliliklar kurulamadi!
            pause
            exit /b 1
        )
        echo [OK] Bagimliliklar kuruldu
    )
)

set BOT_MODE=test
set TEST_MODE=true
set ENV=test
set PYTHONIOENCODING=utf-8

echo.
echo =====================
echo TEST MODU BASLATILIYOR
echo Python: !PYTHON_EXE!
echo Bot: @hlk01_test_bot
echo =====================
echo.

:: Botu baslat — "start" ilk tirnakli arguman pencere basligidir
start "HLK TEST MODU" !PYTHON_EXE! main.py

echo Testten cikmak icin "TESTI BITIR" komutu veriniz
exit /b 0
