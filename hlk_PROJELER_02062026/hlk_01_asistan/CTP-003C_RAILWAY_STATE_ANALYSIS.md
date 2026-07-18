# CTP-003C — RAILWAY STATE ANALYSIS

**Rapor Türü:** Gerçek Durum Analizi (READ ONLY — hiçbir ayar değiştirilmedi)
**Rapor Tarihi:** 17 Temmuz 2026
**Servis:** HLK_01_asistan (`bf8be267-bf53-4e29-886a-e6cf9c8f8ec2`)
**Hazırlayan:** AI Geliştirici (Claude Code — MASTER-007 uyumlu)

---

## 1. MEVCUT SERVİS DURUMU (CLI ile doğrulandı)

```json
{
  "id": "bf8be267-bf53-4e29-886a-e6cf9c8f8ec2",
  "name": "HLK_01_asistan",
  "source": {
    "repo": "haluk4365/Antigravity",
    "image": null
  },
  "status": "FAILED",
  "deploymentStopped": true,
  "volumes": [
    {
      "name": "hlk_01_asistan-volume",
      "mountPath": "/data",
      "currentSizeMb": 0.0,
      "sizeMb": 5000,
      "state": "READY"
    }
  ],
  "replicas": {
    "configured": 1,
    "running": 0,
    "crashed": 0,
    "exited": 0,
    "total": 0
  }
}
```

---

## 2. DEPLOYMENT METADATA (2 başarısız deployment)

### Deployment 1: `163d6ca4` (20:19, 16.07.2026)
| Alan | Değer |
|---|---|
| `repo` | `haluk4365/Antigravity` |
| `branch` | `main` |
| **`rootDirectory`** | **`null`** |
| `commitHash` | `f9b6b68` (doğru) |
| `startCommand` | `null` |
| `builder` | `RAILPACK` |
| `volumes` | `[]` (Volume henüz eklenmemişti) |
| `imageDigest` | YOK (build başlamadı) |

### Deployment 2: `57cc89b5` (20:23, 16.07.2026)
| Alan | Değer |
|---|---|
| `repo` | `haluk4365/Antigravity` |
| `branch` | `main` |
| **`rootDirectory`** | **`null`** |
| `commitHash` | `f9b6b68` (doğru) |
| `startCommand` | `null` |
| `builder` | `RAILPACK` |
| `volumes` | `["/data"]` (Volume eklendi) |
| `imageDigest` | YOK (build başlamadı) |

### Karşılaştırma: ecom-reklam-bot (SUCCESS)
| Alan | Değer |
|---|---|
| `repo` | `haluk4365/Antigravity` |
| `branch` | `main` |
| **`rootDirectory`** | **`Projeler/eCom_Reklam_Otomasyonu`** |
| `commitHash` | `f9b6b68` |
| `startCommand` | `python main.py` |
| `builder` | `RAILPACK` |
| `imageDigest` | `sha256:e44ad5...` (BUILD EDİLMİŞ) |

---

## 3. SORU 1: Railway servisinde kayıtlı repository değeri

```
Değer: "haluk4365/Antigravity"
Kaynak: service.source.repo + deployment.meta.repo
Doğru mu: EVET
```

Her iki deployment'da da `haluk4365/Antigravity` olarak kayıtlı. Repository adı doğru.

---

## 4. SORU 2: Railway servisinde kayıtlı rootDirectory değeri

```
Değer: null (AYARLANMAMIŞ)
Kaynak: deployment.meta.rootDirectory
Olması gereken: "hlk_PROJELER_02062026/HLK_01_asistan"
```

**Her iki deployment'da da `rootDirectory: null`.** Bu, Railway'in repo kökünde build dosyalarını aramasına neden olur. Repo kökünde `requirements.txt` ve `Procfile` yoktur → build başlamaz.

---

## 5. SORU 3: Railway deployment metadata

Komut çıktıları Bölüm 2'de tam olarak verilmiştir. Özet:

- Railway repoyu buluyor ✅
- Railway commit'i çekiyor ✅ (`f9b6b68`)
- Railway build'i BAŞLATAMIYOR ❌ (`rootDirectory: null` → repo kökünde build dosyası yok)
- `imageDigest` yok — build başlamadığının kesin kanıtı
- `startCommand` yok — Procfile okunamadığı için

---

## 6. SORU 4: Repository bağlantısını CLI ile yeniden senkronize etmek mümkün mü?

### Mevcut CLI komutları:

```
railway service source disconnect --service HLK_01_asistan
railway service source connect --service HLK_01_asistan --repo haluk4365/Antigravity --branch main
```

### Değerlendirme:

CLI ile disconnect + reconnect **teknik olarak mümkündür.** Ancak:

- `railway service source connect` komutu **rootDirectory parametresi ALMAZ** (yardım metninde yoktur)
- Yeniden bağlantı kurulsa bile `rootDirectory` hala `null` kalacaktır
- Bu işlem deployment metadata'sındaki repo bağlantısını tazeler, fakat rootDirectory sorununu ÇÖZMEZ

**Sonuç:** Repo bağlantısı CLI ile yeniden kurulabilir, ancak bu tek başına sorunu çözmez. Asıl eksik olan `rootDirectory` değeridir.

---

## 7. SORU 5: Root Directory CLI veya Config-as-Code ile uygulanabilir mi?

### 7.1 CLI Yöntemi

| Komut | rootDirectory desteği |
|---|---|
| `railway add --repo` | ❌ YOK |
| `railway service source connect` | ❌ YOK |
| `railway deployment redeploy` | ❌ YOK (mevcut deployment'ı tekrarlar) |

**CLI rootDirectory ayarlayamaz.** Bu parametre hiçbir CLI komutunda mevcut değildir.

### 7.2 railway.json (Repo-level config)

Mevcut `railway.json` şeması:

```json
{
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "...",
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**`railway.json` içinde `rootDirectory` alanı YOKTUR.** Bu, service-level bir ayardır, repo-level değildir.

### 7.3 railway.ts (Config-as-Code)

`railway config init` ile oluşturulan TypeScript konfigürasyonu teorik olarak tüm service ayarlarını içerebilir. Ancak:

- `railway config init` komutu **Railway TypeScript SDK** gerektirir (projede yüklü değil)
- `railway config pull` ile mevcut konfigürasyon çekilebilir, ancak bu da SDK gerektirir
- SDK kurulumu ve konfigürasyonun test edilmesi bu görevin kapsamı dışındadır

### 7.4 Alternatif: `railway up`

```
railway up [PATH]
```

`railway up` komutu, belirtilen dizindeki projeyi **doğrudan Railway'e yükler.** Bu yöntem:
- GitHub bağlantısını BYPASS eder
- Proje dosyalarını doğrudan bulunduğu dizinden alır
- `rootDirectory` sorununu ortadan kaldırır

**Ancak bu, GitHub'tan deploy modelini değiştirir.** GitHub push → otomatik deploy zinciri yerine, manuel CLI deploy'u gerekir.

---

## 8. DASHBOARD BUG ANALİZİ

### 8.1 Gözlem

Dashboard'da "Apply Changes" butonu repository doğrulama hatası nedeniyle çalışmıyor.

### 8.2 Deployment Pipeline vs Dashboard UI

| Bileşen | Repo Erişimi | Kanıt |
|---|---|---|
| **Deployment Pipeline** | ✅ Çalışıyor | `commitHash: f9b6b68` başarıyla çekildi |
| **Dashboard UI** | ❌ Hata veriyor | "Repository not found or is not accessible" |

Bu iki bileşen **farklı mekanizmalar** kullanıyor olabilir:

- Deployment pipeline: Railway GitHub App (sunucu tarafı, kalıcı OAuth token)
- Dashboard UI: Kullanıcının GitHub oturumu veya ayrı bir doğrulama

### 8.3 Olası Neden

Dashboard'ın repo doğrulaması başarısız olabilir çünkü:

1. **GitHub App kurulumu "Only select repositories" ile yapılmış olabilir** — ecom-reklam-bot oluşturulurken sadece o servis için izin verilmiş, yeni servis için App'in yeniden yetkilendirilmesi gerekiyor olabilir
2. **Dashboard tarayıcı oturumu ile GitHub App token'ı arasında kopukluk** — Dashboard kendi başına repo'yu doğrulamaya çalışıyor ama GitHub App kurulumunda bu repo için explicit izin yok
3. **Railway Dashboard cache** — eski bir hata durumunu gösteriyor olabilir

### 8.4 Bu Bir Bug mı?

**Evet, bu bir kullanıcı deneyimi sorunudur.** Deployment pipeline'ı repoyu başarıyla çekerken Dashboard'un "Repository not found" göstermesi ve "Apply Changes" butonunu bloke etmesi tutarsız bir davranıştır.

Ancak bu, Railway'in kendi sisteminde çözülmesi gereken bir durumdur — HLK projesi tarafında düzeltilebilecek bir şey değildir.

---

## 9. ÖZET TABLO

| Kontrol | Durum | Detay |
|---|---|---|
| Repository değeri | ✅ Doğru | `haluk4365/Antigravity` |
| Branch | ✅ Doğru | `main` |
| Commit erişimi | ✅ Çalışıyor | `f9b6b68` çekildi |
| **rootDirectory** | ❌ **null** | `hlk_PROJELER_02062026/HLK_01_asistan` olmalı |
| startCommand | ❌ null | Procfile okunamıyor |
| build | ❌ Başlamadı | imageDigest yok, railpackInfo yok |
| Volume | ✅ Ready | `/data`, 5 GB |
| Variables | ✅ 15 adet | Tümü ayarlı |
| Repo CLI sync | ✅ Mümkün | Ama rootDirectory'yi çözmez |
| rootDirectory CLI | ❌ Mümkün değil | Hiçbir CLI komutu desteklemez |
| rootDirectory railway.json | ❌ Mümkün değil | Şema desteklemez |
| Dashboard "Apply Changes" | ❌ Bloke | Repo doğrulama hatası |

---

## 10. ÇÖZÜM YOLU

Root Directory yalnızca **Railway Dashboard** üzerinden ayarlanabilir. Dashboard'daki "Apply Changes" butonu bloke ise:

1. **GitHub App'i yeniden yetkilendir:** https://github.com/apps/railway-app → Configure → Repository access → `haluk4365/Antigravity`'e erişim izni ver
2. **Dashboard'da sayfayı yenile** (F5)
3. **Root Directory'yi ayarla:** `hlk_PROJELER_02062026/HLK_01_asistan`
4. **Apply Changes** butonu şimdi çalışmalıdır
5. Yeni deployment otomatik başlayacaktır

Alternatif olarak, CLI bypass yöntemi (`railway up`) GitHub bağlantısını atlayarak doğrudan deploy yapabilir, ancak bu GitHub → Railway otomatik deploy zincirini kırar.

---

REVISION STATUS : COMPLETED
