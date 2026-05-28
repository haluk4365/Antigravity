# 🚀 Deploy Registry — Deployment Kayıt Defteri

Bu dosya, Railway'e deploy edilmiş projelerin kayıt defteridir.

---

## Aktif Deployment'lar

| Proje | Railway Proje ID | Service ID | Ortam | Tip | Durum |
|-------|-----------------|------------|-------|-----|-------|
| eCom_Reklam_Otomasyonu | `69be07e1-f26e-409f-9e03-bf0d2b8cc04d` | `dd5ffc56-7faf-4a60-abdb-5afb74944f4c` | production | Worker | ✅ Aktif |


---

## Deploy Bilgileri Nasıl Eklenir?

Her başarılı deploy sonrasında şu bilgileri ekleyin:

```markdown
| Proje_Adı | prj_xxxxx | srv_xxxxx | production | Worker/Cron | ✅ Aktif |
```

### Gerekli Bilgiler:
- **Railway Proje ID:** GraphQL API'den veya Railway dashboard'dan alınır
- **Service ID:** Aynı projede birden fazla servis olabilir
- **Ortam:** `production` veya `staging`
- **Tip:** `Worker` (7/24), `Cron` (zamanlanmış), `Web` (HTTP)
- **Durum:** ✅ Aktif, ⏸️ Durduruldu, ❌ Kapatıldı

---

## Arşiv (Kapatılmış/Taşınmış)

| Proje | Kapatılma Tarihi | Neden |
|-------|-----------------|-------|
| _(Gerektiğinde buraya taşıyın)_ | | |
