# E-posta Asistanı Görevini Kaldır
$taskName = "EpostaAsistani"
$logPath = "C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\Projeler\e-posta-asistani\delete_log.txt"
"Script started at $(Get-Date)" | Out-File $logPath

try {
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        "✅ '$taskName' gorevi basariyla silindi!" | Out-File $logPath -Append
    } else {
        "ℹ️ '$taskName' gorevi bulunamadi." | Out-File $logPath -Append
    }
} catch {
    "❌ Hata: $_" | Out-File $logPath -Append
}
Start-Sleep -Seconds 2
