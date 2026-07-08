@echo off
chcp 65001 >nul
:: HLK AI Reklam Asistani — TEST BASLAT (HLK_01_asistan surumu)
:: DUZELTILMIS: py launcher kullanir, PowerShell uyumlu

:: Eski python process'lerini oldur
echo Eski bot process'leri kapatiliyor...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Eski HLK TEST MODU pencerelerini kapat
taskkill /F /FI "WINDOWTITLE eq HLK TEST MODU" >nul 2>&1
timeout /t 1 /nobreak >nul

:: .env dosyasi bu dizinde yoksa ARSIV'den oku
if not exist ".env" (
    if exist "..\ARSIV\HLK-AI-Reklam-Asistani\.env" (
        copy "..\ARSIV\HLK-AI-Reklam-Asistani\.env" ".env" >nul
        echo .env ARSIV'den kopyalandi
    )
)

:: Venv aktif et (ARSIV'deki venv kullanilir)
set VENV_PATH=..\ARSIV\HLK-AI-Reklam-Asistani\venv
if exist "%VENV_PATH%\Scripts\python.exe" (
    set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
    echo Venv Python kullaniliyor: %PYTHON_EXE%
) else (
    :: py launcher kullan (Windows'ta her zaman mevcuttur)
    set PYTHON_EXE=py
    echo py launcher kullaniliyor
)

set BOT_MODE=test
set TEST_MODE=true
set ENV=test
set PYTHONIOENCODING=utf-8

:: Botu baslat
echo Bot baslatiliyor...
start "%PYTHON_EXE%" main.py

echo.
echo =====================
echo TEST MODU BASLATILDI
echo Bot: @hlk01_test_bot
echo Testten cikmak icin "TESTI BITIR" komutu veriniz
echo =====================
