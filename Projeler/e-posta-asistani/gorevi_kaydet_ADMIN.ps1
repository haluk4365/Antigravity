# Antigravity — 21:01 Bildirim Görevi Kayıt Scripti

# Yonetici yetkisi kontrolu ve otomatik yukseltme
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

$TaskName = "Antigravity_Bildirim_2101"
$BatPath  = "C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\calistir_bildirim.bat"

# Varsa sil
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Görevi oluştur
$action  = New-ScheduledTaskAction -Execute $BatPath
$trigger = New-ScheduledTaskTrigger -Once -At "21:01"
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $action `
    -Trigger  $trigger `
    -Settings $settings `
    -RunLevel  Highest `
    -Force

Write-Host ""
Write-Host "✅ Görev basariyla kaydedildi!" -ForegroundColor Green
Write-Host "   Ad  : $TaskName" -ForegroundColor Cyan
Write-Host "   Saat: 21:01 bugun" -ForegroundColor Cyan
Write-Host "   E-posta hesabina bildirim gonderilecek." -ForegroundColor Cyan
Write-Host ""
Read-Host "Devam etmek icin Enter'a basin"
