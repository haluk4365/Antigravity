@echo off
chcp 65001 >nul
title E-posta Asistani — Gorev Kurulumu (PowerShell Methodu)

:: Yonetici kontrolu
net session >nul 2>&1
if errorlevel 1 (
    echo [HATA] Yonetici yetkisi gerekiyor!
    echo Bu dosyaya sag tiklayin ve "Yonetici olarak calistir" secin.
    pause
    exit /b 1
)

echo [1/3] Eski gorev siliniyor...
powershell -Command "Unregister-ScheduledTask -TaskName 'EpostaAsistani' -Confirm:$false -ErrorAction SilentlyContinue"

echo [2/3] Gorev olusturuluyor (PIL KISITLAMASI KAPALI)...
powershell -ExecutionPolicy Bypass -Command ^
  "$action  = New-ScheduledTaskAction -Execute 'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\venv\Scripts\python.exe' -Argument 'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\main.py' -WorkingDirectory 'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani';" ^
  "$trigger = New-ScheduledTaskTrigger -Daily -At '21:00';" ^
  "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1);" ^
  "$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType Interactive;" ^
  "Register-ScheduledTask -TaskName 'EpostaAsistani' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null;" ^
  "Write-Host 'Gorev olusturuldu!'"

if errorlevel 1 (
    echo [HATA] Gorev olusturulamadi!
    pause
    exit /b 1
)

echo [3/3] Ayarlar dogrulaniyor...
powershell -Command ^
  "$t = Get-ScheduledTask -TaskName 'EpostaAsistani';" ^
  "$s = $t.Settings;" ^
  "Write-Host ('Pil kisitlamasi (DisallowStartIfOnBatteries): ' + $s.DisallowStartIfOnBatteries);" ^
  "Write-Host ('Pilde durdur   (StopIfGoingOnBatteries)     : ' + $s.StopIfGoingOnBatteries);" ^
  "Write-Host ('Kacirilmissa calistir (StartWhenAvailable)  : ' + $s.StartWhenAvailable);" ^
  "Write-Host ('Durum: ' + $t.State)"

echo.
echo ============================================
echo  BASARILI! Her gun 21:00'da calisir.
echo  - Pil ile de calisir
echo  - 21:00'u kacirsa bilgisayar acilinca
echo    otomatik devreye girer
echo ============================================
echo.

set /p RUN="Simdi test olarak calistirmak ister misiniz? (E/H): "
if /i "%RUN%"=="E" (
    echo Gorev baslatiliyor...
    powershell -Command "Start-ScheduledTask -TaskName 'EpostaAsistani'"
    echo Gorev baslatildi! Logs klasorunu kontrol edin.
    timeout /t 3 >nul
    start "" "C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\logs"
)

pause
