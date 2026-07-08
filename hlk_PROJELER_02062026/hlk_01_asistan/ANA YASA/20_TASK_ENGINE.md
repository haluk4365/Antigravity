# 20 — Task Engine

HLK'nın anayasal görev yönetim katmanıdır. Constitution Diff Engine (CDE)
tarafından üretilen Constitution Task'ları okur, önceliklendirir, geliştirme
paketine dönüştürür, Claude'a iletir ve geliştirme tamamlandıktan sonra sonucu
Constitution Gate'e geri gönderir.

Task Engine **hiçbir zaman kod yazmaz, karar vermez, PASS/FAIL üretmez.**
Yalnızca anayasal görevleri yönetir.

---

## 1. Amaç

Task Engine'in tek görevi; HLK'nın anayasal geliştirme sürecindeki görev
yaşam döngüsünü yönetmektir.

Task Engine;

- CDE'den gelen Constitution Task'ları (TASK-CD-YYYYMMDD-NNNN) okur,
- Görevleri öncelik sırasına göre sıralar,
- Bağımlılıkları çözümler,
- Birleştirilebilir görevleri tek pakette toplar,
- Büyük görevleri alt görevlere böler,
- Her görevi bir Task Package'e dönüştürür,
- Claude'a uygulanmak üzere Task Execution Package hazırlar,
- Geliştirme tamamlandığında sonucu alır,
- Sonucu Constitution Gate'e (POST-CHECK) iletir,
- Görev geçmişini kaydeder.

Task Engine;

- Kod yazmaz,
- Kod değiştirmez,
- Karar vermez,
- PASS/FAIL üretmez,
- Constitution Gate yerine geçmez,
- Yeni bir otorite oluşturmaz.

---

## 2. Mimari Konum

Task Engine, Constitution Gate ile Claude arasında konumlanan **görev yönetim
katmanıdır.**

```
ANA YASA (.md) ────┐
                   │
Kod (.py)     ────┤
                   ├──► CSE ──► CDE ──► CONSTITUTION GATE
Runtime (log) ────┘                            │
                                               ▼
                                        TASK ENGINE
                                               │
                                               ▼
                                            Claude
                                               │
                                               ▼
                                        Kod Geliştirme
                                               │
                                               ▼
                                        CONSTITUTION GATE
                                        (POST-CHECK)
```

Task Engine, CDE ile Claude arasındaki **tek resmi geçiş noktasıdır.**
CDE'den gelen hiçbir görev doğrudan Claude'a iletilemez — Task Engine
tarafından işlenmek zorundadır.

---

## 3. Yetki Alanı

| Eylem | Yetki |
|---|---|
| Constitution Task okumak | ✅ VAR |
| Görev önceliklendirmek | ✅ VAR |
| Görev bağımlılıklarını çözmek | ✅ VAR |
| Görev birleştirmek | ✅ VAR |
| Görev parçalamak | ✅ VAR |
| Task Package oluşturmak | ✅ VAR |
| Task Execution Package hazırlamak | ✅ VAR |
| Claude'a görev iletmek | ✅ VAR |
| Görev sonucunu almak | ✅ VAR |
| Görev geçmişini kaydetmek | ✅ VAR |
| Kod yazmak | ❌ YOK |
| Kod değiştirmek | ❌ YOK |
| PASS/FAIL kararı vermek | ❌ YOK |
| Constitution Gate yerine geçmek | ❌ YOK |
| ANA YASA değiştirmek | ❌ YOK |
| Yeni Constitution Task oluşturmak | ❌ YOK (CDE'in görevi) |

---

## 4. Yetkisiz Olduğu İşlemler

Task Engine aşağıdaki işlemleri **kesinlikle yapamaz:**

1. **Kod yazamaz.** Görev paketini hazırlar, ancak uygulamayı Claude yapar.
2. **Kod değiştiremez.** Hiçbir .py dosyasına müdahale edemez.
3. **PASS veremez.** Anayasal uygunluk kararı yalnızca Constitution Gate'indir.
4. **FAIL veremez.** İhlal tespiti yalnızca CDE'indir.
5. **Yeni Constitution Task oluşturamaz.** Görevleri yalnızca CDE üretir.
6. **ANA YASA değiştiremez.** MASTER-001 gereği yalnızca Proje Yöneticisi.
7. **Snapshot üretemez.** Bu CSE'in görevidir.
8. **Çapraz karşılaştırma yapamaz.** Bu CDE'in görevidir.

---

## 5. Görevleri

Task Engine'in sistem içerisindeki görevleri:

| # | Görev | Girdi | Çıktı |
|---|---|---|---|
| 1 | Constitution Task oku | `TASK-CD-YYYYMMDD-NNNN` (CDE'den) | Task objesi |
| 2 | Öncelik belirle | Task objesi | Öncelik seviyesi (KRİTİK/YÜKSEK/ORTA/DÜŞÜK) |
| 3 | Bağımlılık çözümle | Task listesi | Bağımlılık ağacı |
| 4 | Birleştir | Aynı dosyayı etkileyen task'lar | Birleştirilmiş Task Package |
| 5 | Parçala | Çok büyük task (>5 dosya) | Alt Task Package'ler |
| 6 | Task Execution Package oluştur | Task Package | Claude'a hazır görev paketi |
| 7 | Claude'a ilet | Task Execution Package | Geliştirme başlangıcı |
| 8 | Sonucu al | Claude çıktısı | Task Result |
| 9 | Constitution Gate'e ilet | Task Result | POST-CHECK tetikleyici |
| 10 | Geçmişi kaydet | Task Result | Task History |

---

## 6. Constitution Task Formatı (CDE Çıktısı → Task Engine Girdisi)

CDE tarafından üretilen ve Task Engine'in okuduğu standart format:

```json
{
  "task_id": "TASK-CD-20260702-0001",
  "source_report": "CDE-20260702-0001",
  "priority": "KRITIK",
  "created_at": "2026-07-02T12:45:00",
  "violations": [
    {
      "type": "SCENE_MISSING_IN_REGISTRY",
      "severity": "KRITIK",
      "target": "SAHNE-05",
      "ana_yasa_ref": "08_HLK_FLOW_DIAGRAM.md:141",
      "code_file": "services/scene_registry.py",
      "code_line": 129,
      "evidence_id": "EVID-20260702-0001"
    },
    {
      "type": "SCENE_DELIVERY_NOT_CALLED",
      "severity": "KRITIK",
      "target": "handle_resolution_selection()",
      "ana_yasa_ref": "04_Operational_Rules.md (OR-004_2)",
      "code_file": "handlers/website.py",
      "code_line": 311,
      "evidence_id": "EVID-20260702-0002"
    }
  ],
  "affected_layers": {
    "state_engine": ["STATE_VIDEO_DURATION_SELECTION"],
    "scene_registry": ["SAHNE-05"],
    "handler": ["handle_resolution_selection"],
    "workflow": ["WF-003"],
    "feature": ["FEAT-003"],
    "event": ["EVENT_RESOLUTION_SELECTED"]
  },
  "required_actions": [
    {
      "action": "ADD_SCENE_DEFINITION",
      "file": "services/scene_registry.py",
      "line": 129,
      "detail": "SAHNE-05 SceneDefinition ekle (state=VIDEO_DURATION_SELECTION)"
    },
    {
      "action": "ADD_DELIVERY_CHAIN",
      "file": "handlers/website.py",
      "line": 311,
      "detail": "get_scene_for_state() + cleanup_chat() + produce_and_deliver() ekle"
    },
    {
      "action": "UPDATE_ANA_YASA",
      "file": "ANA YASA/17_SAHNE_KAYIT_DEFTERİ.md",
      "detail": "SAHNE-05 kaydı ekle"
    }
  ],
  "related_ana_yasa": [
    "08_HLK_FLOW_DIAGRAM.md (FD-008_1 SAHNE-05)",
    "07_HLK_STATE_ENGINE.md (SE-007_3/4/5)",
    "17_SAHNE_KAYIT_DEFTERİ.md",
    "MASTER-003"
  ]
}
```

---

## 7. Task Yaşam Döngüsü

Her Task, aşağıdaki standart yaşam döngüsünü izler:

```
┌─────────────────────────────────────────────────────────┐
│                  TASK YAŞAM DÖNGÜSÜ                       │
│                                                         │
│  1. CREATED                                              │
│     CDE tarafından oluşturuldu                           │
│     │                                                    │
│     ▼                                                    │
│  2. RECEIVED                                             │
│     Task Engine tarafından alındı                        │
│     │                                                    │
│     ▼                                                    │
│  3. ANALYZING                                            │
│     Öncelik, bağımlılık, birleştirme analizi             │
│     │                                                    │
│     ├── Birleştirilebilir → MERGED                       │
│     ├── Çok büyük → SPLIT                                │
│     └── Normal → devam                                   │
│     │                                                    │
│     ▼                                                    │
│  4. PACKAGING                                            │
│     Task Package oluşturuluyor                           │
│     │                                                    │
│     ▼                                                    │
│  5. WAITING                                              │
│     Bağımlılıklar çözülene kadar beklemede               │
│     │                                                    │
│     ▼                                                    │
│  6. ASSIGNED                                             │
│     Claude'a atandı                                      │
│     │                                                    │
│     ▼                                                    │
│  7. LOCKED                                               │
│     Görev kilitlendi, başka kimse dokunamaz              │
│     │                                                    │
│     ▼                                                    │
│  8. IN_PROGRESS                                          │
│     Claude geliştirmeyi yapıyor                          │
│     │                                                    │
│     ├── Başarılı → COMPLETED                             │
│     ├── Hata → FAILED → yeniden ASSIGNED                 │
│     └── İptal → CANCELLED                                │
│     │                                                    │
│     ▼                                                    │
│  9. COMPLETED                                            │
│     Geliştirme tamamlandı                                │
│     │                                                    │
│     ▼                                                    │
│  10. VERIFYING                                           │
│      Sonuç Constitution Gate'e gönderildi                │
│      │                                                   │
│      ├── PASS → CLOSED                                   │
│      └── FAIL → yeniden ASSIGNED                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Task Öncelik Sistemi

Task Engine, görevleri aşağıdaki öncelik matrisine göre sıralar:

| Öncelik | Teknik Sabit | Puan | Kriter |
|---|---|---|---|
| KRİTİK | `PRIORITY_CRITICAL` | 100 | MASTER kuralı ihlali, State Engine'de eksik state/event, Scene Registry'de eksik sahne |
| YÜKSEK | `PRIORITY_HIGH` | 75 | Handler'da delivery zinciri eksik, transition tanımsız, cleanup çağrısı eksik |
| ORTA | `PRIORITY_MEDIUM` | 50 | Feature kaydı eksik, Workflow manifest'te eksik WF, dokümantasyon referansı eksik |
| DÜŞÜK | `PRIORITY_LOW` | 25 | Yazım hatası, format sorunu, isteğe bağlı optimizasyon |

### Öncelik Hesaplama

```
TaskPriority = MAX(violation.severity_score) 
             + (violation_count × 5)
             + (affected_layers_count × 3)
             + (dependency_count × 10)

Örnek:
TASK-CD-20260702-0001:
  MAX severity: KRİTİK = 100
  violation_count: 2 × 5 = 10
  affected_layers: 6 × 3 = 18
  dependency_count: 0 × 10 = 0
  Toplam: 128 → KRİTİK
```

---

## 9. Task Queue

Task Engine, üç seviyeli bir kuyruk sistemi kullanır:

```
┌─────────────────────────────────────────────┐
│              TASK QUEUE                      │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Q1: READY QUEUE                    │    │
│  │  Bağımlılığı çözülmüş, bekleyen     │    │
│  │  görevler. Öncelik sırasına göre.   │    │
│  │  [KRİTİK-001] [YÜKSEK-003] [...]    │    │
│  └─────────────────────────────────────┘    │
│              │                              │
│              ▼                              │
│  ┌─────────────────────────────────────┐    │
│  │  Q2: WAITING QUEUE                  │    │
│  │  Bağımlılığı olan, bekleyen görevler│    │
│  │  [ORTA-005 → KRİTİK-001 bekliyor]   │    │
│  └─────────────────────────────────────┘    │
│              │                              │
│              ▼                              │
│  ┌─────────────────────────────────────┐    │
│  │  Q3: ACTIVE QUEUE                   │    │
│  │  Şu anda işlenmekte olan görev      │    │
│  │  Aynı anda en fazla 1 görev         │    │
│  │  [LOCKED: KRİTİK-001]               │    │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

### Kuyruk Kuralları

1. Aynı anda yalnızca **1 görev** ACTIVE durumda olabilir.
2. READY kuyruğu öncelik sırasına göre işlenir.
3. WAITING kuyruğundaki görevler bağımlılıkları çözüldüğünde READY'e taşınır.
4. Aynı dosyayı etkileyen görevler birleştirilir.
5. 5'ten fazla dosyayı etkileyen görevler parçalanır.

---

## 10. Task Kilitleme

Bir görev Claude'a atandığında **kilitlenir.** Kilit, aynı dosyaların başka
bir görev tarafından değiştirilmesini engeller.

### Kilit Modeli

```
TASK LOCK
│
├── lock_id: LOCK-YYYYMMDD-NNNN
├── task_id: TASK-CD-YYYYMMDD-NNNN
├── locked_files: ["services/scene_registry.py", "handlers/website.py"]
├── locked_at: "2026-07-02T12:45:00"
├── locked_by: "Claude"
├── expires_at: "2026-07-02T13:45:00"  (60 dakika timeout)
└── status: ACTIVE / EXPIRED / RELEASED
```

### Kilit Kuralları

1. Bir dosya aynı anda yalnızca bir görev tarafından kilitlenebilir.
2. Kilit süresi 60 dakikadır. Aşımında EXPIRED olur.
3. Görev tamamlandığında kilit otomatik RELEASED olur.
4. EXPIRED kilitler Task Engine tarafından temizlenir.
5. Kilitli dosyayı etkileyen yeni görevler WAITING kuyruğuna alınır.

---

## 11. Task Bağımlılıkları

Görevler arası bağımlılıklar otomatik tespit edilir ve çözümlenir.

### Bağımlılık Türleri

| Tür | Teknik Sabit | Açıklama | Örnek |
|---|---|---|---|
| Dosya Bağımlılığı | `DEP_FILE` | Aynı dosyayı değiştiren görevler | SAHNE-05 → SAHNE-06 aynı dosya |
| State Bağımlılığı | `DEP_STATE` | Önceki state'in tamamlanması gerekir | DURATION_SELECTION → AUDIO_SELECTION |
| Feature Bağımlılığı | `DEP_FEATURE` | Feature'ın kaydı önce tamamlanmalı | FEAT-016 → FEAT-017 |
| Workflow Bağımlılığı | `DEP_WORKFLOW` | Workflow önce tanımlanmalı | WF-012 → WF-013 |

### Bağımlılık Çözümleme

```
TASK-CD-0001 (SAHNE-05 ekle)
      │
      ├──► TASK-CD-0002 (SAHNE-06 ekle) → DEP_FILE: scene_registry.py
      │                                     DEP_STATE: DURATION_SELECTION
      │
      └──► TASK-CD-0003 (handle_duration) → DEP_FILE: handlers/website.py
                                            DEP_STATE: DURATION_SELECTION

Çözümleme:
  1. TASK-CD-0001 → READY (bağımlılık yok)
  2. TASK-CD-0002 → WAITING (DEP_STATE: TASK-CD-0001 bekleniyor)
  3. TASK-CD-0003 → WAITING (DEP_STATE: TASK-CD-0001 bekleniyor)
```

---

## 12. Task Birleştirme

Aynı dosyayı etkileyen ve birbirini dışlamayan görevler birleştirilir.

### Birleştirme Kuralları

```
Birleştirilebilir:
  ✅ Aynı .py dosyasını değiştiren görevler
  ✅ Aynı state'i etkileyen görevler
  ✅ Aynı ANA YASA referansını kullanan görevler
  ✅ Birleşme sonucu 5 dosyayı geçmiyorsa

Birleştirilemez:
  ❌ Farklı katmanları etkileyen görevler (örn. handler + state engine)
  ❌ Birleşme sonucu 5'ten fazla dosya etkileniyorsa → PARÇALA
  ❌ Birbirini dışlayan değişiklikler
```

### Birleştirme Örneği

```
TASK-CD-0001: scene_registry.py SAHNE-05 ekle
TASK-CD-0002: scene_registry.py SAHNE-06 ekle

→ BİRLEŞTİR → MERGED-0001:
  scene_registry.py: SAHNE-05 + SAHNE-06 SceneDefinition ekle
  (2 sahne, 30 satır, tek dosya)
```

---

## 13. Task Parçalama

5'ten fazla dosyayı etkileyen görevler alt görevlere bölünür.

### Parçalama Kuralları

```
Parçala eğer:
  - Etkilenen dosya sayısı > 5
  - Tahmini işlem süresi > 60 dakika
  - Birden fazla bağımsız katman etkileniyor

Parçalama stratejisi:
  1. Katman bazında grupla (handler'lar, registry, state engine, ...)
  2. Her grubu bağımsız alt görev yap
  3. Alt görevler arası bağımlılık zinciri oluştur
```

---

## 14. Task Durumları

| Durum | Teknik Sabit | Açıklama |
|---|---|---|
| `CREATED` | `TASK_STATUS_CREATED` | CDE tarafından oluşturuldu, henüz Task Engine'de değil |
| `RECEIVED` | `TASK_STATUS_RECEIVED` | Task Engine tarafından alındı |
| `ANALYZING` | `TASK_STATUS_ANALYZING` | Öncelik, bağımlılık, birleştirme analizi yapılıyor |
| `MERGED` | `TASK_STATUS_MERGED` | Başka görev(ler) ile birleştirildi |
| `SPLIT` | `TASK_STATUS_SPLIT` | Alt görevlere bölündü |
| `PACKAGING` | `TASK_STATUS_PACKAGING` | Task Package oluşturuluyor |
| `WAITING` | `TASK_STATUS_WAITING` | Bağımlılıkların çözülmesi bekleniyor |
| `ASSIGNED` | `TASK_STATUS_ASSIGNED` | Claude'a atandı |
| `LOCKED` | `TASK_STATUS_LOCKED` | Görev kilitlendi, aktif olarak işleniyor |
| `IN_PROGRESS` | `TASK_STATUS_IN_PROGRESS` | Claude geliştirmeyi yapıyor |
| `COMPLETED` | `TASK_STATUS_COMPLETED` | Geliştirme tamamlandı |
| `VERIFYING` | `TASK_STATUS_VERIFYING` | Constitution Gate doğrulaması yapılıyor |
| `CLOSED` | `TASK_STATUS_CLOSED` | Görev başarıyla kapatıldı (PASS alındı) |
| `FAILED` | `TASK_STATUS_FAILED` | Geliştirme sırasında hata oluştu |
| `CANCELLED` | `TASK_STATUS_CANCELLED` | Görev iptal edildi |

### Durum Geçiş Diyagramı

```
CREATED ──► RECEIVED ──► ANALYZING ──┬──► PACKAGING ──► WAITING
                                      │                      │
                                      ├──► MERGED             ▼
                                      └──► SPLIT          ASSIGNED
                                                             │
                                                             ▼
                                                           LOCKED
                                                             │
                                                             ▼
                                                       IN_PROGRESS
                                                             │
                                              ┌──────────────┼──────────────┐
                                              ▼              ▼              ▼
                                          COMPLETED       FAILED        CANCELLED
                                              │              │              │
                                              ▼              ▼              ▼
                                          VERIFYING     yeniden        CLOSED
                                              │         ASSIGNED
                                        ┌─────┴─────┐
                                        ▼           ▼
                                      CLOSED    yeniden
                                      (PASS)    ASSIGNED
                                                (FAIL)
```

---

## 15. Task Event Ailesi

Task Engine aşağıdaki yeni event'leri Olay Kayıt Merkezi'ne (14_OLAY_KAYIT_MERKEZI.md) ekler:

### OLAY-057 — TASK_CREATED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-057` |
| **Event Adı** | `EVENT_TASK_CREATED` |
| **Açıklama** | CDE tarafından yeni bir Constitution Task oluşturuldu, Task Engine'e iletildi |
| **Üreten Bileşen** | Task Engine (CDE'den alır) |
| **Tetikleyici** | CDE → CONSTITUTIONAL_VIOLATION_FOUND (OLAY-047) |
| **Öncelik** | YÜKSEK |
| **İlişkili Veri** | `task_id`, `source_report`, `priority` |

### OLAY-058 — TASK_ASSIGNED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-058` |
| **Event Adı** | `EVENT_TASK_ASSIGNED` |
| **Açıklama** | Görev Claude'a atandı |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | READY kuyruğundan ACTIVE kuyruğuna geçiş |
| **Öncelik** | NORMAL |
| **İlişkili Veri** | `task_id`, `assigned_to`, `locked_files` |

### OLAY-059 — TASK_STARTED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-059` |
| **Event Adı** | `EVENT_TASK_STARTED` |
| **Açıklama** | Claude görev üzerinde çalışmaya başladı |
| **Üreten Bileşen** | Task Engine (Claude'dan alır) |
| **Tetikleyici** | IN_PROGRESS durumuna geçiş |
| **Öncelik** | NORMAL |
| **İlişkili Veri** | `task_id`, `started_at` |

### OLAY-060 — TASK_LOCKED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-060` |
| **Event Adı** | `EVENT_TASK_LOCKED` |
| **Açıklama** | Görev kilitlendi, etkilenen dosyalara başka görev dokunamaz |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | LOCKED durumuna geçiş |
| **Öncelik** | YÜKSEK |
| **İlişkili Veri** | `lock_id`, `locked_files`, `expires_at` |

### OLAY-061 — TASK_COMPLETED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-061` |
| **Event Adı** | `EVENT_TASK_COMPLETED` |
| **Açıklama** | Geliştirme tamamlandı, sonuçlar Task Engine'e iletildi |
| **Üreten Bileşen** | Task Engine (Claude'dan alır) |
| **Tetikleyici** | COMPLETED durumuna geçiş |
| **Öncelik** | YÜKSEK |
| **İlişkili Veri** | `task_id`, `completed_at`, `changed_files`, `result_summary` |

### OLAY-062 — TASK_FAILED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-062` |
| **Event Adı** | `EVENT_TASK_FAILED` |
| **Açıklama** | Geliştirme sırasında hata oluştu, görev başarısız |
| **Üreten Bileşen** | Task Engine (Claude'dan alır) |
| **Tetikleyici** | FAILED durumuna geçiş |
| **Öncelik** | YÜKSEK |
| **İlişkili Veri** | `task_id`, `failed_at`, `error_reason` |

### OLAY-063 — TASK_WAITING

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-063` |
| **Event Adı** | `EVENT_TASK_WAITING` |
| **Açıklama** | Görev bağımlılıklar nedeniyle beklemede |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | WAITING durumuna geçiş |
| **Öncelik** | DÜŞÜK |
| **İlişkili Veri** | `task_id`, `waiting_for: [task_ids]` |

### OLAY-064 — TASK_CANCELLED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-064` |
| **Event Adı** | `EVENT_TASK_CANCELLED` |
| **Açıklama** | Görev iptal edildi |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | CANCELLED durumuna geçiş |
| **Öncelik** | NORMAL |
| **İlişkili Veri** | `task_id`, `cancelled_at`, `reason` |

### OLAY-065 — TASK_MERGED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-065` |
| **Event Adı** | `EVENT_TASK_MERGED` |
| **Açıklama** | Birden fazla görev tek bir Task Package'te birleştirildi |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | MERGED durumuna geçiş |
| **Öncelik** | DÜŞÜK |
| **İlişkili Veri** | `merged_id`, `source_task_ids: [ids]` |

### OLAY-066 — TASK_CLOSED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-066` |
| **Event Adı** | `EVENT_TASK_CLOSED` |
| **Açıklama** | Görev başarıyla kapatıldı, Constitution Gate PASS aldı |
| **Üreten Bileşen** | Task Engine |
| **Tetikleyici** | CLOSED durumuna geçiş (VERIFYING → PASS → CLOSED) |
| **Öncelik** | NORMAL |
| **İlişkili Veri** | `task_id`, `closed_at`, `gate_result: PASS` |

---

## 16. Workflow Entegrasyonu

### WF-014 — Task Execution Workflow

**Workflow:** Task Execution

**Açıklama:** Task Engine tarafından yürütülen görev yaşam döngüsü sürecini
temsil eder. CDE'den gelen Constitution Task'ı alır, işler, Claude'a iletir
ve sonucu Constitution Gate'e geri gönderir.

**Durum:** AKTİF

**Kullandığı Feature'lar:**
- FEAT-018 Task Engine
- FEAT-002 Karar Mekanizması
- FEAT-003 Durum Motoru

**Workflow Akışı:**
```
WF-TASK-EXECUTION Başlatıldı
      │
      ▼
EVENT_TASK_CREATED (OLAY-057)
      │
      ▼
┌─────────────────────────────┐
│ ANALYZING                    │
│ - Öncelik hesapla           │
│ - Bağımlılık çözümle        │
│ - Birleştir / Parçala       │
└─────────────────────────────┘
      │
      ├── Birleştir → EVENT_TASK_MERGED (OLAY-065)
      ├── Parçala   → Alt task'lar oluştur
      └── Normal    → devam
      │
      ▼
┌─────────────────────────────┐
│ PACKAGING                    │
│ - Task Package oluştur      │
│ - Dosya listesi çıkar       │
│ - Execution plan hazırla    │
└─────────────────────────────┘
      │
      ├── Bağımlılık var → EVENT_TASK_WAITING (OLAY-063)
      │                    │
      │                    └── Bağımlılık çözüldü → devam
      │
      └── Bağımlılık yok → devam
      │
      ▼
EVENT_TASK_ASSIGNED (OLAY-058)
      │
      ▼
EVENT_TASK_LOCKED (OLAY-060)
      │
      ▼
EVENT_TASK_STARTED (OLAY-059)
      │
      ▼
┌─────────────────────────────┐
│ IN_PROGRESS (Claude)        │
│ - Kod analizi               │
│ - Kod geliştirme            │
│ - Dosya değişiklikleri      │
└─────────────────────────────┘
      │
      ├── Başarılı → EVENT_TASK_COMPLETED (OLAY-061)
      │              │
      │              ▼
      │         ┌─────────────────────────────┐
      │         │ VERIFYING (Constitution Gate)│
      │         └─────────────────────────────┘
      │              │
      │              ├── PASS → EVENT_TASK_CLOSED (OLAY-066)
      │              └── FAIL → yeniden ASSIGNED
      │
      ├── Hata → EVENT_TASK_FAILED (OLAY-062)
      │           │
      │           └── yeniden ASSIGNED
      │
      └── İptal → EVENT_TASK_CANCELLED (OLAY-064)
                   │
                   └── EVENT_TASK_CLOSED (OLAY-066)
```

---

## 17. Runtime Davranışı

Task Engine, bot polling sırasında değil, **geliştirme talebi geldiğinde**
çalışır. Runtime davranışı aşağıdaki tetikleyicilere bağlıdır:

| Tetikleyici | Davranış |
|---|---|
| `EVENT_CONSTITUTION_PASS` (OLAY-049) | Task Engine devreye girer, CDE'den gelen task'ları okur |
| `EVENT_CONSTITUTION_FAIL` (OLAY-050) | Task Engine BEKLER. FAIL durumunda görev dağıtılmaz. |
| `EVENT_TASK_COMPLETED` (OLAY-061) | Sonuç alınır, POST-CHECK tetiklenir |
| Manuel geliştirme talebi | Task Engine varsa sıradaki görevi hazırlar |

---

## 18. Production Davranışı

Production ortamında Task Engine aşağıdaki kurallarla çalışır:

1. **Tüm görevler CLOSED olmadan Production'a geçilmez.**
2. Açık görev varsa, CDE-005 (FAZ-3) FAIL verir.
3. Production'da Task Engine pasiftir — yeni görev dağıtılmaz.
4. Production'da yalnızca acil düzeltme (hotfix) görevleri işlenir.
5. Hotfix görevleri normal task yaşam döngüsünü izler.

---

## 19. Constitution Gate Entegrasyonu

Task Engine, Constitution Gate ile iki yönlü çalışır:

```
CONSTITUTION GATE (PASS)
      │
      ▼
TASK ENGINE (görevi hazırla)
      │
      ▼
CLAUDE (geliştir)
      │
      ▼
TASK ENGINE (sonucu al)
      │
      ▼
CONSTITUTION GATE (POST-CHECK)
      │
      ├── PASS → CLOSED
      └── FAIL → TASK ENGINE (yeniden ata)
```

**Kural:** Task Engine, Constitution Gate PASS vermeden Claude'a görev iletemez.
Constitution Gate FAIL durumunda Task Engine pasiftir.

---

## 20. CSE Entegrasyonu

Task Engine, CSE'den Snapshot bilgisini alır:

| CSE Çıktısı | Task Engine Kullanımı |
|---|---|
| `SNAP-...-PRE` | Geliştirme öncesi referans noktası |
| `SNAP-...-POST` | Geliştirme sonrası karşılaştırma referansı |
| Snapshot → `code_scenes` | Hangi sahnelerin mevcut olduğu |
| Snapshot → `registry_scenes` | Hangi sahnelerin kayıtlı olduğu |

---

## 21. CDE Entegrasyonu

Task Engine, CDE'den Constitution Task'ları alır:

```
CDE (FAZ-1)
      │
      ▼
CONSTITUTION REPORT
      │
      ▼
CONSTITUTION TASK (TASK-CD-YYYYMMDD-NNNN)
      │
      ▼
TASK ENGINE ──► Okur, işler, Claude'a iletir
```

Her Constitution Task, Task Engine'e bir girdi olur. Task Engine bu girdiyi
işler ve bir Task Execution Package'e dönüştürür.

---

## 22. Claude Entegrasyonu

Task Engine ile Claude arasındaki veri akışı:

```
TASK ENGINE
      │
      ▼
┌─────────────────────────────────────────┐
│          TASK EXECUTION PACKAGE           │
│                                          │
│  task_id: TASK-CD-20260702-0001          │
│  priority: KRITIK                        │
│  locked_files: [                          │
│    "services/scene_registry.py",         │
│    "handlers/website.py",                │
│    "ANA YASA/17_SAHNE_KAYIT_DEFTERİ.md"  │
│  ]                                       │
│  actions: [                              │
│    {                                     │
│      "type": "ADD_SCENE_DEFINITION",     │
│      "file": "services/scene_registry.py",│
│      "line": 129,                        │
│      "detail": "SAHNE-05 ekle"           │
│    },                                    │
│    {                                     │
│      "type": "ADD_DELIVERY_CHAIN",       │
│      "file": "handlers/website.py",      │
│      "line": 311,                        │
│      "detail": "Delivery zinciri ekle"   │
│    }                                     │
│  ]                                       │
│  constraints: [                          │
│    "CDE-001: PASS almadan başlama",      │
│    "CDE-002: Sadece task'ta yazanı yap", │
│    "Yeni özellik ekleme",                │
│    "Mevcut mimariyi bozma"               │
│  ]                                       │
│  post_check_required: true               │
│                                          │
└─────────────────────────────────────────┘
      │
      ▼
    Claude
```

Claude geliştirmeyi tamamladığında Task Engine'e **Task Result** döner:

```json
{
  "task_id": "TASK-CD-20260702-0001",
  "status": "COMPLETED",
  "completed_at": "2026-07-02T14:00:00",
  "changed_files": [
    {
      "file": "services/scene_registry.py",
      "lines_added": 15,
      "sha256_before": "f6a8390e...",
      "sha256_after": "a1b2c3d4..."
    }
  ],
  "result_summary": "SAHNE-05 SceneDefinition eklendi, delivery zinciri tamamlandı, Sahne Kayıt Defteri güncellendi.",
  "post_check_required": true
}
```

---

## 23. Feature Registry Entegrasyonu

### FEAT-018 — Task Engine

**Türkçe Adı:** Task Engine

**İngilizce Adı:** Task Engine

**Kategori:** SYSTEM

**Tür:** ENGINE

**Durum:** AKTİF

**Açıklama:** HLK'nın anayasal görev yönetim motorudur. Constitution Diff Engine
(CDE) tarafından üretilen Constitution Task'ları okur, önceliklendirir, bağımlılık
analizi yapar, birleştirir veya parçalar, Task Package ve Task Execution Package
oluşturur, Claude'a iletir, geliştirme sonucunu alır ve Constitution Gate'e geri
gönderir. Kod yazmaz, karar vermez, PASS/FAIL üretmez. Yalnızca görev yaşam
döngüsünü yönetir. CSE, CDE ve Constitution Gate ile entegre çalışır.

---

## 24. Olay Kayıt Merkezi Entegrasyonu

Task Engine'in Olay Kayıt Merkezi ile ilişkisi:

| Task Engine Olayı | Tetikleyen | Sonraki Olay |
|---|---|---|
| `EVENT_TASK_CREATED` (OLAY-057) | `EVENT_CONSTITUTION_PASS` (OLAY-049) | `EVENT_TASK_ASSIGNED` veya `EVENT_TASK_WAITING` |
| `EVENT_TASK_ASSIGNED` (OLAY-058) | READY → ACTIVE geçişi | `EVENT_TASK_LOCKED` (OLAY-060) |
| `EVENT_TASK_LOCKED` (OLAY-060) | Görev atandı | `EVENT_TASK_STARTED` (OLAY-059) |
| `EVENT_TASK_STARTED` (OLAY-059) | Claude başladı | `EVENT_TASK_COMPLETED` / `EVENT_TASK_FAILED` |
| `EVENT_TASK_COMPLETED` (OLAY-061) | Claude tamamladı | `EVENT_CONSTITUTION_CHECK_STARTED` (OLAY-045) |
| `EVENT_TASK_FAILED` (OLAY-062) | Hata oluştu | `EVENT_TASK_ASSIGNED` (yeniden) |
| `EVENT_TASK_WAITING` (OLAY-063) | Bağımlılık var | Bağımlılık çözüldüğünde `EVENT_TASK_ASSIGNED` |
| `EVENT_TASK_CANCELLED` (OLAY-064) | İptal edildi | `EVENT_TASK_CLOSED` (OLAY-066) |
| `EVENT_TASK_MERGED` (OLAY-065) | Birleştirildi | `EVENT_TASK_ASSIGNED` (birleşik görev) |
| `EVENT_TASK_CLOSED` (OLAY-066) | Gate PASS aldı | — (son) |

---

## 25. Sahne Sistemi Entegrasyonu

Task Engine, sahne geliştirme görevlerini yönetirken Sahne Kayıt Defteri ve
Scene Registry ile aşağıdaki şekilde çalışır:

| Sahne Durumu | Task Engine Davranışı |
|---|---|
| Sahne Kayıt Defteri'nde yok, Flow Diagram'da var | CDE ihlal üretir → Task Engine görev oluşturur |
| Sahne Kayıt Defteri'nde var, Scene Registry'de yok | CDE ihlal üretir → Task Engine görev oluşturur |
| Her ikisinde de var, handler eksik | CDE delivery ihlali → Task Engine görev oluşturur |
| Hepsi tamam | CDE PASS → Task Engine görev üretmez |

---

## 26. Task Log Yapısı

Her görev için detaylı bir log tutulur:

```
TASK LOG: TASK-CD-20260702-0001
─────────────────────────────────
2026-07-02 12:45:00 | CREATED     | CDE: CDE-20260702-0001
2026-07-02 12:45:01 | RECEIVED    | Task Engine
2026-07-02 12:45:02 | ANALYZING   | Priority: 128 (KRITIK), Deps: 0
2026-07-02 12:45:03 | PACKAGING   | 3 actions, 3 files
2026-07-02 12:45:04 | ASSIGNED    | To: Claude
2026-07-02 12:45:04 | LOCKED      | Files: scene_registry.py, website.py, 17_Sahne_Kayit_Defteri.md
2026-07-02 12:45:05 | IN_PROGRESS | Claude started
2026-07-02 14:00:00 | COMPLETED   | 3 files changed
2026-07-02 14:00:01 | VERIFYING   | POST-CHECK started
2026-07-02 14:00:30 | CLOSED      | Gate: PASS
```

---

## 27. Task JSON Modeli

Tam Task veri modeli:

```json
{
  "task": {
    "task_id": "TASK-CD-20260702-0001",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "CLOSED",
    "priority": {
      "level": "KRITIK",
      "score": 128,
      "technical_constant": "PRIORITY_CRITICAL"
    },
    "created": {
      "by": "CDE",
      "source_report": "CDE-20260702-0001",
      "at": "2026-07-02T12:45:00"
    },
    "violations": [...],
    "affected_layers": {...},
    "required_actions": [...],
    "dependencies": {
      "requires": [],
      "required_by": ["TASK-CD-20260702-0002", "TASK-CD-20260702-0003"]
    },
    "lock": {
      "lock_id": "LOCK-20260702-0001",
      "locked_files": ["services/scene_registry.py", "handlers/website.py"],
      "locked_at": "2026-07-02T12:45:04",
      "released_at": "2026-07-02T14:00:00"
    },
    "execution": {
      "assigned_to": "Claude",
      "started_at": "2026-07-02T12:45:05",
      "completed_at": "2026-07-02T14:00:00",
      "changed_files": 3,
      "lines_added": 72,
      "post_check_result": "PASS"
    },
    "history": [
      {"status": "CREATED", "at": "2026-07-02T12:45:00"},
      {"status": "RECEIVED", "at": "2026-07-02T12:45:01"},
      {"status": "CLOSED", "at": "2026-07-02T14:00:30"}
    ]
  }
}
```

---

## 28. Task UUID

Her görev, `task_id`'ye ek olarak benzersiz bir UUID ile tanımlanır.
UUID formatı: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (RFC 4122, versiyon 4).

```
task_id:  TASK-CD-20260702-0001   ← İnsan okunabilir (CDE formatı)
uuid:     a1b2c3d4-e5f6-7890-abcd-ef1234567890  ← Makine okunabilir (benzersiz)
```

UUID;
- Görev birleştirme sonrası yeni UUID alır,
- Görev parçalama sonrası alt görevler yeni UUID alır,
- Task log'larında ve event'lerde referans olarak kullanılır.

---

## 29. Hata Senaryoları

| Senaryo | Task Engine Davranışı |
|---|---|
| **Görev kilitliyken aynı dosyaya yeni görev** | Yeni görev WAITING kuyruğuna alınır |
| **Kilit süresi aşımı (60 dk)** | Kilit EXPIRED, görev FAILED, dosyalar serbest |
| **Claude hata döndü** | Görev FAILED, hata log'lanır, yeniden ASSIGNED (maks. 3 kez) |
| **POST-CHECK FAIL** | Görev yeniden ASSIGNED, hata nedeni task'a eklenir |
| **Görev birleştirme sonrası 5+ dosya** | Birleştirme İPTAL, görevler PARÇALA'ya yönlendirilir |
| **Bağımlı görev iptal edildi** | Bekleyen görev WAITING'den READY'e taşınır |
| **Aynı anda 2 görev ACTIVE** | ENGELLENİR. İkinci görev hata alır. |
| **Görev ANA YASA değişikliği içeriyor** | Uyarı log'lanır. ANA YASA değişikliği ayrı onay gerektirir. |
| **Task Engine çalışmıyor** | CDE görevleri biriktirir, Task Engine başladığında toplu işler |

---

## 30. Gerçek Örnek — TASK-CD-20260702-0001

Bugünkü SAHNE-05 görevinin Task Engine perspektifinden tam yaşam döngüsü:

```
┌─────────────────────────────────────────────────────────┐
│           TASK-CD-20260702-0001 YAŞAM DÖNGÜSÜ             │
│                                                         │
│  12:45:00  CREATED     CDE ihlal tespit etti             │
│  12:45:01  RECEIVED    Task Engine aldı                  │
│  12:45:02  ANALYZING   Priority: 128 (KRİTİK)            │
│                        Bağımlılık: YOK                   │
│                        Birleştirme: gerek yok             │
│                        Parçalama: gerek yok (3 dosya)    │
│  12:45:03  PACKAGING   3 actions → Task Package           │
│  12:45:04  ASSIGNED    Claude'a atandı                   │
│  12:45:04  LOCKED      3 dosya kilitlendi                │
│  12:45:05  IN_PROGRESS Claude geliştiriyor               │
│  13:48:00  COMPLETED   3 dosya değişti                    │
│  13:48:30  VERIFYING   POST-CHECK başlatıldı             │
│  13:53:00  CLOSED      Constitution PASS                 │
│                                                         │
│  Toplam Süre: 1 saat 8 dakika                            │
│  Sonuç: ✅ BAŞARILI                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 31. Yeni Runtime Akışı (Tüm Modüller Entegre)

Task Engine ile birlikte HLK'nın tam geliştirme akışı:

```
KOD TALEBİ
      │
      ▼
┌──────────┐
│   CSE    │  ← FAZ-0: Snapshot üret (SNAP-...-PRE)
└──────────┘
      │
      ▼
┌──────────┐
│   CDE    │  ← FAZ-0: Çapraz karşılaştır
└──────────┘
      │
      ├── FAIL → Constitution Report + Task
      │         Kod yazılmaz.
      │
      └── PASS
            │
            ▼
      ┌──────────────┐
      │ CONSTITUTION  │  ← FAZ-0: Gate kararı
      │     GATE      │
      └──────────────┘
            │
            ├── FAIL → Kod yazılmaz.
            │
            └── PASS
                  │
                  ▼
            ┌──────────────┐
            │ TASK ENGINE   │  ← Görevi oku, işle, Claude'a ilet
            └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │    CLAUDE     │  ← Kod analizi + geliştirme
            └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │ TASK ENGINE   │  ← Sonucu al
            └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │   CSE (POST)  │  ← FAZ-2: Yeni Snapshot
            └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │   CDE (POST)  │  ← FAZ-2: Yeniden karşılaştır
            └──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │ CONSTITUTION  │  ← POST-CHECK
            │     GATE      │
            └──────────────┘
                  │
                  ├── FAIL → TASK ENGINE (yeniden ata)
                  │
                  └── PASS
                        │
                        ▼
                  ┌──────────────┐
                  │ RUNTIME TEST  │  ← Telegram canlı test
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │   CSE (FINAL) │  ← FAZ-3: Final Snapshot
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │   CDE (FINAL) │  ← FAZ-3: Final karşılaştırma
                  └──────────────┘
                        │
                        ▼
                  ┌──────────────┐
                  │ CONSTITUTION  │  ← FAZ-3: Final Gate
                  │     GATE      │
                  └──────────────┘
                        │
                        ├── FAIL → TASK ENGINE (yeniden ata)
                        │
                        └── PASS
                              │
                              ▼
                        ╔══════════════╗
                        ║  PRODUCTION  ║
                        ╚══════════════╝
```

---

## 32. Task Engine Çalışma Prensibi (Özet)

```
┌──────────────────────────────────────────────────────────┐
│                     TASK ENGINE                           │
│                                                          │
│  GİRDİ:                                                   │
│  - Constitution Task (TASK-CD-YYYYMMDD-NNNN) CDE'den     │
│  - Constitution PASS (OLAY-049) Gate'ten                 │
│  - Snapshot ID (SNAP-YYYYMMDD-NNNN) CSE'den              │
│                                                          │
│  İŞLEM:                                                   │
│  1. Task'ı al ve doğrula                                 │
│  2. Öncelik hesapla                                      │
│  3. Bağımlılık çözümle                                   │
│  4. Birleştir / Parçala                                  │
│  5. Task Package oluştur                                 │
│  6. Task Execution Package hazırla                        │
│  7. Claude'a ilet                                        │
│  8. Dosyaları kilitle                                    │
│  9. Sonucu bekle                                         │
│  10. Sonucu al ve doğrula                                │
│  11. POST-CHECK için Gate'e ilet                         │
│  12. Geçmişi kaydet                                      │
│                                                          │
│  ÇIKTI:                                                   │
│  - Task Execution Package (Claude'a)                     │
│  - Task Result (Gate'e)                                  │
│  - Task History (log)                                    │
│  - Event: TASK_CREATED → ... → TASK_CLOSED              │
│                                                          │
│  KISITLAMA:                                               │
│  - Kod yazmaz                                            │
│  - Kod değiştirmez                                        │
│  - PASS/FAIL üretmez                                      │
│  - Constitution Gate yerine geçmez                        │
│  - ANA YASA'yı değiştirmez                                │
└──────────────────────────────────────────────────────────┘
```

---

## 33. MASTER-001 / MASTER-003 Uyumluluk Tablosu

| MASTER Kuralı | Task Engine Uyumu |
|---|---|
| **MASTER-001** Karar Hiyerarşisi | Task Engine yeni katman değil, yürütme katmanıdır. Karar hiyerarşisini değiştirmez. |
| **MASTER-001** Zorunlu Uygulama | Task Engine, CDE ve Gate kararlarını uygular, kendi kararını vermez. |
| **MASTER-003** Analiz Zorunluluğu | Task Engine, geliştirme öncesi Gate kontrolünü zorunlu kılar. |
| **MASTER-003** Zorunlu Kontroller | Task Engine, her görev için POST-CHECK zorunluluğu getirir. |
| **MASTER-003** Tamamlanma Kriteri | Task Engine, COMPLETED → VERIFYING → CLOSED zinciri ile tamamlanmayı garanti eder. |
| **MASTER-003** Kritik Kural | Task Engine, FAIL durumunda görevi yeniden atar, kapatmaz. |
| **MASTER-004** Karar Mekanizması | Task Engine karar vermez; CDE ve Gate kararlarını uygular. |
| **MASTER-006** Modüler Platform | Task Engine, gelecekteki tüm modüller için ortak görev yönetim katmanıdır. |

---

## 34. Temel İlke

Task Engine, HLK'nın anayasal görev yönetim katmanıdır.

Task Engine'in görevi;

- CDE'den gelen Constitution Task'ları okumak,
- Görevleri önceliklendirmek ve bağımlılıklarını çözmek,
- Task Package ve Task Execution Package oluşturmak,
- Claude'a geliştirme görevini iletmek,
- Geliştirme sonucunu almak ve Constitution Gate'e iletmek,
- Görev yaşam döngüsünü kayıt altına almaktır.

Task Engine'in görevi;

- Kod yazmak,
- Kod değiştirmek,
- PASS/FAIL kararı vermek,
- Constitution Gate yerine geçmek,
- Yeni Constitution Task oluşturmak

**değildir.**

Task Engine olmadan HLK "tespit eden" bir sistemdir.
Task Engine ile HLK **"görevi yöneten ve geliştirme sürecini orkestre eden"**
bir mimariye geçer.

---

## 35. Anayasal Yetki

Bu dosya, MASTER-001 Karar Hiyerarşisi'nde tanımlanan otorite sıralamasına tabidir.

Bu dosya;

- MASTER RULE BOOK'u uygulamak için vardır.
- MASTER RULE BOOK bu dosyayı uygulamak için var değildir.

Task Engine, MASTER-004 (HLK Karar Mekanizması ve Kural Otoritesi Prensibi) gereği:

- bağımsız karar verici değil,
- HLK'nın karar mekanizmasını uygulayan yürütme katmanıdır.

---

## 36. CSE ↔ CDE ↔ Task Engine ↔ Gate Görev Paylaşımı (Genişletilmiş)

| Görev | CSE (19) | CDE (18) | Task Engine (20) | Gate (18) | Claude |
|---|---|---|---|---|---|
| ANA YASA/Kod/Runtime okumak | ✅ | ❌ | ❌ | ❌ | ✅ |
| Snapshot üretmek | ✅ | ❌ | ❌ | ❌ | ❌ |
| Çapraz karşılaştırma | ❌ | ✅ | ❌ | ❌ | ❌ |
| İhlal tespiti | ❌ | ✅ | ❌ | ❌ | ❌ |
| Constitution Report | ❌ | ✅ | ❌ | ❌ | ❌ |
| Constitution Task oluşturma | ❌ | ✅ | ❌ | ❌ | ❌ |
| PASS/FAIL kararı | ❌ | ❌ | ❌ | ✅ | ❌ |
| Görev önceliklendirme | ❌ | ❌ | ✅ | ❌ | ❌ |
| Task Package oluşturma | ❌ | ❌ | ✅ | ❌ | ❌ |
| Claude'a görev iletme | ❌ | ❌ | ✅ | ❌ | ❌ |
| Kod yazma/değiştirme | ❌ | ❌ | ❌ | ❌ | ✅ |
| POST-CHECK tetikleme | ✅ | ✅ | ✅ | ✅ | ❌ |
| Event üretmek | OLAY-051/056 | OLAY-045/050 | OLAY-057/066 | OLAY-049/050 | ❌ |
| Workflow | WF-013 | WF-012 | WF-014 | (WF-012) | ❌ |
| Feature | FEAT-017 | FEAT-016 | FEAT-018 | (FEAT-016) | ❌ |

---

## 37. Final — Task Engine Tek Başına Kod Yazabilir mi?

**Hayır.**

Task Engine yalnızca anayasal görevleri yönetir. Constitution Task'ları okur,
önceliklendirir, paketler ve Claude'a iletir. Kod yazma yetkisi yalnızca
Claude'a aittir. Task Engine, PASS/FAIL kararı vermez — bu yetki yalnızca
Constitution Gate'indir.

Task Engine olmadan CDE'in ürettiği görevler dağınık kalır.
CDE olmadan Task Engine'in yöneteceği görev bulunmaz.
Gate olmadan Task Engine'in ileteceği görev anayasal denetimden geçmez.
**Dört modül birlikte çalışır.**

---

**Hazırlayan:** HLK — Claude Code  
**Tarih:** 2026-07-02  
**Referans:** MASTER-001, MASTER-003, MASTER-004, MASTER-006  
**Bağlı Modüller:** 18_CONSTITUTION_DIFF_ENGINE.md (CDE), 19_CONSTITUTION_SCAN_ENGINE.md (CSE)
