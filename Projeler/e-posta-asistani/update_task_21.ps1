# E-posta Asistanı - Sadece trigger saatini 21:00'a guncelle

# Yonetici yetkisi kontrolu ve otomatik yukseltme
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

$taskName = "EpostaAsistani"

# Mevcut gorevi al
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($null -eq $existing) {
    Write-Host "[HATA] '$taskName' gorevi bulunamadi!" -ForegroundColor Red
    Write-Host "Once setup_task.bat'i yonetici olarak calistirin." -ForegroundColor Yellow
    pause
    exit 1
}

# Yeni trigger olustur (21:00)
$trigger = New-ScheduledTaskTrigger -Daily -At "21:00"

# Trigger'i guncelle
Set-ScheduledTask -TaskName $taskName -Trigger $trigger | Out-Null

# Sonucu dogrula
$updated = Get-ScheduledTask -TaskName $taskName
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " GUNCELLENDI! Her gun 21:00'da calisacak." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host ("Gorev Adi : " + $updated.TaskName) -ForegroundColor Cyan
Write-Host ("Durum     : " + $updated.State) -ForegroundColor Cyan
Write-Host ("Yeni Saat : " + $updated.Triggers[0].StartBoundary) -ForegroundColor Cyan
Write-Host ""
pause
