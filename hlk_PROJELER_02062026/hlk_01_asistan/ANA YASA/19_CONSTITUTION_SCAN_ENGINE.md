# 19 — Constitution Scan Engine (CSE)

HLK'nın anayasal veri toplama katmanıdır. Tüm ANA YASA, kod ve runtime
kaynaklarını tarar, kanıt toplar, Constitution Snapshot üretir ve
Constitution Diff Engine (CDE)'e aktarır.

CSE **hiçbir zaman karar vermez.** PASS/FAIL üretmez. Yalnızca veri toplar.

---

## 1. Amaç

CSE'nin tek görevi; HLK'nın tüm katmanlarını okuyarak **tek bir Constitution
Snapshot** oluşturmak ve bu snapshot'ı Constitution Diff Engine'e (CDE)
aktarmaktır.

CSE;

- ANA YASA (.md) dosyalarını tarar,
- Kod (.py) dosyalarını tarar,
- Runtime log'larını tarar,
- Registry, Workflow, Feature, Event ve Production verilerini toplar,
- Her bulguyu kanıtıyla birlikte kaydeder,
- Tüm veriyi tek bir Snapshot altında birleştirir,
- Snapshot'ı CDE'ye iletir.

CSE;

- Karar vermez,
- PASS/FAIL üretmez,
- Kod yazmaz,
- Kod değiştirmez,
- ANA YASA'yı değiştirmez.

---

## 2. Mimari Konum

CSE, ANA YASA/Kod/Runtime ile CDE arasında konumlanan **veri toplama katmanıdır.**

```
ANA YASA (.md)  ────┐
                     │
Kod (.py)       ────┤
                     ├──► CONSTITUTION SCAN ENGINE (CSE)
Runtime (log)   ────┘         │
                              │  Constitution Snapshot
                              ▼
                     CONSTITUTION DIFF ENGINE (CDE)
                              │
                              ▼
                     CONSTITUTION GATE
                              │
                              ▼
                           Claude
```

CSE, CDE'nin **veri sağlayıcısıdır.** CDE olmadan CSE'in ürettiği veri tek
başına anlam ifade etmez. CSE olmadan CDE'in karşılaştırma yapacağı veri
bulunmaz. İki modül birlikte çalışır.

---

## 3. Temel İlkeler

1. **CSE hiçbir zaman karar vermez.** Yalnızca tarar.
2. **CSE hiçbir zaman PASS/FAIL üretmez.** Yalnızca FOUND/NOT FOUND/UNKNOWN bildirir.
3. **CSE hiçbir zaman kod yazmaz.** Yalnızca okur.
4. **CSE hiçbir zaman kod değiştirmez.** Yalnızca mevcut durumu kaydeder.
5. **CSE hiçbir zaman ANA YASA'yı değiştirmez.** MASTER-001 gereği yalnızca Proje Yöneticisi değiştirebilir.
6. **CSE yalnızca kanıt üretir.** Her bulgu bir kaynak referansıyla belgelenir.
7. **CSE yalnızca Snapshot üretir.** Tüm tarama sonuçları tek bir yapı altında toplanır.
8. **CSE yalnızca CDE'ye veri sağlar.** Tüm anayasal kararlar CDE tarafından verilir.

---

## 4. Taranacak Kaynaklar

CSE aşağıdaki tüm kaynakları tarar:

### 4.1 ANA YASA Kaynakları (.md)

| Dosya | Taranan Veri |
|---|---|
| `00_HLK_MASTER_RULE_BOOK.md` | MASTER-001 — MASTER-006 kuralları |
| `01_Global_Configuration.md` | GC parametreleri ve değerleri |
| `02_General_Rules.md` | GK kuralları |
| `03_Architecture_Rules.md` | AR-002_1 — AR-002_n kuralları |
| `04_Operational_Rules.md` | OR-004_0 — OR-004_n kuralları |
| `05_Quality_Rules.md` | QR kuralları |
| `06_Module_Rule.md` | MR kuralları |
| `07_HLK_STATE_ENGINE.md` | SE-007_3 State listesi, SE-007_4 geçişler, SE-007_5 event tetikleyicileri, SE-007_6 aksiyon eşleştirmeleri |
| `08_HLK_FLOW_DIAGRAM.md` | FD-008_1 akış diyagramı, FD-008_2 referans tablosu, FD-008_6 geliştirme durumu |
| `09_WORKFLOW_MANIFEST.md` | WF-001 — WF-012 workflow kayıtları |
| `10_FEATURE_REGISTRY.md` | FEAT-001 — FEAT-017 feature kayıtları |
| `11_WORKFLOW_FEATURE_MAP.md` | WF-FEAT ilişki haritası |
| `12_DIGITAL_ASSET_ARCHIVE.md` | Dijital varlık kayıtları |
| `13_DIGITAL_ASSET_CATALOG.md` | Dijital varlık kataloğu |
| `14_OLAY_KAYIT_MERKEZI.md` | OLAY-001 — OLAY-050 event kayıtları |
| `15_KARAR_GEREKCESI_STANDARDI.md` | Karar gerekçesi teknik sabitleri |
| `16_PRODUCTION_PACKAGE_STANDARD.md` | Production Package standardı |
| `17_SAHNE_KAYIT_DEFTERİ.md` | SAHNE-01 — SAHNE-14 sahne kayıtları |
| `18_CONSTITUTION_DIFF_ENGINE.md` | CDE kuralları, gate, faz tanımları |
| `19_CONSTITUTION_SCAN_ENGINE.md` | Bu dosya (kendisi) |

### 4.2 Kod Kaynakları (.py)

| Dosya | Taranan Veri |
|---|---|
| `utils/state_engine.py` | `UserState` enum, `UserEvent` enum, `STATE_TRANSITIONS` dict, `STATE_ACTION_MAP` dict, `StateEngine` sınıfı |
| `utils/scene_lock.py` | `SceneLock`, `SceneLockState` |
| `utils/session_timeout.py` | Timeout mekanizması |
| `utils/validators.py` | Doğrulama fonksiyonları |
| `services/scene_registry.py` | `SCENE_REGISTRY` listesi, `SceneDefinition` dataclass, `get_scene_for_state()` |
| `services/scene_engine.py` | `ConversationSceneEngine`, `produce_and_deliver()` |
| `services/scene_delivery.py` | `SceneDeliveryModule`, `ScenePayload`, `DeliveryReceipt` |
| `services/voice_generator.py` | `AHUVoiceGenerator` |
| `services/research_orchestrator.py` | Araştırma modülleri, `_module_registry` |
| `handlers/start.py` | `/start` akışı, `handle_language_selection`, `message_handler` |
| `handlers/website.py` | `handle_website_link`, `handle_material_choice`, `handle_format_selection`, `handle_resolution_selection`, `handle_platform_selection`, `handle_material_upload` |
| `handlers/cancel.py` | `handle_cancel` |
| `helpers/typewriter_animation.py` | `typewriter_animation`, `strip_html` |
| `config/settings.py` | `Settings` sınıfı |
| `config/video_paths.py` | GC-001 path sabitleri |
| `main.py` | Handler kayıtları, `CallbackQueryHandler` pattern'leri, bot başlatma |

### 4.3 Runtime Kaynakları (canlı log)

| Kaynak | Taranan Veri |
|---|---|
| `bot_stderr.log` | State geçişleri (`STATE: X --[EVENT]--> Y`), Event tetiklenmeleri, hata log'ları, SENDMESSAGE TRACE, timeout log'ları |
| `logs/bot.log` | FileHandler log'ları (eğer mevcutsa) |
| `bot_stdout.log` | Konsol çıktısı |
| Canlı process (PID) | Çalışan Python process'i, başlangıç zamanı, working directory |
| Telegram API durumu | `getMe`, `getUpdates`, `sendMessage` HTTP yanıtları |

---

## 5. Scan Katmanları

CSE sekiz bağımsız tarama katmanından oluşur. Her katman kendi kaynaklarını
tarar ve kendi sonuç listesini üretir. Katmanlar birbirinden bağımsız çalışır.

### 5.1 SCAN-1 — ANA YASA Scan

**Hedef:** Tüm .md dosyalarındaki anayasal tanımları çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| MASTER kuralları | `00_HLK_MASTER_RULE_BOOK.md` | `master_rules: list[dict]` |
| GC parametreleri | `01_Global_Configuration.md` | `gc_params: dict` |
| AR kuralları | `03_Architecture_Rules.md` | `arch_rules: list[dict]` |
| OR kuralları | `04_Operational_Rules.md` | `oper_rules: list[dict]` |
| State tanımları | `07_HLK_STATE_ENGINE.md` (SE-007_3) | `ana_yasa_states: list[str]` |
| State geçişleri | `07_HLK_STATE_ENGINE.md` (SE-007_4) | `ana_yasa_transitions: list[dict]` |
| Event-State tablosu | `07_HLK_STATE_ENGINE.md` (SE-007_5) | `ana_yasa_event_map: list[dict]` |
| Sahne tanımları | `08_HLK_FLOW_DIAGRAM.md` (FD-008_1) | `ana_yasa_scenes: list[dict]` |
| Workflow kayıtları | `09_WORKFLOW_MANIFEST.md` | `ana_yasa_workflows: list[dict]` |
| Feature kayıtları | `10_FEATURE_REGISTRY.md` | `ana_yasa_features: list[dict]` |
| Olay kayıtları | `14_OLAY_KAYIT_MERKEZI.md` | `ana_yasa_events: list[dict]` |
| Sahne kayıt defteri | `17_SAHNE_KAYIT_DEFTERİ.md` | `ana_yasa_scene_records: list[dict]` |

### 5.2 SCAN-2 — Kod Scan

**Hedef:** Tüm .py dosyalarındaki kod tanımlarını çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| State enum | `utils/state_engine.py` → `UserState` | `code_states: list[str]` |
| Event enum | `utils/state_engine.py` → `UserEvent` | `code_events: list[str]` |
| State transitions | `utils/state_engine.py` → `STATE_TRANSITIONS` | `code_transitions: list[dict]` |
| State action map | `utils/state_engine.py` → `STATE_ACTION_MAP` | `code_action_map: dict` |
| Scene definitions | `services/scene_registry.py` → `SCENE_REGISTRY` | `code_scenes: list[dict]` |
| Handler fonksiyonları | `handlers/website.py` | `code_handlers: list[dict]` |
| Handler kayıtları | `main.py` → `CallbackQueryHandler` | `code_handler_registrations: list[dict]` |
| Delivery çağrıları | `handlers/*.py`, `services/*.py` | `code_delivery_calls: list[dict]` |
| Cleanup çağrıları | `handlers/*.py`, `services/*.py` | `code_cleanup_calls: list[dict]` |
| İmport zinciri | Tüm .py dosyaları | `code_imports: dict` |

### 5.3 SCAN-3 — Runtime Scan

**Hedef:** Canlı log ve process verilerini çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| Aktif state | `bot_stderr.log` → son `STATE:` geçişi | `runtime_current_state: str` |
| State geçiş geçmişi | `bot_stderr.log` → tüm `STATE:` satırları | `runtime_state_history: list[dict]` |
| Event geçmişi | `bot_stderr.log` → `--[EVENT]-->` | `runtime_event_history: list[dict]` |
| Çalışan process | `tasklist` / `ps` | `runtime_process: dict` |
| Process başlangıç zamanı | `Get-Process` StartTime | `runtime_start_time: str` |
| Working directory | Process CommandLine | `runtime_working_dir: str` |
| Telegram API durumu | `bot_stderr.log` → HTTP yanıtları | `runtime_api_status: list[dict]` |
| Hata log'ları | `bot_stderr.log` → ERROR satırları | `runtime_errors: list[dict]` |
| Timeout log'ları | `bot_stderr.log` → TIMEOUT satırları | `runtime_timeouts: list[dict]` |
| Aktif session | `bot_stderr.log` → chat_id, user_id | `runtime_sessions: list[dict]` |

### 5.4 SCAN-4 — Registry Scan

**Hedef:** Scene Registry'deki kayıtları çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| Scene listesi | `SCENE_REGISTRY` → her `SceneDefinition` | `registry_scenes: list[dict]` |
| Scene ID'leri | `scene_id` alanı | `registry_scene_ids: list[str]` |
| State eşleştirmeleri | `state` alanı | `registry_state_map: dict` |
| Next state'ler | `next_state` alanı | `registry_next_states: dict` |
| Buton tanımları | `buttons` alanı | `registry_buttons: list[dict]` |
| Voice enabled | `voice_enabled` alanı | `registry_voice_flags: dict` |
| Timeout değerleri | `timeout_seconds` alanı | `registry_timeouts: dict` |
| Toplam kayıt sayısı | `len(SCENE_REGISTRY)` | `registry_total_count: int` |

### 5.5 SCAN-5 — Workflow Scan

**Hedef:** Workflow Manifest ve Workflow-Feature Map verilerini çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| Workflow listesi | `09_WORKFLOW_MANIFEST.md` | `workflows: list[dict]` |
| WF-FEAT ilişkileri | `11_WORKFLOW_FEATURE_MAP.md` | `workflow_feature_map: dict` |
| Workflow durumları | Manifest → Durum alanı | `workflow_statuses: dict` |
| Kod karşılıkları | İlgili .py dosyaları | `workflow_code_map: dict` |

### 5.6 SCAN-6 — State Scan

**Hedef:** State Engine'in ANA YASA ve kod katmanlarındaki durumunu çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| ANA YASA state listesi | `07_HLK_STATE_ENGINE.md` (SE-007_3) | `ana_yasa_states: list[str]` |
| Kod state listesi | `utils/state_engine.py` → `UserState` | `code_states: list[str]` |
| ANA YASA'da olup kodda olmayan | Karşılaştırma (CSE yapmaz, CDE yapar) | — (ham veri olarak iletilir) |
| Kodda olup ANA YASA'da olmayan | Karşılaştırma (CSE yapmaz, CDE yapar) | — (ham veri olarak iletilir) |
| State geçiş kuralları | `STATE_TRANSITIONS` | `code_transitions_raw: dict` |
| State aksiyon haritası | `STATE_ACTION_MAP` | `code_action_map_raw: dict` |

### 5.7 SCAN-7 — Feature Scan

**Hedef:** Feature Registry ve kod arasındaki feature durumunu çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| Feature listesi | `10_FEATURE_REGISTRY.md` | `features: list[dict]` |
| Feature kategorileri | Registry → Kategori | `feature_categories: dict` |
| Feature durumları | Registry → Durum | `feature_statuses: dict` |
| Kod karşılıkları | İlgili .py dosyaları | `feature_code_map: dict` |

### 5.8 SCAN-8 — Production Scan

**Hedef:** Production Package, Digital Asset ve Decision Record verilerini çıkarmak.

| Veri Tipi | Kaynak | Çıktı |
|---|---|---|
| Production Package'ler | `FORMLAR/`, Production çıktıları | `production_packages: list[dict]` |
| PID listesi | `bot_stderr.log` → PID satırları | `production_pids: list[str]` |
| Dijital varlıklar | `12_DIGITAL_ASSET_ARCHIVE.md` | `digital_assets: list[dict]` |
| Karar kayıtları | `15_KARAR_GEREKCESI_STANDARDI.md` | `decision_standards: dict` |
| Karar geçmişi | Runtime log → karar event'leri | `decision_history: list[dict]` |

---

## 6. Constitution Snapshot

Her tarama oturumunun sonunda tek bir **Constitution Snapshot** üretilir.
Snapshot, CSE'in CDE'ye aktardığı standart veri paketidir.

### 6.1 Snapshot Yapısı

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTION SNAPSHOT                                    ║
╠═══════════════════════════════════════════════════════════╣
║  Snapshot ID    : SNAP-YYYYMMDD-NNNN                      ║
║  Oluşturan      : Constitution Scan Engine (CSE)          ║
║  Tarih          : YYYY-MM-DD HH:MM:SS                     ║
║  Tetikleyici    : FAZ-0 / FAZ-2 / FAZ-3 / MANUAL          ║
╠═══════════════════════════════════════════════════════════╣
║  ÖZET:                                                    ║
║  ANA YASA Scenes    : <N> bulundu                         ║
║  Kod Scenes         : <N> bulundu                         ║
║  Registry Scenes    : <N> kayıtlı                         ║
║  Workflows          : <N> kayıtlı                         ║
║  Features           : <N> kayıtlı                         ║
║  States (ANA YASA)  : <N> tanımlı                         ║
║  States (Kod)       : <N> tanımlı                         ║
║  Events (ANA YASA)  : <N> tanımlı                         ║
║  Events (Kod)       : <N> tanımlı                         ║
║  Handlers           : <N> tespit edildi                   ║
║  Runtime Durum      : <AKTİF / DURDU / HATA>              ║
║  Aktif PID          : <PID / YOK>                         ║
╠═══════════════════════════════════════════════════════════╣
║  SCAN SONUÇLARI:                                          ║
║  SCAN-1 (ANA YASA)  : <toplam bulgu> kayıt                ║
║  SCAN-2 (Kod)       : <toplam bulgu> kayıt                ║
║  SCAN-3 (Runtime)   : <toplam bulgu> kayıt                ║
║  SCAN-4 (Registry)  : <toplam bulgu> kayıt                ║
║  SCAN-5 (Workflow)  : <toplam bulgu> kayıt                ║
║  SCAN-6 (State)     : <toplam bulgu> kayıt                ║
║  SCAN-7 (Feature)   : <toplam bulgu> kayıt                ║
║  SCAN-8 (Production): <toplam bulgu> kayıt                ║
╠═══════════════════════════════════════════════════════════╣
║  DURUM         : SNAPSHOT_READY                            ║
╚═══════════════════════════════════════════════════════════╝
```

### 6.2 Snapshot Veri Blokları

Snapshot içerisinde her veri tipi için ayrı blok bulunur:

```
SNAP-YYYYMMDD-NNNN
│
├── meta.json              ← Snapshot ID, tarih, tetikleyici, özet
├── scan_01_ana_yasa.json  ← ANA YASA tarama sonuçları
├── scan_02_kod.json       ← Kod tarama sonuçları
├── scan_03_runtime.json   ← Runtime tarama sonuçları
├── scan_04_registry.json  ← Registry tarama sonuçları
├── scan_05_workflow.json  ← Workflow tarama sonuçları
├── scan_06_state.json     ← State tarama sonuçları
├── scan_07_feature.json   ← Feature tarama sonuçları
├── scan_08_production.json← Production tarama sonuçları
├── evidence/              ← Kanıt dosyaları (log kesitleri, SHA256, diff)
│   ├── evidence_001.txt
│   ├── evidence_002.txt
│   └── ...
└── raw/                   ← Ham kaynak kopyaları (referans)
    ├── state_engine.py.snap
    ├── scene_registry.py.snap
    └── ...
```

---

## 7. Scan Sonuç Formatı

CSE **hiçbir zaman PASS/FAIL üretmez.** Her tarama sonucu için yalnızca şu üç
durumdan biri bildirilir:

| Durum | Teknik Sabit | Anlamı |
|---|---|---|
| **FOUND** | `SCAN_RESULT_FOUND` | Aranan öğe kaynakta mevcut |
| **NOT FOUND** | `SCAN_RESULT_NOT_FOUND` | Aranan öğe kaynakta bulunamadı |
| **UNKNOWN** | `SCAN_RESULT_UNKNOWN` | Kaynak okunamadı veya belirsiz |

Bu değerler birer **karar** değil, **gözlem**dir. CDE bu gözlemleri kullanarak
PASS/FAIL kararını kendisi üretir.

### Örnek Scan Kaydı

```json
{
  "scan_layer": "SCAN-4",
  "scan_target": "Scene Registry",
  "record_type": "SceneDefinition",
  "scene_id": "SAHNE-05",
  "result": "NOT_FOUND",
  "source_ana_yasa": {
    "file": "08_HLK_FLOW_DIAGRAM.md",
    "line": "141-153",
    "reference": "FD-008_1 SAHNE-05"
  },
  "source_code": {
    "file": "services/scene_registry.py",
    "line": "129",
    "checked": "SCENE_REGISTRY listesi"
  },
  "evidence": "evidence/scene_registry_scan_004.txt"
}
```

---

## 8. Constitution Evidence (Kanıt Standardı)

Her tarama kaydı, bulguyu destekleyen kanıtla birlikte saklanır.

### 8.1 Kanıt Formatı

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTION EVIDENCE                                    ║
╠═══════════════════════════════════════════════════════════╣
║  Evidence ID    : EVID-YYYYMMDD-NNNN                      ║
║  Bağlı Snapshot : SNAP-YYYYMMDD-NNNN                      ║
║  Scan Katmanı   : SCAN-N                                  ║
╠═══════════════════════════════════════════════════════════╣
║  ARANAN         : <Ne arandı?>                            ║
║  KAYNAK         : <Hangi dosya(lar) tarandı?>             ║
║  SATIR          : <İlgili satır numarası>                 ║
║  BULUNDU        : EVET / HAYIR                            ║
╠═══════════════════════════════════════════════════════════╣
║  ANA YASA REFERANSI:                                       ║
║  Dosya          : <ANA YASA .md dosyası>                  ║
║  Bölüm          : <SE-007_x / FD-008_x / OR-004_x>       ║
║  Satır          : <ilgili satır>                          ║
╠═══════════════════════════════════════════════════════════╣
║  KOD REFERANSI:                                            ║
║  Dosya          : <.py dosyası>                           ║
║  Satır          : <ilgili satır>                          ║
║  SHA256         : <dosya hash'i>                          ║
╠═══════════════════════════════════════════════════════════╣
║  RUNTIME REFERANSI (varsa):                                ║
║  Log Dosyası    : <log dosyası>                           ║
║  Log Satırı     : <log içeriği>                           ║
║  Zaman Damgası  : <YYYY-MM-DD HH:MM:SS>                  ║
╚═══════════════════════════════════════════════════════════╝
```

### 8.2 Kanıt Türleri

| Kanıt Türü | Açıklama | Örnek |
|---|---|---|
| `FILE_EXISTS` | Dosya mevcut mu? | `scene_registry.py` → FOUND |
| `FILE_HASH` | Dosya SHA256 değeri | `abc123...` |
| `LINE_CONTAINS` | Belirli satır belirli ifadeyi içeriyor mu? | `get_scene_for_state` → FOUND |
| `LINE_MISSING` | Belirli ifade dosyada yok mu? | `produce_and_deliver` → NOT FOUND |
| `LOG_CONTAINS` | Log'da belirli ifade var mı? | `STATE_VIDEO_DURATION_SELECTION` → FOUND |
| `LOG_MISSING` | Log'da belirli ifade yok mu? | `SceneDelivery` → NOT FOUND |
| `PROCESS_RUNNING` | Process çalışıyor mu? | PID 18268 → FOUND |
| `API_RESPONSE` | API yanıt kodu | `getMe 200 OK` → FOUND |
| `ENUM_MEMBER` | Enum'da üye var mı? | `UserState.VIDEO_DURATION_SELECTION` → FOUND |
| `REGISTRY_ENTRY` | Registry'de kayıt var mı? | `SCENE_REGISTRY[SAHNE-05]` → NOT FOUND |

---

## 9. Diff Hazırlığı

CSE **hiçbir karşılaştırma yapmaz.** Diff işlemi tamamen CDE'ye aittir.

CSE'in Diff Engine için hazırladığı veri:

```
CSE ÇIKTISI (Snapshot)          CDE GİRDİSİ (Diff için)
─────────────────────────       ─────────────────────────
ana_yasa_scenes: [...]    →     ANA YASA tarafı
code_scenes: [...]        →     Kod tarafı
registry_scenes: [...]    →     Registry tarafı
                              
CDE bu üç listeyi alır,        CDE çapraz karşılaştırır:
çapraz karşılaştırır,          - ANA YASA'da var, Registry'de yok → İHLAL
ihlalleri tespit eder.         - Registry'de var, ANA YASA'da yok → UYARI
                               - Kodda var, ANA YASA'da yok → İHLAL
```

CSE yalnızca **ham veriyi** hazırlar. Karşılaştırma mantığı, ihlal tespiti,
PASS/FAIL kararı ve rapor formatı CDE'in sorumluluğundadır.

---

## 10. Runtime Snapshot

Runtime'dan alınan bilgiler, canlı sistemin anlık durumunu yansıtır.

### 10.1 Runtime Veri Modeli

```
RUNTIME SNAPSHOT
│
├── process
│   ├── pid: int
│   ├── start_time: datetime
│   ├── working_dir: path
│   ├── python_executable: path
│   └── memory_usage: str
│
├── telegram
│   ├── bot_token_prefix: str (ilk 8 karakter)
│   ├── get_me_status: str
│   ├── get_updates_status: str
│   └── last_poll_time: datetime
│
├── session
│   ├── active_chat_ids: list[int]
│   ├── active_user_ids: list[int]
│   └── session_count: int
│
├── state
│   ├── current_state: str (son STATE geçişi)
│   ├── state_history: list[dict]
│   └── blocked_transitions: list[dict]
│
├── event
│   ├── recent_events: list[dict]
│   └── blocked_events: list[dict]
│
├── scene
│   ├── current_scene: str (son teslim edilen sahne)
│   ├── last_delivery_message_id: int
│   └── delivery_status: str
│
├── errors
│   ├── error_count: int
│   └── recent_errors: list[dict]
│
└── production
    ├── active_pids: list[str]
    └── last_production_event: dict
```

---

## 11. Snapshot Arşivi

Her tarama oturumu bir Snapshot olarak arşivlenir. Snapshot'lar zaman
içinde HLK'nın anayasal durumunun geçmişini oluşturur.

### 11.1 Arşiv Yapısı

```
ANA YASA/
└── snapshots/
    ├── SNAP-20260702-0001/
    │   ├── meta.json
    │   ├── scan_01_ana_yasa.json
    │   ├── scan_02_kod.json
    │   ├── ...
    │   └── evidence/
    ├── SNAP-20260702-0002/
    │   └── ...
    └── snapshot_index.json
```

### 11.2 Snapshot Index

```json
{
  "snapshots": [
    {
      "id": "SNAP-20260702-0001",
      "timestamp": "2026-07-02T12:45:00",
      "trigger": "FAZ-0",
      "scenes_found": 4,
      "workflows_found": 12,
      "features_found": 17,
      "runtime_status": "AKTIF"
    }
  ]
}
```

---

## 12. CSE Event Ailesi

CSE aşağıdaki yeni event'leri Olay Kayıt Merkezi'ne (14_OLAY_KAYIT_MERKEZI.md) ekler:

### OLAY-051 — SCAN_STARTED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-051` |
| **Event Adı** | `EVENT_SCAN_STARTED` |
| **Açıklama** | CSE anayasal tarama oturumunu başlattı |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | FAZ-0 / FAZ-2 / FAZ-3 başlangıcı |
| **Öncelik** | NORMAL |

### OLAY-052 — SCAN_COMPLETED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-052` |
| **Event Adı** | `EVENT_SCAN_COMPLETED` |
| **Açıklama** | CSE anayasal tarama oturumunu tamamladı, Snapshot hazır |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | Tüm 8 scan katmanı tamamlandı |
| **Öncelik** | NORMAL |

### OLAY-053 — SCAN_SOURCE_READ

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-053` |
| **Event Adı** | `EVENT_SCAN_SOURCE_READ` |
| **Açıklama** | CSE bir kaynak dosyayı başarıyla okudu |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | Her .md / .py dosyası okunduğunda |
| **Öncelik** | DÜŞÜK |

### OLAY-054 — SCAN_RUNTIME_READ

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-054` |
| **Event Adı** | `EVENT_SCAN_RUNTIME_READ` |
| **Açıklama** | CSE runtime log'larını başarıyla okudu |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | Runtime verisi okunduğunda |
| **Öncelik** | DÜŞÜK |

### OLAY-055 — SCAN_SNAPSHOT_CREATED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-055` |
| **Event Adı** | `EVENT_SCAN_SNAPSHOT_CREATED` |
| **Açıklama** | CSE yeni bir Constitution Snapshot oluşturdu |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | Snapshot başarıyla oluşturuldu |
| **Öncelik** | YÜKSEK |

### OLAY-056 — SCAN_ERROR

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-056` |
| **Event Adı** | `EVENT_SCAN_ERROR` |
| **Açıklama** | CSE tarama sırasında bir hata ile karşılaştı |
| **Üreten Bileşen** | Constitution Scan Engine (CSE) |
| **Tetikleyici** | Dosya okunamadı, parse hatası, erişim hatası |
| **Öncelik** | YÜKSEK |

---

## 13. Yeni Workflow: WF-013

### WF-013

**Workflow:** Constitution Scan

**Açıklama:** CSE tarafından yürütülen anayasal veri toplama sürecini temsil eder.
Sekiz bağımsız tarama katmanını çalıştırır, kanıt toplar ve Constitution Snapshot
üretir. CDE'e veri sağlar.

**Durum:** AKTİF

**Kullandığı Feature'lar:**
- FEAT-017 Constitution Scan Engine (CSE)
- FEAT-002 Karar Mekanizması
- FEAT-003 Durum Motoru

**Workflow Akışı:**
```
WF-CONSTITUTION-SCAN Başlatıldı
      │
      ▼
EVENT_SCAN_STARTED (OLAY-051)
      │
      ▼
┌─────────────────────────────┐
│ SCAN-1: ANA YASA Scan       │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-2: Kod Scan            │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-3: Runtime Scan        │ → EVENT_SCAN_RUNTIME_READ
├─────────────────────────────┤
│ SCAN-4: Registry Scan       │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-5: Workflow Scan       │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-6: State Scan          │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-7: Feature Scan        │ → EVENT_SCAN_SOURCE_READ
├─────────────────────────────┤
│ SCAN-8: Production Scan     │ → EVENT_SCAN_SOURCE_READ
└─────────────────────────────┘
      │
      ▼
Constitution Snapshot Oluşturulur
      │
      ▼
EVENT_SCAN_SNAPSHOT_CREATED (OLAY-055)
      │
      ▼
Snapshot → CDE'ye Aktarılır
      │
      ▼
EVENT_SCAN_COMPLETED (OLAY-052)
```

---

## 14. Yeni Feature: FEAT-017

### FEAT-017

**Türkçe Adı:** Constitution Scan Engine

**İngilizce Adı:** Constitution Scan Engine

**Kategori:** SYSTEM

**Tür:** ENGINE

**Durum:** AKTİF

**Açıklama:** HLK'nın anayasal veri toplama motorudur. Tüm ANA YASA (.md),
kod (.py) ve runtime (log) kaynaklarını tarar, kanıt toplar ve Constitution
Snapshot üretir. Sekiz bağımsız tarama katmanından oluşur (ANA YASA, Kod,
Runtime, Registry, Workflow, State, Feature, Production). Hiçbir zaman karar
vermez, PASS/FAIL üretmez. Yalnızca FOUND/NOT FOUND/UNKNOWN gözlemi yapar.
Tüm veriyi Constitution Diff Engine (CDE)'e aktarır. CDE'in veri sağlayıcısıdır.

---

## 15. Çalışma Zamanı

CSE dört farklı zamanda otomatik olarak çalışır:

| Zaman | Tetikleyici | Ürettiği Snapshot |
|---|---|---|
| **Kod geliştirme başlamadan önce** | FAZ-0 CONSTITUTION GATE | `SNAP-...-PRE` |
| **Kod geliştirme bittikten sonra** | FAZ-2 POST-CHECK | `SNAP-...-POST` |
| **Runtime Testi bittikten sonra** | FAZ-3 RUNTIME-CHECK | `SNAP-...-RUNTIME` |
| **Production öncesinde** | FAZ-3 FINAL CHECK | `SNAP-...-FINAL` |

Her çalışmada:

1. CSE sekiz scan katmanını sırayla çalıştırır.
2. Her katman kendi kaynaklarını okur.
3. Tüm bulgular kanıtlarıyla birlikte toplanır.
4. Tek bir Constitution Snapshot oluşturulur.
5. Snapshot CDE'e aktarılır.
6. CDE çapraz karşılaştırmayı yapar.

---

## 16. Çalışma Yetkisi

CSE'in yetki sınırları kesin olarak tanımlanmıştır:

| Eylem | Yetki |
|---|---|
| .md dosyalarını okumak | ✅ VAR |
| .py dosyalarını okumak | ✅ VAR |
| Log dosyalarını okumak | ✅ VAR |
| Process bilgilerini okumak | ✅ VAR |
| SHA256 hesaplamak | ✅ VAR |
| Snapshot üretmek | ✅ VAR |
| Kanıt dosyası oluşturmak | ✅ VAR |
| CDE'e veri aktarmak | ✅ VAR |
| Kod yazmak | ❌ YOK |
| Kod değiştirmek | ❌ YOK |
| ANA YASA değiştirmek | ❌ YOK |
| .md dosyası oluşturmak | ❌ YOK |
| .py dosyası oluşturmak | ❌ YOK |
| PASS kararı vermek | ❌ YOK |
| FAIL kararı vermek | ❌ YOK |
| Karar üretmek | ❌ YOK |
| Constitution Report üretmek | ❌ YOK (CDE'in görevi) |
| Constitution Task oluşturmak | ❌ YOK (CDE'in görevi) |

---

## 17. CDE Entegrasyonu

CSE ve CDE arasındaki veri akışı:

```
┌─────────────────────────────────────────────────────────┐
│                     VERİ AKIŞI                           │
│                                                         │
│  CSE                                    CDE              │
│  ┌──────────┐                          ┌──────────┐     │
│  │ SCAN-1   │──┐                       │          │     │
│  │ SCAN-2   │  │                       │ ÇAPRAZ   │     │
│  │ SCAN-3   │  │    ┌──────────────┐   │ KARŞI-   │     │
│  │ SCAN-4   │──┼───►│ CONSTITUTION │──►│ LAŞTIRMA │     │
│  │ SCAN-5   │  │    │ SNAPSHOT     │   │          │     │
│  │ SCAN-6   │  │    └──────────────┘   │ İHLAL    │     │
│  │ SCAN-7   │  │                       │ TESPİTİ  │     │
│  │ SCAN-8   │──┘                       │          │     │
│  └──────────┘                          │ PASS/    │     │
│       │                                │ FAIL     │     │
│       │  FOUND/NOT FOUND/UNKNOWN       └──────────┘     │
│       │  (gözlem)                             │          │
│       │                                (karar)  │          │
│       │                                         ▼          │
│       │                                CONSTITUTION GATE   │
│       │                                         │          │
│       │                                         ▼          │
│       │                                      Claude        │
└─────────────────────────────────────────────────────────┘
```

Her Scan tamamlandığında:

1. `EVENT_SCAN_SNAPSHOT_CREATED` (OLAY-055) tetiklenir.
2. Snapshot ID'si CDE'e iletilir.
3. CDE otomatik olarak `EVENT_CONSTITUTION_CHECK_STARTED` (OLAY-045) ile denetime başlar.
4. CDE, Snapshot içerisindeki veriyi kullanarak çapraz karşılaştırma yapar.
5. CDE, PASS veya FAIL kararını üretir.

---

## 18. MASTER Uyumluluğu

### MASTER-001 — Karar Hiyerarşisi

CSE, MASTER-001 Karar Hiyerarşisi'ne yeni bir katman eklemez. Mevcut hiyerarşide
**veri toplama katmanı** olarak konumlanır. Karar verme yetkisi yoktur.

### MASTER-003 — ANA YASA / Kod Uyumluluk Denetimi

CSE, MASTER-003'ün "Zorunlu Kontroller" (6 soru) maddesinin **veri toplama**
aşamasını oluşturur:

| MASTER-003 Sorusu | CSE Karşılığı |
|---|---|
| 1. Bu kuraldan hangi dosyalar etkileniyor? | SCAN-1 + SCAN-2 — etkilenen tüm dosyaları listeler |
| 2. Çalışan kodda bu kurala aykırı yapı var mı? | SCAN-2 — kod yapısını çıkarır (karar CDE'de) |
| 3. Hardcoded değerler mevcut mu? | SCAN-2 — sabit değerleri tespit eder (karar CDE'de) |
| 4. Eski mimari kalıntıları mevcut mu? | SCAN-4 + SCAN-8 — registry ve production'ı tarar |
| 5. Runtime davranışı yeni kuralla uyumlu mu? | SCAN-3 — runtime log'larını toplar (karar CDE'de) |
| 6. Hangi dosyalar güncellenmeli? | Tüm SCAN'lar — etkilenen dosyaları listeler (karar CDE'de) |

CSE soruları **cevaplamaz.** Soruların cevaplanması için gerekli **ham veriyi**
toplar. Cevaplar CDE tarafından üretilir.

### MASTER-004 — Karar Mekanizması ve Kural Otoritesi

CSE, MASTER-004 gereği:

- bağımsız karar verici değil,
- HLK'nın karar mekanizmasını yönlendiren veri toplama katmanıdır.

---

## 19. CSE Çalışma Prensibi (Özet)

```
┌──────────────────────────────────────────────────────────┐
│               CONSTITUTION SCAN ENGINE                    │
│                                                          │
│  GİRDİ:                                                   │
│  - Tüm ANA YASA .md dosyaları                             │
│  - Tüm proje .py dosyaları                                │
│  - Runtime log dosyaları                                  │
│  - Process bilgileri                                      │
│                                                          │
│  İŞLEM:                                                   │
│  1. SCAN-1: ANA YASA'yı tara                              │
│  2. SCAN-2: Kodu tara                                     │
│  3. SCAN-3: Runtime'ı tara                                │
│  4. SCAN-4: Registry'yi tara                              │
│  5. SCAN-5: Workflow'ları tara                            │
│  6. SCAN-6: State'leri tara                               │
│  7. SCAN-7: Feature'ları tara                             │
│  8. SCAN-8: Production'ı tara                             │
│  9. Constitution Snapshot oluştur                         │
│  10. Snapshot'ı CDE'e aktar                               │
│                                                          │
│  ÇIKTI:                                                   │
│  - Constitution Snapshot (SNAP-YYYYMMDD-NNNN)             │
│  - Her bulgu için kanıt (EVID-YYYYMMDD-NNNN)              │
│  - FOUND / NOT FOUND / UNKNOWN gözlemleri                 │
│                                                          │
│  KISITLAMA:                                               │
│  - PASS/FAIL üretmez                                      │
│  - Karar vermez                                           │
│  - Kod yazmaz                                             │
│  - Kod değiştirmez                                        │
│  - ANA YASA'yı değiştirmez                                │
└──────────────────────────────────────────────────────────┘
```

---

## 20. Temel İlke

CSE, HLK'nın anayasal veri toplama katmanıdır.

CSE'in görevi;

- Tüm ANA YASA, kod ve runtime kaynaklarını taramak,
- Her bulguyu kanıtıyla birlikte kaydetmek,
- Tek bir Constitution Snapshot üretmek,
- Snapshot'ı CDE'e aktarmak,
- Geliştirme öncesi, sonrası, runtime sonrası ve production öncesi otomatik çalışmaktır.

CSE'in görevi;

- Karar vermek,
- PASS/FAIL üretmek,
- Kod yazmak,
- Kod değiştirmek,
- ANA YASA'yı değiştirmek

**değildir.**

CSE olmadan CDE'in karşılaştırma yapacağı veri bulunmaz.
CDE olmadan CSE'in topladığı veri tek başına anlam ifade etmez.
**İki modül birlikte çalışır.**

---

## 21. Anayasal Yetki

Bu dosya, MASTER-001 Karar Hiyerarşisi'nde tanımlanan otorite sıralamasına tabidir.

Bu dosya;

- MASTER RULE BOOK'u uygulamak için vardır.
- MASTER RULE BOOK bu dosyayı uygulamak için var değildir.

CSE, MASTER-004 (HLK Karar Mekanizması ve Kural Otoritesi Prensibi) gereği:

- bağımsız karar verici değil,
- HLK'nın karar mekanizmasına veri sağlayan toplama katmanıdır.

---

## 22. CSE ↔ CDE Görev Paylaşımı (Referans Tablo)

Bu tablo, CSE ve CDE arasındaki sorumluluk sınırlarını kesin olarak tanımlar.
Gelecekte bu iki modülün görevlerinin karışmasını önleyecek referans bölümdür.

| Görev | CSE (19) | CDE (18) | Açıklama |
|---|---|---|---|
| **ANA YASA .md okumak** | ✅ YAPAR | ❌ YAPMAZ | CSE okur, CDE sonuçları kullanır |
| **Kod .py okumak** | ✅ YAPAR | ❌ YAPMAZ | CSE okur, CDE sonuçları kullanır |
| **Runtime log okumak** | ✅ YAPAR | ❌ YAPMAZ | CSE okur, CDE sonuçları kullanır |
| **Process bilgisi toplamak** | ✅ YAPAR | ❌ YAPMAZ | PID, başlangıç zamanı, working dir |
| **SHA256 hesaplamak** | ✅ YAPAR | ❌ YAPMAZ | Kanıt için dosya hash'leri |
| **Snapshot üretmek** | ✅ YAPAR | ❌ YAPMAZ | SNAP-YYYYMMDD-NNNN |
| **Kanıt dosyası oluşturmak** | ✅ YAPAR | ❌ YAPMAZ | EVID-YYYYMMDD-NNNN |
| **FOUND/NOT FOUND/UNKNOWN** | ✅ YAPAR | ❌ YAPMAZ | Gözlem — karar değil |
| **Çapraz karşılaştırma** | ❌ YAPMAZ | ✅ YAPAR | ANA YASA ↔ Kod ↔ Runtime |
| **İhlal tespiti** | ❌ YAPMAZ | ✅ YAPAR | CONSTITUTIONAL_VIOLATION |
| **PASS/FAIL kararı** | ❌ YAPMAZ | ✅ YAPAR | CONSTITUTION GATE |
| **Constitution Report** | ❌ YAPMAZ | ✅ YAPAR | MASTER-003 formatında rapor |
| **Constitution Task** | ❌ YAPMAZ | ✅ YAPAR | TASK-CD-YYYYMMDD-NNNN |
| **Kod yazmak** | ❌ YAPMAZ | ❌ YAPMAZ | İkisi de yazmaz |
| **Kod değiştirmek** | ❌ YAPMAZ | ❌ YAPMAZ | İkisi de değiştirmez |
| **ANA YASA değiştirmek** | ❌ YAPMAZ | ❌ YAPMAZ | MASTER-001: sadece Proje Yöneticisi |
| **Karar vermek** | ❌ YAPMAZ | ❌ YAPMAZ | MASTER-004: sadece HLK |
| **Event üretmek** | ✅ YAPAR | ✅ YAPAR | CSE: OLAY-051/056, CDE: OLAY-045/050 |
| **Workflow çalıştırmak** | ✅ YAPAR | ✅ YAPAR | CSE: WF-013, CDE: WF-012 |
| **Feature kaydı** | FEAT-017 | FEAT-016 | İkisi de SYSTEM/ENGINE |

### Veri Akış Yönü

```
CSE (19)                        CDE (18)
───────                         ───────
ANA YASA okur ──────────────►   ANA YASA verisini alır
Kod okur     ──────────────►   Kod verisini alır
Runtime okur ──────────────►   Runtime verisini alır
Snapshot     ──────────────►   Snapshot'tan okur
FOUND/NOT    ──────────────►   İhlal tespitinde kullanır
Kanıt        ──────────────►   Raporlamada kullanır
              ◄──────────────   PASS/FAIL (CSE'e dönmez)
              ◄──────────────   Report (CSE'e dönmez)
              ◄──────────────   Task (CSE'e dönmez)
```

**Veri akışı tek yönlüdür:** CSE → CDE. CDE'den CSE'e geri bildirim yoktur.
CSE taramayı yapar, veriyi iletir ve görevi biter. Tüm değerlendirme CDE'dedir.

---

## 23. Final — CSE Tek Başına Karar Verebilir mi?

**Hayır.**

CSE yalnızca anayasal kanıtları toplar, Constitution Snapshot oluşturur ve
bunları Constitution Diff Engine'e (CDE) aktarır. CSE'in ürettiği FOUND /
NOT FOUND / UNKNOWN değerleri birer **gözlemdir,** karar değildir.

PASS/FAIL kararı yalnızca CDE tarafından, Constitution Gate süreci içinde verilir.
CSE bu kararın **veri altyapısını** sağlar, ancak kararın kendisini üretmez.

CSE olmadan CDE eksik veriyle karar verir.
CDE olmadan CSE topladığı veriyi değerlendirecek bir mekanizmaya sahip değildir.
**İki modül birbirini tamamlar.**

---

**Hazırlayan:** HLK — Claude Code  
**Tarih:** 2026-07-02  
**Referans:** MASTER-001, MASTER-003, MASTER-004, MASTER-006  
**Bağlı Modül:** 18_CONSTITUTION_DIFF_ENGINE.md (CDE) — veri sağlayıcısı
