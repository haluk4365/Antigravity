# Yonetici yetkisi kontrolu ve otomatik yukseltme
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

$taskName = "EpostaAsistani"

$task = Get-ScheduledTask -TaskName $taskName
$settings = $task.Settings
$settings.DisallowStartIfOnBatteries = $false
$settings.StopIfGoingOnBatteries = $false
$settings.StartWhenAvailable = $true

Set-ScheduledTask -TaskName $taskName -Settings $settings

Write-Host ""
Write-Host "=== SONUC ===" -ForegroundColor Green
$updated = Get-ScheduledTask -TaskName $taskName | Select-Object -ExpandProperty Settings
Write-Host "Pil kisitlamasi (DisallowStartIfOnBatteries): $($updated.DisallowStartIfOnBatteries)" -ForegroundColor Cyan
Write-Host "Pilde durdur (StopIfGoingOnBatteries):        $($updated.StopIfGoingOnBatteries)" -ForegroundColor Cyan
Write-Host "Kacirilmissa calistir (StartWhenAvailable):   $($updated.StartWhenAvailable)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Gorev simdi manuel test edilsin mi? (E/H)"
$choice = Read-Host
if ($choice -eq "E" -or $choice -eq "e") {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "Gorev baslatildi! Logs klasorunu kontrol edin." -ForegroundColor Yellow
}
