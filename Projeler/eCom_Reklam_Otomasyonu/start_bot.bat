@echo off
cd /d "c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\eCom_Reklam_Otomasyonu"
title HLK Reklam Bot - AKTIF

:LOOP
echo.
echo ============================================================
echo  [%date% %time%] Bot baslatiliyor...
echo ============================================================
echo [%date% %time%] Bot baslatiliyor... >> logs\bot_startup.log

python main.py >> logs\bot_output.log 2>&1

echo.
echo [%date% %time%] Bot durdu veya coktu! (Exit code: %errorlevel%) >> logs\bot_startup.log
echo  [%date% %time%] BOT DURDU - 15 saniye sonra yeniden baslatilacak...
echo  Kapatmak istiyorsaniz bu pencereyi kapatin.
echo.

timeout /t 15 /nobreak

goto LOOP
