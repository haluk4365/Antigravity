@echo off
chcp 65001 >nul
:: HLK AI Reklam Asistani — TEST BASLAT (HLK_01_asistan surumu)
:: Windows 11 uyumlu — py launcher kullanir, PowerShell destekler

:: Eski python process'lerini oldur
echo Eski bot process'leri kapatiliyor...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Eski HLK TEST MODU pencerelerini kapat
taskkill /F /FI "WINDOWTITLE eq HLK TEST MODU" >nul 2>&1
timeout /t 1 /nobreak >nul

:: Python bul: once .venv, sonra py launcher
set PYTHON_EXE=py
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo .venv Python kullaniliyor: %PYTHON_EXE%
) else (
    echo py launcher kullaniliyor
)

set BOT_MODE=test
set TEST_MODE=true
set ENV=test
set PYTHONIOENCODING=utf-8

:: Botu baslat
echo Bot baslatiliyor...
:: start komutu: ilk tirnakli arguman pencere basligidir
start "HLK TEST MODU" %PYTHON_EXE% main.py

echo.
echo =====================
echo TEST MODU BASLATILDI
echo Bot: @hlk01_test_bot
echo Testten cikmak icin "TESTI BITIR" komutu veriniz
echo =====================
