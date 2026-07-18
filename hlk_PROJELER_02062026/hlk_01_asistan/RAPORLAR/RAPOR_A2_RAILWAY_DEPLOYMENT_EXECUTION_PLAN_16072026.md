# RAPOR A2 — RAILWAY DEPLOYMENT EXECUTION PLAN

**Rapor Türü:** Uygulama Planı (Execution Plan)
**Rapor Tarihi:** 16 Temmuz 2026 · **Revizyon:** R2 — SON RAPOR REVİZYONU
**Proje:** HLK_01_asistan (hlk_PROJELER_02062026/HLK_01_asistan)
**Referans Analiz:** RAPOR_RAILWAY_DEPLOYMENT_ANALIZ_16072026.md (R2)
**Hazırlayan:** AI Geliştirici (Claude Code — MASTER-007 uyumlu)
**Durum:** PLAN — hiçbir adım uygulanmamıştır; her faz Proje Yöneticisi onayı ile başlar

---

## GENEL İLKELER

1. Bu plan yalnızca uygulama sırasını tanımlar. **Hiçbir dosya bu rapor ile oluşturulmamıştır.**
2. Sıra değiştirilemez; her faz bir önceki fazın kabul kriterleri PASS olmadan başlayamaz (AR-002_70 çalışma sırası ilkesiyle uyumlu).
3. Görev ayrımı (MASTER-007): **AI Geliştirici** = dosya oluşturma, git işlemleri, log analizi. **Proje Yöneticisi** = Railway dashboard işlemleri, Telegram production testi, tüm onaylar, TAMAMLANDI işareti (FD-008_7).
4. PASS/FAIL yetkisi yalnızca CEE'dedir (AR-002_60); AI Geliştirici yalnızca kanıt toplar ve raporlar.
5. MASTER-003: Tüm fazlar bitse bile **Runtime + Telegram doğrulaması PASS olmadan görev TAMAMLANDI raporlanamaz.**

---

## FAZ 0 — CEE PRE-CHECK: ANAYASAL GÖREV PAKETİ (CTP)

**Sorumlu:** AI Geliştirici hazırlar → Proje Yöneticisi onaylar

```
╔═══════════════════════════════════════════════════════════════╗
║  CONSTITUTIONAL TASK PACKAGE — RAILWAY DEPLOYMENT             ║
╠═══════════════════════════════════════════════════════════════╣
║  GÖREV TANIMI                                                 ║
║  - 4 deployment dosyası oluştur (FAZ 1)                       ║
║  - Projeyi git'e al ve push et (FAZ 2)                        ║
║  - Railway kurulumu ve deploy (FAZ 3-4)                       ║
║  - Runtime + Telegram doğrulaması (FAZ 5-7)                   ║
║  BAŞARI KRİTERİ: Bölüm FAZ-5/7 kabul kriterleri + CEE PASS   ║
╠═══════════════════════════════════════════════════════════════╣
║  İLGİLİ ANA YASA MADDELERİ                                    ║
║  ☐ MASTER-002/003/011/012  ☐ GC (PID/CEE/Executor param.)    ║
║  ☐ AR-002_57/58/59/60/61/62/70/71/72                          ║
║  ☐ 14_OLAY  ☐ 16_PKG  ☐ 21_CEE  ☐ 22_EEC                     ║
╠═══════════════════════════════════════════════════════════════╣
║  ZORUNLU KONTROLLER                                           ║
║  1. requirements.txt UTF-8 + yalnızca 6 gerçek paket          ║
║  2. .env ve data/ git'e girmeyecek                            ║
║  3. Volume env yönlendirmeleri girilecek                      ║
║  4. numReplicas=1 (Telegram 409 Conflict önlemi)              ║
╠═══════════════════════════════════════════════════════════════╣
║  DEĞİŞTİRİLMEZ ALANLAR                                        ║
║  ❌ ANA YASA dosyaları        ❌ State/Event isimleri          ║
║  ❌ Workflow yapısı           ❌ Çalışan tüm .py kodu          ║
║  ❌ Referans Formlar (.png)   ❌ Medya dosyaları               ║
╠═══════════════════════════════════════════════════════════════╣
║  BEKLENEN ÇIKTI                                               ║
║  Yeni: Procfile, .python-version, railway.json                ║
║  Yeniden: requirements.txt                                    ║
║  Kod değişikliği: YOK                                         ║
╚═══════════════════════════════════════════════════════════════╝
```

**Kabul kriteri:** Proje Yöneticisi CTP'yi onaylar → FAZ 1 başlar.

---

## FAZ 1 — DOSYA OLUŞTURMA SIRASI

**Sorumlu:** AI Geliştirici · **Ön koşul:** FAZ 0 onayı

| Sıra | Dosya | İşlem | İçerik referansı |
|:-:|---|---|---|
| 1.1 | `.python-version` | OLUŞTUR | İçerik: `3.14` (Analiz R2 Bölüm 2 — tek karar) |
| 1.2 | `requirements.txt` | **ÜZERİNE YAZ** (mevcut UTF-16 dosya geçersiz) | Analiz R2 Bölüm 7.1 — 6 paket, UTF-8, BOM'suz |
| 1.3 | `Procfile` | OLUŞTUR | `worker: python main.py` |
| 1.4 | `railway.json` | OLUŞTUR | Analiz R2 Bölüm 7.3 — numReplicas 1, ON_FAILURE |

**Doğrulama (her dosya sonrası):**
- 1.2 için: `file requirements.txt` → "UTF-8 text" olmalı; `pip install --dry-run -r requirements.txt` yerelde hatasız çözümlenmeli.
- EEC karşılığı: her dosya işlemi `EVENT_FILE_CREATED` / `EVENT_FILE_UPDATED` niteliğindedir (OLAY-091/092) — rapora işlenir.

**Kabul kriteri:** 4 dosya mevcut, kod dosyalarına dokunulmamış (`git status` yalnızca beklenen dosyaları göstermeli).

---

## FAZ 2 — GİT

**Sorumlu:** AI Geliştirici (komutlar) + Proje Yöneticisi (onay) · **Ön koşul:** FAZ 1 kabul

| Sıra | Adım | Komut/İşlem |
|:-:|---|---|
| 2.1 | Güvenlik ön adımı (önerilir) | Remote URL'deki gömülü PAT kaldırılır: `git remote set-url origin https://github.com/haluk4365/Antigravity.git` + token rotasyonu (PM, GitHub'da) |
| 2.2 | Kapsam kontrolü | `.env`, `data/`, `logs/`, kök test medyaları hariç tutulacak (Analiz R2 Bölüm 3.2). Kök `.gitignore` `.env` ve `*.log`'u zaten kapsıyor; `data/` için seçici `git add` uygulanır |
| 2.3 | Staged içerik onayı | `git add` sonrası `git status` çıktısı Proje Yöneticisine sunulur — **onay alınmadan commit atılmaz** |
| 2.4 | Commit | Tek commit: kod + ANA YASA + FORMLAR + medya + 4 deployment dosyası |
| 2.5 | Push | `git push origin main` |

**Kabul kriteri:** GitHub'da `hlk_PROJELER_02062026/HLK_01_asistan/` altında `main.py`, `ANA YASA/`, `VİDEO Dosyaları/`, `Procfile` görünür; `.env` ve `data/` görünmez.

---

## FAZ 3 — RAILWAY KURULUMU

**Sorumlu:** Proje Yöneticisi (dashboard) — AI Geliştirici yalnızca rehberlik eder · **Ön koşul:** FAZ 2 kabul

| Sıra | Adım | Değer |
|:-:|---|---|
| 3.1 | Yeni proje / mevcut projeye service ekle | GitHub repo: `haluk4365/Antigravity`, branch `main` |
| 3.2 | **Root Directory** | `hlk_PROJELER_02062026/HLK_01_asistan` |
| 3.3 | Watch Paths (önerilir) | `hlk_PROJELER_02062026/HLK_01_asistan/**` |
| 3.4 | **Volume oluştur ve bağla** | Mount path: `/data` (ZORUNLU — Analiz R2 Bölüm 5) |
| 3.5 | Variables — zorunlu | `TELEGRAM_TOKEN` (production) |
| 3.6 | Variables — Volume yönlendirme | `PID_STATE_DIR=/data`, `GC_CEE_REPORT_DIR=/data/enforcement`, `GC_EXECUTOR_STATE_DIR=/data`, `GC_PACKAGE_STORAGE_DIR=/data/production_packages` |
| 3.7 | Variables — üretim API'leri | `FAL_KEY`, `KIE_AI_API_KEY`, `ELEVENLABS_API_KEY`, `HEDRA_API_KEY`, `HIGGSFIELD_KEY_ID`, `HIGGSFIELD_KEY_SECRET`, `DESCRIPT_API_KEY`, `OPENAI_API_KEY` |
| 3.8 | Variables — opsiyonel | `ENV=production`, `LOG_LEVEL=INFO` (isteğe bağlı) |

**Kritik uyarı:** Yerel test botu ile production botu **farklı token** kullanmalıdır. Railway canlıya alındığında aynı production token ile yerelde bot ÇALIŞTIRILMAMALIDIR (getUpdates 409 Conflict).

**Kabul kriteri:** Variables eksiksiz (Analiz R2 Bölüm 6 kontrol listesi), Volume bağlı, Root Directory doğru.

---

## FAZ 4 — DEPLOY

**Sorumlu:** Railway otomatik (push tetikler) · **İzleyen:** AI Geliştirici + Proje Yöneticisi

| Sıra | Kontrol | Beklenen |
|:-:|---|---|
| 4.1 | Build log | Nixpacks Python 3.14 algılar; `pip install -r requirements.txt` 6 paketi kurar; hata yok |
| 4.2 | Build süresi/boyut | Küçük olmalı (torch vb. yok) — dakikalar içinde |
| 4.3 | Deploy log — boot dizisi | Analiz R2 Bölüm 8.1'deki sıralı log dizisi eksiksiz (gerçek runtime sırası: `BOT STARTED` → TRACE → `🚀 Bot polling başlıyor...` → CONSTITUTIONAL BOOT → `Application started`) |
| 4.4 | `CONSTITUTION_READY` | ✅ görünmeli — `CONSTITUTION_DEGISIKLIK_VAR` görünürse FAIL |
| 4.5 | Polling | Sırasıyla: `========== BOT STARTED ==========` → `🔍 SENDMESSAGE TRACE monkey-patch aktif` → `🚀 Bot polling başlıyor...` → (post_init) CONSTITUTIONAL BOOT SEQUENCE TAMAMLANDI → `Application started` |

**Kırmızı bayraklar:** `ImportError` / `ModuleNotFoundError` (requirements eksik), `ValueError: TELEGRAM_TOKEN` (variable eksik), `UnicodeDecodeError` (requirements kodlaması), pip çözümleme hatası, 18 katmandan azının yüklenmesi (`YÜKLENEMEDİ` → ANA YASA git'e eksik girmiş).

**Kabul kriteri:** 4.1–4.5 tamamı PASS.

---

## FAZ 5 — VALIDATION (Runtime Doğrulama — MASTER-011 / AR-002_62)

**Sorumlu:** AI Geliştirici (log analizi) + Proje Yöneticisi (Telegram komutları)

| Sıra | Doğrulama | Yöntem | PASS kriteri |
|:-:|---|---|---|
| 5.1 | Constitution Cache (FAZ 0 boot) | Railway log | 23 dosya tarandı, hash'lendi (`Cache: .../23 dosya`) |
| 5.2 | 18 Katman Boot | Railway log | `18/18 katman yüklendi` |
| 5.3 | CEE PRE-CHECK | Railway log | `CTP: CEE-CTP-...` üretildi |
| 5.4 | EEC | Railway log | `TASK_STARTED` event'i, PID=`BOT-<pid>` |
| 5.5 | Olay Kayıt Merkezi | `/audit` (Telegram, yönetici) | Boot event'leri listede |
| 5.6 | LAC | `/audit` çıktısı | Panel gerçek Event gösteriyor; Fake Progress YOK (EEC-001) |
| 5.7 | Constitution durumu | `/constitution` | CONSTITUTION_READY + 18 katman manifesti |
| 5.8 | PID Runtime kilidi | Railway log + `/data` | `fcntl.flock` hatasız; `pid_runtime_state.json` `/data` altında oluşur (ilk üretimde) |
| 5.9 | MASTER-011 tablosu | Analiz R2 Bölüm 8.2 doldurulur | Tüm satırlar AKTİF |

**Kabul kriteri:** 9 satır PASS → MASTER-011 tablosu "AKTİF" olarak raporlanır. Herhangi bir PASİF satır = FAZ 7 Rollback değerlendirmesi + CEE FAIL raporu.

---

## FAZ 6 — PRODUCTION TEST (Telegram — MASTER-012)

**Sorumlu:** Proje Yöneticisi (kullanıcı + yönetici rolleri) · **Ön koşul:** FAZ 5 tamamı PASS

| Sıra | Test | PASS kriteri |
|:-:|---|---|
| 6.1 | `/start` → SAHNE-01 | Karşılama videosu oynar, bitince silinir, 8 dil butonu gelir (FD-008_1) |
| 6.2 | Dil seçimi → SAHNE-02 | Seçilen dilde video oynar (git'ten gelen disk medyası) → daktilo balonu → link istenir |
| 6.3 | Ürün linki → doğrulama | Link doğrulanır, araştırma başlar (GK-001_2, WF-001) |
| 6.4 | SAHNE-03…11 | Tüm seçim ekranları; her geçişte EKRAN SİLİNİR |
| 6.5 | SAHNE-12 brief onayı | Tüm seçimler tikli listelenir; EVET → SAHNE-13 |
| 6.6 | Senaryo → ONAY | Senaryo formu gelir; ONAY → yönetici fiyatlandırma |
| 6.7 | Fiyat → ödeme zinciri | Yönetici fiyat formu → kullanıcı teklif formu → ONAY → "ÖDEMEM GERÇEKLEŞTİ" → yönetici "ÖDEMEYİ ONAYLA" (OR-004_10: onay olmadan üretim BAŞLAMAZ) |
| 6.8 | PID | Log: `PID-YYYYMMDD-NNNN` formatı (AR-002_57); `/data/pid_runtime_state.json` güncellendi |
| 6.9 | Üretim + teslim | Görsel → ses → video zinciri; video kullanıcıya Telegram'dan teslim |
| 6.10 | **Kalıcılık testi** | Manuel redeploy → günlük PID sayacı sıfırlanmadan devam ediyor (Volume kanıtı — AR-002_57 tekillik) |

**Kabul kriteri:** 6.1–6.10 PASS → CEE POST-CHECK 6 boyutlu denetim → **CEE PASS** → MASTER-012 formatında nihai rapor:

```
İlgili ANA YASA durumu : DEĞİŞİKLİK YOK
Kod güncelleme durumu  : 4 deployment dosyası (kod değişikliği yok)
Runtime doğrulama      : FAZ 5 sonucu
Hedef Ortam doğrulama  : FAZ 6 sonucu (Railway + Telegram Production)
Nihai Durum            : TAMAMLANDI / TAMAMLANMADI
```

FD-008_7 gereği "Tamamlandı" işareti yalnızca Proje Yöneticisi tarafından verilir; AI Geliştirici yalnızca "Tamamlandı Adayı" önerebilir.

---

## FAZ 7 — ROLLBACK PLANI

**Tetikleyiciler:** FAZ 4 build FAIL · FAZ 5'te PASİF bileşen · FAZ 6'da üretim zinciri kırılması · CEE 3×FAIL (CEE-005 eskalasyonu)

| Senaryo | Rollback aksiyonu | Sorumlu |
|---|---|---|
| Build hatası (pip/sürüm) | Railway'de önceki deployment yok (ilk deploy) → servis durdurulur; hata CEE FAIL raporu ile Executor'a döner (maks. 3 döngü) | PM durdurur, AI Geliştirici düzeltir |
| Boot hatası (`CONSTITUTION_DEGISIKLIK_VAR`, ImportError) | Aynı süreç; kod değişikliği YAPILMAZ, yalnızca deployment dosyası/git kapsamı düzeltilir | AI Geliştirici |
| Sonraki deploylarda regresyon | Railway "Rollback to previous deployment" | PM |
| Git seviyesi geri alma | `git revert <commit>` (history korunur; `git reset --hard` KULLANILMAZ) | AI Geliştirici + PM onayı |
| Production bot çalışamaz durumda | Railway servisi durdurulur; yerel test botu (`ENV=test`, ayrı token) etkilenmez — kullanıcı iletişimi PM kararıyla | PM |
| 3×FAIL | Anayasal Kanıt Raporu (CE-YYYYMMDD-NNNN) üretilir, eskalasyon PM'e (CEE-005/006) | CEE → PM |

**Rollback GEREKMEZ koşulu (önceki A1 raporuyla uyumlu):** Import hatası yok + CONSTITUTION_READY + PID formatı doğru + video üretim/teslim zinciri çalışıyor.

**Not:** Volume rollback'ten etkilenmez; `/data` içeriği (PID state, event kayıtları) deploy sürümünden bağımsız korunur — 14_OLAY "silinemez" ilkesi rollback sırasında da geçerlidir.

---

## FAZ ÖZETİ VE BAĞIMLILIK ZİNCİRİ

```
FAZ 0  CTP Onayı (PM)
  ↓
FAZ 1  Dosyalar: .python-version → requirements.txt → Procfile → railway.json
  ↓
FAZ 2  Git: PAT temizliği → kapsam → staged onay (PM) → commit → push
  ↓
FAZ 3  Railway: Root Directory → Volume(/data) → Variables (PM)
  ↓
FAZ 4  Deploy: build → import boot → BOT STARTED → polling başlangıcı → CONSTITUTIONAL BOOT → CONSTITUTION_READY → Application started
  ↓
FAZ 5  Validation: MASTER-011 tablosu (9 kontrol) → tümü AKTİF
  ↓
FAZ 6  Production Test: E2E 10 adım + kalıcılık testi → CEE POST-CHECK → PASS
  ↓
FAZ 7  (yalnızca gerektiğinde) Rollback / Eskalasyon
  ↓
MASTER-012 Nihai Rapor → PM "Tamamlandı" kararı (FD-008_7)
```

---

**Bu plan uygulanmamıştır.** FAZ 0 CTP onayı verildiğinde FAZ 1'den itibaren her adım tek tek, onaylı şekilde yürütülecektir.

---

## RİSKLER (NİHAİ)

> Bu bölüm, planın mevcut fazlarında zaten tanımlı olan risklerin konsolide listesidir. R2 revizyonunda **yeni risk EKLENMEMİŞTİR**. Detaylı risk tablosu: Analiz R2 Bölüm 14.

| # | Risk | Yakalandığı faz | Aksiyon (planda tanımlı) |
|---|---|---|---|
| RSK-1 | requirements.txt kodlama/paket hatası (`UnicodeDecodeError`, pip çözümleme, `ImportError`/`ModuleNotFoundError`) | FAZ 1 doğrulama + FAZ 4 kırmızı bayraklar | FAZ 1.2 yerel `pip install --dry-run`; FAIL → FAZ 7 (CEE döngüsü, maks. 3) |
| RSK-2 | `ValueError: TELEGRAM_TOKEN` (variable eksik) | FAZ 4 kırmızı bayraklar | FAZ 3.5 zorunlu variable kontrolü |
| RSK-3 | 18 katmandan azının yüklenmesi / `CONSTITUTION_DEGISIKLIK_VAR` (ANA YASA git'e eksik girmiş) | FAZ 4.4 + FAZ 5.1–5.2 | FAZ 2 kabul kriteri: GitHub'da `ANA YASA/` (23 doküman) görünür olmalı |
| RSK-4 | Telegram 409 Conflict (çift instance / yerel + production aynı token) | FAZ 3 kritik uyarı | `numReplicas: 1` + token ayrımı; Railway canlıyken yerelde production token ÇALIŞTIRILMAZ |
| RSK-5 | Volume eksikliği → PID sayacı sıfırlanması / paket ve event kaybı | FAZ 5.8 + FAZ 6.10 kalıcılık testi | FAZ 3.4 Volume ZORUNLU; redeploy sonrası sayaç devamlılığı kanıtlanır |
| RSK-6 | `.env` / `data/` yanlışlıkla git'e girmesi | FAZ 2.2–2.3 | Seçici `git add` + staged içerik PM onayı olmadan commit atılmaz |
| RSK-7 | Üretim zinciri kırılması / CEE 3×FAIL | FAZ 6 + FAZ 7 tetikleyiciler | FAZ 7 rollback senaryoları + Anayasal Kanıt Raporu eskalasyonu |

---

REVISION STATUS : COMPLETED

CONSTITUTION REVIEW STATUS : APPROVED FOR EXECUTION
