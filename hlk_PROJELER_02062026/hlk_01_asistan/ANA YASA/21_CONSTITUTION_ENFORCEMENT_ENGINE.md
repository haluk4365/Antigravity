# 21 — Constitution Enforcement Engine (CEE)

HLK'nın anayasal uygulatma katmanıdır. Executor'dan (Claude) önce anayasal
görev paketini oluşturur, Executor'dan sonra çıktıyı anayasal kurallara göre
denetler, uygunsuzluğu REDDEDER, eksikleri Executor'a geri gönderir ve yalnızca
tam uyum sağlandığında PASS vererek görevi tamamlanmış kabul eder.

CEE, HLK'nın **"öneri veren" bir sistem olmaktan çıkıp "uygulatan, denetleyen,
kabul eden, reddeden" anayasal otorite haline gelmesini sağlayan katmandır.**

---

## 1. Anayasal Konum

CEE, MASTER-001 Karar Hiyerarşisi'ne yeni bir katman eklemez. Mevcut hiyerarşiyi
destekleyen ve Executor ile HLK arasında konumlanan **zorunlu geçiş katmanıdır.**

```
MASTER RULE BOOK
       │
       ▼
  [Karar Hiyerarşisi: GC → GK → AR → SE → FD → OR → QR → MR → Kod]
       │
       ▼
  DECISION ENGINE (HLK — tek karar verici, MASTER-004)
       │
       ▼
  ┌─────────────────────────────────────────────┐
  │  CONSTITUTION ENFORCEMENT ENGINE (CEE)       │
  │                                               │
  │  ┌──────────┐   ┌──────────┐   ┌──────────┐  │
  │  │ PRE-CHECK│──▶│ EXECUTE  │──▶│POST-CHECK│  │
  │  │ (Paket   │   │ (Claude'a│   │ (Denetim │  │
  │  │  Hazırla)│   │  gönder) │   │  + PASS/ │  │
  │  └──────────┘   └──────────┘   │  FAIL)   │  │
  │                     ▲          └────┬─────┘  │
  │                     │       FAIL    │        │
  │                     └───────────────┘        │
  └─────────────────────────────────────────────┘
       │
       ▼
  EXECUTOR (Claude — yalnızca uygulayıcı)
```

**Karar yetkisi:** CEE karar vermez. Karar yalnızca Decision Engine'indir
(MASTER-004). CEE, Decision Engine'in kararını **uygulatır, denetler ve
gerektiğinde reddeder.**

**Otorite:** MASTER-001 Karar Hiyerarşisi'ne tabidir. CEE'nin PASS/FAIL
kararları MASTER-003 (ANA YASA / Kod Uyumluluk Denetim Prensibi) kapsamında
değerlendirilir.

---

## 2. Amaç

HLK içerisinde;

- Executor'un (Claude) ne yapacağını anayasal kurallardan otomatik üretmek,
- Executor'un yaptığı işi otomatik denetlemek,
- Anayasaya uymayan hiçbir geliştirmeyi kabul etmemek,
- Eksik uygulamaları otomatik tespit edip tekrar Executor'a göndermek,
- PASS verilmeden görevi tamamlanmış kabul etmemek

CEE'nin amacı kodu değiştirmek değil; HLK'nın anayasal otoritesini Executor
üzerinde **zorunlu kılmak** ve Executor'un anayasa dışına çıkmasını
**kesin olarak engellemektir.**

---

## 3. Temel İlkeler

1. **CEE karar vermez.** Karar Decision Engine'indir (MASTER-004). CEE uygulatır.
2. **CEE kod yazmaz.** Kod yalnızca Executor (Claude) tarafından yazılır.
3. **CEE ANA YASA'yı değiştirmez.** MASTER-001 gereği yalnızca Proje Yöneticisi değiştirebilir.
4. **CEE tek PASS/FAIL otoritesidir.** CSE, CDE, Task Engine PASS/FAIL veremez. Yalnızca CEE verir.
5. **PASS olmadan görev tamamlanmış kabul edilemez.** MASTER-003 Tamamlanma Kriteri'nin operasyonel uygulamasıdır.
6. **FAIL durumunda görev Executor'a geri gönderilir.** Eksikler giderilene kadar döngü devam eder.
7. **CEE zorunlu geçiş noktasıdır.** Hiçbir geliştirme görevi CEE'nin PRE-CHECK'inden geçmeden başlayamaz, POST-CHECK'inden geçmeden tamamlanamaz.
8. **Executor yalnızca uygulayıcıdır.** Claude hiçbir zaman karar verici değildir; yalnızca CEE'nin hazırladığı anayasal paketi uygular.

---

## 4. CEE'nin 3 Fazı

CEE üç aşamalı çalışır:

### FAZ 1: PRE-CHECK — Anayasal Görev Paketi Oluşturma

CEE, Executor göreve başlamadan önce:

#### 4.1.1 İlgili Anayasa Maddelerini Toplar

| Kaynak | Toplanan Veri |
|---|---|
| `00_HLK_MASTER_RULE_BOOK.md` | İlgili MASTER kuralları (MASTER-001 — MASTER-006) |
| `03_Architecture_Rules.md` | İlgili AR kuralları |
| `04_Operational_Rules.md` | İlgili OR kuralları |
| `07_HLK_STATE_ENGINE.md` | İlgili State, Event, Transition, Action tanımları |
| `08_HLK_FLOW_DIAGRAM.md` | İlgili FD-008_1 akış adımları, FD-008_2 referans tablosu |
| `06_Module_Rule.md` | İlgili MR kuralları |
| `01_Global_Configuration.md` | İlgili GC parametreleri |

#### 4.1.2 Anayasal Görev Paketi (Constitutional Task Package) Oluşturur

Her görev paketi aşağıdaki bölümleri içerir:

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTIONAL TASK PACKAGE (CEE-CTP-YYYYMMDD-NNNN)     ║
╠═══════════════════════════════════════════════════════════╣
║  GÖREV TANIMI                                             ║
║  - Ne yapılacak                                           ║
║  - Hangi dosyalar etkilenecek                             ║
║  - Başarı kriterleri                                      ║
╠═══════════════════════════════════════════════════════════╣
║  İLGİLİ ANA YASA MADDELERİ                                ║
║  ☐ MASTER-XXX: <kural özeti>                              ║
║  ☐ AR-XXX: <kural özeti>                                  ║
║  ☐ OR-XXX: <kural özeti>                                  ║
║  ☐ FD-008_X: <akış adımı>                                 ║
║  ☐ SE-007_X: <state/event kuralı>                         ║
╠═══════════════════════════════════════════════════════════╣
║  ZORUNLU KONTROLLER (Executor'un yapmak zorunda oldukları)║
║  1. <Kontrol 1> — Kural: <ANA YASA referansı>             ║
║  2. <Kontrol 2> — Kural: <ANA YASA referansı>             ║
║  ...                                                      ║
╠═══════════════════════════════════════════════════════════╣
║  DEĞİŞTİRİLMEZ ALANLAR                                    ║
║  ❌ State isimleri                                        ║
║  ❌ State geçiş kuralları                                 ║
║  ❌ Workflow yapısı                                       ║
║  ❌ Mevcut mimari                                         ║
║  ❌ ANA YASA maddeleri                                    ║
╠═══════════════════════════════════════════════════════════╣
║  BEKLENEN ÇIKTI FORMATI                                   ║
║  - Hangi dosyalar değişecek                               ║
║  - Hangi yeni dosyalar oluşacak                           ║
║  - Hangi testler yapılacak                                ║
╚═══════════════════════════════════════════════════════════╝
```

#### 4.1.3 Executor'a İletir

- Hazırlanan CTP, Executor'a (Claude) iletilir
- Executor yalnızca pakette tanımlanan işlemleri yapabilir
- Paket dışına çıkan işlemler POST-CHECK'te otomatik reddedilir
- "Değiştirilmez" alanlara müdahale tespit edilirse anında FAIL

### FAZ 2: EXECUTE — Executor Denetimli Çalışır

Executor (Claude) paketi uygular. CEE bu aşamada pasiftir; yalnızca görev
tanımlandığı şekilde ilerler. Executor'un görev süresi dolduğunda veya
Executor "tamamlandı" bildirdiğinde FAZ 3 başlar.

### FAZ 3: POST-CHECK — Anayasal Denetim ve PASS/FAIL

Executor işlemi tamamladığını bildirdiğinde CEE devreye girer ve aşağıdaki
denetimleri sırayla uygular:

#### 4.3.1 Kod-Anayasa Karşılaştırması (CDE Matrisi ile)

CDE'nin çapraz denetim matrisini kullanarak:

| Denetim | Kontrol |
|---|---|
| State Denetimi | ANA YASA state'leri kodda enum olarak var mı? |
| Event Denetimi | ANA YASA event'leri kodda enum olarak var mı? |
| Transition Denetimi | ANA YASA geçişleri STATE_TRANSITIONS'da tanımlı mı? |
| Scene Denetimi | Flow Diagram sahneleri SCENE_REGISTRY'de kayıtlı mı? |
| Handler Denetimi | Handler'lar main.py'de kayıtlı mı? |
| Delivery Denetimi | Her handler produce_and_deliver() çağırıyor mu? |
| Cleanup Denetimi | Her sahne geçişinde cleanup_chat() çağrılıyor mu? |

#### 4.3.2 Flow Diagram Uyumluluk Kontrolü

- FD-008_1'de tanımlı her SAHNE'nin kodda karşılığı var mı?
- SAHNE geçişleri Flow Diagram'daki yönde mi?
- Ekran temizleme ("EKRAN SİLİNİR") adımları uygulanmış mı?
- Buton davranışları Flow Diagram ile uyumlu mu?
- "Birden Fazla Seçim" / "Tek Seçim" kuralları doğru uygulanmış mı?
- Üretilen konuşma, aktif sahnenin amacı ile uyumlu mu?
- Üretilen konuşma yalnızca Flow Diagram'da tanımlanan sahne kapsamında mı?
- Konuşma, sahnede belirtilen sunum yöntemiyle (konuşma baloncuğu, daktilo efekti vb.) gösteriliyor mu?
- Flow Diagram'da belirtilen "EKRAN SİLİNİR" adımları eksiksiz uygulanıyor mu?
- Executor (Claude), sahnede tanımlanmayan ek soru, açıklama veya yönlendirme üretmiş mi?
- Bir sonraki sahneye yalnızca ilgili Event oluştuktan sonra geçilmiş mi?

### Beklenen Sonuç

Constitution Enforcement Engine, yalnızca **State** ve **Event** uyumluluğunu değil;

* Sahne davranışını,
* Konuşma akışını,
* Sunum şeklini

de anayasal olarak denetler.

#### 4.3.3 State Engine Uyumluluk Kontrolü

- State isimleri ANA YASA'daki halleriyle korunmuş mu? (DEĞİŞTİRİLMEMİŞ olmalı)
- Transition kuralları SE-007_4 ile uyumlu mu?
- Event tetikleyicileri SE-007_5 ile uyumlu mu?
- State Action Map SE-007_6 ile uyumlu mu?
- Yeni eklenen state/event varsa, SE-007_3/4/5/6'ya kaydedilmiş mi?

#### 4.3.4 Operational Rules Uyumluluk Kontrolü

- OR-004_x kurallarına uyulmuş mu?
- Zorunlu validasyonlar (link, süre, format) yapılmış mı?
- Cleanup zinciri eksiksiz mi?
- Timeout mekanizması her state için çalışıyor mu?
- "Kesinlikle yasak" işlemler yapılmamış mı?

#### 4.3.5 Mimari Bütünlük Kontrolü

- Mevcut mimari bozulmuş mu?
- Mevcut state isimleri değiştirilmiş mi?
- Mevcut workflow bozulmuş mu?
- Hardcoded değerler eklenmiş mi? (GC parametreleri kullanılmalı)
- Yeni kod mevcut kod formatına uygun mu?

#### 4.3.6 Runtime Davranış Doğrulaması (MASTER-003)

- Kod çalışıyor mu? (Syntax kontrolü)
- Beklenen davranışı üretiyor mu?
- Log çıktıları ANA YASA ile uyumlu mu?
- STATE geçiş logları doğru mu?
- Aktif sahneye ait konuşma baloncuğu başarıyla oluşturuldu mu?
- Konuşma baloncuğu daktilo efekti ile görüntülendi mi?
- Kullanıcıya gösterilen konuşma, Flow Diagram'daki aktif sahnenin amacı ile uyumlu mu?
- Flow Diagram'da tanımlanan "EKRAN SİLİNİR" adımları çalışma anında eksiksiz uygulandı mı?
- Sahne tamamlanmadan sonraki sahneye geçiş yapılmış mı?
- Runtime davranışı ile `08_HLK_FLOW_DIAGRAM.md` arasında herhangi bir sapma oluşmuş mu?

### Beklenen Sonuç

Runtime doğrulaması yalnızca kodun çalışmasını değil;

* Konuşma davranışını,
* Sunum davranışını,
* Sahne akışını,
* Flow Diagram uyumluluğunu

da doğrular.

Herhangi bir sapma tespit edilirse anayasal ihlal olarak raporlanır.

## 5. PASS/FAIL Mekanizması

CEE, HLK içerisinde **PASS ve FAIL verme yetkisine sahip tek katmandır.**
CSE, CDE ve Task Engine PASS/FAIL üretemez.

### 5.1 PASS — Geçti

Tüm denetimlerden başarıyla geçildiğinde:

```
╔═══════════════════════════════════════════════════════════╗
║                    ✅ PASS                                 ║
╠═══════════════════════════════════════════════════════════╣
║  Tüm anayasal kontroller başarıyla tamamlandı.            ║
║  Görev "TAMAMLANDI" olarak işaretlenir.                   ║
║  Kod değişiklikleri kalıcı hale gelir.                    ║
║  Geliştirme süreci bu görev için sonlanır.                ║
╚═══════════════════════════════════════════════════════════╝
```

### 5.2 FAIL — Kaldı

Herhangi bir denetimden geçilemediğinde:

```
╔═══════════════════════════════════════════════════════════╗
║                    ❌ FAIL                                 ║
╠═══════════════════════════════════════════════════════════╣
║  Aşağıdaki anayasal uyumsuzluklar tespit edildi:          ║
║                                                           ║
║  ❌ <Eksik 1> — Kural: <ANA YASA referansı>               ║
║     Açıklama: <ne eksik, neden önemli>                    ║
║                                                           ║
║  ❌ <Eksik 2> — Kural: <ANA YASA referansı>               ║
║     Açıklama: <ne eksik, neden önemli>                    ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  GÖREV EXECUTOR'A GERİ GÖNDERİLDİ                         ║
║  Yukarıdaki eksikler giderilene kadar PASS verilmez.      ║
╚═══════════════════════════════════════════════════════════╝
```

### 5.3 FAIL Sonrası Akış

1. CEE, Enforcement Report ile birlikte eksikleri Executor'a iletir
2. Executor eksikleri giderir
3. Executor "düzeltme tamamlandı" bildirir
4. CEE POST-CHECK'i tekrar çalıştırır
5. PASS alınana kadar döngü devam eder
6. **Maksimum 3 FAIL döngüsü.** 3. FAIL'den sonra görev ESCALATE edilir; Proje Yöneticisi müdahalesi gerekir.

---

## 6. CEE Enforcement Report Formatı

Her POST-CHECK sonucu aşağıdaki standart formatta raporlanır:

```
╔═══════════════════════════════════════════════════════════╗
║  CONSTITUTION ENFORCEMENT REPORT (CEE)                   ║
╠═══════════════════════════════════════════════════════════╣
║  Report No     : CEE-YYYYMMDD-NNNN                        ║
║  Bağlı CTP     : CEE-CTP-YYYYMMDD-NNNN                   ║
║  Executor      : Claude                                  ║
║  Denetim Fazı  : POST-CHECK                              ║
║  Deneme        : N / 3                                   ║
║  Tarih         : YYYY-MM-DD HH:MM:SS                      ║
╠═══════════════════════════════════════════════════════════╣
║  NİHAİ SONUÇ   : ✅ PASS / ❌ FAIL                         ║
╠═══════════════════════════════════════════════════════════╣
║  DENETİM SONUÇLARI:                                       ║
║  ☑ Kod-Anayasa Karşılaştırması — <PASS/FAIL>             ║
║  ☑ Flow Diagram Uyumu — <PASS/FAIL>                      ║
║  ☑ State Engine Uyumu — <PASS/FAIL>                      ║
║  ☑ Operational Rules Uyumu — <PASS/FAIL>                 ║
║  ☑ Mimari Bütünlük — <PASS/FAIL>                         ║
║  ☑ Runtime Davranış — <PASS/FAIL>                        ║
╠═══════════════════════════════════════════════════════════╣
║  (FAIL durumunda)                                         ║
║  EKSİK SAYISI : N                                        ║
║                                                           ║
║  ❌ Eksik 1: <açıklama>                                   ║
║     Kural: <ANA YASA referansı>                           ║
║     Dosya: <etkilenen dosya>                              ║
║                                                           ║
║  ❌ Eksik 2: <açıklama>                                   ║
║     Kural: <ANA YASA referansı>                           ║
║     Dosya: <etkilenen dosya>                              ║
╠═══════════════════════════════════════════════════════════╣
║  DURUM: <PASS: GELİŞTİRME TAMAMLANDI>                    ║
║         <FAIL: EXECUTOR'A GERİ GÖNDERİLDİ>               ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 7. Denetim Kapsamı ve Kontrol Listesi

CEE POST-CHECK sırasında aşağıdaki kontrol listesini uygular:

### 7.1 Kod-Anayasa Karşılaştırması

| # | Kontrol | Kriter |
|---|---|---|
| K1 | State varlığı | ANA YASA'daki her state kodda UserState enum'ında var mı? |
| K2 | Event varlığı | ANA YASA'daki her event kodda UserEvent enum'ında var mı? |
| K3 | Transition varlığı | ANA YASA'daki her geçiş STATE_TRANSITIONS'da tanımlı mı? |
| K4 | Scene varlığı | Flow Diagram'daki her SAHNE SCENE_REGISTRY'de kayıtlı mı? |
| K5 | Handler kaydı | Her sahne callback'i main.py'de CallbackQueryHandler olarak kayıtlı mı? |
| K6 | Delivery zinciri | Her handler produce_and_deliver() çağırıyor mu? |
| K7 | Cleanup zinciri | Her sahne geçişinde cleanup_chat() çağrılıyor mu? |
| K8 | Action Map | Her state için STATE_ACTION_MAP'te aksiyon tanımlı mı? |

### 7.2 Flow Diagram Uyumu

| # | Kontrol | Kriter |
|---|---|---|
| F1 | Sahne sırası | SAHNE'ler FD-008_1'deki sırada mı? |
| F2 | Geçiş yönü | SAHNE'ler arası geçişler FD-008_1'deki yönde mi? |
| F3 | Ekran temizleme | Her "EKRAN SİLİNİR" adımı uygulanmış mı? |
| F4 | Buton davranışı | Seçim tipleri (tek/çoklu) doğru uygulanmış mı? |
| F5 | Bilgi metinleri | "📌" ile belirtilen kurallar ekranda gösteriliyor mu? |
| F6 | DEVAM butonu | Doğru zamanda görünüp kayboluyor mu? |

### 7.3 State Engine Uyumu

| # | Kontrol | Kriter |
|---|---|---|
| S1 | State isimleri | ANA YASA'daki state isimleri değiştirilmemiş mi? |
| S2 | Event isimleri | ANA YASA'daki event isimleri değiştirilmemiş mi? |
| S3 | Transition bütünlüğü | Mevcut transition'lar silinmemiş mi? |
| S4 | Yeni state kaydı | Yeni eklenen state'ler SE-007_3'e kaydedilmiş mi? |
| S5 | Yeni event kaydı | Yeni eklenen event'ler SE-007_5 ve OLAY Kayıt Merkezi'ne kaydedilmiş mi? |

### 7.4 Operational Rules Uyumu

| # | Kontrol | Kriter |
|---|---|---|
| O1 | Validasyon | Zorunlu giriş kontrolleri (link, süre) yapılmış mı? |
| O2 | Cleanup | Her sahne sonrası mesaj temizliği yapılıyor mu? |
| O3 | Timeout | Her interaktif state'te timeout mekanizması var mı? |
| O4 | Retry limit | GC_MAX_PRODUCT_LINK_RETRY gibi limitlere uyulmuş mu? |
| O5 | Yasak işlemler | OR'da "kesinlikle yasak" denilen işlemler yapılmamış mı? |

### 7.5 Mimari Bütünlük

| # | Kontrol | Kriter |
|---|---|---|
| M1 | Katman koruması | State isimleri, workflow, mevcut mimari bozulmamış mı? |
| M2 | GC uyumu | Hardcoded değer yerine GC parametreleri kullanılmış mı? |
| M3 | Kod formatı | Yeni kod mevcut format ve standartlara uygun mu? |
| M4 | Singleton'lar | scene_delivery, conversation_scene_engine gibi singleton'lar korunmuş mu? |
| M5 | Import düzeni | Gereksiz import eklenmemiş, mevcut import'lar bozulmamış mı? |

### 7.6 Runtime Davranış

| # | Kontrol | Kriter |
|---|---|---|
| R1 | Syntax | Kod hatasız derleniyor mu? |
| R2 | State log'ları | State geçiş log'ları beklenen formatta mı? |
| R3 | Cleanup log'ları | CLEANUP TRACE çıktıları doğru mu? |
| R4 | Hata log'ları | Kritik olmayan hatalar sessizce handle ediliyor mu? |

---

## 8. CEE İhlal Türleri (ENFORCEMENT_VIOLATION Types)

| İhlal Türü | Teknik Sabit | Açıklama | Ciddiyet |
|---|---|---|---|
| Anayasa dışı state değişikliği | `STATE_NAME_MODIFIED` | ANA YASA'daki state ismi değiştirilmiş | KRİTİK |
| Anayasa dışı event değişikliği | `EVENT_NAME_MODIFIED` | ANA YASA'daki event ismi değiştirilmiş | KRİTİK |
| Eksik transition | `TRANSITION_MISSING` | ANA YASA'da tanımlı geçiş kodda yok | KRİTİK |
| Eksik sahne | `SCENE_MISSING` | Flow Diagram'daki SAHNE kodda yok | KRİTİK |
| Mimari bozulma | `ARCHITECTURE_BROKEN` | Mevcut mimari yapı bozulmuş | KRİTİK |
| Workflow bozulması | `WORKFLOW_BROKEN` | Mevcut workflow değiştirilmiş | KRİTİK |
| Eksik cleanup | `CLEANUP_MISSING` | Sahne geçişinde cleanup yok | YÜKSEK |
| Eksik delivery | `DELIVERY_MISSING` | Handler produce_and_deliver çağırmıyor | YÜKSEK |
| Hardcoded değer | `HARDCODED_VALUE` | GC parametresi yerine sabit değer | YÜKSEK |
| Eksik handler kaydı | `HANDLER_NOT_REGISTERED` | Callback handler main.py'de kayıtlı değil | YÜKSEK |
| Flow uyumsuzluğu | `FLOW_MISMATCH` | SAHNE davranışı Flow Diagram'dan farklı | ORTA |
| Eksik validasyon | `VALIDATION_MISSING` | Zorunlu giriş kontrolü yapılmamış | ORTA |
| Timeout eksik | `TIMEOUT_MISSING` | İnteraktif state'te timeout mekanizması yok | ORTA |
| Format uyumsuzluğu | `FORMAT_MISMATCH` | Yeni kod mevcut format standartlarına uymuyor | DÜŞÜK |
| Gereksiz import | `UNNECESSARY_IMPORT` | Kullanılmayan import eklenmiş | DÜŞÜK |
| Paket dışı işlem | `OUT_OF_SCOPE` | Executor CTP kapsamı dışında işlem yapmış | KRİTİK |
| Değiştirilmez alan ihlali | `IMMUTABLE_VIOLATION` | "Değiştirilmez" işaretli alana müdahale | KRİTİK |

---

## 9. Diğer Katmanlarla Entegrasyon

CEE aşağıdaki mevcut katmanlarla birlikte çalışır:

| Katman | CEE ile İlişkisi | Veri Akışı |
|---|---|---|
| **Decision Engine** | CEE, Decision Engine'in kararını uygulatır | Decision Engine → CEE (karar) |
| **Constitutional Validator** | CEE, Validator'ün BLOCK verdiği durumlarda Executor'u durdurur | Validator → CEE (BLOCK sinyali) |
| **CSE (Constitution Scan Engine)** | CEE, PRE-CHECK'te CSE'den Snapshot alır | CSE → CEE (Snapshot) |
| **CDE (Constitution Diff Engine)** | CEE, POST-CHECK'te CDE'nin çapraz denetim matrisini kullanır | CDE → CEE (ihlal verisi) |
| **Task Engine** | CEE, görev paketini Task Engine üzerinden Executor'a iletir | CEE → Task Engine → Claude |
| **Feedback Loop** | CEE FAIL verdiğinde Feedback Loop'u tetikler → Decision Engine yeniden karar üretir | CEE → Feedback Loop → Decision Engine |
| **Constitution Gate** | CEE, Gate ile aynı prensipte çalışır; Gate'i operasyonel olarak uygular | CEE ↔ Gate (çift yönlü) |

### Entegrasyon Akışı

```
KOD TALEBİ
    │
    ▼
DECISION ENGINE (HLK karar üretir)
    │
    ▼
CEE PRE-CHECK ──── CSE'den Snapshot alır
    │
    ▼
CEE → Task Engine → Claude (CTP iletilir)
    │
    ▼
Claude kodu yazar (EXECUTE — CEE pasif)
    │
    ▼
CEE POST-CHECK ──── CDE matrisi + Flow kontrol + State kontrol + OR kontrol
    │
    ├── PASS ──► TAMAMLANDI
    │
    └── FAIL ──► Enforcement Report → Executor'a geri gönder
         │
         └── 3. FAIL ──► ESCALATE → Proje Yöneticisi
```

---

## 10. CEE Teknik Sabitleri

| Teknik Sabit | Değer | Açıklama |
|---|---|---|
| `CEE_MAX_ENFORCEMENT_RETRIES` | 3 | Maksimum FAIL döngüsü sayısı |
| `CEE_ENFORCEMENT_TIMEOUT` | 300 | Denetim zaman aşımı (saniye) |
| `CEE_PRE_CHECK_PHASE` | `FAZ-1` | PRE-CHECK faz tanımlayıcısı |
| `CEE_POST_CHECK_PHASE` | `FAZ-3` | POST-CHECK faz tanımlayıcısı |
| `CEE_EXECUTE_PHASE` | `FAZ-2` | EXECUTE faz tanımlayıcısı |
| `CEE_REPORT_PREFIX` | `CEE` | Rapor numarası ön eki |
| `CEE_CTP_PREFIX` | `CEE-CTP` | Constitutional Task Package ön eki |

---

## 11. CEE Event'leri (Olay Kayıt Merkezi)

CEE aşağıdaki event'leri OLAY KAYIT MERKEZİ'ne kaydeder:

| Olay No | Teknik Sabit | Açıklama | Öncelik |
|---|---|---|---|
| OLAY-067 | `CEE_PRE_CHECK_STARTED` | PRE-CHECK başlatıldı | NORMAL |
| OLAY-068 | `CEE_PRE_CHECK_COMPLETED` | PRE-CHECK tamamlandı, CTP oluşturuldu | YÜKSEK |
| OLAY-069 | `CEE_CTP_DELIVERED` | CTP Executor'a iletildi | YÜKSEK |
| OLAY-070 | `CEE_POST_CHECK_STARTED` | POST-CHECK başlatıldı | YÜKSEK |
| OLAY-071 | `CEE_POST_CHECK_COMPLETED` | POST-CHECK tamamlandı | YÜKSEK |
| OLAY-072 | `CEE_PASS` | Tüm denetimlerden geçti — görev tamamlandı | YÜKSEK |
| OLAY-073 | `CEE_FAIL` | Denetim başarısız — görev Executor'a geri gönderildi | KRİTİK |
| OLAY-074 | `CEE_ESCALATE` | 3 FAIL sonrası Proje Yöneticisine eskalasyon | KRİTİK |
| OLAY-075 | `CEE_VIOLATION_FOUND` | Anayasal ihlal tespit edildi | YÜKSEK |
| OLAY-104 | `CEE_CONSTITUTIONAL_EVIDENCE_REPORT` | Anayasal Kanıt Raporu oluşturuldu — eskalasyon kanıt paketi | KRİTİK |
| OLAY-105 | `CEE_SELF_CORRECTION_ATTEMPTED` | Kendi kendine düzeltme girişimi yapıldı (CEE-006) | YÜKSEK |
| OLAY-106 | `CEE_SELF_CORRECTION_RESULT` | Kendi kendine düzeltme sonucu (PASS/FAIL) | YÜKSEK |

---

## 12. Yetki Sınırları

### CEE'nin Yapabilecekleri

| Eylem | Yetki |
|---|---|
| Anayasa maddelerini toplamak ve CTP oluşturmak | ✅ VAR |
| Executor'u anayasal kurallarla yönlendirmek | ✅ VAR |
| Executor çıktısını anayasaya göre denetlemek | ✅ VAR |
| Kod-Anayasa farklarını tespit etmek | ✅ VAR |
| Eksik uygulanan kuralları listelemek | ✅ VAR |
| Flow Diagram uyumluluğunu kontrol etmek | ✅ VAR |
| State Engine uyumluluğunu kontrol etmek | ✅ VAR |
| Operational Rules uyumluluğunu kontrol etmek | ✅ VAR |
| Mimari bütünlüğü kontrol etmek | ✅ VAR |
| Runtime davranışını doğrulamak | ✅ VAR |
| **PASS kararı vermek** | ✅ **VAR (SADECE CEE)** |
| **FAIL kararı vermek** | ✅ **VAR (SADECE CEE)** |
| **Görevi reddetmek ve Executor'a geri göndermek** | ✅ **VAR (SADECE CEE)** |
| Eksikleri maddeler halinde Executor'a iletmek | ✅ VAR |
| 3 FAIL sonrası eskalasyon başlatmak | ✅ VAR |

### CEE'nin Yapamayacakları

| Eylem | Yetki | Gerçek Sahibi |
|---|---|---|
| Ne yapılacağına karar vermek | ❌ YOK | Decision Engine (MASTER-004) |
| Kod yazmak | ❌ YOK | Executor — Claude |
| Kodu değiştirmek | ❌ YOK | Executor — Claude |
| ANA YASA değiştirmek | ❌ YOK | Proje Yöneticisi (MASTER-001) |
| Yeni kural oluşturmak | ❌ YOK | MASTER / AR / OR katmanları |
| Yeni state oluşturmak | ❌ YOK | SE-007_3 |
| Yeni event oluşturmak | ❌ YOK | SE-007_5 / OLAY Kayıt Merkezi |
| Yeni Feature oluşturmak | ❌ YOK | Feature Registry |
| Yeni Workflow oluşturmak | ❌ YOK | Workflow Manifest |
| PASS/FAIL yetkisini devretmek | ❌ YOK | — (yetki devredilemez) |

---

## 13. CEE Yönetim Kuralları (CEE-001 — CEE-005)

### CEE-001 — Zorunlu Geçiş Kuralı

Hiçbir geliştirme görevi CEE PRE-CHECK'inden geçmeden başlayamaz.
Hiçbir geliştirme görevi CEE POST-CHECK'inden geçmeden tamamlanamaz.
CEE, Executor ile HLK arasındaki **zorunlu tek geçiş noktasıdır.**

### CEE-002 — Executor Sınırlandırma Kuralı

Executor (Claude) yalnızca CEE tarafından hazırlanan CTP (Constitutional Task
Package) kapsamında işlem yapabilir. CTP dışına çıkan her işlem POST-CHECK'te
`OUT_OF_SCOPE` ihlali olarak tespit edilir ve otomatik FAIL verilir.

### CEE-003 — Değiştirilmez Alan Kuralı

CEE, CTP içerisinde "Değiştirilmez" olarak işaretlenen alanlara yapılan her
müdahaleyi `IMMUTABLE_VIOLATION` olarak tespit eder. Bu ihlal türü KRİTİK
ciddiyettedir ve derhal FAIL ile sonuçlanır.

### CEE-004 — PASS Olmadan Tamamlanma Kuralı

CEE'den PASS almamış hiçbir görev "TAMAMLANDI" olarak işaretlenemez.
Bu kural MASTER-003'ün operasyonel uygulamasıdır:
ANA YASA Güncellendi + Kod Güncellendi + Runtime Doğrulandı + **CEE PASS** = TAMAMLANDI

### CEE-005 — Eskalasyon Kuralı

Aynı görev için 3 FAIL döngüsünden sonra CEE otomatik düzeltme döngüsünü
sonlandırır ve görevi Proje Yöneticisine eskalasyon olarak iletir.
Eskalasyon sonrası karar yalnızca Proje Yöneticisine aittir.

### CEE-006 — Kendi Kendine Düzeltme Kuralı (Self-Correction)

HLK, anayasal bir sapma tespit ettiğinde görevi doğrudan Executor'a (Claude)
veya geliştiriciye göndermeden ÖNCE kendi kendine düzeltme girişiminde bulunur.

Kendi kendine düzeltme şu adımları izler:

1. **Sapma Analizi:** CEE, tespit edilen anayasal sapmanın türünü (STATE_NAME_MODIFIED,
   SCENE_MISSING, HARDCODED_VALUE, vb.) ve kapsamını belirler.

2. **Düzeltme Stratejisi Seçimi:** HLK, sapma türüne göre uygun düzeltme stratejisini
   belirler:
   - **State uyumsuzluğu:** ANA YASA'daki state ismi ile uyumlu hale getirir
   - **Eksik transition:** STATE_TRANSITIONS'a gerekli geçişi ekler
   - **Eksik sahne:** SCENE_REGISTRY'ye gerekli SceneDefinition'ı ekler
   - **Eksik handler:** main.py'ye gerekli CallbackQueryHandler'ı kaydeder
   - **Hardcoded değer:** GC parametresi ile değiştirir
   - **Eksik cleanup:** cleanup_chat() çağrısını ekler
   - **Eksik validasyon:** Zorunlu giriş kontrolünü ekler

3. **Düzeltme Uygulaması:** HLK, seçilen stratejiyi uygular. Bu aşamada:
   - Yalnızca sapma ile doğrudan ilişkili kod/dosya değişiklikleri yapılır
   - Mevcut mimari, state isimleri, workflow yapısı KORUNUR
   - Değiştirilmez alanlara (IMMUTABLE) müdahale edilmez
   - Her düzeltme adımı EEC tarafından Event olarak kaydedilir

4. **Düzeltme Sonrası Doğrulama:** Düzeltme uygulandıktan sonra CEE POST-CHECK
   (6 boyutlu denetim) yeniden çalıştırılır:
   - PASS → Düzeltme başarılı, normal akışa devam edilir
   - FAIL → Yeniden düzeltme stratejisi denenir (farklı bir strateji ile)

5. **Düzeltme Döngü Sınırı:** Kendi kendine düzeltme en fazla **2 kez** denenir.
   2 başarısız kendi kendine düzeltme girişiminden sonra:
   - HLK kendi kendine düzeltmenin mümkün olmadığına karar verir
   - Anayasal Kanıt Raporu hazırlar (bkz. Bölüm 14)
   - Görevi Executor'a geri gönderir (standart FAIL akışı)
   - Executor da başarısız olursa toplam 3 FAIL sonrası CEE-005 eskalasyonu uygulanır

**Önemli Kısıtlama:** CEE-006 kapsamında HLK'nın yapacağı kendi kendine düzeltme;
- Karar değişikliği içermez (karar Decision Engine'indir — MASTER-004)
- ANA YASA değişikliği içermez (yetki Proje Yöneticisindedir — MASTER-001)
- Yeni kural, state, event veya feature oluşturmaz
- Mevcut mimari yapıyı bozmaz
- Yalnızca tespit edilen spesifik anayasal sapmayı gidermeye yöneliktir

CEE-006, HLK'nın AR-002_62'de tanımlanan "kendi kendine müdahale etmeyi denemeden
CONSTITUTION_READY üretemez" ilkesinin operasyonel uygulamasıdır.

---

## 14. Anayasal Kanıt Raporu (Constitutional Evidence Report)

HLK, kendi kendine düzeltme girişimlerinin başarısız olduğu ve eskalasyonun
zorunlu hale geldiği durumlarda, Proje Yöneticisine sunulmak üzere bir
**Anayasal Kanıt Raporu (Constitutional Evidence Report)** hazırlar.

Bu rapor, HLK'nın "yardım çağrısı" niteliğindedir ve geliştiricinin/Proje
Yöneticisinin durumu hızlıca anlayıp müdahale edebilmesi için tüm kanıtları
standart bir formatta sunar.

### 14.1 Rapor Formatı

```
╔═══════════════════════════════════════════════════════════════════╗
║  ANAYASAL KANIT RAPORU (Constitutional Evidence Report)         ║
╠═══════════════════════════════════════════════════════════════════╣
║  Rapor No       : CE-YYYYMMDD-NNNN                               ║
║  Bağlı CTP      : CEE-CTP-YYYYMMDD-NNNN                          ║
║  Eskalasyon     : OTOMATİK (CEE-006 + CEE-005)                   ║
║  Tarih          : YYYY-MM-DD HH:MM:SS                             ║
║  Öncelik        : KRİTİK / YÜKSEK / ORTA                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  1. SAPMA ÖZETİ                                                   ║
║  ───────────────────────────────────────────────────────────────  ║
║  Tespit edilen anayasal sapmanın kısa açıklaması.                 ║
║  Ne? Nerede? Hangi kural ihlal edildi?                            ║
║                                                                   ║
║  2. ANAYASAL DAYANAK                                              ║
║  ───────────────────────────────────────────────────────────────  ║
║  İhlal edilen anayasal kural(lar):                                ║
║  📜 MASTER-XXX: <kural metni>                                     ║
║  📜 AR-002_XX: <kural metni>                                      ║
║  📜 CEE-00X: <kural metni>                                        ║
║  📜 FD-008_X: <akış adımı>                                        ║
║  📜 SE-007_X: <state/event kuralı>                                ║
║                                                                   ║
║  3. RUNTIME KANITLARI                                             ║
║  ───────────────────────────────────────────────────────────────  ║
║  Anayasal beklenti ile runtime gerçeği arasındaki fark:           ║
║                                                                   ║
║  📋 ANAYASAL BEKLENTİ:                                            ║
║  <Anayasa kaynaklarından çıkarılan beklenen davranış>             ║
║                                                                   ║
║  📊 RUNTIME GERÇEĞİ:                                              ║
║  <Boot çıktısı, log, test sonucu veya kod analizi ile            ║
║   tespit edilen gerçek durum>                                     ║
║                                                                   ║
║  🔍 SAPMA KANITI:                                                 ║
║  <İkisi arasındaki spesifik fark, dosya:satır bilgisi>           ║
║                                                                   ║
║  4. KENDİ KENDİNE DÜZELTME GİRİŞİMLERİ                            ║
║  ───────────────────────────────────────────────────────────────  ║
║  Deneme 1: <strateji> — ❌ BAŞARISIZ                              ║
║    Neden başarısız: <açıklama>                                    ║
║  Deneme 2: <strateji> — ❌ BAŞARISIZ                              ║
║    Neden başarısız: <açıklama>                                    ║
║                                                                   ║
║  5. NEDEN KENDİ KENDİNE ÇÖZÜLEMEDİ?                               ║
║  ───────────────────────────────────────────────────────────────  ║
║  <HLK'nın neden bu sorunu kendi başına çözemediğine dair         ║
║   teknik açıklama. Örn: "Değiştirilmez alan ihlali",              ║
║   "Karar yetkisi CEE'de değil", "ANA YASA değişikliği gerekli">  ║
║                                                                   ║
║  6. ÖNERİLEN GELİŞTİRİCİ AKSİYONU                                 ║
║  ───────────────────────────────────────────────────────────────  ║
║  <Proje Yöneticisi veya geliştiricinin yapması önerilen          ║
║   spesifik işlem(ler)>                                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 14.2 Rapor Üretim Tetikleyicileri

Anayasal Kanıt Raporu aşağıdaki durumlarda otomatik olarak üretilir:

| Tetikleyici | Açıklama |
|---|---|
| CEE-006 2 başarısız düzeltme | HLK 2 kez kendi kendine düzeltmeyi denedi, başarısız |
| CEE-005 3 FAIL döngüsü | Executor 3 kez düzeltme girişiminde bulundu, başarısız |
| IMMUTABLE_VIOLATION | Değiştirilmez alana müdahale gerekiyor |
| CONSTITUTION_CHANGE_REQUIRED | Sapmanın giderilmesi ANA YASA değişikliği gerektiriyor |
| DECISION_REQUIRED | HLK'nın karar yetkisi dışında bir karar gerekiyor |

### 14.3 Rapor Kayıt ve İletim

- Anayasal Kanıt Raporu, Olay Kayıt Merkezi'ne `OLAY-104` (CONSTITUTIONAL_EVIDENCE_REPORT_CREATED) olarak kaydedilir
- Rapor, LAC üzerinden Proje Yöneticisine görüntülenebilir formatta sunulur
- Rapor numarası formatı: `CE-YYYYMMDD-NNNN` (CE = Constitutional Evidence)
- Her rapor benzersizdir ve değiştirilemez
- Eskalasyon sonrası süreç Proje Yöneticisinin kararına bağlıdır

---

## 15. Beklenen Sonuç

Bu dokümanın yürürlüğe girmesiyle birlikte:

- HLK, "öneri veren" bir sistem olmaktan çıkar; **"uygulatan, denetleyen, kabul eden, reddeden"** anayasal otorite haline gelir.
- Executor (Claude) yalnızca uygulayıcı olarak çalışır; hiçbir zaman karar verici olamaz.
- Hiçbir kod, anayasal denetimden geçmeden kalıcı hale gelemez.
- Eksik veya hatalı uygulamalar otomatik tespit edilir ve düzeltilene kadar reddedilir.
- Geliştirme süreci, HLK'nın anayasal denetimi altında, kontrollü ve güvenli şekilde ilerler.
- **CEE-006 ile:** HLK, anayasal sapma tespit ettiğinde önce kendi kendine düzeltme girişiminde bulunur; Executor'a göndermeden önce 2 kez farklı stratejilerle düzeltmeyi dener.
- **Anayasal Kanıt Raporu ile:** Kendi kendine çözülemeyen durumlar, tüm kanıtlarıyla birlikte standart bir formatta Proje Yöneticisine sunulur; geliştirici yalnızca gerçekten çözülemeyen durumlarda devreye girer.

---

_CEE, HLK'nın anayasal otoritesinin Executor üzerindeki operasyonel karşılığıdır.
HLK karar verir. CEE uygulatır. Claude yalnızca uygular._

_CEE-006 ile HLK artık yalnızca "uygulatan ve denetleyen" değil, aynı zamanda
"kendi kendine düzelten" bir anayasal sistemdir. Eskalasyon son çaredir._
