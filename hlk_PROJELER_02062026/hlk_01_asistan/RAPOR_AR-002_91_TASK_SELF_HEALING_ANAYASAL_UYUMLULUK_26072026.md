# AR-002_91 — TASK SELF-HEALING ARCHITECTURE
## ANAYASAL UYUMLULUK RAPORU

**Tarih:** 26.07.2026
**Hazırlayan:** HLK Runtime (Claude)
**Referans:** AR-002_82 / AR-002_83 / AR-002_87 / AR-002_90 / MASTER-013
**Yeni Madde No:** **AR-002_91**

---

## 1. ÇAKIŞMA ANALİZİ

### 1.1 Mevcut Maddelerle Pozisyon İlişkisi

```
┌──────────────────────────────────────────────────────────────────┐
│ MASTER-013: HLK Karar Otoritesi                                  │
│   "Tüm kararlar HLK Runtime tarafından üretilir"                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ AR-002_82: MISSION PERSISTENCE                                   │
│   "İlk başarısızlıkta görevi sonlandırma"                       │
│   8 adımlı başarısızlık değerlendirmesi                          │
│   Kapsam: HLK Runtime seviyesinde GÖREV ISRARI                   │
│   Karar: Recovery'ye GEÇİLSİN Mİ?                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
          ╔══════════════════╧══════════════════════════╗
          ║  AR-002_91: TASK SELF-HEALING (YENİ)       ║
          ║  "Kendini iyileştir, sonra yükselt"        ║
          ║  10 adımlı self-healing workflow            ║
          ║  Kapsam: Task seviyesinde KENDI KENDINE     ║
          ║  TAMIR — eksik package/resource/event/      ║
          ║  artifact oluşturma                          ║
          ╚══════════════════╦══════════════════════════╝
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ AR-002_83: RECOVERY POLICY                                       │
│   "Sistematik, tutarlı, anayasal karar süreci"                  │
│   Retry + Provider + Model + Prompt + Queue + Escalation         │
│   Kapsam: HLK Runtime seviyesinde ÜST POLİTİKA                   │
│   Karar: HANGİ recovery stratejisi uygulanacak?                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ AR-002_87: EXTERNAL RESOURCE RECOVERY                            │
│   "Tüm harici kaynaklar aynı recovery yaşam döngüsü"            │
│   11 aşamalı recovery yaşam döngüsü                               │
│   Kapsam: Provider / API / AI Model / Agent / Harici Araç        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ AR-002_90: PRODUCTION GATE                                       │
│   "WF-001..WF-007 COMPLETED olmadan üretim başlamaz"            │
│   Pre-production doğrulama kapısı                                 │
│   Max 3 recovery döngüsü → Eskalasyon                             │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Görev Ayrımı Tablosu

| Katman | Sorumluluk | Karar Verir mi? | Nerede Çalışır? |
|---|---|---|---|
| **AR-002_82** Mission Persistence | Görevden vazgeçmemek | EVET — Recovery'ye geçiş kararı | HLK Runtime |
| **AR-002_91** Task Self-Healing | Eksik bağımlılıkları gidermek | HAYIR — Yalnızca tamir eder, karar üretmez | Task / Executor |
| **AR-002_83** Recovery Policy | Sistematik kurtarma stratejisi | EVET — Hangi strateji uygulanacak | HLK Runtime |
| **AR-002_87** External Resource Recovery | Harici kaynak kurtarma | HAYIR — Protokol uygular | Provider katmanı |
| **AR-002_90** Production Gate | Üretim öncesi doğrulama | EVET — Kapı açık/kapalı | Production Runtime |

### 1.3 Çakışma Tespiti

| Kontrol | Sonuç |
|---|---|
| AR-002_82 ile çakışma | **YOK** — AR-002_82 görev seviyesinde ısrar eder; AR-002_91 task seviyesinde kendi kendini tamir eder |
| AR-002_83 ile çakışma | **YOK** — AR-002_83 Self-Healing başarısız olduğunda devreye girer; üst politika katmanıdır |
| AR-002_87 ile çakışma | **YOK** — AR-002_87 harici kaynaklara özeldir; AR-002_91 task'ın kendi iç bağımlılıkları içindir |
| AR-002_90 ile çakışma | **YOK** — AR-002_90 pre-production gate; AR-002_91 task execution sırasında çalışır |
| Aynı görevi üstlenme | **YOK** — Mevcut hiçbir madde "Task kendi eksik Package'ını yeniden oluştursun" demez |
| Tekrar eden mekanizma | **YOK** — Mevcut maddeler task-seviyesinde self-healing tanımlamaz |

### 1.4 Eksik Katman Tespiti

Mevcut anayasal mimaride şu kopukluk mevcuttur:

```
Task başarısız olur
       │
       ▼
AR-002_82: "Vazgeçme, değerlendir"  ← Görev seviyesinde
       │
       ▼
       │  ❌ KOPUKLUK: Task kendi başına ne yapabilir?
       │     - Eksik Package'ı yeniden oluşturabilir mi?
       │     - Eksik Resource'u yeniden oluşturabilir mi?
       │     - Event bekleyebilir mi?
       │     - Artifact bekleyebilir mi?
       │     → TANIMSIZ
       │
       ▼
AR-002_83: "Recovery Policy uygula"  ← Sistem seviyesinde
```

**AR-002_91 bu kopukluğu giderir.**

---

## 2. ETKİLENEN ARCHITECTURE RULES

| Madde | Etki | Açıklama |
|---|---|---|
| **AR-002_82** | Referans | Self-Healing başarısız olursa → Mission Persistence değerlendirmesi |
| **AR-002_83** | Referans | Self-Healing başarısız olursa → Recovery Policy'ye geçiş |
| **AR-002_87** | Referans | Provider Self-Healing → AR-002_87 yaşam döngüsüne uygun |
| **AR-002_90** | Referans | Production Gate açılmadan önce tüm WF'ler Self-Healing'den geçer |
| **AR-002_76** | Değişiklik | `_execute_task` — Task başarısız olduğunda önce Self-Healing uygula |
| **AR-002_70** | Değişiklik | `_run_reproduction` — START_AS_NEW'de task_packages boşsa Self-Healing ile oluştur |
| **AR-002_79** | Referans | Self-Healing → Recovery → Üretim Sürekliliği zinciri |
| **AR-002_81** | Değişiklik | Yeni DecisionCategory: `SELF_HEALING` — Self-Healing karar kaydı |
| **AR-002_22** | Referans | Self-Healing başarısız → Feedback Loop → Re-evaluation |

---

## 3. ETKİLENEN GLOBAL CONFIGURATION

### 3.1 Mevcut GC Parametreleri (KORUNACAK)

| Parametre | Değer | Açıklama |
|---|---|---|
| `GC_EXECUTOR_MAX_RETRY` | 3 | Task başına maksimum deneme |
| `GC_EXECUTOR_RETRY_DELAY` | 0.5s | Denemeler arası bekleme |
| `GC_MAX_RE_EVALUATION_COUNT` | 3 | Maksimum yeniden değerlendirme |
| `GC_PROVIDER_POLL_COUNT` | 10 | Provider durum sorgusu sayısı |
| `GC_IMAGE_POLL_INTERVAL` | 3s | Görsel poll aralığı |
| `GC_VIDEO_POLL_INTERVAL` | 5s | Video poll aralığı |
| `GC_PRODUCTION_TIMEOUT` | 3600s | Toplam üretim timeout |
| `GC_PRODUCTION_STEP_TIMEOUT` | 300s | Adım timeout |
| `GC_RUNTIME_HEARTBEAT_INTERVAL` | 60s | Heartbeat aralığı |

### 3.2 Yeni GC Parametreleri (EKLENECEK)

| Parametre | Önerilen Değer | Açıklama | İlişkili Mevcut GC |
|---|---|---|---|
| `GC_TASK_SELF_HEAL_MAX_COUNT` | 3 | Self-Healing maksimum deneme sayısı | `GC_EXECUTOR_MAX_RETRY` |
| `GC_TASK_SELF_HEAL_DELAY` | 2.0s | Self-Healing adımları arası bekleme | `GC_EXECUTOR_RETRY_DELAY` |
| `GC_PACKAGE_REBUILD_MAX_COUNT` | 2 | Package yeniden oluşturma denemesi | `GC_MAX_RE_EVALUATION_COUNT` |
| `GC_PACKAGE_REBUILD_DELAY` | 1.0s | Package rebuild bekleme | — |
| `GC_RESOURCE_RECOVERY_DELAY` | 3.0s | Resource kurtarma bekleme | — |
| `GC_EVENT_RECOVERY_DELAY` | 1.0s | Event oluşmasını bekleme | — |
| `GC_EVENT_RECOVERY_MAX_COUNT` | 5 | Event bekleme maksimum deneme | `GC_PROVIDER_POLL_COUNT` |
| `GC_FILE_RECOVERY_DELAY` | 0.5s | Dosya oluşmasını bekleme | — |
| `GC_FILE_RECOVERY_MAX_COUNT` | 10 | Dosya bekleme maksimum deneme | — |
| `GC_ARTIFACT_RECOVERY_DELAY` | 2.0s | Artifact doğrulama bekleme | `GC_IMAGE_POLL_INTERVAL` |
| `GC_ARTIFACT_RECOVERY_MAX_COUNT` | 5 | Artifact bekleme maksimum deneme | `GC_PROVIDER_POLL_COUNT` |

### 3.3 GC Uyumluluk Matrisi

```
GC_TASK_SELF_HEAL_MAX_COUNT ≤ GC_EXECUTOR_MAX_RETRY
GC_TASK_SELF_HEAL_DELAY ≥ GC_EXECUTOR_RETRY_DELAY
GC_PACKAGE_REBUILD_MAX_COUNT ≤ GC_MAX_RE_EVALUATION_COUNT
GC_EVENT_RECOVERY_MAX_COUNT ≤ GC_PROVIDER_POLL_COUNT
GC_ARTIFACT_RECOVERY_MAX_COUNT ≤ GC_PROVIDER_POLL_COUNT
```

---

## 4. ETKİLENEN RUNTIME

### 4.1 Production Runtime (`services/production_runtime.py`)

| Metod | Satır | Değişiklik |
|---|---|---|
| `_run_reproduction` | 1032-1181 | `prepare_for_reproduction` ile `executor.recover` arasına Self-Healing task oluşturma adımı ekle |
| `_run_managed` | 2098-2114 | Self-Healing Gateway — task oluşturma öncesi eksik kontrolü |
| `_handle_failure` | 2284 | Self-Healing uygulanmadan FAILED kararı alınmışsa CEE Violation kaydı |
| `_handle_reproduction_failure` | 1376 | Aynı CEE kontrolü |

### 4.2 Production Executor (`services/production_executor.py`)

| Metod | Satır | Değişiklik |
|---|---|---|
| `_execute_task` | 434-559 | Retry öncesi Self-Healing adımı ekle |
| `_run_task_handler` | 561-632 | Boş task/eksik kaynak kontrolü — `None`/`[]` erken dönüş yerine Self-Healing |
| `_load_task_packages` | 403-428 | `return []` yerine Self-Healing ile package rebuild dene |
| `recover` | 826-933 | Boş `pending_tasks` durumunda Self-Healing uygula |

### 4.3 Production Package Runtime (`services/production_package_runtime.py`)

| Metod | Satır | Değişiklik |
|---|---|---|
| `prepare_for_reproduction` | 906-1049 | START_AS_NEW/REPLAY için boş task_packages → varsayılan task'ları oluştur |

---

## 5. ETKİLENEN WORKFLOW

| Workflow | Etki |
|---|---|
| **WF-002** Background Research | `research_results`/`refs` eksikse Self-Healing ile yeniden oluştur |
| **WF-005** Scenario Generation | `scenario` eksikse Self-Healing ile yeniden oluştur |
| **WF-007** Pricing | `decision_history` eksikse Self-Healing ile yeniden değerlendir |
| **WF-008** Video Production | Tüm task'lar Self-Healing zincirinden geçer |
| **WF-010** Delivery | `delivery_info` eksikse Self-Healing ile yeniden dene |

---

## 6. ETKİLENEN TASK

| Task Agent | Self-Healing Davranışı |
|---|---|
| **ImageGenerator** | Eksik `research_results`/`refs` → yeniden araştırma başlat. Eksik `img_path` → yeniden üret. |
| **VoiceGenerator** | Eksik `voice_script` → HLK Runtime'dan CREATIVE_CONTENT kararı al. Eksik `voice_path` → yeniden üret. |
| **VideoRenderer** | Eksik `img_path`/`voice_path` → önceki task'ların tamamlanmasını bekle. Eksik `video_path` → yeniden render. |
| **DeliveryAgent** | Eksik `video_path` → VideoRenderer'ı bekle. Eksik `chat_id` → package brief'ten oku. |

---

## 7. ETKİLENEN EXECUTOR

| Bileşen | Mevcut Davranış | Self-Healing Sonrası |
|---|---|---|
| `_load_task_packages` | Package yoksa `return []` | Package rebuild dene, sonra `[]` |
| `_execute_task` retry | `asyncio.sleep(_GC_EXECUTOR_RETRY_DELAY)` | Önce Self-Healing, sonra retry |
| `recover` boş task | Sessiz tamamlanır (0/0) | Self-Healing ile task oluşturmayı dene |
| `_run_task_handler` | COMPLETED task → erken dönüş | Proof doğrulaması — proof geçersizse yeniden çalıştır |

---

## 8. ETKİLENEN RECOVERY

| Recovery Türü | Self-Healing Öncesi | Self-Healing Sonrası |
|---|---|---|
| **RESUME** | Kaldığı yerden devam | Önce eksik bağımlılıkları Self-Healing ile gider |
| **RETRY** | Başarısız task'ları yeniden dene | Önce Self-Healing, sonra retry |
| **REPLAY** | Tüm task'ları sıfırla, baştan başla | Her task kendi Self-Healing'ini uygular |
| **START_AS_NEW** | Boş task_packages → 0 task çalışır ❌ | Self-Healing ile task_packages oluşturulur ✅ |

---

## 9. ETKİLENEN WAITING POLICY

### 9.1 Hard-coded Bekleme Analizi

| Dosya | Satır | Değer | Self-Healing Sonrası |
|---|---|---|---|
| `scene_delivery.py` | 201 | `(1, 0), (2, 0.3)` | → `GC_SCENE_RETRY_DELAYS` (yeni) |
| `scene_delivery.py` | 317 | `asyncio.sleep(1.5)` | → `GC_VOICE_DELIVERY_DELAY` (yeni) |
| `scene_delivery.py` | 421 | `asyncio.sleep(1.5 * attempt)` | → `GC_DELIVERY_BACKOFF_BASE` (yeni) × attempt |
| `scene_engine.py` | 207 | `asyncio.sleep(0.3)` | → `GC_SCENE_CLEANUP_RETRY_DELAY` (yeni) |
| `pid_runtime.py` | 242 | `time.sleep(0.05)` | → `GC_PID_LOCK_RETRY_DELAY` (yeni) |
| `pid_runtime.py` | 322 | `time.sleep(0.01)` | → `GC_PID_FILE_RETRY_DELAY` (yeni) |
| `pid_runtime.py` | 941 | `time.sleep(0.05 * (2 ** attempt))` | → `GC_PID_BACKOFF_BASE` (yeni) × (2^attempt) |
| `hedra_generator.py` | 131 | `time.sleep(5)` | → `GC_HEDRA_WAIT` (yeni) |

> **Not:** Bu hard-coded değerlerin GC'ye taşınması AR-002_91'in "sabit kodlu bekleme yasağı" kuralının doğrudan uygulamasıdır. Bu değerlerin herbiri için yeni GC parametresi eklenecektir.

### 9.2 Duplicate Mekanizma Analizi

| Mekanizma | Konum 1 | Konum 2 | Konum 3 | Tekilleştirme |
|---|---|---|---|---|
| **Failure handling** | `_handle_failure` (L2284) | `_handle_reproduction_failure` (L1376) | `_reject_reproduction` (L1342) | Ortak `_handle_terminal_failure(state, error, pid)` |
| **Retry loop** | `_execute_task` (L457-558) | `scene_delivery` (L201) | `pid_runtime` (L941) | Ortak `_anayasal_retry(max_count, delay, task)` |
| **Polling loop** | `production_pipeline` (L288) | `production_pipeline` (L406) | `production_pipeline` (L750) | Ortak `_anayasal_poll(interval, max_count, check_fn)` |
| **Event emission + registration** | `_run_managed` (L2026-2036) | `_run_reproduction` (L1089-1097) | `_handle_failure` (L2345-2360) | Ortak `_emit_and_register(event_type, description, phase, result)` |

> **Not:** Bu tekilleştirme, AR-002_91'in "Tek Waiting Policy / Tek Retry Policy / Tek Recovery Policy" ilkesinin doğrudan uygulamasıdır.

---

## 10. YENİ AR MADDE NUMARASI

**AR-002_91** — Task Self-Healing Architecture

Mevcut son AR numarası AR-002_90'dır. AR-002_91 bir sonraki kullanılabilir numaradır.

---

## 11. GÜNCELLENMESİ GEREKEN DOSYALAR

### 11.1 ANA YASA Dosyaları

| Dosya | Değişiklik |
|---|---|
| `ANA YASA/03_Architecture_Rules.md` | AR-002_91 maddesi ekle (AR-002_90'dan sonra) |
| `ANA YASA/01_Global_Configuration.md` | 12 yeni GC parametresi ekle |
| `ANA YASA/09_WORKFLOW_MANIFEST.md` | WF-008'e Self-Healing referansı ekle |
| `ANA YASA/14_OLAY_KAYIT_MERKEZI.md` | Yeni Self-Healing event'leri tanımla |
| `ANA YASA/20_TASK_ENGINE.md` | Self-Healing task state'leri ekle |

### 11.2 Kod Dosyaları

| Dosya | Değişiklik | Öncelik |
|---|---|---|
| `services/production_runtime.py` | `_run_reproduction`: START_AS_NEW/REPLAY için task_packages oluşturma | **KRİTİK** |
| `services/production_runtime.py` | `_run_reproduction`: `prepare_for_reproduction` ile `executor.recover` arasına Self-Healing adımı | **KRİTİK** |
| `services/production_executor.py` | `_execute_task`: Retry öncesi Self-Healing kontrolü | **YÜKSEK** |
| `services/production_executor.py` | `_load_task_packages`: Boş dönüş yerine Self-Healing | **YÜKSEK** |
| `services/production_executor.py` | `_run_task_handler`: Eksik kaynak kontrolü | **YÜKSEK** |
| `services/production_package_runtime.py` | `prepare_for_reproduction`: Boş task_packages için varsayılan oluşturma | **KRİTİK** |
| `services/constitution_enforcement.py` | Self-Healing uygulanmadan FAILED olan task'lar için CEE Violation | **YÜKSEK** |
| `services/hlk_runtime.py` | Yeni `DecisionCategory.SELF_HEALING` | ORTA |
| `services/execution_event_collector.py` | Yeni `EECEventType.SELF_HEALING_*` event'leri | ORTA |
| `config/settings.py` | 12 yeni GC parametresi için env var okuma | **KRİTİK** |
| `.env` | 12 yeni GC değişkeni | **KRİTİK** |
| `web/data_providers.py` | OPS ekranı Self-Healing durumu göstergesi | ORTA |
| `services/scene_delivery.py` | Hard-coded `1.5` → GC parametresi | DÜŞÜK |
| `services/scene_engine.py` | Hard-coded `0.3` → GC parametresi | DÜŞÜK |
| `services/pid_runtime.py` | Hard-coded `0.05`/`0.01` → GC parametresi | DÜŞÜK |

---

## 12. KODDA BULUNMASI GEREKEN DEĞİŞİKLİKLER

### 12.1 KRİTİK: `_run_reproduction` — START_AS_NEW Task Oluşturma

```python
# services/production_runtime.py — _run_reproduction içinde
# prepare_for_reproduction ile executor.recover arasına eklenecek:

if procedure in ("START_AS_NEW", "REPLAY"):
    pkg = await package_runtime.load(pid)
    task_packages = pkg.task_packages if pkg else []
    
    if not task_packages:
        # AR-002_91: Self-Healing — eksik task_packages oluştur
        logger.info(f"🩹 [Self-Healing] Boş task_packages tespit edildi: {pid} — oluşturuluyor")
        real_tasks = [
            {"task_id": f"TASK-{pid}-001", "agent": "ImageGenerator",
             "status": "PENDING", "pid": pid,
             "description": "Ürün görseli üretimi"},
            {"task_id": f"TASK-{pid}-002", "agent": "VoiceGenerator",
             "status": "PENDING", "pid": pid,
             "description": "AI seslendirme üretimi"},
            {"task_id": f"TASK-{pid}-003", "agent": "VideoRenderer",
             "status": "PENDING", "pid": pid,
             "description": "Video render"},
            {"task_id": f"TASK-{pid}-004", "agent": "DeliveryAgent",
             "status": "PENDING", "pid": pid,
             "description": "Teslimat"},
        ]
        await package_runtime.update_section(pid, "task_packages", real_tasks)
        
        # Self-Healing olayı kaydı
        await self._record_reproduction_event(
            pid,
            event_constant="EVENT_SELF_HEALING_PACKAGE_REBUILT",
            event_name="Self-Healing: Task Package Yeniden Oluşturuldu",
            description=f"START_AS_NEW: Boş task_packages için {len(real_tasks)} task oluşturuldu",
            result=f"{len(real_tasks)} task",
        )
```

### 12.2 YÜKSEK: `_execute_task` — Self-Healing Ön Kontrolü

```python
# services/production_executor.py — _execute_task içinde
# Retry döngüsü başlamadan ÖNCE eklenecek:

# AR-002_91: Self-Healing ön kontrolü
for healing_attempt in range(1, _GC_TASK_SELF_HEAL_MAX_COUNT + 1):
    healing_needed, healing_action = await self._check_self_healing(task, pid)
    if not healing_needed:
        break
    logger.info(f"🩹 [Self-Healing] {healing_action} — deneme {healing_attempt}")
    await self._apply_self_healing(healing_action, task, pid)
    await asyncio.sleep(_GC_TASK_SELF_HEAL_DELAY)
```

### 12.3 YÜKSEK: `_load_task_packages` — Boş Dönüş Yerine Self-Healing

```python
# services/production_executor.py — _load_task_packages içinde:

pkg = await package_runtime.load(pid)
if pkg is None:
    # AR-002_91: Self-Healing — package rebuild dene
    for attempt in range(1, _GC_PACKAGE_REBUILD_MAX_COUNT + 1):
        logger.warning(f"🩹 [Self-Healing] Package bulunamadı: {pid} — rebuild deneniyor ({attempt})")
        await asyncio.sleep(_GC_PACKAGE_REBUILD_DELAY)
        pkg = await package_runtime.load(pid)
        if pkg is not None:
            break
    if pkg is None:
        logger.error(f"❌ [Self-Healing] Package rebuild başarısız: {pid}")
        return []  # Son çare — Recovery Policy devreye girer
```

---

## 13. ANA YASA / KOD UYUMLULUK RAPORU

### 13.1 MASTER Rule Book Standardına Göre Değerlendirme

| MASTER Kural | Uyum | Açıklama |
|---|---|---|
| **MASTER-001** Analiz Zorunluluğu | ✅ | Tüm anayasal kaynaklar okundu, çakışma analizi yapıldı |
| **MASTER-003** PipelineContext Anayasal Gerçeği | ✅ | Self-Healing, PipelineContext'i anayasal gerçeğe getirir |
| **MASTER-004** Karar Mekanizması | ✅ | Self-Healing karar vermez; yalnızca tamir eder. Karar HLK Runtime'ındır |
| **MASTER-011** Runtime Aktiflik | ✅ | Self-Healing, Runtime'lar aktifken çalışır |
| **MASTER-013** Karar Otoritesi | ✅ | Self-Healing başarısız olursa karar HLK Runtime'a iletilir |

### 13.2 Architecture Rules Uyum Matrisi

| AR | Uyum | Açıklama |
|---|---|---|
| AR-002_22 | ✅ | Self-Healing başarısız → Feedback Loop → Re-evaluation |
| AR-002_57 | ✅ | Tüm Self-Healing event'leri PID ile kaydedilir |
| AR-002_60 | ✅ | CEE, Self-Healing atlanarak FAILED olan task'ları violation sayar |
| AR-002_70 | ✅ | Production Runtime içinde Self-Healing Gateway |
| AR-002_75 | ✅ | Self-Healing provider'ı değiştirmez; yalnızca eksik bağımlılıkları giderir |
| AR-002_76 | ✅ | Executor seviyesinde Self-Healing entegrasyonu |
| AR-002_79 | ✅ | Self-Healing → Recovery → Süreklilik zinciri |
| AR-002_81 | ✅ | Self-Healing kararları Decision History'ye kaydedilir |
| AR-002_82 | ✅ | Self-Healing, Mission Persistence'ın task seviyesindeki uygulamasıdır |
| AR-002_83 | ✅ | Self-Healing başarısız → Recovery Policy |
| AR-002_84 | ✅ | START_AS_NEW Self-Healing ile task_packages oluşturur |
| AR-002_86 | ✅ | Self-Healing uygulanmaması → Anayasal Yürütme ihlali |
| AR-002_87 | ✅ | Provider Self-Healing, AR-002_87 yaşam döngüsüne uyar |
| AR-002_90 | ✅ | Production Gate öncesi tüm WF'ler Self-Healing'den geçer |

### 13.3 Operational Rules Uyum Matrisi

| OR | Uyum | Açıklama |
|---|---|---|
| OR-004_12 | ✅ | Self-Healing karar kaydı Decision History'ye yazılır |

### 13.4 State Engine Uyum Matrisi

| SE | Uyum | Açıklama |
|---|---|---|
| SE-007_3 | ✅ | Self-Healing, STATE_VIDEO_PRODUCTION içinde çalışır |
| SE-007_4 | ✅ | Self-Healing başarısız → EVENT_VIDEO_PRODUCTION_FAILED |
| SE-007_5 | ✅ | Self-Healing tamamlanmış task'ları COMPLETED yapar |

---

## 14. AR-002_91 TAM METİN TASLAĞI

Aşağıdaki metin, `ANA YASA/03_Architecture_Rules.md` dosyasına AR-002_90'dan sonra eklenecektir.

---

## AR-002_91

### Başlık

Task Self-Healing Architecture (Task Kendi Kendini İyileştirme Mimarisi)

### Amaç

HLK sisteminde hiçbir Task; eksik bağımlılık, geçici hata, henüz oluşmamış kaynak veya gecikmeli çalışan sistem bileşenleri nedeniyle hemen sonlanamaz.

Recovery Policy başlamadan önce, Task kendi görevini anayasal sınırlar içerisinde kendi kendine tamamlamaya çalışmalıdır.

Bu mimari; AR-002_82 Mission Persistence ile AR-002_83 Recovery Policy arasındaki eksik anayasal katmandır.

### Kapsam

Bu madde; tüm Runtime Task'ları, tüm Workflow Task'ları, tüm Agent Task'ları, tüm Provider Task'ları, tüm Production Task'ları, START_AS_NEW, REPLAY, Retry, Restart ve Recovery süreçleri için zorunludur.

### Constitutional Principle

Task'ın görevi yalnızca `execute()` edilmek değildir. Task'ın görevi; kendisine verilen anayasal görevi SUCCESS durumuna ulaştırmaktır.

İlk başarısızlık, Task'ın sonlanması için yeterli gerekçe değildir.

### Self-Healing Workflow

Bir Task aşağıdaki anayasal sırayı uygulamak zorundadır:

1. **Mevcut kaynak kullanılabiliyorsa kullan.**
2. **Eksik Resource varsa yeniden oluştur.**
3. **Eksik Task Package varsa yeniden üret.**
4. **Eksik Workflow Package varsa yeniden oluştur.**
5. **Eksik Event oluşmasını bekle.** Gerekliyse yeniden üret.
6. **Eksik Digital Asset oluşmasını bekle.** Gerekliyse yeniden oluştur.
7. **Eksik Provider sonucu varsa anayasal polling mekanizmasını uygula.**
8. **Self-Healing başarısız olursa Recovery Policy'ye geç.**
9. **Recovery Policy başarısız olursa HLK Runtime yeniden anayasal karar üretir.**
10. **Tüm anayasal yollar tüketildikten sonra FAILED kararı verilebilir.**

### Controlled Waiting Policy

Task; geçici (Transient) olduğu değerlendirilen durumlarda hemen FAILED olamaz.

Geçici durumlar en az aşağıdakileri kapsar:
- Provider cevap bekleniyor
- Provider polling devam ediyor
- Task Package oluşturuluyor
- Workflow Package oluşturuluyor
- Production Package hazırlanıyor
- Event henüz oluşmadı
- Digital Asset oluşturuluyor
- Artifact doğrulaması tamamlanmadı
- Dosya yazılıyor
- Queue işleniyor

### Waiting Policy Rules

- Bekleme süreleri sabit kod olarak yazılamaz.
- Bekleme süreleri yalnızca Global Configuration üzerinden okunacaktır.
- Her bekleme nedeni Decision History ve Execution Event Collector içerisine kayıt edilmek zorundadır.
- Her yeniden deneme Decision History'ye gerekçesiyle yazılacaktır.

### Yasaklar

Task aşağıdaki nedenlerle sonlanamaz:
- `None`
- `[]`
- boş Task Package
- eksik Resource
- eksik Event
- eksik Artifact
- ilk Exception
- ilk Timeout
- ilk Provider Hatası
- geçici servis hatası
- ilk Queue hatası
- ilk dosya oluşturma hatası

### Constitution Enforcement

Constitution Enforcement Engine; Task'ın Self-Healing uygulanmadan, Recovery uygulanmadan ve anayasal yollar tüketilmeden FAILED olduğunu tespit ederse:
- Constitution Violation oluşturacaktır.
- Violation Event oluşturacaktır.
- Decision History'ye kaydedecektir.
- HLK Runtime yöneticiye rapor verecektir.

### Runtime Requirement

Aşağıdaki süreçler aynı anayasal Self-Healing davranışını kullanacaktır:
- START_AS_NEW
- REPLAY
- Retry
- Recovery
- Restart
- Crash Recovery
- Scheduled Restart

Hiçbiri kendi özel Self-Healing mekanizmasını oluşturamaz. Tek anayasal Self-Healing Architecture kullanılacaktır.

### Tekilleştirme İlkesi

Kod tekrarına izin verilmez:
- Tek Waiting Policy
- Tek Retry Policy
- Tek Recovery Policy
- Tek Self-Healing Policy
- Tek Runtime Decision mekanizması

### Global Configuration

Aşağıdaki GC parametreleri bu mimariyi desteklemek üzere tanımlanmıştır:

| Parametre | Açıklama |
|---|---|
| `GC_TASK_SELF_HEAL_MAX_COUNT` | Self-Healing maksimum deneme sayısı |
| `GC_TASK_SELF_HEAL_DELAY` | Self-Healing adımları arası bekleme (saniye) |
| `GC_PACKAGE_REBUILD_MAX_COUNT` | Package yeniden oluşturma maksimum deneme |
| `GC_PACKAGE_REBUILD_DELAY` | Package rebuild denemeleri arası bekleme (saniye) |
| `GC_RESOURCE_RECOVERY_DELAY` | Resource kurtarma bekleme süresi (saniye) |
| `GC_EVENT_RECOVERY_DELAY` | Event oluşmasını bekleme süresi (saniye) |
| `GC_EVENT_RECOVERY_MAX_COUNT` | Event bekleme maksimum deneme sayısı |
| `GC_FILE_RECOVERY_DELAY` | Dosya oluşmasını bekleme süresi (saniye) |
| `GC_FILE_RECOVERY_MAX_COUNT` | Dosya bekleme maksimum deneme sayısı |
| `GC_ARTIFACT_RECOVERY_DELAY` | Artifact doğrulama bekleme süresi (saniye) |
| `GC_ARTIFACT_RECOVERY_MAX_COUNT` | Artifact bekleme maksimum deneme sayısı |

Bu parametreler mevcut `GC_EXECUTOR_MAX_RETRY`, `GC_EXECUTOR_RETRY_DELAY`, `GC_MAX_RE_EVALUATION_COUNT`, `GC_PROVIDER_POLL_COUNT`, `GC_IMAGE_POLL_INTERVAL`, `GC_VIDEO_POLL_INTERVAL` ile uyumlu çalışır. Hiçbir mevcut GC parametresi değiştirilmez veya devre dışı bırakılmaz.

### Anayasal Dayanak

| Katman | Referans | Açıklama |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü |
| **MASTER** | MASTER-003 | PipelineContext anayasal gerçeği yansıtır |
| **MASTER** | MASTER-004 | Self-Healing karar vermez; HLK Runtime karar verir |
| **MASTER** | MASTER-011 | Runtime aktiflik doğrulaması |
| **MASTER** | MASTER-013 | Self-Healing başarısız → HLK Runtime kararı |
| **AR** | AR-002_22 | Feedback Loop — Self-Healing sonrası yeniden değerlendirme |
| **AR** | AR-002_57 | PID Standardı — Self-Healing kayıtlarında PID zorunlu |
| **AR** | AR-002_60 | CEE — Self-Healing atlanırsa violation |
| **AR** | AR-002_70 | Production Runtime — Self-Healing Gateway |
| **AR** | AR-002_76 | Production Execution — Self-Healing entegrasyonu |
| **AR** | AR-002_79 | Üretim Sürekliliği — Self-Healing → Recovery zinciri |
| **AR** | AR-002_81 | Karar Talep Protokolü — SELF_HEALING karar kategorisi |
| **AR** | AR-002_82 | Mission Persistence — Self-Healing'in üst katmanı |
| **AR** | AR-002_83 | Recovery Policy — Self-Healing başarısız olursa geçiş |
| **AR** | AR-002_84 | Yönetici Yeniden Üretim — START_AS_NEW Self-Healing |
| **AR** | AR-002_86 | Anayasal Yürütme — Self-Healing uygulanmaması ihlal |
| **AR** | AR-002_87 | External Resource Recovery — Provider Self-Healing referansı |
| **AR** | AR-002_90 | Production Gate — Pre-production Self-Healing |

### Beklenen Sonuç

- Hiçbir Task eksik bağımlılık nedeniyle hemen FAILED olmaz.
- Task'lar kendi Package, Resource, Event ve Artifact'lerini onarabilir.
- Self-Healing başarısız olursa Recovery Policy otomatik devreye girer.
- START_AS_NEW ve REPLAY prosedürleri boş task_packages ile karşılaşmaz.
- Tüm bekleme süreleri GC parametrelerinden okunur, hard-coded değer kalmaz.
- Tek Waiting Policy, tek Retry Policy, tek Recovery Policy kullanılır.
- CEE, Self-Healing atlanarak FAILED olan task'ları violation olarak kaydeder.
- Tüm Self-Healing adımları Decision History ve Event Log'a kaydedilir.

---

## 15. ÖZET

AR-002_91, mevcut dört anayasal maddeyle (AR-002_82, AR-002_83, AR-002_87, AR-002_90) çakışmaz, onları tekrar etmez ve onların görevini üstlenmez.

**Tek yaptığı şey:** Mission Persistence ile Recovery Policy arasındaki anayasal boşluğu doldurmak — Task'ın, Recovery'ye yükseltilmeden önce kendi başına eksik bağımlılıklarını gidermeye çalışmasını sağlamak.

Bu, 26.07.2026 tarihinde tespit edilen START_AS_NEW kopukluğunun (PID-20260726-0001) doğrudan anayasal çözümüdür.
