# ANA YASA / KOD UYUMLULUK RAPORU

**Konu:** HLK Karar Otoritesi — HLK Runtime ↔ Claude (Production Executor) Görev, Yetki ve Karar Hiyerarşisi
**Tarih:** 18.07.2026
**Dayanak:** MASTER-003 (ANA YASA / KOD Uyumluluk Denetim Prensibi), MASTER-012 (Hedef Çalışma Ortamı Doğrulama Prensibi)

---

## Kural

HLK_01_asistan projesinde tek karar otoritesi HLK Runtime'dır. Bu kural, kullanıcının sistemi başlatan ilk tetikleyici komutunu (örneğin /start) verdiği anda yürürlüğe girer ve oturum tamamen kapanıncaya kadar geçerlidir. Claude yalnızca Production Executor'dur; bağımsız karar verici değildir. Karar gerektiren bütün durumlarda yürütme durdurulur, karar talebi HLK Runtime'a iletilir, HLK Runtime kararını verir, yürütme bu karara göre devam eder. Tereddüt halinde karar üretmek yasaktır.

Bu rol tanımı kalıcı anayasal rol tanımıdır ve aksi HLK Anayasasında açıkça tanımlanmadıkça değiştirilemez.

---

## 1. Güncellenen Anayasa Dosyaları

Mevcut kurallar silinmedi ve değiştirilmedi; tüm maddeler mevcut son madde numaraları tespit edilerek uygun sıra numarası ile eklendi.

| Dosya | Önceki Son Madde | Eklenen Madde | İçerik |
|---|---|---|---|
| `00_HLK_MASTER_RULE_BOOK.md` | MASTER-012 | **MASTER-013** | HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı Prensibi (karar otoritesi, Claude'un rolü, yetki sınırları, karar prensibi, kapsam, kalıcılık) |
| `03_Architecture_Rules.md` | AR-002_80 | **AR-002_81** | HLK Runtime Karar Otoritesi ve Karar Talep Protokolü (DecisionRequest/RuntimeDecision, 8 karar kategorisi, Production Pipeline Karar Yasağı, Sayısal Değer Yasağı) |
| `04_Operational_Rules.md` | OR-004_11 | **OR-004_12** | Üretim Sırasında Karar Talebi Operasyon Kuralı (durdur → talep et → karar → devam et; kullanıcı bilgilendirme sınırı; kayıt zorunluluğu) |
| `06_Module_Rule.md` | MR-0005_6 | **MR-0005_7** | Modül Karar Bağımlılığı Kuralı (tüm modüller + gelecekte eklenecek modüller HLK Runtime hiyerarşik kontrolünde) |
| `09_WORKFLOW_MANIFEST.md` | WF-016 | **WF-017** | Runtime Decision Request workflow'u (AKTİF) |
| `01_Global_Configuration.md` | — | **13 yeni GC parametresi** | Aşağıdaki GC tablosu |

### Yeni GC Parametreleri (01_Global_Configuration.md)

| Parametre | Değer | Devraldığı Hardcoded Değer |
|---|---|---|
| `GC_PRODUCTION_TIMEOUT` | 3600 saniye | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_PRODUCTION_STEP_TIMEOUT` | 300 saniye | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_EXECUTOR_MAX_RETRY` | 3 | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_EXECUTOR_TASK_TIMEOUT` | 300 saniye | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_EXECUTOR_RETRY_DELAY` | 0.5 saniye | `asyncio.sleep(0.5)` (production_executor.py) |
| `GC_EXECUTOR_STATE_DIR` | `data` | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_RUNTIME_HEARTBEAT_INTERVAL` | 60 saniye | Kodda env ile okunuyordu, GC'de kayıtlı değildi |
| `GC_PROVIDER_HTTP_TIMEOUT` | 30 saniye | `timeout=30` (production_pipeline.py, 5 nokta) |
| `GC_PROVIDER_STATUS_TIMEOUT` | 10 saniye | `timeout=10` (production_pipeline.py, 3 nokta) |
| `GC_PROVIDER_POLL_COUNT` | 10 | `range(8)`, `range(10)` (production_pipeline.py) |
| `GC_IMAGE_POLL_INTERVAL` | 3 saniye | `asyncio.sleep(3)` (production_pipeline.py) |
| `GC_VIDEO_POLL_INTERVAL` | 5 saniye | `asyncio.sleep(5)` (production_pipeline.py) |

---

## 2. Etkilenen Dosyalar

**Anayasa:** `00_HLK_MASTER_RULE_BOOK.md`, `01_Global_Configuration.md`, `03_Architecture_Rules.md`, `04_Operational_Rules.md`, `06_Module_Rule.md`, `09_WORKFLOW_MANIFEST.md`

**Kod:** `services/hlk_runtime.py`, `services/production_pipeline.py`, `services/production_runtime.py`, `services/production_executor.py`

**Test:** `test_hlk_karar_otoritesi.py` (yeni), `test_production_runtime.py` (test kusurları düzeltildi)

---

## 3. Uyumsuz Dosyalar (Tespit Edilen Karar Noktaları)

Yeni anayasal role aykırı tespit edilen tüm karar noktaları ve uygulanan devirler:

| # | Dosya / Konum | Aykırı Karar Mekanizması | Uygulanan Düzeltme |
|---|---|---|---|
| 1 | `production_pipeline.py` → `trigger_feedback_loop()` | Retry sayacı karşılaştırması (`retry_count > max_retry`), eskalasyon kararı, yeniden değerlendirme kararı pipeline içindeydi | Kararın tamamı `hlk_runtime.request_decision()` EXECUTION_FAILURE kategorisine devredildi; fonksiyon karar üretmeyen sarmalayıcıya dönüştürüldü |
| 2 | `production_pipeline.py` → `task_image()` | Provider kabul/red kararı, sıradaki provider'a geçiş kararı (`break`/döngü), feedback tetikleme kararı (`if has_image_fallback`) | Her provider denemesi sonrası PROVIDER_RESULT karar talebi; ACCEPT/NEXT_PROVIDER/REPORT_FAILURE kararları HLK Runtime'da; başarısızlıkta EXECUTION_FAILURE talebi (yedek varlığı ham kanıt olarak iletilir) |
| 3 | `production_pipeline.py` → `task_voice()` | Seslendirme metni pipeline'da üretiliyordu (yaratıcı içerik kararı — AR-002_77 ihlali) | CREATIVE_CONTENT karar talebi; metin HLK Runtime kararı ile belirlenir |
| 4 | `production_pipeline.py` → `task_video()` | Provider kabul/red + değiştirme kararları, feedback tetikleme kararı, yeni Decision Packet'i uygulama kararı | PROVIDER_RESULT + EXECUTION_FAILURE karar talepleri; yeni paket yalnızca HLK Runtime RE_EVALUATE kararı ile uygulanır |
| 5 | `production_pipeline.py` → `task_delivery()` | Teslim tipi kararı (video/bilgilendirme) ve kullanıcıya süreç mesajı üretimi ("Uretim Tamamlandi!") | DELIVERY karar talebi; teslim şekli ve mesaj içeriği HLK Runtime kararı; pipeline onaylı metni değiştirmeden iletir |
| 6 | `production_pipeline.py` | Bilinmeyen provider adlarının sessizce atlanması (örtük karar) | AMBIGUITY (tereddüt) karar talebi — MASTER-013 Tereddüt Kuralı uygulanır |
| 7 | `production_pipeline.py` | Hardcoded sayılar: `range(8)`, `range(10)`, `sleep(3)`, `sleep(5)`, `timeout=30`, `timeout=10` | Tamamı GC parametrelerine devredildi (bkz. GC tablosu) |
| 8 | `production_runtime.py` → `run_request()` | COMPLETED/success işaretlemesi yürütme katmanında üretiliyordu | COMPLETION karar talebi — tamamlanma kararı HLK Runtime'da (AR-002_80) |
| 9 | `production_runtime.py` → `_handle_failure()` | Başarısızlık durumunda kullanıcı mesajı yürütme katmanında üretiliyordu | USER_NOTIFICATION karar talebi — bildirim metni HLK Runtime kararı ile |
| 10 | `production_executor.py` | `asyncio.sleep(0.5)` hardcoded retry beklemesi | `GC_EXECUTOR_RETRY_DELAY` parametresine devredildi |

### HLK Runtime'a Eklenen Karar Otoritesi Altyapısı (`services/hlk_runtime.py`)

- `DecisionCategory` — 8 karar kategorisi (PROVIDER_RESULT, PROVIDER_SWITCH, EXECUTION_FAILURE, CREATIVE_CONTENT, DELIVERY, COMPLETION, USER_NOTIFICATION, AMBIGUITY)
- `DecisionRequest` — karar talebi (karar/öneri içermez; yalnızca ham teknik kanıt)
- `RuntimeDecision` — karar kimliği, karar, parametreler ve 15_KARAR_GEREKCESI_STANDARDI.md uyumlu gerekçe
- `HLKRuntime.request_decision()` — yürütme katmanları için TEK karar üretim noktası
- Karar destek bileşenleri (Decision Engine, Escalation Engine) yalnızca HLK Runtime'ın hiyerarşik kontrolü altında çağrılır
- Tüm kararlar PID ile ilişkilendirilerek karar günlüğüne kaydedilir (`get_decisions(pid)`)

---

## 4. Gerekli Düzeltmeler

Tüm gerekli düzeltmeler bu çalışma kapsamında uygulanmıştır. Çalışma sırasında tespit edilen ve düzeltilen mevcut (önceden var olan) runtime hataları:

| # | Hata | Düzeltme |
|---|---|---|
| 1 | `production_pipeline.py`: `requests.urlretrieve` çağrısı — `requests` modülünde `urlretrieve` yoktur; başarı yolunda AttributeError üretip provider'ı başarısız gösteriyordu (3 nokta) | `urllib.request.urlretrieve` ile düzeltildi |
| 2 | `production_runtime.py` → `recover()`: PID bulunamadığında kilit altında `start_production()` çağrısı → **deadlock** (asyncio.Lock reentrant değildir); test koşusunda 300+ saniye askıda kalma ile doğrulandı | PID doğrulaması kilit alınmadan yapılacak şekilde düzeltildi (AR-002_79 süreklilik yolu güvencesi) |
| 3 | `production_executor.py` → `recover()`: Yeni Executor instance'ı ile recovery'de `self._report=None` → AttributeError; ayrıca checkpoint'le tamamlanmış task'lar rapora yansımıyordu | Rapor recovery başında başlatılır; önceden tamamlanmış task'lar `completed_tasks` sayacına eklenir (AR-002_79 Kaldığı Noktadan Devam) |
| 4 | `test_production_runtime.py`: Global/lokal instance karışıklığı (TEST 1/4/13 çökmesi), TEST 6 iptal yarış koşulu, TEST 7/8'in AR-002_80'e aykırı beklentisi (kapanmış üretimin yeniden yürütülmesini bekliyordu) | Test dosyası anayasal davranışa göre düzeltildi; kapanmış üretimin yeniden yürütme reddi doğru davranış olarak doğrulanır |

---

## 5. Runtime Davranış Doğrulaması

| Test Paketi | Kapsam | Sonuç |
|---|---|---|
| `test_hlk_karar_otoritesi.py` (yeni) | MASTER-013 / AR-002_81 / OR-004_12: 8 karar kategorisinin HLK Runtime'da üretildiği, kararların PID ile kaydedildiği, pipeline'ın karar üretmediği (statik doğrulama), Sayısal Değer Yasağı | **19/19 PASS** |
| `test_production_executor.py` | Executor tam akış, retry, checkpoint, recovery, event entegrasyonu | **11/11 PASS** |
| `test_production_runtime.py` | 10 adımlı üretim akışı, timeout, iptal, recovery, çoklu üretim, raporlama | **13/13 PASS** |
| `test_constitution_enforcement.py` | CEE PRE/POST-CHECK zinciri (regresyon) | **11/11 PASS** |
| **TOPLAM** | | **54/54 PASS** |

### MASTER-011 Runtime Aktiflik Raporu — HLK Runtime Karar Otoritesi

| Soru | Sonuç |
|---|---|
| Kod mevcut mu? | ✅ `services/hlk_runtime.py` (DecisionRequest/RuntimeDecision/request_decision) |
| Runtime'da çağrıldı mı? | ✅ 8 kategori için `request_decision()` runtime testinde gerçek çağrılarla çalıştırıldı; pipeline/runtime kod yolları karar taleplerini bu noktaya iletiyor |
| Görevini tamamladı mı? | ✅ Tüm kategorilerde karar + gerekçe üretildi (19/19) |
| Event/kayıt üretti mi? | ✅ Her karar `[HLK Runtime Decision]` log kaydı + PID ilişkili karar günlüğü (`get_decisions`) |
| Sonraki mimari katmanı tetikledi mi? | ✅ EXECUTION_FAILURE kararı Decision Engine / Escalation Engine zincirini HLK Runtime kontrolünde tetikliyor; yürütme katmanları kararları uygulayarak devam ediyor |
| **Runtime sonucu** | **AKTİF** |

---

## 6. MASTER-003 / MASTER-012 Tamamlanma Değerlendirmesi

| Aşama | Durum |
|---|---|
| İlgili ANA YASA kuralları güncellendi | ✅ TAMAMLANDI (MASTER-013, AR-002_81, OR-004_12, MR-0005_7, WF-017, 13 GC parametresi) |
| İlgili kod güncellendi | ✅ TAMAMLANDI (4 servis dosyası; hardcoded karar mekanizması ve hardcoded sayısal değer kalmadı) |
| Runtime davranışı doğrulandı | ✅ TAMAMLANDI (54/54 test PASS — lokal runtime) |
| Hedef Çalışma Ortamı (Telegram/Railway) doğrulaması | ⏳ BEKLİYOR — canlı ortam doğrulaması Proje Yöneticisinin Railway prod botu (@HLK_01_asistan_bot) üzerinde üretim başlatmasıyla yapılabilir; kod değişiklikleri henüz commit/deploy edilmedi |

**Not:** MASTER-012 uyarınca Telegram canlı doğrulaması yapılmadan geliştirme "Hedef Ortamda Doğrulanmış" sayılmaz. Bu rapor, anayasal uyumluluk ve lokal runtime doğrulamasını belgeler; canlı doğrulama için deploy kararı Proje Yöneticisine aittir.

---

## Sonuç

**UYUMLU**

- ANA YASA Güncellendi ✅
- Kod Güncellendi ✅
- Runtime Davranışı Doğrulandı (lokal) ✅
- Karar üretimi münhasıran HLK Runtime'da; production_pipeline.py hiçbir koşulda karar üretmiyor
- Kod içerisinde hardcoded karar mekanizması ve hardcoded sayısal değer kalmadı
