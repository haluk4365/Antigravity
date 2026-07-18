# HLK PRODUCTION REINTEGRATION PLAN (PRP)

**Plan Türü:** Mimari Geçiş Planı (Architectural Transition Plan)
**Hazırlanma Tarihi:** 15 Temmuz 2026
**Referans Raporlar:** RAPOR_LAC_ROOT_CAUSE_ANALIZI_15072026.md, RAPOR_LAC_VERIFICATION_15072026.md
**Anayasal Dayanak:** AR-002_70 (10 Adım), AR-002_57 (PID), AR-002_58 (Package), AR-002_71 (PID Runtime), AR-002_76 (Executor), FEAT-015 (LAC), 16_PRODUCTION_PACKAGE_STANDARD.md

---

## 1. GENEL MİMARİ DEĞERLENDİRME

### 1.1 Mevcut Durum

```
🧪 ÇALIŞAN PRODUCTION AKIŞI (handle_admin_payment_approve → _run_production_pipeline)
   ✅ Video üretiyor — gerçek API çağrıları (Fal.ai, ElevenLabs, Hedra, Higgsfield)
   ❌ Anayasal zincirden tamamen kopuk
   ❌ PID formatı bozuk (HHMMSS yerine NNNN olmalı)
   ❌ Event takibi yok
   ❌ Production Package yok
   ❌ LAC entegrasyonu yok
   ❌ Railway endpoint yok

📜 ANAYASAL PRODUCTION ZİNCİRİ (AR-002_70 — 10 Adım)
   ✅ Kod mevcut (~4.400 satır)
   ✅ Test edilmiş (36 test)
   ❌ Production'da hiç çağrılmıyor
   ❌ _run_production_pipeline ile bağlantısı yok
```

### 1.2 Temel Strateji: Alttan Yukarı (Bottom-Up) Entegrasyon

Mevcut `_run_production_pipeline` fonksiyonu **çalışan bir üretim hattıdır.** Gerçek API çağrılarını yapar, görsel/ses/video üretir ve teslim eder. Bu fonksiyonun silinmesi veya tamamen değiştirilmesi production'ı durdurur.

**Strateji:** Production akışını, en temel modülden başlayarak, anayasal zincire **aşamalı olarak sarmak (wrapping).**

```
Aşama 1:    PID Runtime bağlantısı         ← En temel, en düşük risk
Aşama 2:    EEC + EventRegistry bağlantısı ← Event akışı başlar
Aşama 3:    Production Package bağlantısı  ← Veri kalıcılığı
Aşama 4:    ProductionExecutor sarmalama   ← Task yürütme
Aşama 5:    ProductionRuntime sarmalama    ← Tam anayasal akış
Aşama 6:    CEE entegrasyonu               ← Anayasal denetim
Aşama 7:    LAC bağlantısı                 ← Canlı izleme
Aşama 8:    Railway Web Endpoint           ← Web erişimi
Aşama 9:    "Canlı Takip" Butonu           ← Telegram UX
```

---

## 2. PRODUCTION REINTEGRATION YOL HARİTASI

### AŞAMA 1: PID Runtime Entegrasyonu

**Amaç:** `_run_production_pipeline` içindeki manuel PID üretimini (`website.py:2738`) kaldırıp, `pid_runtime.generate()` ile anayasal PID formatına geçmek.

**Kapsam:**
- `handlers/website.py:2738` — manuel PID satırını değiştir
- `services/pid_runtime.py` — mevcut, değişiklik gerektirmez
- `services/pid_runtime.py:495 generate()` — çağrı eklenecek

**Mevcut Kod (değişecek):**
```python
# website.py:2738 — MEVCUT (anayasaya aykırı)
pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
# Üretilen: PID-20260715-115926 (HHMMSS, 6 hane)
```

**Hedef Davranış:**
```python
# PID Runtime üzerinden anayasal PID
from services.pid_runtime import pid_runtime
record = await pid_runtime.generate()
pid = record.pid
# Üretilen: PID-20260715-0001 (NNNN, 4 haneli sayaç)
```

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| `pid_runtime.generate()` cross-process kilit hatası | PID üretilemez, production başlamaz | DÜŞÜK | `data/pid_runtime.lock` önceden temizlenir | Eski manuel PID satırına geri dön |
| PID format değişikliği mevcut log'ları etkiler | Log aramaları kırılır | DÜŞÜK | Yeni ve eski PID'ler farklı formatta, karışmaz | Yok — yeni format kalıcı |
| İlk çalıştırmada state dosyası yok | PID-20260715-0001'den başlar, normal | YOK | PID Runtime boş state ile başlar | Gerekmez |

**Başarı Kriteri:**
- [ ] `pid_runtime.generate()` başarıyla çağrılır
- [ ] Üretilen PID formatı: `PID-YYYYMMDD-NNNN` (örn: `PID-20260715-0001`)
- [ ] PID `data/pid_runtime_state.json` dosyasına kaydedilir
- [ ] Aynı gün ikinci production'da sayaç artar (0001 → 0002)
- [ ] `data/pid_runtime.lock` cross-process kilit çalışır
- [ ] Production videosu başarıyla üretilir ve teslim edilir

**Rollback Planı:**
1. `website.py:2738` satırını eski manuel PID formatına geri döndür
2. Değişiklik tek satır olduğu için anında geri alınabilir

**Anayasal Dayanak:**
- AR-002_57: PID format standardı (`PID-YYYYMMDD-NNNN`)
- AR-002_71: PID Runtime — tek yetkili PID üreticisi
- AR-002_57: PID Merkeziyet Kuralı — hiçbir modül kendi PID'sini üretemez

---

### AŞAMA 2: EEC + Olay Kayıt Merkezi Entegrasyonu

**Amaç:** Production adımlarını (görsel üretimi, ses üretimi, video üretimi, teslimat) EEC Event'lerine dönüştürüp Olay Kayıt Merkezi'ne kaydetmek.

**Kapsam:**
- `handlers/website.py` — `_run_production_pipeline` içine EEC emit_event() çağrıları ekle
- `services/execution_event_collector.py` — mevcut, değişiklik gerektirmez
- `services/olay_kayit_merkezi.py` — mevcut, değişiklik gerektirmez

**Üretilecek Event'ler:**

| Production Adımı | Event Tipi | Faz |
|-----------------|------------|-----|
| Production başlangıcı | `TASK_STARTED` | PRE_CHECK |
| Görsel üretimi başlangıç | `TASK_CREATED` | EXECUTE |
| Görsel üretimi tamamlandı | `CODE_COMPLETED` | EXECUTE |
| Ses üretimi başlangıç | `TASK_CREATED` | EXECUTE |
| Ses üretimi tamamlandı | `CODE_COMPLETED` | EXECUTE |
| Video üretimi başlangıç | `TASK_CREATED` | EXECUTE |
| Video üretimi tamamlandı | `CODE_COMPLETED` | EXECUTE |
| Teslimat tamamlandı | `RUNTIME_TEST_COMPLETED` | POST_CHECK |

**ÖNEMLİ:** Bu aşamada `execution_event_collector` ve `event_registry` ZATEN `handlers/website.py`'de import edilmiş durumdadır (satır 29-32). Mevcut import'lar kullanılacak, yeni import gerekmez.

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| EEC emit_event() exception'ı production'ı durdurur | Video üretilemez | DÜŞÜK | Tüm emit_event() çağrıları try/except içinde | emit_event() satırlarını kaldır |
| EventRegistry memory kullanımı artar | Memory baskısı | DÜŞÜK | Event'ler memory'de tutulur, session sonu temizlenir | EventRegistry.reset() |
| PID alanı boş geçilir | Event kaydı eksik olur | DÜŞÜK | Aşama 1'den gelen PID kullanılır | Aşama 1 ile birlikte geri alınır |

**Başarı Kriteri:**
- [ ] Her production adımı için EEC event'i üretilir
- [ ] Her event `event_registry.register_from_eec()` ile kaydedilir
- [ ] Tüm event'lerde PID alanı dolu ve doğru formattadır
- [ ] `event_registry.get_by_pid(pid)` ile production event'leri sorgulanabilir
- [ ] `/audit` komutu production event'lerini LAC panelinde gösterir
- [ ] Production videosu başarıyla üretilir ve teslim edilir (mevcut akış bozulmaz)

**Rollback Planı:**
1. `_run_production_pipeline` içindeki EEC/EventRegistry satırlarını kaldır
2. `event_registry.reset()` ile birikmiş event'leri temizle

**Anayasal Dayanak:**
- AR-002_61: EEC — Execution Event Collector mimarisi
- EEC-001: Her Executor işlemi Event'e dönüştürülür
- EEC-002: Her Event PID ile ilişkilendirilir
- 14_OLAY_KAYIT_MERKEZI.md: Tüm event'ler merkezi olarak kaydedilir
- AR-002_22: Constitutional Feedback Loop

---

### AŞAMA 3: Production Package Runtime Entegrasyonu

**Amaç:** Production başlangıcında `package_runtime.create(pid)` ile Production Package oluşturmak, production verilerini (brief, senaryo, maliyet raporu, servis kullanımı) package içine kaydetmek.

**Kapsam:**
- `handlers/website.py` — `_run_production_pipeline` başında package oluşturma
- `services/production_package_runtime.py` — mevcut, değişiklik gerektirmez

**Package Bölümleri (16_PRODUCTION_PACKAGE_STANDARD.md uyumlu):**

| Bölüm | Kaynak Veri | Zorunluluk |
|-------|------------|:----------:|
| PID | `pid_runtime` (Aşama 1) | Zorunlu |
| Production Metadata | timestamp, tür, durum | Zorunlu |
| Brief | `context.user_data` → tüm brief verileri | Zorunlu |
| Senaryo | `context.user_data` → senaryo verileri | Zorunlu |
| Video Parametreleri | format, çözünürlük, süre, platform | Zorunlu |
| Servis Kullanımları | `cost_report` → hangi API kullanıldı | Zorunlu |
| Event Logları | EEC event'leri (Aşama 2) | Zorunlu |
| Karar Gerekçeleri | Yönetici onay kararları | Zorunlu |
| Referans Görseller | Üretilen görsel path'i | Zorunlu |
| Ses Dosyaları | Üretilen ses path'i | İsteğe Bağlı |
| Nihai Video | Üretilen video path'i | Zorunlu |

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| Package oluşturma başarısız | Production durur | DÜŞÜK | try/except, hata log'lanır | Package oluşturma atlanır, production devam eder |
| Package disk kullanımı artar | Disk dolabilir | DÜŞÜK | Archive mekanizması mevcut | Eski package'ler arşivlenir |
| Aynı PID için duplicate package | ValueError fırlatır | DÜŞÜK | Package Runtime duplicate kontrolü yapar | Mevcut package kullanılır |

**Başarı Kriteri:**
- [ ] `package_runtime.create(pid)` başarıyla çağrılır
- [ ] Package `data/production_packages/` altında JSON olarak kaydedilir
- [ ] Brief, senaryo, video parametreleri bölümleri doldurulur
- [ ] Servis kullanım bilgileri kaydedilir
- [ ] Event log'ları package ile ilişkilendirilir
- [ ] Production sonunda package durumu COMPLETED olarak güncellenir
- [ ] `package_runtime.load(pid)` ile package geri yüklenebilir
- [ ] Production videosu başarıyla üretilir ve teslim edilir (mevcut akış bozulmaz)

**Rollback Planı:**
1. Package oluşturma satırları kaldırılır
2. `data/production_packages/` altındaki test package'leri temizlenir
3. Production manuel PID ile devam eder (Aşama 1 ve 2'nin geri alınması gerekmez)

**Anayasal Dayanak:**
- AR-002_58: Production Package Architecture
- 16_PRODUCTION_PACKAGE_STANDARD.md: 21 bölümlü package yapısı
- AR-002_72: Production Package Runtime
- 16_PRODUCTION_PACKAGE_STANDARD.md Bölüm 6: Yaşam Döngüsü

---

### AŞAMA 4: Production Executor Sarmalama

**Amaç:** `_run_production_pipeline` içindeki API çağrılarını (Fal.ai, ElevenLabs, Hedra, Higgsfield) Task Package'lere dönüştürüp `production_executor.execute(pid)` üzerinden yürütmek.

**Kapsam:**
- `handlers/website.py` — mevcut API çağrılarını Task tanımlarına dönüştür
- `services/production_executor.py` — mevcut, `_run_task_handler` genişletilecek

**Task Package Yapısı:**

```json
[
  {
    "task_id": "TASK-{PID}-001",
    "agent": "ImageGenerator",
    "status": "PENDING",
    "pid": "{PID}",
    "handler": "_exec_image_generation",
    "input_data": {"brand": "...", "product_name": "...", "user_id": 123}
  },
  {
    "task_id": "TASK-{PID}-002",
    "agent": "VoiceGenerator",
    "status": "PENDING",
    "pid": "{PID}",
    "handler": "_exec_voice_generation",
    "input_data": {"text": "...", "language": "tr"}
  },
  {
    "task_id": "TASK-{PID}-003",
    "agent": "VideoRenderer",
    "status": "PENDING",
    "pid": "{PID}",
    "handler": "_exec_video_generation",
    "input_data": {"img_path": "...", "voice_path": "...", "duration": 15}
  },
  {
    "task_id": "TASK-{PID}-004",
    "agent": "DeliveryAgent",
    "status": "PENDING",
    "pid": "{PID}",
    "handler": "_exec_delivery",
    "input_data": {"chat_id": 123, "brand": "...", "product_name": "..."}
  }
]
```

**Kritik Tasarım Kararı:** `production_executor._run_task_handler()` metodu (satır 494), şu anda fake task yürütme yapar (sadece "executed" sonucu döner). Bu aşamada, `task.handler` alanına göre gerçek API çağrılarını yapacak şekilde genişletilecektir. Bu, mevcut API çağrılarının ProductionExecutor çatısı altına alınmasını sağlar.

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| Executor task sıralaması yanlış | Görsel olmadan video üretilmeye çalışılır | ORTA | Task'lar task_id sırasına göre çalışır, sıra korunur | Doğrudan API çağrılarına geri dön |
| Task timeout (300s) yetersiz | Hedra/Higgsfield uzun sürer | ORTA | `GC_EXECUTOR_TASK_TIMEOUT` env ile artırılabilir | Timeout değeri yükseltilir |
| Retry mekanizması API kotasını tüketir | API limit aşımı | DÜŞÜK | GC_EXECUTOR_MAX_RETRY=3, API'ler zaten try/except içinde | Retry kapatılır (MAX_RETRY=1) |
| Executor crash olursa checkpoint kaybı | Kaldığı yerden devam edemez | DÜŞÜK | Checkpoint mekanizması mevcut (`_checkpoint_task_completion`) | Manuel restart |

**Başarı Kriteri:**
- [ ] 4 Task Package oluşturulur ve `package_runtime.update_section()` ile kaydedilir
- [ ] `production_executor.execute(pid)` başarıyla çağrılır
- [ ] Task'lar sırayla ve deterministik olarak yürütülür
- [ ] Her task için ExecutionResult üretilir
- [ ] Başarısız task için retry mekanizması çalışır
- [ ] Executor report'u (toplam/başarılı/başarısız task sayısı) doğru
- [ ] Production videosu başarıyla üretilir ve teslim edilir (mevcut akış bozulmaz)

**Rollback Planı:**
1. `_run_production_pipeline` içindeki executor çağrısı kaldırılır
2. Doğrudan API çağrılarına geri dönülür
3. Aşama 1-3 (PID, EEC, Package) korunabilir, executor'dan bağımsızdır

**Anayasal Dayanak:**
- AR-002_76: Production Execution Architecture
- AR-002_76 Adım 3: Task'ları sırayla yürütme
- AR-002_76 FAZ 4: Sonuç kaydetme ve durum güncelleme
- AR-002_47: Task Package Engine Architecture

---

### AŞAMA 5: Production Runtime Sarmalama (Tam Anayasal Akış)

**Amaç:** `production_runtime.start_production()` ile AR-002_70'in 10 adımlık anayasal zincirini tam olarak devreye almak. Bu aşamada `_run_production_pipeline` artık doğrudan çağrılmaz; `production_runtime` tarafından Adım 10'da başlatılır.

**Kapsam:**
- `handlers/website.py:2688` — `asyncio.create_task(_run_production_pipeline(...))` yerine `asyncio.create_task(production_runtime.start_production())` 
- `services/production_runtime.py` — mevcut, production context'i genişletilecek

**Mimari Değişiklik:**

```
MEVCUT:
  handle_admin_payment_approve()
    └─ asyncio.create_task(_run_production_pipeline(chat_id, context, user.id))

HEDEF:
  handle_admin_payment_approve()
    └─ asyncio.create_task(_run_production_flow(chat_id, context, user.id))
         │
         └─ production_runtime.start_production()
              ├─ Adım 1-4: Ön koşul doğrulamaları
              ├─ Adım 5: Production Runtime başlatma
              ├─ Adım 6: CEE PRE-CHECK
              ├─ Adım 7: PID oluşturma (Aşama 1)
              ├─ Adım 8: Package oluşturma (Aşama 3)
              ├─ Adım 9: Task hazırlığı
              └─ Adım 10: production_executor.execute(pid) (Aşama 4)
                   └─ Task handler → API çağrıları (Fal.ai, ElevenLabs, Hedra, Higgsfield)
                        └─ Teslimat
```

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| Ön koşul doğrulaması başarısız | Production başlamaz | ORTA | `_validate_prerequisites` şu an hep başarılı (sadece log) | Manuel override |
| CEE PRE-CHECK FAIL | Production durur | DÜŞÜK | CEE şu an best-effort, FAIL'de bile devam edilebilir | CEE kontrolü atlanır |
| Production timeout (3600s) | Uzun süren API'ler timeout olur | DÜŞÜK | GC_PRODUCTION_TIMEOUT env ile yapılandırılabilir | Timeout artırılır |
| Zincirin herhangi bir adımında hata | Production yarım kalır | ORTA | Her adım try/except içinde, hata log'lanır | Recovery modu (`recover(pid)`) |

**Başarı Kriteri:**
- [ ] `production_runtime.start_production()` başarıyla çağrılır
- [ ] 10 adımın tamamı sırayla yürütülür
- [ ] `ProductionResult.completed_steps == 10`
- [ ] `ProductionResult.success == True`
- [ ] `production_runtime.get_state()` → COMPLETED
- [ ] `production_runtime.get_result()` → tam rapor mevcut
- [ ] CEE PRE-CHECK ve POST-CHECK raporları mevcut
- [ ] Production videosu başarıyla üretilir ve teslim edilir
- [ ] Crash recovery: `production_runtime.recover(pid)` çalışır

**Rollback Planı:**
1. `handle_admin_payment_approve` içindeki `production_runtime.start_production()` çağrısı kaldırılır
2. Eski `_run_production_pipeline(chat_id, context, user.id)` çağrısına geri dönülür
3. Aşama 1-4'teki tüm entegrasyonlar korunabilir

**Anayasal Dayanak:**
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime Architecture (10 Adım)
- AR-002_70: Çalışma Sırası Zorunluluğu
- AR-002_22: Constitutional Feedback Loop
- SE-007_4: STATE_PAYMENT_VERIFICATION → STATE_VIDEO_PRODUCTION geçişi

---

### AŞAMA 6: CEE (Constitution Enforcement Engine) Tam Entegrasyonu

**Amaç:** Aşama 5'te best-effort olarak çalışan CEE entegrasyonunu tam anayasal denetime dönüştürmek. CEE PRE-CHECK FAIL durumunda production'ı durdurmak.

**Kapsam:**
- `services/constitution_enforcement.py` — mevcut, değişiklik gerektirmez
- `services/production_runtime.py:493-525` — `_run_cee_pre_check` ve `_run_cee_post_check` zaten mevcut

**CEE Denetim Boyutları (6 boyut):**

| Boyut | Kontrol | Kaynak |
|-------|---------|--------|
| code_anayasa_check | Kod ↔ Anayasa uyumu | MASTER-003 |
| flow_compliance | Flow Diagram uyumu | FD-008_1 |
| state_compliance | State Engine uyumu | SE-007_4 |
| operational_compliance | Operational Rules uyumu | OR-004 |
| architectural_integrity | Mimari bütünlük | AR-002_70 |
| runtime_behavior | Runtime davranışı | POST_CHECK |

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| CEE PRE-CHECK FAIL → production durur | Kullanıcı videosunu alamaz | DÜŞÜK | Aşama 1-5 başarıyla tamamlanmışsa CEE PASS vermeli | CEE PRE-CHECK sonucu yok sayılır |
| CEE POST-CHECK FAIL | Production tamamlanır ama uyumsuzluk raporu çıkar | ORTA | POST-CHECK FAIL production'ı durdurmaz, sadece raporlar | Manuel inceleme |

**Başarı Kriteri:**
- [ ] CEE PRE-CHECK her production'da çalışır
- [ ] PRE-CHECK PASS → production devam eder
- [ ] PRE-CHECK FAIL → production durur, hata log'lanır
- [ ] CEE POST-CHECK her production sonunda çalışır
- [ ] CEE raporu `data/enforcement/CEE-*.json` olarak kaydedilir
- [ ] 3 FAIL sonrası eskalasyon tetiklenir (CEE-005)

**Rollback Planı:**
1. `production_runtime.py:203-210` — PRE-CHECK FAIL'de production durdurma kodu kaldırılır
2. CEE best-effort moduna geri dönülür (FAIL'de devam et)

**Anayasal Dayanak:**
- CEE-007: Hiçbir görev CEE PRE-CHECK'inden geçmeden başlayamaz
- CEE-005: Eskalasyon mekanizması
- 21_CONSTITUTION_ENFORCEMENT_ENGINE.md
- 15_KARAR_GEREKCESI_STANDARDI.md

---

### AŞAMA 7: LAC (Live Activity Center) Entegrasyonu

**Amaç:** Production sırasında LAC'ın canlı event akışını göstermesini sağlamak. Aşama 2'de EEC event'leri zaten üretilmeye başlandı. Bu aşamada LAC'ın production sırasında aktif olarak event'leri okuması ve kullanıcıya/yöneticiye göstermesi sağlanır.

**Kapsam:**
- `services/lac.py` — mevcut, değişiklik gerektirmez
- `handlers/website.py` — production durum güncellemeleri için LAC refresh çağrıları

**LAC Entegrasyon Noktaları:**

| Nokta | Ne Gösterilir | Tetikleyici |
|-------|--------------|------------|
| `/audit` komutu | Production event akışı (PID bazlı) | Kullanıcı manuel |
| Production başlangıcı | "Üretim başladı" bildirimi | Otomatik |
| Production Durum Butonu | Anlık production durumu | Yeni buton (Aşama 9) |

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| LAC cache stale veri gösterir | Yanlış durum bilgisi | DÜŞÜK | 2 saniye cache TTL, `invalidate_cache()` çağrısı | Manuel refresh |
| Çok sayıda event LAC'ı yavaşlatır | Telegram mesajı uzar | DÜŞÜK | limit=15 ile sınırlı | Limit düşürülür |

**Başarı Kriteri:**
- [ ] `/audit` komutu production event'lerini gösterir
- [ ] LAC panelinde PID, event adı, faz, süre bilgileri görünür
- [ ] Production sırasında `lac.invalidate_cache()` çağrıları yapılır
- [ ] LAC paneli "Henüz kaydedilmiş olay yok" yerine gerçek event'leri gösterir

**Rollback Planı:**
1. LAC refresh çağrıları kaldırılır
2. `/audit` sadece boot event'lerini göstermeye devam eder

**Anayasal Dayanak:**
- FEAT-015: Live Activity Center
- WF-016: LAC Workflow
- AR-002_61: EEC → LAC entegrasyonu

---

### AŞAMA 8: Railway Web Endpoint

**Amaç:** LAC'a tarayıcıdan erişim sağlayacak bir HTTP endpoint oluşturmak. Bu, LAC'ın Telegram dışında da izlenebilmesini sağlar.

**Kapsam:**
- Yeni bir web server modülü (ör: `services/lac_web.py`)
- `main.py` — web server'ı başlatma (polling ile paralel)

**Mimari:**

```
main.py
├── app.run_polling()          ← Telegram bot (mevcut)
└── lac_web.start_server()     ← HTTP server (yeni)
     └── GET /lac/{pid}        → LAC paneli (HTML)
     └── GET /lac/{pid}/json   → LAC verisi (JSON API)
     └── GET /health            → Health check
```

**Teknoloji Seçimi:**
- `aiohttp` — asyncio uyumlu, hafif, Python native

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| Web server polling'i engeller | Bot yanıt vermez | DÜŞÜK | aiohttp aynı event loop'ta çalışır | Web server kapatılır |
| Railway port çakışması | Deploy başarısız | ORTA | `PORT` env değişkeni kullanılır | Port değiştirilir |
| Yetkisiz erişim | LAC verisi herkese açık olur | ORTA | Basit token auth veya Railway internal network | Auth eklenir |
| Deployment yok (Procfile vb.) | Railway deploy edilemez | ORTA | Gerekli deployment dosyaları oluşturulur | Manuel deploy |

**Başarı Kriteri:**
- [ ] `GET /health` → 200 OK
- [ ] `GET /lac/{pid}` → HTML LAC paneli
- [ ] `GET /lac/{pid}/json` → JSON event listesi
- [ ] Railway'de deploy edilebilir
- [ ] Tarayıcıdan erişilebilir
- [ ] Bot polling'i ile aynı anda çalışır

**Rollback Planı:**
1. Web server kodu kaldırılır
2. `main.py`'deki web server başlatma kaldırılır
3. LAC'a sadece Telegram `/audit` ile erişilir

**Anayasal Dayanak:**
- FEAT-015: LAC — çoklu erişim kanalı
- WF-016: LAC Workflow

---

### AŞAMA 9: Telegram "Canlı Takip" Butonu

**Amaç:** Production başladığında kullanıcıya ve yöneticiye production durumunu takip edebilecekleri bir buton sunmak.

**Kapsam:**
- `handlers/website.py` — production bilgilendirme mesajına buton ekleme

**Buton Davranışı:**

| Kullanıcı | Buton | Aksiyon |
|-----------|-------|---------|
| Kullanıcı | "🔍 Canlı Takip" | LAC panelini Telegram mesajı olarak gösterir |
| Yönetici | "🔍 Canlı Takip" | LAC panelini Telegram mesajı olarak gösterir |
| Yönetici | "🌐 Web'de Aç" | Railway LAC URL'sine yönlendirir (Aşama 8 sonrası) |

**Risk Değerlendirmesi:**

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|---------|--------|-----------|
| Buton LAC boş gösterir | Kullanıcı "çalışmıyor" der | DÜŞÜK | Aşama 2 ile event'ler zaten üretiliyor | Buton kaldırılır |
| Web URL'si yanlış/ölü | Kullanıcı 404 alır | DÜŞÜK | Aşama 8 öncesi sadece Telegram butonu gösterilir | URL düzeltilir |

**Başarı Kriteri:**
- [ ] Production bilgilendirme mesajında "Canlı Takip" butonu görünür
- [ ] Butona tıklandığında LAC paneli Telegram mesajı olarak gelir
- [ ] Panel PID, durum, event listesini içerir
- [ ] Aşama 8 tamamlandıysa "Web'de Aç" butonu da görünür

**Rollback Planı:**
1. Buton satırı kaldırılır
2. Eski düz bilgilendirme mesajına geri dönülür

**Anayasal Dayanak:**
- FD-008_1: STATE_VIDEO_PRODUCTION UX akışı
- FEAT-015: LAC kullanıcı erişimi

---

## 3. HER AŞAMANIN ÖZET TABLOSU

| Aşama | Adı | Değişen Dosya | Risk Seviyesi | Süre Tahmini | Bağımlılık |
|:-----:|-----|--------------|:------------:|:-----------:|-----------|
| 1 | PID Runtime | `website.py:2738` | 🟢 DÜŞÜK | 1 saat | Yok |
| 2 | EEC + EventRegistry | `website.py` (emit_event ekleme) | 🟢 DÜŞÜK | 2 saat | Aşama 1 |
| 3 | Production Package | `website.py` (package create) | 🟡 ORTA | 3 saat | Aşama 1 |
| 4 | Production Executor | `website.py` + `production_executor.py` | 🟡 ORTA | 5 saat | Aşama 1, 3 |
| 5 | Production Runtime | `website.py:2688` + `production_runtime.py` | 🔴 YÜKSEK | 4 saat | Aşama 1-4 |
| 6 | CEE Tam Entegrasyon | `production_runtime.py` | 🟡 ORTA | 2 saat | Aşama 5 |
| 7 | LAC Entegrasyonu | `lac.py` + `website.py` | 🟢 DÜŞÜK | 1 saat | Aşama 2 |
| 8 | Railway Web Endpoint | Yeni `lac_web.py` + `main.py` | 🔴 YÜKSEK | 6 saat | Aşama 7 |
| 9 | Telegram Butonu | `website.py` | 🟢 DÜŞÜK | 30 dk | Aşama 7 |

---

## 4. TEST PLANI

### 4.1 Aşama 1 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T1.1 | PID format doğrulama | `PID-YYYYMMDD-NNNN` formatı | `validate_pid_static(pid).is_valid == True` |
| T1.2 | PID tekillik | Aynı gün iki production → farklı PID | `pid1 != pid2`, sayaç artar |
| T1.3 | PID persistence | Restart sonrası sayaç devam eder | `data/pid_runtime_state.json` güncellenir |
| T1.4 | Cross-process kilit | İki worker aynı anda generate() | Sadece biri başarılı, diğeri bekler |
| T1.5 | Production çalışıyor mu? | Video üretilir ve teslim edilir | Kullanıcı videosunu alır |

### 4.2 Aşama 2 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T2.1 | Event üretimi | Her adım için event oluşur | `len(execution_event_collector._events) > 0` |
| T2.2 | EventRegistry kaydı | Event'ler kaydedilir | `event_registry.get_by_pid(pid)` dolu |
| T2.3 | PID alanı | Tüm event'lerde PID dolu | Her event'te `pid == expected_pid` |
| T2.4 | `/audit` komutu | Production event'leri görünür | LAC panelinde event listesi |
| T2.5 | Production çalışıyor mu? | Video üretilir ve teslim edilir | Kullanıcı videosunu alır |

### 4.3 Aşama 3 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T3.1 | Package oluşturma | `package_runtime.create(pid)` başarılı | Package JSON dosyası mevcut |
| T3.2 | Brief bölümü | Brief verileri package'te | `pkg.brief` dolu |
| T3.3 | Servis kullanımı | Hangi API'ler kullanıldı | `pkg.service_usage` dolu |
| T3.4 | Package tamamlanma | Production sonunda COMPLETED | `pkg.metadata.status == "COMPLETED"` |
| T3.5 | Production çalışıyor mu? | Video üretilir ve teslim edilir | Kullanıcı videosunu alır |

### 4.4 Aşama 4 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T4.1 | Task oluşturma | 4 task package hazırlanır | `len(tasks) == 4` |
| T4.2 | Task sıralaması | Deterministik sırada çalışır | task_id sırası korunur |
| T4.3 | Retry mekanizması | Başarısız task tekrar denenir | `result.attempt > 1` |
| T4.4 | Executor report | Doğru task sayıları | `completed + failed == total` |
| T4.5 | Production çalışıyor mu? | Video üretilir ve teslim edilir | Kullanıcı videosunu alır |

### 4.5 Aşama 5 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T5.1 | 10 adım tamamlanma | Tüm adımlar sırayla | `completed_steps == 10` |
| T5.2 | ProductionResult | success=True | `result.success == True` |
| T5.3 | CEE entegrasyonu | PRE-CHECK ve POST-CHECK çalışır | `result.pre_check_report` dolu |
| T5.4 | Recovery | `recover(pid)` kaldığı yerden devam | Recovery sonrası COMPLETED |
| T5.5 | Production çalışıyor mu? | Video üretilir ve teslim edilir | Kullanıcı videosunu alır |

### 4.6 Aşama 6 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T6.1 | PRE-CHECK PASS | Production devam eder | Normal akış |
| T6.2 | PRE-CHECK FAIL simülasyonu | Production durur | `result.state == "FAILED"` |
| T6.3 | Eskalasyon | 3 FAIL → CEE-005 | `cee.needs_escalation() == True` |
| T6.4 | POST-CHECK kaydı | Rapor JSON olarak kaydedilir | `data/enforcement/CEE-*.json` mevcut |

### 4.7 Aşama 7 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T7.1 | `/audit` production event'leri | Event listesi görünür | Panel boş değil |
| T7.2 | PID filtreleme | Belirli PID'nin event'leri | `get_lac_feed(pid=pid)` doğru |
| T7.3 | Cache invalidation | Yeni event sonrası panel güncellenir | `lac.invalidate_cache()` çalışır |

### 4.8 Aşama 8 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T8.1 | Health check | `GET /health` → 200 | HTTP 200 |
| T8.2 | LAC HTML paneli | `GET /lac/{pid}` → HTML | Sayfa render edilir |
| T8.3 | LAC JSON API | `GET /lac/{pid}/json` → JSON | Geçerli JSON |
| T8.4 | Railway deploy | Railway'de çalışır | Deploy başarılı |
| T8.5 | Bot + Web aynı anda | Polling ve HTTP birlikte çalışır | İkisi de yanıt verir |

### 4.9 Aşama 9 Testleri

| Test | Amaç | Beklenen Sonuç | Başarı Kriteri |
|------|------|---------------|---------------|
| T9.1 | Buton görünürlüğü | "Canlı Takip" butonu mesajda | Buton render edilir |
| T9.2 | Buton tıklama | LAC paneli Telegram'da gösterilir | HTML mesaj gelir |
| T9.3 | "Web'de Aç" butonu | Doğru URL'ye yönlendirir | URL açılır |

---

## 5. ANAYASAL UYUM ANALİZİ

### 5.1 MASTER Kuralları

| Kural | Gereklilik | Entegrasyon Sonrası Durum |
|-------|-----------|--------------------------|
| **MASTER-001** | Analiz Zorunluluğu — önce anayasa, sonra kod | ✅ Her aşama ilgili AR/SE/FD referanslarıyla başlar |
| **MASTER-003** | Kod ↔ Anayasa ↔ Runtime uyumu | ✅ Aşama 5 ile tam uyum sağlanır |
| **MASTER-004** | Karar Mekanizması — CEE denetimi | ✅ Aşama 6 ile CEE PRE/POST-CHECK aktif |
| **MASTER-009** | Flow Diagram Otoritesi | ✅ FD-008_1 STATE_VIDEO_PRODUCTION akışı referans alınır |

### 5.2 GC (Global Configuration)

| Parametre | Mevcut Değer | Aşama |
|-----------|-------------|:-----:|
| `GC_PID_PREFIX` | `PID` | Aşama 1 |
| `GC_PID_SEQUENCE_LENGTH` | `4` | Aşama 1 |
| `GC_PRODUCTION_TIMEOUT` | `3600.0` | Aşama 5 |
| `GC_EXECUTOR_MAX_RETRY` | `3` | Aşama 4 |
| `GC_EXECUTOR_TASK_TIMEOUT` | `300.0` | Aşama 4 |

### 5.3 AR (Architecture Rules)

| Kural | Açıklama | Karşılayan Aşama |
|-------|----------|:---------------:|
| **AR-002_57** | PID Mimari Standardı | Aşama 1 |
| **AR-002_58** | Production Package Mimarisi | Aşama 3 |
| **AR-002_70** | STATE_VIDEO_PRODUCTION Runtime (10 Adım) | Aşama 5 |
| **AR-002_71** | PID Runtime Architecture | Aşama 1 |
| **AR-002_72** | Production Package Runtime | Aşama 3 |
| **AR-002_76** | Production Execution Architecture | Aşama 4 |
| **AR-002_22** | Constitutional Feedback Loop | Aşama 2, 6 |
| **AR-002_60** | Constitution Enforcement Engine | Aşama 6 |
| **AR-002_61** | Execution Event Collector | Aşama 2 |

### 5.4 SE (State Engine)

| Kural | Gereklilik | Karşılayan Aşama |
|-------|-----------|:---------------:|
| **SE-007_3** | STATE_VIDEO_PRODUCTION tanımı | Aşama 5 |
| **SE-007_4** | STATE_PAYMENT_VERIFICATION → STATE_VIDEO_PRODUCTION geçişi | Aşama 5 |
| **SE-007_5** | EVENT_PAYMENT_APPROVED tetikleme | Mevcut (`website.py:2650`) |

### 5.5 FD (Flow Diagram)

| Referans | Gereklilik | Karşılayan Aşama |
|----------|-----------|:---------------:|
| **FD-008_1** | STATE_VIDEO_PRODUCTION UX akışı | Aşama 9 |

### 5.6 OR (Operational Rules)

| Kural | Gereklilik | Karşılayan Aşama |
|-------|-----------|:---------------:|
| **OR-004_9** | Oturum kapatma | Mevcut (timeout) |
| **OR-004_10** | Ödeme doğrulama | Mevcut |

### 5.7 QR (Quality Rules) ve MR (Module Rules)

| Kural | Gereklilik | Karşılayan Aşama |
|-------|-----------|:---------------:|
| **QR-004** | Kalite kontrol | Aşama 4 (Executor report) |
| **MR** | Modül bağımsızlığı | Tüm aşamalar (her modül kendi sorumluluğunda) |

---

## 6. NİHAİ YOL HARİTASI

### Önem Sırasına Göre Entegrasyon:

```
AŞAMA 1: PID Runtime                    🟢 EN DÜŞÜK RİSK
  └─ Tek satır değişiklik, anında rollback
  └─ AR-002_57 PID format ihlalini giderir
  └─ Süre: 1 saat

AŞAMA 2: EEC + EventRegistry            🟢 DÜŞÜK RİSK
  └─ Event akışını başlatır, LAC için veri üretir
  └─ Mevcut import'ları kullanır, yeni bağımlılık yok
  └─ Süre: 2 saat

AŞAMA 3: Production Package             🟡 ORTA RİSK
  └─ Production verilerini kalıcı hale getirir
  └─ Package oluşturma hatası production'ı durdurmaz
  └─ Süre: 3 saat

AŞAMA 4: Production Executor            🟡 ORTA RİSK
  └─ Task yürütme çatısı, retry, checkpoint
  └─ Mevcut API çağrılarını task handler'a taşır
  └─ Süre: 5 saat

AŞAMA 5: Production Runtime             🔴 YÜKSEK RİSK
  └─ 10 adımlık tam anayasal zincir
  └─ En kritik aşama — tüm alt sistemleri bağlar
  └─ Süre: 4 saat

AŞAMA 6: CEE Tam Entegrasyon            🟡 ORTA RİSK
  └─ Anayasal denetim aktif
  └─ PRE-CHECK FAIL production'ı durdurur
  └─ Süre: 2 saat

AŞAMA 7: LAC Entegrasyonu               🟢 DÜŞÜK RİSK
  └─ Canlı event izleme
  └─ Panel ve cache yönetimi
  └─ Süre: 1 saat

AŞAMA 8: Railway Web Endpoint           🔴 YÜKSEK RİSK
  └─ Yeni altyapı (HTTP server)
  └─ Deployment değişikliği
  └─ Süre: 6 saat

AŞAMA 9: Telegram Butonu                🟢 DÜŞÜK RİSK
  └─ UX iyileştirmesi
  └─ Süre: 30 dakika
```

### Kritik Yol (Critical Path):

```
Aşama 1 → Aşama 2 → Aşama 3 → Aşama 4 → Aşama 5 → Aşama 6
              │                                    │
              └──→ Aşama 7 → Aşama 8               │
                         └──→ Aşama 9               │
                                                    │
         (Aşama 7-9, Aşama 2'den sonra paralel yapılabilir)
```

### Toplam Süre Tahmini: ~25 saat (3-4 iş günü)

---

## 7. NİHAİ DURUM

Plan tamamlandığında production zinciri şu hale gelecektir:

```
✅ STATE_VIDEO_PRODUCTION girişi (SE-007_4)
✅ ProductionRuntime.start_production() (AR-002_70 — 10 Adım)
   ├── ✅ Adım 1-4: Ön koşul doğrulamaları
   ├── ✅ Adım 5: Production Runtime başlatma
   ├── ✅ Adım 6: Production Event (EEC)
   ├── ✅ Adım 7: PID oluşturma (AR-002_57, PID-YYYYMMDD-NNNN)
   ├── ✅ Adım 8: Production Package (AR-002_58)
   ├── ✅ Adım 9: Task Package hazırlığı
   └── ✅ Adım 10: ProductionExecutor.execute(pid) (AR-002_76)
        ├── ✅ Task 1: Görsel üretimi (Fal.ai/Kie AI)
        ├── ✅ Task 2: Ses üretimi (ElevenLabs)
        ├── ✅ Task 3: Video üretimi (Hedra/Higgsfield)
        └── ✅ Task 4: Teslimat
✅ CEE PRE-CHECK + POST-CHECK (AR-002_60)
✅ EEC Event akışı (AR-002_61)
✅ EventRegistry kayıtları (14_OLAY_KAYIT_MERKEZI.md)
✅ LAC canlı izleme (FEAT-015)
✅ Railway Web Endpoint (HTTP)
✅ Telegram "Canlı Takip" butonu (FD-008_1)
```

---

**Planı Hazırlayan:** Claude Code (DeepSeek V4 Pro)
**Hazırlanma Tarihi:** 15 Temmuz 2026
**Anayasal Referans:** AR-002_70, AR-002_57, AR-002_58, AR-002_71, AR-002_72, AR-002_76, AR-002_22, AR-002_60, AR-002_61
**Risk Seviyesi:** Kontrollü (her aşama bağımsız rollback'li)
