# Yonetici yetkisi kontrolu ve otomatik yukseltme
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Unregister-ScheduledTask -TaskName 'EpostaAsistani' -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction `
    -Execute 'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\venv\Scripts\python.exe' `
    -Argument '"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\main.py"' `
    -WorkingDirectory 'C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani'

$trigger = New-ScheduledTaskTrigger -Daily -At '12:00'

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -RunLevel Highest `
    -LogonType Interactive

Register-ScheduledTask `
    -TaskName 'EpostaAsistani' `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force | Out-Null

Write-Host ""
Write-Host "=== GOREV OLUSTURULDU ===" -ForegroundColor Green
$t = Get-ScheduledTask -TaskName 'EpostaAsistani'
$s = $t.Settings
Write-Host "DisallowStartIfOnBatteries : $($s.DisallowStartIfOnBatteries)" -ForegroundColor Cyan
Write-Host "StopIfGoingOnBatteries     : $($s.StopIfGoingOnBatteries)" -ForegroundColor Cyan
Write-Host "StartWhenAvailable         : $($s.StartWhenAvailable)" -ForegroundColor Cyan
Write-Host "Durum                      : $($t.State)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Test calistiriliyor..." -ForegroundColor Yellow
Start-ScheduledTask -TaskName 'EpostaAsistani'
Start-Sleep -Seconds 3

Write-Host "Gorev tetiklendi! Logs klasorunu kontrol edin." -ForegroundColor Green
Write-Host "Logs: C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\logs"
