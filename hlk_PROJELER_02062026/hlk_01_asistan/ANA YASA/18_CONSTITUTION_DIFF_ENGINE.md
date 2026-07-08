# 18 — Constitution Diff Engine (CDE)

HLK'nın anayasal denetim katmanıdır. ANA YASA ile çalışan kodu sürekli karşılaştırır,
ihlalleri tespit eder, rapor üretir ve düzeltme görevi oluşturur.

---

## 1. Anayasal Konum

CDE, MASTER-001 Karar Hiyerarşisi'ne yeni bir katman eklemez. Mevcut hiyerarşiyi
destekleyen çapraz denetim katmanıdır.

```
MASTER RULE BOOK
       │
       ▼
CDE ──── Anayasal Denetim (çapraz — tüm katmanları tarar)
│  │  │
│  │  └──► Kod (.py)
│  └─────► ANA YASA (.md)
└────────► Runtime (canlı sistem)
```

**Karar yetkisi:** CDE karar vermez. Yalnızca denetler, karşılaştırır ve rapor üretir.

**Otorite:** MASTER-001 Karar Hiyerarşisi'ne tabidir. CDE'nin bulguları MASTER-003
(ANA YASA / Kod Uyumluluk Denetim Prensibi) kapsamında değerlendirilir.

---

## 2. Amaç

HLK içerisinde;

- ANA YASA'da tanımlanmış fakat kodda karşılığı olmayan bileşenleri,
- Kodda var olan fakat ANA YASA'da tanımlanmamış bileşenleri,
- ANA YASA ile kod arasında çelişki oluşturan bileşenleri

otomatik olarak tespit etmek ve her ihlal için Constitution Report + Constitution Task
üretmektir.

CDE'nin amacı kodu değiştirmek değil; HLK'nın anayasal tutarlılığını sürekli
denetleyerek uyumsuzlukları görünür kılmaktır.

---

## 3. Temel İlkeler

1. **CDE karar vermez.** Yalnızca tespit eder.
2. **CDE kod yazmaz.** Yalnızca görev tanımlar.
3. **CDE kod değiştirmez.** Yalnızca rapor üretir.
4. **CDE ANA YASA'yı değiştirmez.** MASTER-001 gereği yalnızca Proje Yöneticisi değiştirebilir.
5. **CDE'nin tespitleri MASTER-003 kapsamındadır.** Her ihlal "ANA YASA / KOD UYUMLULUK RAPORU" formatında sunulur.
6. **CDE sürekli çalışır.** Her geliştirme öncesi, sonrası ve runtime test sonrası otomatik tetiklenir.
7. **CDE çapraz denetim yapar.** Tek bir kaynağa bakmaz; tüm katmanları birlikte değerlendirir.

---

## 4. Denetim Kapsamı

CDE aşağıdaki kaynakları çapraz karşılaştırır:

### 4.1 ANA YASA Kaynakları (.md)

| Dosya | Denetim Hedefi |
|---|---|
| `00_HLK_MASTER_RULE_BOOK.md` | MASTER kuralları, Karar Hiyerarşisi |
| `01_Global_Configuration.md` | GC parametreleri |
| `03_Architecture_Rules.md` | AR kuralları |
| `04_Operational_Rules.md` | OR kuralları |
| `07_HLK_STATE_ENGINE.md` | SE-007_3 State listesi, SE-007_4 geçişler, SE-007_5 event tetikleyicileri, SE-007_6 aksiyon eşleştirmeleri |
| `08_HLK_FLOW_DIAGRAM.md` | FD-008_1 akış, FD-008_2 referans tablosu, FD-008_6 geliştirme durumu |
| `09_WORKFLOW_MANIFEST.md` | WF kayıtları |
| `10_FEATURE_REGISTRY.md` | FEAT kayıtları |
| `11_WORKFLOW_FEATURE_MAP.md` | WF-FEAT ilişkileri |
| `14_OLAY_KAYIT_MERKEZI.md` | OLAY kayıtları |
| `17_SAHNE_KAYIT_DEFTERİ.md` | Sahne kayıtları |

### 4.2 Kod Kaynakları (.py)

| Dosya | Denetim Hedefi |
|---|---|
| `utils/state_engine.py` | State enum, Event enum, STATE_TRANSITIONS, STATE_ACTION_MAP |
| `services/scene_registry.py` | SCENE_REGISTRY, SceneDefinition kayıtları |
| `services/scene_engine.py` | ConversationSceneEngine |
| `services/scene_delivery.py` | SceneDeliveryModule |
| `services/voice_generator.py` | AHUVoiceGenerator |
| `services/research_orchestrator.py` | Araştırma modülleri |
| `handlers/start.py` | /start akışı, sahne handler'ları |
| `handlers/website.py` | Link, materyal, format, çözünürlük handler'ları |
| `handlers/cancel.py` | İptal handler'ı |
| `config/settings.py` | Settings sınıfı |
| `config/video_paths.py` | GC-001 video path'leri |
| `main.py` | Handler kayıtları, bot başlatma |

### 4.3 Runtime Kaynakları (canlı log)

| Kaynak | Denetim Hedefi |
|---|---|
| `bot_stderr.log` / `logs/bot.log` | State geçişleri, Event tetiklenmeleri, hatalar |
| `bot_stdout.log` | Konsol çıktısı |

---

## 5. Çapraz Denetim Matrisi

CDE her denetimde aşağıdaki matrisi uygular:

```
                  ANA YASA (.md)
                       │
                       ▼
              ┌─────────────────┐
              │  ÇAPRAZ DENETİM  │
              └─────────────────┘
               │       │       │
               ▼       ▼       ▼
          State     Scene    Handler
          Engine    Registry  (.py)
          (.py)     (.py)
```

### 5.1 State Denetimi

| ANA YASA Kaynağı | Kod Karşılığı | Kontrol |
|---|---|---|
| `SE-007_3` State listesi | `utils/state_engine.py` → `UserState` enum | Her ANA YASA state'i kodda enum olarak var mı? |
| `SE-007_4` Geçiş kuralları | `utils/state_engine.py` → `STATE_TRANSITIONS` | Her ANA YASA geçişi kodda tanımlı mı? |
| `SE-007_5` Event-State tablosu | `utils/state_engine.py` → `UserEvent` enum | Her ANA YASA event'i kodda enum olarak var mı? |
| `SE-007_6` Aksiyon eşleştirmeleri | `utils/state_engine.py` → `STATE_ACTION_MAP` | Her state için aksiyon tanımlı mı? |

### 5.2 Sahne Denetimi

| ANA YASA Kaynağı | Kod Karşılığı | Kontrol |
|---|---|---|
| `FD-008_1` akış diyagramındaki SAHNE'ler | `scene_registry.py` → `SCENE_REGISTRY` | Flow Diagram'da olup registry'de olmayan sahne var mı? |
| `17_SAHNE_KAYIT_DEFTERİ.md` kayıtları | `scene_registry.py` → `SceneDefinition` | Kayıt defterinde olup kodda olmayan sahne var mı? |
| `FD-008_6` durum işaretleri | `scene_registry.py` → mevcut sahneler | Kodda olup ANA YASA'da durumu belirsiz sahne var mı? |

### 5.3 Handler Denetimi

| ANA YASA Kaynağı | Kod Karşılığı | Kontrol |
|---|---|---|
| `FD-008_1` SAHNE-XX → sonraki SAHNE | `handlers/website.py` → handler fonksiyonları | Her handler `produce_and_deliver()` çağırıyor mu? |
| `SE-007_5` Event → State geçişi | `main.py` → `CallbackQueryHandler` kayıtları | Her sahne butonu için handler kaydedilmiş mi? |
| `OR` operasyonel kuralları | Handler fonksiyonları | Her handler cleanup + delivery yapıyor mu? |

### 5.4 Workflow Denetimi

| ANA YASA Kaynağı | Kod Karşılığı | Kontrol |
|---|---|---|
| `09_WORKFLOW_MANIFEST.md` → WF'ler | İlgili servis/handler dosyaları | Her WF'nin kodda karşılığı var mı? |
| `11_WORKFLOW_FEATURE_MAP.md` → WF-FEAT ilişkileri | İlgili kod | Her Feature WF'si ile ilişkilendirilmiş mi? |

### 5.5 Feature Denetimi

| ANA YASA Kaynağı | Kod Karşılığı | Kontrol |
|---|---|---|
| `10_FEATURE_REGISTRY.md` → FEAT'ler | İlgili servis/modül dosyaları | Her FEAT'in kodda karşılığı var mı? |
| Kodda var olan modüller | `10_FEATURE_REGISTRY.md` | Kodda olup Feature Registry'de kaydı olmayan bileşen var mı? |

---

## 6. CDE Yaşam Döngüsü — Üç Fazlı Denetim

CDE üç farklı zamanda otomatik olarak çalışır:

### FAZ 1: Geliştirme Öncesi Denetim (Pre-Development Check)

```
Kod İsteği Geldi
      │
      ▼
┌──────────┐
│ CDE FAZ 1 │ ← ANA YASA (.md) ↔ Kod (.py) karşılaştır
└──────────┘
      │
      ├── UYUMSUZLUK VAR ──► Constitution Report üret
      │                      Kod yazma. Önce ihlalleri çöz.
      │
      └── UYUMSUZLUK YOK ──► Kod üretimine izin ver.
```

### FAZ 2: Geliştirme Sonrası Denetim (Post-Development Check)

```
Kod Üretildi
      │
      ▼
┌──────────┐
│ CDE FAZ 2 │ ← Yeni kod ↔ ANA YASA karşılaştır
└──────────┘
      │
      ├── UYUMLU ──► PASS
      │
      └── UYUMSUZ ──► FAIL → Constitution Task oluştur
```

### FAZ 3: Runtime Sonrası Denetim (Post-Runtime Check)

```
Runtime Test Tamamlandı
      │
      ▼
┌──────────┐
│ CDE FAZ 3 │ ← Runtime log ↔ ANA YASA ↔ Kod karşılaştır
└──────────┘
      │
      ├── PASS ──► Production hazır
      │
      └── FAIL ──► Constitution Task oluştur
```

---

## 7. Constitution Report Formatı

Her ihlal için aşağıdaki standart formatta rapor üretilir:

```
╔═══════════════════════════════════════════════════════════╗
║  ANA YASA / KOD UYUMLULUK RAPORU (MASTER-003)           ║
╠═══════════════════════════════════════════════════════════╣
║  Rapor No     : CDE-YYYYMMDD-NNNN                        ║
║  Tespit Eden  : Constitution Diff Engine (CDE)           ║
║  Denetim Fazı : FAZ-1 / FAZ-2 / FAZ-3                    ║
║  Tarih        : YYYY-MM-DD HH:MM:SS                      ║
╠═══════════════════════════════════════════════════════════╣
║  İHLAL TİPİ   : <CONSTITUTIONAL_VIOLATION türü>          ║
║  CİDDİYET     : KRİTİK / YÜKSEK / ORTA / DÜŞÜK           ║
╠═══════════════════════════════════════════════════════════╣
║  Kural        : <İhlal edilen MASTER/AR/OR/GK/QR maddesi>║
║  Sebep        : <İhlalin açıklaması>                     ║
║  ANA YASA'da  : <ANA YASA'daki tanım>                    ║
║  Kodda         : <Kodun mevcut durumu>                    ║
║  Dosya         : <İlgili .py veya .md dosyası>            ║
║  Satır         : <İlgili satır numarası>                  ║
║  Kanıt         : <SHA256, log, stack trace, diff>         ║
╠═══════════════════════════════════════════════════════════╣
║  ETKİLENEN KATMANLAR:                                    ║
║  State Engine  : <etkilenen state'ler>                   ║
║  Scene Registry: <etkilenen sahneler>                    ║
║  Handler       : <etkilenen handler'lar>                  ║
║  Workflow      : <etkilenen WF'ler>                      ║
║  Feature       : <etkilenen FEAT'ler>                    ║
║  Event         : <etkilenen OLAY'lar>                    ║
╠═══════════════════════════════════════════════════════════╣
║  DURUM         : ❌ UYUMSUZ                               ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 8. Constitution Task Formatı

Her rapor için bir görev (task) oluşturulur:

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTION TASK                                       ║
╠═══════════════════════════════════════════════════════════╣
║  Task No       : TASK-CD-YYYYMMDD-NNNN                   ║
║  Bağlı Rapor   : CDE-YYYYMMDD-NNNN                       ║
║  Öncelik       : KRİTİK / YÜKSEK / ORTA / DÜŞÜK          ║
╠═══════════════════════════════════════════════════════════╣
║  EKSİK BİLEŞEN :                                          ║
║  □ Eksik Sahne                                            ║
║  □ Eksik Workflow                                         ║
║  □ Eksik Feature                                          ║
║  □ Eksik State                                            ║
║  □ Eksik Handler                                          ║
║  □ Eksik SceneDefinition                                  ║
║  □ Eksik Event                                            ║
║  □ Eksik Registry Kaydı                                   ║
║  □ Eksik produce_and_deliver() çağrısı                    ║
║  □ Eksik Production Package                               ║
║  □ ANA YASA / Kod çelişkisi                               ║
╠═══════════════════════════════════════════════════════════╣
║  İLGİLİ ANA YASA:                                         ║
║  - 08_HLK_FLOW_DIAGRAM.md (FD-008_1)                      ║
║  - 17_SAHNE_KAYIT_DEFTERİ.md                              ║
║  - MASTER-003                                             ║
╠═══════════════════════════════════════════════════════════╣
║  İLGİLİ DOSYALAR:                                         ║
║  - <dosya1.py>:<satır>                                    ║
║  - <dosya2.py>:<satır>                                    ║
╠═══════════════════════════════════════════════════════════╣
║  YAPILACAK İŞLEM:                                         ║
║  1. <adım 1>                                              ║
║  2. <adım 2>                                              ║
║  ...                                                      ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 9. İhlal Türleri (CONSTITUTIONAL_VIOLATION Types)

| İhlal Türü | Teknik Sabit | Açıklama |
|---|---|---|
| Eksik State | `STATE_MISSING_IN_CODE` | ANA YASA'da tanımlı state kodda yok |
| Eksik Event | `EVENT_MISSING_IN_CODE` | ANA YASA'da tanımlı event kodda yok |
| Eksik Sahne | `SCENE_MISSING_IN_REGISTRY` | Flow Diagram'da olan sahne Scene Registry'de yok |
| Eksik Workflow | `WORKFLOW_MISSING_IN_CODE` | Workflow Manifest'te olan WF kodda yok |
| Eksik Feature | `FEATURE_MISSING_IN_CODE` | Feature Registry'de olan FEAT kodda yok |
| Eksik Handler Kaydı | `HANDLER_NOT_REGISTERED` | Sahne butonları için handler main.py'de kaydedilmemiş |
| Eksik Scene Delivery | `SCENE_DELIVERY_NOT_CALLED` | Handler produce_and_deliver() çağırmıyor |
| Eksik Transition | `TRANSITION_MISSING` | ANA YASA geçişi STATE_TRANSITIONS'da yok |
| Kodlanmamış State | `STATE_NOT_IMPLEMENTED` | State tanımlı ama hiçbir modül/handler bağlı değil |
| ANA YASA'da Olmayan Kod | `CODE_WITHOUT_ANA_YASA` | Kodda var ama ANA YASA'da referansı yok |
| Çelişki | `ANA_YASA_CODE_CONFLICT` | ANA YASA ile kod farklı şey söylüyor |
| Eksik Cleanup | `CLEANUP_NOT_CALLED` | Handler'da scene_delivery.cleanup_chat() çağrısı yok |

---

## 10. CDE Event Ailesi

CDE aşağıdaki yeni event'leri Olay Kayıt Merkezi'ne (14_OLAY_KAYIT_MERKEZI.md) ekler:

### OLAY-045 — CONSTITUTION_CHECK_STARTED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-045` |
| **Event Adı** | `EVENT_CONSTITUTION_CHECK_STARTED` |
| **Açıklama** | CDE anayasal uyumluluk denetimini başlattı |
| **Kaynak Durum** | — (State'ten bağımsız, sistem event'i) |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | Kod isteği (FAZ-1), Kod üretimi tamamlandı (FAZ-2), Runtime test tamamlandı (FAZ-3) |
| **Öncelik** | YÜKSEK |
| **Kayıt Politikası** | Her denetim başlangıcında kaydedilir |

### OLAY-046 — CONSTITUTION_CHECK_COMPLETED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-046` |
| **Event Adı** | `EVENT_CONSTITUTION_CHECK_COMPLETED` |
| **Açıklama** | CDE anayasal uyumluluk denetimini tamamladı |
| **Kaynak Durum** | — |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | Denetim tamamlandı |
| **Öncelik** | YÜKSEK |
| **Kayıt Politikası** | Her denetim sonunda, sonuç (PASS/FAIL) ile birlikte kaydedilir |

### OLAY-047 — CONSTITUTIONAL_VIOLATION_FOUND

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-047` |
| **Event Adı** | `EVENT_CONSTITUTIONAL_VIOLATION_FOUND` |
| **Açıklama** | CDE bir anayasal ihlal tespit etti |
| **Kaynak Durum** | — |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | Çapraz denetimde ihlal bulundu |
| **Öncelik** | KRİTİK |
| **Kayıt Politikası** | Her ihlal için ayrı ayrı kaydedilir. Rapor No (CDE-...) ilişkilendirilir |

### OLAY-048 — CONSTITUTION_TASK_CREATED

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-048` |
| **Event Adı** | `EVENT_CONSTITUTION_TASK_CREATED` |
| **Açıklama** | CDE bir düzeltme görevi (Constitution Task) oluşturdu |
| **Kaynak Durum** | — |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | İhlal tespit edildi ve görev oluşturuldu |
| **Öncelik** | YÜKSEK |
| **Kayıt Politikası** | Her görev oluşturmada kaydedilir. Task No (TASK-CD-...) ilişkilendirilir |

### OLAY-049 — CONSTITUTION_PASS

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-049` |
| **Event Adı** | `EVENT_CONSTITUTION_PASS` |
| **Açıklama** | CDE denetimi başarıyla geçti, ihlal bulunamadı |
| **Kaynak Durum** | — |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | Denetim sonucu: PASS |
| **Öncelik** | NORMAL |
| **Kayıt Politikası** | Her başarılı denetim sonunda kaydedilir |

### OLAY-050 — CONSTITUTION_FAIL

| Alan | Değer |
|---|---|
| **Olay Kimliği** | `OLAY-050` |
| **Event Adı** | `EVENT_CONSTITUTION_FAIL` |
| **Açıklama** | CDE denetimi başarısız oldu, ihlal(ler) mevcut |
| **Kaynak Durum** | — |
| **Hedef Durum** | — |
| **Üreten Bileşen** | Constitution Diff Engine (CDE) |
| **Tetikleyici** | Denetim sonucu: FAIL |
| **Öncelik** | KRİTİK |
| **Kayıt Politikası** | Her başarısız denetim sonunda, toplam ihlal sayısı ile birlikte kaydedilir |

---

## 11. Yeni Workflow: WF-CONSTITUTION

### WF-012

**Workflow:** Constitution Diff Check

**Açıklama:** CDE tarafından yürütülen anayasal uyumluluk denetimi sürecini temsil eder.
Üç fazda çalışır: geliştirme öncesi, geliştirme sonrası, runtime sonrası.

**Durum:** AKTİF

**Kullandığı Feature'lar:**
- FEAT-016 Constitution Diff Engine (CDE)
- FEAT-002 Karar Mekanizması
- FEAT-003 Durum Motoru

**Workflow Akışı:**
```
WF-CONSTITUTION Başlatıldı
      │
      ▼
EVENT_CONSTITUTION_CHECK_STARTED (OLAY-045)
      │
      ▼
Çapraz Denetim Matrisi Uygulanır
      │
      ├── İhlal Bulundu ──► EVENT_CONSTITUTIONAL_VIOLATION_FOUND (OLAY-047)
      │                      │
      │                      ▼
      │                   Constitution Report Üretilir
      │                      │
      │                      ▼
      │                   Constitution Task Oluşturulur
      │                      │
      │                      ▼
      │                   EVENT_CONSTITUTION_TASK_CREATED (OLAY-048)
      │                      │
      │                      ▼
      │                   EVENT_CONSTITUTION_FAIL (OLAY-050)
      │
      └── İhlal Yok ──► EVENT_CONSTITUTION_PASS (OLAY-049)
                         │
                         ▼
                      EVENT_CONSTITUTION_CHECK_COMPLETED (OLAY-046)
```

---

## 12. Yeni Feature: FEAT-016

### FEAT-016

**Türkçe Adı:** Constitution Diff Engine

**İngilizce Adı:** Constitution Diff Engine

**Kategori:** SYSTEM

**Tür:** ENGINE

**Durum:** AKTİF

**Açıklama:** HLK'nın anayasal denetim motorudur. ANA YASA (.md) ile çalışan kodu (.py)
sürekli çapraz karşılaştırır. State Engine, Scene Registry, Handler, Workflow, Feature
ve Event katmanlarını birlikte denetler. Her ihlal için Constitution Report ve
Constitution Task üretir. Karar vermez, kod yazmaz, kod değiştirmez. Yalnızca
anayasal uyumluluğu denetler ve raporlar. MASTER-003 (ANA YASA / Kod Uyumluluk
Denetim Prensibi) kapsamında çalışır.

---

## 13. Yeni Karar Gerekçeleri

15_KARAR_GEREKCESI_STANDARDI.md'ye aşağıdaki yeni gerekçe teknik sabitleri eklenir:

### Anayasal Denetim Gerekçeleri

| Teknik Sabit | Açıklama |
|---|---|
| `CONSTITUTION_PASS` | Anayasal denetim başarıyla geçti |
| `CONSTITUTION_FAIL_CRITICAL` | Kritik anayasal ihlal tespit edildi |
| `CONSTITUTION_FAIL_HIGH` | Yüksek ciddiyetli anayasal ihlal tespit edildi |
| `CONSTITUTION_FAIL_MEDIUM` | Orta ciddiyetli anayasal ihlal tespit edildi |
| `CONSTITUTION_FAIL_LOW` | Düşük ciddiyetli anayasal ihlal tespit edildi |
| `STATE_MISSING_IN_CODE` | ANA YASA state'i kodda tanımlanmamış |
| `SCENE_MISSING_IN_REGISTRY` | Flow Diagram sahnesi Scene Registry'de kayıtlı değil |
| `HANDLER_MISSING_DELIVERY` | Handler produce_and_deliver() çağrısı içermiyor |
| `TRANSITION_NOT_IMPLEMENTED` | ANA YASA geçişi STATE_TRANSITIONS'da tanımlanmamış |
| `CODE_WITHOUT_ANA_YASA_REFERENCE` | Kod bileşeni ANA YASA'da referanssız |
| `ANA_YASA_CODE_MISMATCH` | ANA YASA ile kod arasında çelişki var |
| `FLOW_DIALOG_MISMATCH` | Üretilen konuşma, Flow Diagram'daki aktif sahne davranışı ile uyumsuz |
| `SCENE_PRESENTATION_MISMATCH` | Konuşma, sahnede tanımlanan sunum standardına (konuşma baloncuğu, daktilo efekti vb.) uymuyor |
| `SCENE_SEQUENCE_VIOLATION` | Bir sonraki sahneye, Flow Diagram'daki işlem sırası tamamlanmadan geçilmiş |
| `FLOW_OPERATION_MISSING` | Flow Diagram'da zorunlu tanımlanan bir operasyon (ör. "EKRAN SİLİNİR") uygulanmamış |
| `UNAUTHORIZED_DIALOG_GENERATION` | Executor (Claude), Flow Diagram'da tanımlanmayan konuşma veya yönlendirme üretmiş |

### Beklenen Sonuç

Constitution Diff Engine;

* Kod ile ANA YASA arasındaki farkları,
* State ve Event uyumluluğunu,
* Flow Diagram sahne davranışlarını,
* Konuşma davranışını,
* Sunum davranışını

anayasal olarak raporlayabilir hale gelir.

---

## 14. Mevcut Mimariye Entegrasyon

CDE mevcut mimariye **ek katman** olarak tasarlanmıştır. Mevcut hiçbir katmanı
değiştirmez, kaldırmaz veya yeniden tanımlamaz.

### 14.1 State Engine ile İlişki

CDE, State Engine'i değiştirmez. State Engine'in mevcut state, event ve transition
tanımlarını ANA YASA ile karşılaştırarak okur.

### 14.2 Scene Registry ile İlişki

CDE, Scene Registry'yi değiştirmez. SCENE_REGISTRY listesini ANA YASA'daki
Flow Diagram ve Sahne Kayıt Defteri ile karşılaştırarak okur.

### 14.3 Workflow Manifest ile İlişki

CDE, Workflow Manifest'e WF-012 (Constitution Diff Check) olarak eklenir.
Mevcut WF-001 — WF-011 workflow'ları değişmez.

### 14.4 Feature Registry ile İlişki

CDE, Feature Registry'ye FEAT-016 (Constitution Diff Engine) olarak eklenir.
Mevcut FEAT-001 — FEAT-015 feature'ları değişmez.

### 14.5 Karar Hiyerarşisi ile İlişki

CDE, MASTER-001 Karar Hiyerarşisi'nde mevcut katmanların arasına değil,
**çapraz denetim katmanı** olarak konumlanır:

```
MASTER RULE BOOK
       │
       ▼
Global Configuration
       │
       ▼
General Rules
       │
       ▼
Architecture Rules
       │
       ▼
State Engine
       │
       ▼
Flow Diagram
       │
       ▼
Operational Rules
       │
       ▼
Quality Rules
       │
       ▼
Module Rules
       │
       ▼
      KOD
```

CDE bu hiyerarşiyi değiştirmez. Tüm katmanları yatay olarak tarar.

---

## 15. Ciddiyet Seviyeleri

| Seviye | Teknik Sabit | Açıklama |
|---|---|---|
| KRİTİK | `SEVERITY_CRITICAL` | MASTER kuralı ihlali, State Engine'de eksik state/event, Flow Diagram sahnesi registry'de yok |
| YÜKSEK | `SEVERITY_HIGH` | Handler'da produce_and_deliver() eksik, transition tanımsız |
| ORTA | `SEVERITY_MEDIUM` | Feature kaydı eksik, Workflow manifest'te eksik WF |
| DÜŞÜK | `SEVERITY_LOW` | Dokümantasyon referansı eksik, cleanup çağrısı eksik |

---

## 16. Örnek CDE Raporu

Gerçek bir örnek — bugün tespit edilen ihlal:

```
╔═══════════════════════════════════════════════════════════╗
║  ANA YASA / KOD UYUMLULUK RAPORU (MASTER-003)           ║
╠═══════════════════════════════════════════════════════════╣
║  Rapor No     : CDE-20260702-0001                        ║
║  Tespit Eden  : Constitution Diff Engine (CDE)           ║
║  Denetim Fazı : FAZ-1 (Pre-Development)                  ║
║  Tarih        : 2026-07-02 12:45:00                      ║
╠═══════════════════════════════════════════════════════════╣
║  İHLAL TİPİ   : SCENE_MISSING_IN_REGISTRY                ║
║               : SCENE_DELIVERY_NOT_CALLED                ║
║  CİDDİYET     : KRİTİK                                   ║
╠═══════════════════════════════════════════════════════════╣
║  Kural        : MASTER-003 (ANA YASA / Kod Uyumluluk)    ║
║  Sebep        : STATE_VIDEO_DURATION_SELECTION için      ║
║                 SceneDefinition kaydı bulunmuyor.        ║
║                 handle_resolution_selection() içinde      ║
║                 produce_and_deliver() çağrısı yok.        ║
║  ANA YASA'da  : FD-008_1 SAHNE-05 tanımlı               ║
║                 SE-007_3 STATE_VIDEO_DURATION_SELECTION  ║
║                 state'i tanımlı                          ║
║                 SE-007_5 RESOLUTION_SELECTED →            ║
║                 DURATION_SELECTION geçişi tanımlı        ║
║  Kodda         : scene_registry.py'de SAHNE-05 YOK       ║
║                 handle_resolution_selection() delivery    ║
║                 çağrısı YOK                              ║
║  Dosya         : services/scene_registry.py:129          ║
║                 handlers/website.py:311                  ║
║  Kanıt         : Runtime log: STATE_VIDEO_DURATION_      ║
║                 SELECTION geçişi oldu ama sahne teslim   ║
║                 edilmedi. 5dk sonra timeout.              ║
╠═══════════════════════════════════════════════════════════╣
║  ETKİLENEN KATMANLAR:                                    ║
║  State Engine  : STATE_VIDEO_DURATION_SELECTION          ║
║  Scene Registry: SAHNE-05 (eksik)                        ║
║  Handler       : handle_resolution_selection()            ║
║  Workflow      : WF-003 (Brief Collection)               ║
║  Feature       : FEAT-003 (State Engine)                 ║
║  Event         : EVENT_RESOLUTION_SELECTED               ║
╠═══════════════════════════════════════════════════════════╣
║  DURUM         : ❌ UYUMSUZ                               ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 17. Örnek Constitution Task

Yukarıdaki raporun oluşturacağı görev:

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTION TASK                                       ║
╠═══════════════════════════════════════════════════════════╣
║  Task No       : TASK-CD-20260702-0001                   ║
║  Bağlı Rapor   : CDE-20260702-0001                       ║
║  Öncelik       : KRİTİK                                  ║
╠═══════════════════════════════════════════════════════════╣
║  EKSİK BİLEŞEN :                                          ║
║  ☑ Eksik Sahne                                            ║
║  ☑ Eksik SceneDefinition                                  ║
║  ☑ Eksik produce_and_deliver() çağrısı                    ║
╠═══════════════════════════════════════════════════════════╣
║  İLGİLİ ANA YASA:                                         ║
║  - 08_HLK_FLOW_DIAGRAM.md (FD-008_1 SAHNE-05)             ║
║  - 17_SAHNE_KAYIT_DEFTERİ.md (Gelecek Genişletmeler)       ║
║  - 07_HLK_STATE_ENGINE.md (SE-007_3/4/5)                  ║
║  - MASTER-003                                             ║
╠═══════════════════════════════════════════════════════════╣
║  İLGİLİ DOSYALAR:                                         ║
║  - services/scene_registry.py:129 (SAHNE-05 eklenecek)    ║
║  - handlers/website.py:311 (produce_and_deliver展开       ║
║   展开                                           ║
╠═══════════════════════════════════════════════════════════╣
║  YAPILACAK İŞLEM:                                         ║
║  1. scene_registry.py'e SAHNE-05 SceneDefinition ekle     ║
║     (state=VIDEO_DURATION_SELECTION)                      ║
║  2. handle_resolution_selection() içine                    ║
║     get_scene_for_state() + cleanup_chat() +              ║
║     produce_and_deliver() çağrısı ekle                     ║
║  3. 17_SAHNE_KAYIT_DEFTERİ.md'e SAHNE-05 kaydı ekle       ║
║  4. Runtime test ile doğrula                              ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 18. CDE'nin Çalışma Prensibi (Özet)

```
┌──────────────────────────────────────────────────────────┐
│                 CONSTITUTION DIFF ENGINE                   │
│                                                          │
│  GİRDİ:                                                   │
│  - Tüm ANA YASA .md dosyaları                             │
│  - Tüm proje .py dosyaları                                │
│  - Runtime log dosyaları                                  │
│                                                          │
│  İŞLEM:                                                   │
│  1. ANA YASA'yı tara → State, Event, Scene, WF, FEAT     │
│  2. Kodu tara → Enum, Registry, Handler, Delivery        │
│  3. Runtime'ı tara → State geçişleri, Event tetikleri    │
│  4. Çapraz karşılaştır → İhlal matrisini uygula          │
│                                                          │
│  ÇIKTI:                                                   │
│  - Constitution Report (her ihlal için)                   │
│  - Constitution Task (her ihlal için)                     │
│  - Event: PASS veya FAIL                                  │
│                                                          │
│  KISITLAMA:                                               │
│  - Kod yazmaz                                            │
│  - Kod değiştirmez                                        │
│  - Karar vermez                                           │
│  - ANA YASA'yı değiştirmez                                │
└──────────────────────────────────────────────────────────┘
```

---

## 19. CONSTITUTION GATE — Geliştirme Giriş Kapısı

CONSTITUTION GATE, HLK geliştirme sürecinin **zorunlu anayasal giriş kapısıdır.**
Bu kapıdan PASS almadan hiçbir kod geliştirme görevi başlayamaz.

### 19.1 Tanım

CONSTITUTION GATE;

- MASTER-003 (ANA YASA / Kod Uyumluluk Denetim Prensibi) maddesinin **operasyonel uygulamasıdır.**
- Yeni bir otorite değildir.
- MASTER-001 Karar Hiyerarşisi'ni değiştirmez.
- Yeni bir karar katmanı oluşturmaz.
- Sadece MASTER-003'ün zorunlu uygulama mekanizmasını oluşturur.

### 19.2 Yetki

CDE, CONSTITUTION GATE üzerinden;

- **PASS** kararı üretir → kod geliştirmesine izin verilir.
- **FAIL** kararı üretir → kod geliştirmesi DURDURULUR.

CDE;

- Karar vermez (MASTER-004).
- Kod yazmaz.
- Kod değiştirmez.
- ANA YASA'yı değiştirmez (MASTER-001).

Ancak CONSTITUTION GATE'ten geçiş izni yalnızca CDE tarafından verilir.

### 19.3 Anayasal Dayanak

CONSTITUTION GATE'in anayasal dayanağı MASTER-003'tür:

> *"HLK sisteminde bir ANA YASA güncellemesinin tamamlanmış kabul edilebilmesi için
> yalnızca dokümantasyonun güncellenmiş olması yeterli değildir. İlgili çalışan
> kodların da yeni kurallarla uyumlu olduğunun doğrulanması zorunludur."*
>
> — MASTER-003, ANA YASA / KOD UYUMLULUK DENETİM PRENSİBİ

CONSTITUTION GATE, bu prensibin **geliştirme sürecindeki operasyonel karşılığıdır.**
MASTER-003'ün "Zorunlu Uyum Analizi" ve "Zorunlu Kontroller" maddelerini
geliştirme yaşam döngüsünün her aşamasında uygulanabilir hale getirir.

### 19.4 Kapı Kapsamı

CONSTITUTION GATE'ten geçmesi zorunlu olan geliştirme türleri:

| Geliştirme Türü | Gate Zorunlu mu? |
|---|---|
| Yeni State ekleme | ✅ ZORUNLU |
| Yeni Event ekleme | ✅ ZORUNLU |
| Yeni Handler yazma | ✅ ZORUNLU |
| Yeni SceneDefinition ekleme | ✅ ZORUNLU |
| Yeni Workflow ekleme | ✅ ZORUNLU |
| Yeni Feature ekleme | ✅ ZORUNLU |
| Yeni Sahne ekleme | ✅ ZORUNLU |
| Mevcut handler'ı değiştirme | ✅ ZORUNLU |
| Mevcut state_engine.py değişikliği | ✅ ZORUNLU |
| Mevcut scene_registry.py değişikliği | ✅ ZORUNLU |
| main.py handler kaydı ekleme | ✅ ZORUNLU |
| ANA YASA .md dosyası değişikliği | ✅ ZORUNLU |
| Sadece log mesajı değişikliği | ⚪ MUAF |
| Sadece yorum satırı değişikliği | ⚪ MUAF |
| Sadece yazım hatası düzeltme (.md) | ⚪ MUAF |

---

## 20. FAZ-0 — CONSTITUTION GATE (Geliştirme Öncesi Zorunlu Denetim)

FAZ-0, mevcut üç fazdan (FAZ-1, FAZ-2, FAZ-3) **önce** çalışan yeni zorunlu
denetim aşamasıdır. FAZ-0, kod yazımına başlanmadan **hemen önce** çalışır.

### 20.1 FAZ-0 Akışı

```
Kod Talebi Geldi
      │
      ▼
┌─────────────────────────────────────────────┐
│           CONSTITUTION GATE (FAZ-0)          │
│                                              │
│  1. İlgili ANA YASA dosyalarını belirle      │
│     │                                        │
│     ▼                                        │
│  2. Kod ile çapraz karşılaştır               │
│     │                                        │
│     ▼                                        │
│  3. Eksik / Çelişki / İhlal ara              │
│     │                                        │
│     ├── İHLAL YOK ──► PASS                  │
│     │                 │                      │
│     │                 ▼                      │
│     │           Kod geliştirmesine           │
│     │           İZİN VERİLDİ                 │
│     │                                       │
│     └── İHLAL VAR ──► FAIL                  │
│                       │                      │
│                       ▼                      │
│                 Kod geliştirmesi             │
│                 DURDURULDU                   │
│                       │                      │
│                       ▼                      │
│                 Constitution Report          │
│                 +                            │
│                 Constitution Task            │
│                 üretilir                     │
└─────────────────────────────────────────────┘
```

### 20.2 FAZ-0 ile FAZ-1 Arasındaki Fark

| Özellik | FAZ-0 (CONSTITUTION GATE) | FAZ-1 (Pre-Development) |
|---|---|---|
| **Ne zaman çalışır?** | Kod talebi gelir gelmez, İLK adım | FAZ-0 PASS sonrası, kod yazımı öncesi |
| **Bağlayıcılık** | ZORUNLU — geçilmeden kod yazılamaz | Denetim amaçlı |
| **Sonuç** | PASS → izin ver / FAIL → durdur | Rapor üret, devam et |
| **Kapsam** | Kod talebiyle ilgili spesifik ANA YASA dosyaları | Tüm ANA YASA ↔ Kod çapraz denetimi |
| **FAIL'de ne olur?** | KOD YAZILMAZ. Sadece rapor + task. | Rapor + task. Düzeltme önerilir. |

FAZ-0 **kapıdır** — geçilmesi zorunludur.
FAZ-1, FAZ-2, FAZ-3 **denetimdir** — bilgilendirme ve doğrulama amaçlıdır.

---

## 21. CDE Anayasal Kuralları

CDE'nin yetkisini ve geliştirme sürecindeki konumunu tanımlayan anayasal kurallardır.
Bu kurallar MASTER-003 (ANA YASA / Kod Uyumluluk Denetim Prensibi) altında,
CDE modülüne özel operasyonel kurallar olarak tanımlanmıştır.

### CDE-001 — Geliştirme Öncesi Zorunlu Gate

**Başlık:** Hiçbir kod geliştirme görevi, CONSTITUTION GATE PASS almadan başlayamaz.

**Kapsam:** Yeni kod yazımı, mevcut kod değişikliği, handler ekleme, state ekleme,
scene ekleme, workflow ekleme, feature ekleme ve ANA YASA'da değişiklik gerektiren
tüm geliştirme görevleri bu kurala tabidir.

**İstisna:** Yazım hatası düzeltmeleri, yorum satırı değişiklikleri ve log mesajı
güncellemeleri bu kuraldan muaftır.

**Dayanak:** MASTER-003 — "Analiz Zorunluluğu" maddesi: "HLK içerisinde yeni bir
geliştirme yapılmadan önce aşağıdaki sıra uygulanmalıdır: 1. İlgili MASTER RULE
maddeleri incelenir. ... 7. Daha sonra geliştirme yapılır."

### CDE-002 — FAIL Durumunda Kod Üretimi Yasağı

**Başlık:** CONSTITUTION GATE FAIL durumunda Claude kod üretmez. Yalnızca
Constitution Report ve Constitution Task oluşturur.

**Kapsam:** FAIL sonucu alındığında, hiçbir .py dosyası oluşturulamaz, hiçbir
.py dosyası değiştirilemez, hiçbir kod önerisi sunulamaz.

**İzin Verilen:** Constitution Report (ihlal raporu) ve Constitution Task
(düzeltme görevi) üretilebilir. Eksik ANA YASA .md kayıtları tamamlanabilir.

**Dayanak:** MASTER-003 — "Kritik Kural" maddesi: "HLK aşağıdaki ifadeyi
kullanamaz: 'Kural güncellendi, işlem tamam.' eğer kod uyumluluk analizi
yapılmamışsa."

### CDE-003 — PASS Sonrası Geliştirme İzni

**Başlık:** CONSTITUTION GATE PASS alındığında kod geliştirmesine izin verilir.

**Kapsam:** PASS kararı, geliştirme görevinin anayasal olarak uygun olduğunu
gösterir. Kod yazımı başlayabilir.

**Sorumluluk:** PASS kararı, kodun hatasız olacağını garanti etmez. Yalnızca
ANA YASA ile çelişen bir durum olmadığını belirtir. Kod kalitesi, testler ve
runtime davranışı ayrıca denetlenir.

**Dayanak:** MASTER-003 — "Gerçek Tamamlanma Tanımı" maddesi: "ANA YASA
Güncellendi + Kod Güncellendi + Runtime Davranışı Doğrulandı = TAMAMLANDI"

### CDE-004 — Kod Sonrası Zorunlu Denetim

**Başlık:** Kod geliştirmesi tamamlandıktan sonra CDE tekrar çalışır (FAZ-2).

**Kapsam:** Yazılan yeni kod veya değiştirilen mevcut kod, FAZ-2 denetiminden
geçer. Yeni kodun ANA YASA ile uyumu doğrulanır.

**FAIL Durumunda:** Constitution Task oluşturulur. Kod düzeltilene kadar
FAZ-3'e geçilemez.

**Dayanak:** MASTER-003 — "Zorunlu Uyum Analizi" maddesi: "Yeni AR kuralı
eklendiğinde, Mevcut bir kural güncellendiğinde, Mimari değişiklik yapıldığında
HLK zorunlu olarak ANA YASA / KOD uyumluluk analizi yapmak zorundadır."

### CDE-005 — Runtime Sonrası Nihai Denetim

**Başlık:** Runtime testinden sonra CDE üçüncü kez çalışır (FAZ-3).

**Kapsam:** Canlı sistem logları, ANA YASA ve kod üçgeninde son uyumluluk
denetimi yapılır. State geçişleri, event tetiklenmeleri, scene delivery
çağrıları gerçek çalışma verisiyle doğrulanır.

**FAIL Durumunda:** Production'a geçiş ENGELLENİR. Constitution Task oluşturulur.

**PASS Durumunda:** Production'a geçişe izin verilir.

**Dayanak:** MASTER-003 — "Gerçek Tamamlanma Tanımı" maddesi: "Bir değişiklik
ancak aşağıdaki durumda tamamlanmış kabul edilir: ANA YASA Güncellendi + Kod
Güncellendi + Runtime Davranışı Doğrulandı = TAMAMLANDI"

---

## 22. Dört Zorunlu Kontrol Noktası

HLK geliştirme yaşam döngüsünde dört zorunlu CDE kontrol noktası bulunur:

```
┌──────────────────────────────────────────────────────────────┐
│              HLK GELİŞTİRME YAŞAM DÖNGÜSÜ                     │
│                                                              │
│  1. PRE-CHECK (FAZ-0)                                        │
│     CONSTITUTION GATE                                         │
│     │                                                        │
│     ├── FAIL → KOD YAZILMAZ → Rapor + Task                   │
│     │                                                        │
│     └── PASS → Aşama 2'ye geç                                │
│                                                              │
│  2. IMPLEMENTATION                                           │
│     Kod Analizi → Kod Geliştirme                              │
│     │                                                        │
│     ▼                                                        │
│  3. POST-CHECK (FAZ-2)                                       │
│     Kod ↔ ANA YASA uyumluluk                                  │
│     │                                                        │
│     ├── FAIL → Düzeltme → Tekrar POST-CHECK                  │
│     │                                                        │
│     └── PASS → Aşama 4'e geç                                 │
│                                                              │
│  4. RUNTIME-CHECK (FAZ-3)                                    │
│     Runtime log ↔ ANA YASA ↔ Kod                              │
│     │                                                        │
│     ├── FAIL → Production ENGELLENİR → Task                  │
│     │                                                        │
│     └── PASS → ✅ Production hazır                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 23. Resmi Geliştirme Akışı

Bundan sonra HLK içerisinde resmi geliştirme akışı aşağıdaki gibidir:

```
KOD TALEBİ
      │
      ▼
┌──────────────────┐
│ CONSTITUTION GATE │  ← FAZ-0 (ZORUNLU)
│   (PRE-CHECK)     │
└──────────────────┘
      │
      ├── FAIL ──► Constitution Report + Task
      │            Kod yazılmaz. Eksik giderilir.
      │            Tekrar Gate'e dönülür.
      │
      └── PASS
            │
            ▼
      ┌──────────────┐
      │  KOD ANALİZİ   │  ← Mevcut kodu anlama
      └──────────────┘
            │
            ▼
      ┌──────────────────┐
      │  KOD GELİŞTİRME   │  ← Yeni kod / değişiklik
      └──────────────────┘
            │
            ▼
      ┌──────────────┐
      │  POST-CHECK   │  ← FAZ-2 (ZORUNLU)
      └──────────────┘
            │
            ├── FAIL ──► Constitution Task → Düzelt → Tekrar POST-CHECK
            │
            └── PASS
                  │
                  ▼
            ┌──────────────┐
            │ RUNTIME TEST  │  ← Canlı sistemde test
            └──────────────┘
                  │
                  ▼
            ┌──────────────────────┐
            │ FINAL CONSTITUTION    │  ← FAZ-3 (ZORUNLU)
            │ CHECK (RUNTIME-CHECK) │
            └──────────────────────┘
                  │
                  ├── FAIL ──► Constitution Task → Düzelt → Tekrar RUNTIME
                  │
                  └── PASS
                        │
                        ▼
                  ╔══════════════╗
                  ║  PRODUCTION  ║
                  ╚══════════════╝
```

---

## 24. FAIL Senaryosu — Örnek Akış

Gerçek bir örnek üzerinden FAIL → Düzeltme → PASS döngüsü:

```
Kod Talebi: "SAHNE-05 için handler yaz"
      │
      ▼
┌─────────────────────────────────────────────┐
│ CONSTITUTION GATE (FAZ-0)                    │
│                                              │
│ Kontrol:                                     │
│ 1. FD-008_1 SAHNE-05 → VAR (Flow Diagram)   │
│ 2. Scene Registry SAHNE-05 → YOK            │
│ 3. SE-007_3 DURATION_SELECTION → VAR        │
│ 4. handle_resolution_selection() delivery    │
│    → produce_and_deliver() çağrısı YOK       │
│                                              │
│ SONUÇ: CONSTITUTION FAIL                     │
│ CİDDİYET: KRİTİK                              │
└─────────────────────────────────────────────┘
      │
      ▼
KOD YAZILMAZ.
      │
      ▼
┌─────────────────────────────────────────────┐
│ Constitution Report CDE-20260702-0001        │
│ Constitution Task TASK-CD-20260702-0001      │
│                                              │
│ EKSİK:                                       │
│ ☑ SAHNE-05 SceneDefinition                  │
│ ☑ produce_and_deliver() çağrısı             │
│ ☑ SAHNE-05 Sahne Kayıt Defteri kaydı        │
└─────────────────────────────────────────────┘
      │
      ▼
Eksik giderilir:
  1. scene_registry.py'e SAHNE-05 eklenir
  2. handle_resolution_selection() delivery eklenir
  3. 17_SAHNE_KAYIT_DEFTERİ.md güncellenir
      │
      ▼
┌─────────────────────────────────────────────┐
│ CONSTITUTION GATE (FAZ-0) — TEKRAR           │
│                                              │
│ Kontrol:                                     │
│ 1. FD-008_1 SAHNE-05 → VAR ✅               │
│ 2. Scene Registry SAHNE-05 → VAR ✅         │
│ 3. handle_resolution_selection() delivery    │
│    → produce_and_deliver() VAR ✅            │
│                                              │
│ SONUÇ: CONSTITUTION PASS                     │
└─────────────────────────────────────────────┘
      │
      ▼
Kod geliştirmesi devam eder.
```

---

## 25. MASTER-003 Entegrasyonu

CONSTITUTION GATE ve CDE kuralları, MASTER-003'ün aşağıdaki maddelerinin
operasyonel uygulamasıdır:

| MASTER-003 Maddesi | CDE Karşılığı |
|---|---|
| **Zorunlu Uyum Analizi** | FAZ-0 CONSTITUTION GATE — her geliştirme öncesi otomatik tetiklenir |
| **Zorunlu Kontroller** (6 soru) | Çapraz Denetim Matrisi — 5.1–5.5 arası tüm kontroller |
| **Tamamlanma Kriteri** | CDE-003 + CDE-004 + CDE-005 — üç aşamalı PASS zinciri |
| **Uyumluluk Raporu Zorunluluğu** | Constitution Report formatı (Bölüm 7) |
| **Kritik Kural** ("Kural güncellendi, işlem tamam") | CDE-002 — FAIL'de kod yazılmaz |
| **Gerçek Tamamlanma Tanımı** | Dört zorunlu kontrol noktası (Bölüm 22) |
| **Workaround Politikası** | CONSTITUTIONAL_VIOLATION — her workaround ihlal olarak raporlanır |

CONSTITUTION GATE;

- MASTER-003'ün **yerine geçmez.**
- MASTER-003'ü **değiştirmez.**
- MASTER-003'ün **zorunlu uygulama mekanizmasıdır.**

MASTER-003'te tanımlanan "Analiz Zorunluluğu" sırası, CONSTITUTION GATE
tarafından otomatik ve zorunlu hale getirilir. Geliştirici (Claude dahil) bu
sırayı atlayarak kod yazamaz.

---

## 26. Temel İlke

CDE, HLK'nın anayasal denetim katmanıdır.

CDE'nin görevi;

- ANA YASA ile kod arasındaki uyumsuzlukları tespit etmek,
- Her ihlali MASTER-003 formatında raporlamak,
- Her ihlal için düzeltme görevi (Constitution Task) üretmek,
- Geliştirme öncesi (FAZ-0), sonrası (FAZ-2) ve runtime sonrası (FAZ-3) otomatik denetim yapmaktır.

CDE'nin görevi;

- Karar vermek,
- Kod yazmak,
- Kod değiştirmek,
- ANA YASA'yı değiştirmek

**değildir.**

CONSTITUTION GATE sayesinde HLK;

```
ANA YASA → Kod
```

değil,

```
ANA YASA ⇄ Kod
```

ilişkisini yönetir.

Bu modül, MASTER-003'te tanımlanan "ANA YASA Güncellendi ≠ Kod Güncellendi" ilkesini
sistematik, otomatik ve **zorunlu** hale getirir.

**Bugünden itibaren:**

- Hiçbir kod, CONSTITUTION GATE PASS almadan geliştirilemez.
- Hiçbir handler, CDE denetimi olmadan yazılamaz.
- Hiçbir workflow, ANA YASA kaydı olmadan oluşturulamaz.
- Hiçbir state, State Engine'de karşılığı olmadan tanımlanamaz.
- Hiçbir feature, Feature Registry kaydı olmadan eklenemez.
- Hiçbir scene, Scene Registry'de SceneDefinition olmadan kullanılamaz.

---

## 27. Anayasal Yetki

Bu dosya, MASTER-001 Karar Hiyerarşisi'nde tanımlanan otorite sıralamasına tabidir.

Bu dosya;

- MASTER RULE BOOK'u uygulamak için vardır.
- MASTER RULE BOOK bu dosyayı uygulamak için var değildir.

CDE, MASTER-004 (HLK Karar Mekanizması ve Kural Otoritesi Prensibi) gereği:

- bağımsız karar verici değil,
- HLK'nın karar mekanizmasını yönlendiren denetim katmanıdır.

CONSTITUTION GATE, MASTER-001 Karar Hiyerarşisi'ne **yeni bir katman eklemez.**
Mevcut hiyerarşideki MASTER-003 maddesinin **zorunlu operasyonel uygulamasıdır.**

CONSTITUTION GATE'in PASS/FAIL kararı;

- MASTER-001 otorite hiyerarşisini değiştirmez.
- MASTER-004 karar mekanizmasını değiştirmez.
- Yalnızca MASTER-003'ün uygulanmasını **garanti eder.**

---

**Hazırlayan:** HLK — Claude Code  
**Tarih:** 2026-07-02  
**Güncelleme:** 2026-07-02 — CONSTITUTION GATE, FAZ-0, CDE-001/005 kuralları eklendi  
**Referans:** MASTER-001, MASTER-003, MASTER-004, MASTER-006
