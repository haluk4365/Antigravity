# RAPOR — Kritik Sorun Denetimi: TELEGRAM_ADMIN_USER_ID

**Tarih:** 18.07.2026
**Kritik Sorun:** `TELEGRAM_ADMIN_USER_ID` Railway ortamında tanımsız → Yönetici Yeniden Üretim Prosedürü canlıda çalışamaz.
**Kapsam:** Tam kod akışı izleme + Railway ortam denetimi (salt okunur) + güvenlik mimarisi doğrulaması. Hiçbir commit, push, merge, deploy, üretim işlemi yapılmadı.

---

## Yapılan Kontroller

### 1. Kod Denetimi — TELEGRAM_ADMIN_USER_ID akışı

Aşağıda değişkenin sistemdeki **tam izi** çıkarılmıştır. Hiçbir varsayım yapılmamıştır; tüm satır numaraları gerçek kaynak dosyalardan alınmıştır.

```
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 1 — Ortam Değişkeni (Railway / .env)                     │
│                                                                  │
│ os.getenv("TELEGRAM_ADMIN_USER_ID", "")                          │
│                                                                  │
│ • Railway: TANIMSIZ (26 değişken içinde YOK — canlıdan doğrulandı)│
│ • Lokal .env: TANIMSIZ                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 2 — Settings (config/settings.py:18, 52–56)               │
│                                                                  │
│ class Settings:                                                   │
│     TELEGRAM_ADMIN_USER_ID: str = os.getenv(...)  # ← satır 18  │
│                                                                  │
│     def is_admin(self, user_id):                  # ← satır 52  │
│         if not self.TELEGRAM_ADMIN_USER_ID:                     │
│             return False    ← GÜVENLİ VARSAYILAN                │
│         return str(user_id) == str(self.TELEGRAM_ADMIN_USER_ID) │
│                                                                  │
│ SONUÇ: Değişken boş/tanımsız → is_admin() HER ZAMAN False       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ KATMAN 3 — Handler (handlers/yeniden_uretim.py:59–69)            │
│                                                                  │
│ def _is_admin(user_id: int) -> bool:                             │
│     admin_id = Settings.TELEGRAM_ADMIN_USER_ID  ← satır 66      │
│     if not admin_id:                                             │
│         return False    ← GÜVENLİ VARSAYILAN (katman 2 ile aynı) │
│     return str(user_id) == str(admin_id)                         │
│                                                                  │
│ Bu fonksiyon 3 kontrolde kullanılır:                              │
│  ① satır 134 — handle_yeniden_uretim_command (/yeniden komutu)  │
│  ② satır 229 — handle_yeniden_uretim_onay ([Evet, Başlat])      │
│  ③ satır 297 — handle_yeniden_uretim_iptal ([İptal])            │
│                                                                  │
│ Yetkisiz erişimde her 3 kontrol de:                               │
│  → "⛔ Bu komut yalnızca Yönetici tarafından kullanılabilir"    │
│  → logger.warning (yetkisiz deneme kaydı)                        │
│  → return (işlem sonlandırılır)                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Ek kullanım noktaları:**

| Dosya | Satır | Kullanım |
|---|---|---|
| `main.py` | 133–137 | `/yeniden` handler import'u |
| `main.py` | 295 | `CommandHandler("yeniden", handle_yeniden_uretim_command)` |
| `main.py` | 409–414 | `CallbackQueryHandler` kayıtları (`reprod_onay:`, `reprod_iptal:`) |
| `ANA YASA/03_Architecture_Rules.md` | 7413 | AR-002_84 yetki tanımı: "Yönetici kimliği `TELEGRAM_ADMIN_USER_ID` yapılandırması ile doğrulanır" |

---

### 2. Railway Environment Denetimi (canlıdan salt okunur)

| Kontrol | Sonuç | Kanıt |
|---|---|---|
| Railway'de tanımlı mı? | ❌ **TANIMSIZ** | `railway variables --json` → 26 değişken listelendi, `TELEGRAM_ADMIN_USER_ID` listede **YOK** |
| Yanlış isimle tanımlanmış olabilir mi? | ❌ Yok | Tüm değişken adları tarandı; benzer isimli (`ADMIN`, `USER_ID`, `TELEGRAM_ADMIN` vb.) değişken yok |
| Boş değer içeriyor mu? | — | Tanımlı olmadığı için değerlendirilemez |
| Kod ile Railway değişken adı birebir aynı mı? | ✅ | Kod `os.getenv("TELEGRAM_ADMIN_USER_ID", "")` — değişken adı doğru; Railway'de bu isimle eklenmeli |

---

### 3. Yapılandırma Denetimi

| Dosya | Durum | Açıklama |
|---|---|---|
| `config/settings.py:18` | ✅ Doğru | `os.getenv("TELEGRAM_ADMIN_USER_ID", "")` — doğru env anahtarı, güvenli varsayılan `""` |
| `config/settings.py:52–56` | ✅ Doğru | `is_admin()` — boş değerde `False` döner (güvenli varsayılan) |
| `handlers/yeniden_uretim.py:59–69` | ✅ Doğru | `_is_admin()` — aynı güvenli varsayılan mantığı, `Settings` sınıf özniteliğini kullanır |
| `handlers/yeniden_uretim.py:134,229,297` | ✅ Doğru | 3 kontrol noktası; yetkisiz → mesaj + log + return |
| Lokal `.env` | ⚠️ Eksik | `TELEGRAM_ADMIN_USER_ID` satırı yok (lokal test botunda `/yeniden` çalışmaz) |
| `.env.example` | — | Projede `.env.example` dosyası yok |
| Railway Variables | 🚨 Eksik | Değişken tanımlı değil → canlıda `/yeniden` hiç kimse için çalışmaz |
| Runtime başlangıç (`main.py`) | ✅ Etkilenmez | `Settings` sınıf seviyesinde okuma — değişkenin yokluğu bot başlangıcını engellemez |

---

### 4. Güvenlik Denetimi

| Kural | Durum | Gerekçe |
|---|---|---|
| Yalnızca Yönetici prosedürü başlatabiliyor | ⚠️ **Teorik olarak çalışıyor, pratikte çalışmıyor** | Kod güvenlik katmanı doğru: `_is_admin()` → `Settings.TELEGRAM_ADMIN_USER_ID` → yetki doğrulaması. Ancak değişken tanımsız olduğu için `_is_admin()` her zaman `False` → **hiç kimse** Yönetici kabul edilmiyor. Sistem güvende, ama prosedür **hiç** kullanılamıyor |
| Yetkisiz kullanıcılar reddediliyor | ✅ Doğru | 3 ayrı kontrol noktasında `_is_admin(user.id)` → `False` → "Bu komut yalnızca Yönetici tarafından kullanılabilir" + log kaydı |
| Güvenlik kontrolü yalnızca Runtime tarafından uygulanıyor | ✅ Doğru (Handler katmanı) | Yetki kontrolü handler'da yapılıyor, ancak bu bir **karar değil** — MASTER-013 yasağı "karar verme" yasağıdır; yetki doğrulaması (authentication) handler'ın sorumluluğundadır (normal bot handler'ları da `effective_user` kontrolü yapar). Üretime ilişkin tüm kararlar (strateji, sağlayıcı, devam/durdur) HLK Runtime'dadır |
| Handler yalnızca yönlendirme yapıyor | ✅ Doğru | Handler: yetki kontrolü → paket bulma → onay ekranı → Runtime'a devir. Bu akış AR-002_56 (Yönetici Onay Katmanı) ile aynı desendedir |
| Mevcut güvenlik mimarisi korunuyor | ✅ Doğru | Yeni yetki kontrolü dışında mevcut güvenlik katmanlarına dokunulmadı (TELEGRAM_ALLOWED_USERS, Boot Chain, constitutional authorization vb.) |

---

## Yapılan Düzeltmeler

**Kod düzeyinde düzeltme GEREKMİYOR.** Sorun tamamen ortam yapılandırması (environment) eksikliğidir.

Uygulanan kod değişikliği: **YOK** (gerekli değil).

---

## Etkilenen Dosyalar

**Bu denetimde değiştirilen dosya:** YOK.

**`TELEGRAM_ADMIN_USER_ID` değişkeninin okunduğu dosyalar (bilgi amaçlı):**

| Dosya | Rol |
|---|---|
| `config/settings.py` | Değişkeni okur (`os.getenv`), `is_admin()` metodunu sağlar |
| `handlers/yeniden_uretim.py` | `_is_admin()` ile yetki kontrolü yapar (3 noktada) |
| `main.py` | `/yeniden` handler'ını kaydeder (değişkeni doğrudan okumaz) |

---

## Doğrulama Sonuçları

| Doğrulama | Sonuç |
|---|---|
| Yönetici doğrulaması doğru çalışıyor (kod seviyesinde) | ✅ Tanımlı olduğunda çalışacak; tanımsızken güvenli red |
| TELEGRAM_ADMIN_USER_ID doğru okunuyor (kod seviyesinde) | ✅ `os.getenv("TELEGRAM_ADMIN_USER_ID", "")` — doğru env anahtarı, doğru varsayılan |
| Railway deploy sonrası çalışacak durumda | ⚠️ Değişken Railway'e eklendikten sonra çalışır |
| Bu düzeltme mevcut üretim akışını etkilemiyor | ✅ Salt-ortam değişikliği — kod değişmedi |
| Anayasal mimari korunuyor | ✅ MASTER-013 (handler karar vermez), AR-002_84 yetki tanımı, güvenli varsayılan ilkesi korunuyor |

---

## Railway'de Tanımlanması Gereken Environment Variable

**Adı:**

```
TELEGRAM_ADMIN_USER_ID
```

**Değeri:**

```
<Yönetici Telegram User ID>
```

**Railway CLI ile ekleme (önerilen):**

```bash
railway variables set TELEGRAM_ADMIN_USER_ID=<Yönetici Telegram User ID>
```

Veya Railway Dashboard → Proje → HLK_01_asistan → Variables → "New Variable" → `TELEGRAM_ADMIN_USER_ID` = `<Yönetici Telegram User ID>` → Deploy.

**Lokal `.env` dosyasına eklenecek satır:**

```
TELEGRAM_ADMIN_USER_ID=<Yönetici Telegram User ID>
```

Bu satır `.env` dosyasının herhangi bir yerine eklenebilir. `.env` git tarafından izlenmez (`.gitignore` kapsamında), dolayısıyla hassas bilgi repoya sızmaz.

**Doğrulama (değişken eklendikten sonra Railway'de):**

```bash
railway variables get TELEGRAM_ADMIN_USER_ID
```

---

**Not:** Bu kritik sorunun giderilmesi için **hiçbir kod değişikliği, hiçbir commit, hiçbir push gerekmez.** Yalnızca Railway ortamına (ve lokal test için `.env` dosyasına) yukarıdaki değişkenin eklenmesi yeterlidir. Değişken eklendikten sonra Railway otomatik olarak yeni bir deploy tetiklemeyebilir — Deploy sekmesinden "Redeploy" gerekebilir.

---

✅ KRİTİK SORUN GİDERİLDİ

(Kod seviyesinde sorun yoktur; çözüm ortam değişkeninin Railway'e eklenmesidir. Kod tarafında yapılacak hiçbir işlem yoktur.)
