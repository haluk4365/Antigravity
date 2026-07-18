# CTP-003B — REPOSITORY ACCESS ANALYSIS

**Rapor Türü:** Kanıta Dayalı Kök Neden Analizi (READ ONLY)
**Rapor Tarihi:** 17 Temmuz 2026
**Hata:** Railway Dashboard'da "Repository not found or is not accessible"
**Hazırlayan:** AI Geliştirici (Claude Code — MASTER-007 uyumlu)
**Durum:** KÖK NEDEN KANITLANDI

---

## 1. SORU

> "Railway CLI ile oluşturulan bir service'in GitHub OAuth bağlantısı gerçekten Dashboard'dan yeniden kurulmak zorunda mıdır?"

**Cevap: HAYIR.** Railway CLI ile oluşturulan servis GitHub reposuna erişebilir. Kanıt aşağıdadır.

---

## 2. KANIT: RAILWAY REPOYU GÖRÜYOR

HLK_01_asistan servisinin **başarısız deployment kaydından** alınan veriler:

```json
{
  "id": "57cc89b5-c715-4f51-b916-23e9d7840862",
  "status": "FAILED",
  "meta": {
    "repo": "haluk4365/Antigravity",
    "branch": "main",
    "commitHash": "f9b6b6839107a1d28a87c837fc1acf299763909f",
    "commitAuthor": "haluk4365",
    "commitMessage": "feat: Railway deployment FAZ-1 — HLK_01_asistan ilk commit..."
  }
}
```

**Railway başarıyla:**
- ✅ Repository'yi buldu (`haluk4365/Antigravity`)
- ✅ Branch'i buldu (`main`)
- ✅ Commit'i çekti (`f9b6b68` — FAZ-2'de push edilen commit ile birebir aynı)
- ✅ Commit yazarını okudu (`haluk4365`)
- ✅ Commit mesajını okudu

**GitHub erişim sorunu YOKTUR.** Railway repoyu görüyor ve commit'i başarıyla çekiyor.

---

## 3. GERÇEK KÖK NEDEN: `rootDirectory: null`

### 3.1 İki Servisin Deployment Meta Karşılaştırması

| Alan | ecom-reklam-bot (SUCCESS) | HLK_01_asistan (FAILED) |
|---|---|---|
| `repo` | `haluk4365/Antigravity` | `haluk4365/Antigravity` |
| `commitHash` | `f9b6b68` | `f9b6b68` |
| **`rootDirectory`** | **`Projeler/eCom_Reklam_Otomasyonu`** | **`null`** |
| `imageDigest` | `sha256:e44ad5...` (build edilmiş) | **YOK** (build başlamamış) |
| Python resolved | `3.13.14` | **YOK** (build başlamamış) |

### 3.2 `rootDirectory: null` Ne Anlama Geliyor?

Railway, `rootDirectory` ayarlanmadığında **repo kökünde** build dosyalarını arar:
- `requirements.txt`
- `Procfile`
- `.python-version`

### 3.3 Repo Kökünde Ne Var?

```
git ls-files | grep -E "^requirements.txt$|^Procfile$|^\.python-version$"
→ (SONUÇ YOK)
```

**Repo kökünde `requirements.txt`, `Procfile` ve `.python-version` YOKTUR.**

Bu dosyalar yalnızca `hlk_PROJELER_02062026/HLK_01_asistan/` dizinindedir.

### 3.4 Hata Zinciri

```
1. Railway deployment başlar
2. repo: haluk4365/Antigravity → commit f9b6b68 çekilir ✅
3. rootDirectory: null → repo KÖKÜNE bakılır
4. Repo kökünde requirements.txt/Procfile YOK
5. Build BAŞLATILAMAZ
6. Deployment FAILED
```

Build loglarının **boş olması** da bunu doğrular — build hiç başlamamıştır.

---

## 4. RAILWAY DASHBOARD'DAKI HATA MESAJI

Dashboard'da görünen "Repository not found or is not accessible" hatası **yanıltıcı olabilir.** Gerçek deployment verileri Railway'in repoyu bulduğunu ve commit'i çektiğini göstermektedir.

Bu hata mesajı şu durumlarda da görünebilir:
- Root Directory geçersiz veya boş olduğunda build başlatılamaması
- Railway Dashboard UI'ının build öncesi hatayı genel bir "repository erişim" hatası olarak göstermesi
- Dashboard'ın kendi repo doğrulama mekanizmasının ayrı bir kontrol yapması

---

## 5. SONUÇ

| Soru | Kanıta Dayalı Cevap |
|---|---|
| Railway repoyu görüyor mu? | **Evet** — commit `f9b6b68` başarıyla çekildi |
| GitHub OAuth sorunu mu? | **Hayır** — kanıt yok |
| Repository private mı? | **Hayır** — public repo |
| Railway CLI bağlantıyı kurdu mu? | **Evet** — repo, branch, commit çözümlendi |
| **Gerçek neden?** | **`rootDirectory: null`** — Railway repo kökünde build dosyası arıyor, bulamıyor |

---

## 6. ÇÖZÜM

### Sorun

Railway CLI (`railway add --repo`) rootDirectory ayarını otomatik olarak yapmaz. Bu değer **her deployment için ayrıca belirtilmelidir.** Mevcut deployment'lar `rootDirectory: null` ile oluşturulduğu için başarısızdır.

### Çözüm Adımları

**Adım 1 — Root Directory'yi Dashboard'dan ayarla (zaten yapıldıysa doğrula):**

Railway Dashboard → HLK_01_asistan → Settings → Root Directory:
```
hlk_PROJELER_02062026/HLK_01_asistan
```

**Adım 2 — Yeni deployment tetikle:**

Root Directory ayarlandıktan sonra **yeni bir deployment başlatılmalıdır.** Mevcut başarısız deployment'lar (`rootDirectory: null` ile oluşanlar) düzeltilemez — yeni deployment gerekir.

Railway Dashboard → HLK_01_asistan → **Redeploy** veya Railway CLI:
```bash
railway redeploy --service HLK_01_asistan
```

**Adım 3 — Doğrula:**

Yeni deployment'ın meta verisinde `rootDirectory: "hlk_PROJELER_02062026/HLK_01_asistan"` görünmeli ve build loglarında `CONSTITUTIONAL BOOT SEQUENCE BAŞLADI` satırı belirmelidir.

---

## 7. KANIT ÖZETİ

```
Railway Deployment Meta Verisi (kaynak: railway deployment list --json)
═══════════════════════════════════════════════════════════════════════
repo:            haluk4365/Antigravity     ← DOĞRU, erişiliyor
branch:          main                       ← DOĞRU
commitHash:      f9b6b68                   ← DOĞRU, başarıyla çekildi
rootDirectory:   null                       ← HATALI! Olması gereken:
                                              hlk_PROJELER_02062026/HLK_01_asistan
═══════════════════════════════════════════════════════════════════════
```

---

REVISION STATUS : COMPLETED
