@echo off
chcp 65001 >nul
title E-posta Asistanı

cd /d "%~dp0"

echo ============================================================
echo   E-posta Asistani Kurulum ve Ilk Calistirma
echo ============================================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.10+ yukleyin.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Virtual environment oluştur (yoksa)
if not exist "venv\" (
    echo [1/3] Virtual environment olusturuluyor...
    python -m venv venv
)

:: Bağımlılıkları kur
echo [2/3] Bagimliliklar yukleniyor...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

:: credentials.json kontrolü
if not exist "credentials.json" (
    echo.
    echo ============================================================
    echo [ONEMLI] credentials.json bulunamadi!
    echo.
    echo Google Cloud Console'dan indirip bu klasore koymaniz gerekiyor:
    echo %~dp0credentials.json
    echo.
    echo Adimlar icin README.md dosyasini okuyun.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

echo [3/3] E-posta Asistani baslatiliyor...
echo.
python main.py

echo.
echo ============================================================
echo   Islem tamamlandi. Log dosyalari: logs\ klasorunde
echo ============================================================
pause
