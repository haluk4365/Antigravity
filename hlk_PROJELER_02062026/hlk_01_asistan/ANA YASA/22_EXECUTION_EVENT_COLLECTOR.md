# 22 — Execution Event Collector (EEC)

HLK'nın Executor (Claude) işlemlerini gerçek zamanlı Event'lere dönüştüren,
Olay Kayıt Merkezi'ne kaydeden ve Live Activity Center (LAC) tarafından
anlık görüntülenebilmesini sağlayan Event toplama katmanıdır.

EEC **hiçbir zaman Fake Progress üretmez.** Yalnızca Executor'un
gerçekleştirdiği gerçek işlemleri Event'e dönüştürür.

---

## 1. Anayasal Konum

EEC, Executor ile Olay Kayıt Merkezi arasında konumlanan **Event dönüştürme
ve toplama katmanıdır.** MASTER-001 Karar Hiyerarşisi'ne yeni katman eklemez.

```
EXECUTOR (Claude — kod yazar, dosya açar, test eder)
       │
       │  (her işlem Event olarak EEC'ye bildirilir)
       ▼
┌─────────────────────────────────────────────┐
│  EXECUTION EVENT COLLECTOR (EEC)             │
│                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │ LISTEN   │──▶│ TRANSFORM│──▶│ REGISTER │  │
│  │ (Executor│   │ (İşlem → │   │ (Olay    │  │
│  │  işlemini│   │  Event)  │   │  Kayıt   │  │
│  │  dinle)  │   └──────────┘   │  Merkezi)│  │
│  └──────────┘                  └────┬─────┘  │
│                                    │        │
│                                    ▼        │
│                           OLAY KAYIT MERKEZİ │
│                           (14_OLAY_KAYIT_)   │
└─────────────────────────────────────────────┘
       │
       │  (LAC yalnızca Olay Kayıt Merkezi'ni okur — Event üretmez)
       ▼
┌─────────────────────────────────────────────┐
│  LIVE ACTIVITY CENTER (LAC)                  │
│  (AR-002_59, FEAT-015)                       │
│                                               │
│  Yalnızca gerçek Event'leri kronolojik       │
│  olarak gösterir. Fake Progress kullanmaz.   │
└─────────────────────────────────────────────┘
```

**Karar yetkisi:** EEC karar vermez. Yalnızca dinler, dönüştürür ve kaydeder.

**Otorite:** MASTER-001 Karar Hiyerarşisi'ne tabidir. EEC'nin Event'leri
Olay Kayıt Merkezi standardına uygun olmak zorundadır.

---

## 2. Amaç

HLK içerisinde;

- Executor tarafından gerçekleştirilen her önemli işlemi Event'e dönüştürmek,
- Her Event'i PID ile ilişkilendirerek izlenebilir kılmak,
- Tüm Event'leri Olay Kayıt Merkezi'ne standart formatta kaydetmek,
- LAC'ın bu Event'leri gerçek zamanlı okuyabilmesini sağlamak,
- Fake Progress'i mimari seviyede kesin olarak engellemek

EEC'nin amacı Executor'un çalışma sürecini şeffaf ve izlenebilir hale getirmek;
LAC'a gerçek zamanlı, doğrulanmış ve güvenilir Event akışı sağlamaktır.

---

## 3. Temel İlkeler

1. **EEC yalnızca gerçek Event üretir.** Fake Progress, sahte durum mesajı veya tahmini ilerleme kesinlikle kullanılamaz.
2. **EEC karar vermez.** Yalnızca Executor işlemlerini Event'e dönüştürür.
3. **EEC kod yazmaz.** Yalnızca Event toplar ve kaydeder.
4. **EEC ANA YASA'yı değiştirmez.** MASTER-001 gereği yalnızca Proje Yöneticisi değiştirebilir.
5. **Her Event PID ile ilişkilendirilir.** PID, tüm Event'lerin ortak referansıdır.
6. **Event'ler değiştirilemez ve silinemez.** Olay Kayıt Merkezi'nin kayıt kuralları geçerlidir.
7. **LAC yalnızca Olay Kayıt Merkezi'ni okur.** LAC hiçbir Event üretmez; yalnızca tüketicidir.
8. **Görev tamamlanmadan PASS Event'i oluşturulmaz.** CEE-004 ile uyumludur.
9. **Constitution Scan tamamlanmadan görev tamamlandı kabul edilmez.** MASTER-003 ile uyumludur.
10. **Runtime doğrulaması tamamlanmadan PASS oluşturulmaz.**

---

## 4. EEC Mimarisi — LISTEN → TRANSFORM → REGISTER

EEC üç aşamalı çalışır:

### 4.1 LISTEN — Executor'u Dinle

EEC, Executor'un (Claude) aşağıdaki işlemlerini dinler:

- Görev yönetimi işlemleri (görev başlangıcı, Executor ataması)
- Anayasa tarama işlemleri (MASTER, Flow, State, Architecture, Operational)
- Dosya işlemleri (dosya açma, okuma, güncelleme, oluşturma)
- Kod geliştirme işlemleri (analiz, implementasyon, tamamlanma)
- Denetim işlemleri (Constitution Scan, Runtime Test, Syntax Check)
- Sonuç işlemleri (PASS, FAIL, Tamamlanma, Eskalasyon)

### 4.2 TRANSFORM — İşlemi Event'e Dönüştür

Her Executor işlemi, Olay Kayıt Merkezi'nin standart formatına uygun bir
Event'e dönüştürülür. Dönüştürme sırasında:

- PID otomatik eklenir
- Zaman damgası (başlangıç ve bitiş) kaydedilir
- Süre hesaplanır
- İlgili dosya, workflow ve state bilgileri ilişkilendirilir
- ExecutorID ("Claude") eklenir
- ExecutionPhase (PRE-CHECK / EXECUTE / POST-CHECK) belirtilir

### 4.3 REGISTER — Olay Kayıt Merkezi'ne Kaydet

Dönüştürülen Event, Olay Kayıt Merkezi standardında kaydedilir:

- 21 zorunlu alan + 8 EEC ek alanı
- Olay Kimliği (OLAY-XXX) atanır
- Kayıt Politikası'na göre loglanır ve Operasyon Hafızası'na yazılır
- LAC tarafından anlık okunabilir hale gelir

---

## 5. EEC Event Kategorileri

### 5.1 Kategori 1: Görev Yönetimi Event'leri

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-076 | `EVENT_TASK_STARTED` | Görev başladı | PRE-CHECK |
| OLAY-077 | `EVENT_TASK_CREATED` | Görev paketi (CTP) oluşturuldu | PRE-CHECK |
| OLAY-078 | `EVENT_EXECUTOR_ASSIGNED` | Executor (Claude) görevlendirildi | EXECUTE |

### 5.2 Kategori 2: Anayasa Tarama Event'leri

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-079 | `EVENT_MASTER_SCAN_STARTED` | MASTER kuralları taranıyor | PRE-CHECK |
| OLAY-080 | `EVENT_MASTER_SCAN_COMPLETED` | MASTER taraması tamamlandı | PRE-CHECK |
| OLAY-081 | `EVENT_FLOW_SCAN_STARTED` | Flow Diagram taranıyor | PRE-CHECK |
| OLAY-082 | `EVENT_FLOW_SCAN_COMPLETED` | Flow Diagram taraması tamam | PRE-CHECK |
| OLAY-083 | `EVENT_STATE_SCAN_STARTED` | State Engine taranıyor | PRE-CHECK |
| OLAY-084 | `EVENT_STATE_SCAN_COMPLETED` | State Engine taraması tamam | PRE-CHECK |
| OLAY-085 | `EVENT_ARCHITECTURE_SCAN_STARTED` | Mimari kurallar taranıyor | PRE-CHECK |
| OLAY-086 | `EVENT_ARCHITECTURE_SCAN_COMPLETED` | Mimari tarama tamamlandı | PRE-CHECK |
| OLAY-087 | `EVENT_OPERATIONAL_SCAN_STARTED` | Operasyonel kurallar taranıyor | PRE-CHECK |
| OLAY-088 | `EVENT_OPERATIONAL_SCAN_COMPLETED` | Operasyonel tarama tamam | PRE-CHECK |

### 5.3 Kategori 3: Dosya İşlem Event'leri

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-089 | `EVENT_FILE_OPENED` | Dosya açıldı | EXECUTE |
| OLAY-090 | `EVENT_FILE_READ` | Dosya okundu | EXECUTE |
| OLAY-091 | `EVENT_FILE_UPDATED` | Dosya güncellendi | EXECUTE |
| OLAY-092 | `EVENT_FILE_CREATED` | Yeni dosya oluşturuldu | EXECUTE |

### 5.4 Kategori 4: Kod Geliştirme Event'leri

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-093 | `EVENT_CODE_ANALYSIS_STARTED` | Kod analizi başladı | EXECUTE |
| OLAY-094 | `EVENT_CODE_ANALYSIS_COMPLETED` | Kod analizi tamamlandı | EXECUTE |
| OLAY-095 | `EVENT_CODE_IMPLEMENTATION_STARTED` | Kod yazımı başladı | EXECUTE |
| OLAY-096 | `EVENT_CODE_IMPLEMENTATION_COMPLETED` | Kod yazımı tamamlandı | EXECUTE |
| OLAY-097 | `EVENT_CODE_COMPLETED` | Tüm kod değişiklikleri tamam | EXECUTE |

### 5.5 Kategori 5: Denetim Event'leri

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-098 | `EVENT_CONSTITUTION_SCAN_STARTED` | Anayasal tarama başladı | POST-CHECK |
| OLAY-099 | `EVENT_CONSTITUTION_SCAN_COMPLETED` | Anayasal tarama tamamlandı | POST-CHECK |
| OLAY-100 | `EVENT_RUNTIME_TEST_STARTED` | Runtime test başladı | POST-CHECK |
| OLAY-101 | `EVENT_RUNTIME_TEST_COMPLETED` | Runtime test tamamlandı | POST-CHECK |
| OLAY-102 | `EVENT_SYNTAX_CHECK_STARTED` | Syntax kontrolü başladı | POST-CHECK |
| OLAY-103 | `EVENT_SYNTAX_CHECK_COMPLETED` | Syntax kontrolü tamamlandı | POST-CHECK |

### 5.6 Kategori 6: Sonuç Event'leri (CEE ile paylaşımlı)

| Olay No | Teknik Sabit | Açıklama | Faz |
|---|---|---|---|
| OLAY-072 | `EVENT_PASS` | Tüm denetimlerden geçti | POST-CHECK |
| OLAY-073 | `EVENT_FAIL` | Denetim başarısız | POST-CHECK |
| OLAY-074 | `EVENT_ESCALATION` | 3 FAIL sonrası eskalasyon | POST-CHECK |

> **Not:** OLAY-072, OLAY-073 ve OLAY-074 CEE tarafından tanımlanmıştır.
> EEC bu event'leri tekrar tanımlamaz; yalnızca LAC'a iletmek üzere dinler.

---

## 6. EEC Event Veri Standardı

EEC Event'leri, Olay Kayıt Merkezi'nin 21 alanlı standardını temel alır ve
aşağıdaki **8 ek alanı** zorunlu olarak ekler:

| # | Alan | Türkçe Adı | Zorunluluk |
|---|------|-----------|:----------:|
| 22 | `PID` | Production ID | **Zorunlu** |
| 23 | `EventDuration` | Event Süresi (ms) | **Zorunlu** |
| 24 | `RelatedFile` | İlgili Dosya | İsteğe Bağlı |
| 25 | `RelatedWorkflow` | İlgili Workflow | İsteğe Bağlı |
| 26 | `RelatedState` | İlgili State | İsteğe Bağlı |
| 27 | `ExecutorID` | Executor Kimliği | **Zorunlu** |
| 28 | `ExecutionPhase` | Yürütme Fazı | **Zorunlu** |
| 29 | `LACVisible` | LAC'ta Görünür | **Zorunlu** |

### ExecutionPhase Değerleri

| Teknik Sabit | Açıklama |
|---|---|
| `PHASE_PRE_CHECK` | PRE-CHECK — CEE görev paketi hazırlıyor |
| `PHASE_EXECUTE` | EXECUTE — Executor kodu yazıyor |
| `PHASE_POST_CHECK` | POST-CHECK — CEE çıktıyı denetliyor |

---

## 7. PID İlişkilendirme Standardı

Her EEC Event'i mutlaka bir `PID` ile ilişkilendirilir.

- PID formatı: `PID-YYYYMMDD-NNNN` (AR-002_57 standardı)
- PID, görev başlangıcında CEE tarafından oluşturulur veya mevcut PID kullanılır
- Aynı PID'ye sahip tüm Event'ler aynı görev zincirine aittir
- LAC, PID'ye göre filtreleme yaparak bir görevin tüm Event'lerini görüntüler

---

## 8. Olay Kayıt Merkezi Entegrasyonu

EEC'nin TEK çıktı hedefi Olay Kayıt Merkezi'dir (14_OLAY_KAYIT_MERKEZI.md).

### Entegrasyon Kuralları

1. Her EEC Event'i, Olay Kayıt Merkezi'nin 21 alanlı standardına uygun olmalıdır
2. Her Event, benzersiz bir Olay Kimliği (OLAY-XXX) ile kaydedilmelidir
3. Tüm Event'ler Olay Yaşam Döngüsü'nü takip etmelidir (Oluşturuldu → Doğrulandı → İşleniyor → Tamamlandı → Kaydedildi)
4. Event kayıtları değiştirilemez ve silinemez
5. Her Event, Operasyon Hafızası'na (MR-0005_4) kaydedilebilir olmalıdır

### LAC Görünürlük Kontrolü

Her EEC Event'i `LACVisible` alanı ile LAC'ta gösterilip gösterilmeyeceğini belirtir:

- `true`: Event LAC Event Feed'de görünür
- `false`: Event yalnızca kayıt altına alınır, LAC'ta gösterilmez (iç operasyon event'leri)

---

## 9. LAC Entegrasyonu

LAC (AR-002_59, FEAT-015), EEC Event'lerinin birincil tüketicisidir.

### LAC Görünüm Standardı

LAC, her PID için EEC Event'lerini kronolojik olarak aşağıdaki formatta gösterir:

```
🟢 PID-20260703-0001                          [FAZ: PRE-CHECK]

📋 PRE-CHECK — Anayasal Görev Paketi Hazırlanıyor
 ✔ MASTER taranıyor                          09:30:01
 ✔ MASTER taraması tamam                     09:30:03  (2.1s)
 ✔ Flow Diagram doğrulanıyor                 09:30:04
 ✔ Flow Diagram doğrulandı                   09:30:05  (1.2s)
 ✔ State Engine doğrulanıyor                 09:30:06
 ✔ State Engine doğrulandı                   09:30:07  (0.8s)
 ✔ Mimari kurallar taranıyor                 09:30:08
 ✔ Mimari tarama tamam                       09:30:11  (3.1s)
 ✔ Operasyonel kurallar taranıyor            09:30:12
 ✔ Operasyonel tarama tamam                  09:30:14  (1.5s)
 ✔ Task oluşturuldu                          09:30:15

⚙️ EXECUTE — Executor Kodu Yazıyor            [FAZ: EXECUTE]
 ✔ Executor görevlendirildi                  09:30:16
 ✔ Dosya açıldı: scene_registry.py           09:30:17
 ✔ Dosya okundu: scene_registry.py           09:30:17
 ✔ Kod analizi başladı                       09:30:18
 ✔ Kod analizi tamamlandı                    09:30:22  (4.1s)
 ✔ Kod yazımı başladı                        09:30:23
 ✔ Dosya güncellendi: scene_registry.py      09:30:28
 ✔ Dosya güncellendi: website.py             09:30:35
 ✔ Dosya güncellendi: main.py                09:30:40
 ✔ Kod yazımı tamamlandı                     09:30:42  (19.2s)
 ✔ Kod tamamlandı                            09:30:43
 ✔ Syntax kontrolü başladı                   09:30:44
 ✔ Syntax kontrolü tamamlandı                09:30:44  (0.3s)

🔍 POST-CHECK — Anayasal Denetim              [FAZ: POST-CHECK]
 ✔ Constitution Scan başladı                  09:30:45
 ✔ Constitution Scan tamamlandı               09:30:50  (5.2s)
 ✔ Runtime test başladı                       09:30:51
 ✔ Runtime test tamamlandı                    09:30:53  (2.1s)

✅ PASS — Görev tamamlandı                    09:30:54  (Toplam: 53.2s)
```

### LAC Güncelleme Kuralı

- Her yeni EEC Event'i oluştuğu anda LAC otomatik güncellenir
- LAC, Olay Kayıt Merkezi'ni sürekli dinler (polling veya event-driven)
- LAC hiçbir Event üretmez; yalnızca tüketir
- LAC'ta gösterilen her bilgi bir gerçek Event'ten gelir

---

## 10. Diğer Katmanlarla Entegrasyon

| Katman | EEC ile İlişkisi | Veri Akışı |
|---|---|---|
| **Decision Engine** | EEC, Decision Engine kararlarını Event olarak kaydeder | DE → EEC |
| **CEE** | EEC, CEE'nin PRE-CHECK/POST-CHECK fazlarını Event'e dönüştürür | CEE → EEC |
| **Task Engine** | EEC, Task Engine görev atamalarını Event olarak kaydeder | TE → EEC |
| **Executor (Claude)** | EEC'nin birincil veri kaynağıdır | Executor → EEC |
| **CSE** | EEC, CSE tarama fazlarını Event olarak kaydeder | CSE → EEC (dolaylı) |
| **CDE** | EEC, CDE denetim sonuçlarını Event olarak kaydeder | CDE → EEC (dolaylı) |
| **Olay Kayıt Merkezi** | EEC'nin TEK çıktı hedefidir | EEC → OKM |
| **LAC** | EEC Event'lerinin birincil tüketicisidir | OKM → LAC |
| **Feedback Loop** | EEC, Feedback Loop tetiklenmelerini Event olarak kaydeder | FL → EEC |

---

## 11. EEC Event Yaşam Döngüsü

Her EEC Event'i aşağıdaki yaşam döngüsünü izler:

```
1. Executor işlemi gerçekleşir
        │
        ▼
2. EEC işlemi algılar (LISTEN)
        │
        ▼
3. EEC işlemi Event'e dönüştürür (TRANSFORM)
   - PID eklenir
   - Zaman damgası eklenir
   - Süre hesaplanır
   - İlgili dosya/workflow/state ilişkilendirilir
        │
        ▼
4. Event Olay Kayıt Merkezi'ne kaydedilir (REGISTER)
        │
        ▼
5. LAC otomatik güncellenir (yalnızca LACVisible=true ise)
        │
        ▼
6. Event Operasyon Hafızası'na yazılır (MR-0005_4)
```

---

## 12. EEC Teknik Sabitleri

| Teknik Sabit | Değer | Açıklama |
|---|---|---|
| `EEC_EVENT_COUNT` | 28 | Toplam EEC Event sayısı (OLAY-076 — OLAY-103) |
| `EEC_CATEGORY_COUNT` | 6 | Event kategorisi sayısı |
| `EEC_PHASE_PRE_CHECK` | `PHASE_PRE_CHECK` | PRE-CHECK faz tanımlayıcısı |
| `EEC_PHASE_EXECUTE` | `PHASE_EXECUTE` | EXECUTE faz tanımlayıcısı |
| `EEC_PHASE_POST_CHECK` | `PHASE_POST_CHECK` | POST-CHECK faz tanımlayıcısı |
| `EEC_EXECUTOR_ID` | `Claude` | Varsayılan Executor kimliği |
| `EEC_LAC_POLL_INTERVAL` | 1 | LAC polling aralığı (saniye) |
| `EEC_EVENT_RETENTION` | 90 | Event saklama süresi (gün) |

---

## 13. EEC Yönetim Kuralları (EEC-001 — EEC-005)

### EEC-001 — Gerçek Event Kuralı

EEC yalnızca Executor tarafından gerçekleştirilmiş işlemleri Event'e dönüştürür.
Fake Progress, tahmini ilerleme, sahte durum mesajı veya gerçekleşmemiş işlem
Event'e dönüştürülemez. Bu kuralın ihlali, Event'in geçersiz sayılmasına ve
ilgili LAC gösteriminin durdurulmasına neden olur.

### EEC-002 — PID Zorunluluk Kuralı

Her EEC Event'i mutlaka bir PID ile ilişkilendirilmelidir. PID'si olmayan
Event'ler Olay Kayıt Merkezi'ne kaydedilemez ve LAC'ta gösterilemez.

### EEC-003 — LAC Bağımsızlık Kuralı

LAC, EEC Event'lerinin tüketicisidir; üreticisi değildir. LAC hiçbir zaman
Event üretmez, Event değiştirmez veya Event silmez. LAC yalnızca Olay Kayıt
Merkezi'ni okuyarak Event'leri görüntüler.

### EEC-004 — Sıralı Kayıt Kuralı

Event'ler, gerçekleştikleri kronolojik sırayla kaydedilmelidir. Bir Event'in
zaman damgası, kendisinden sonra gelen Event'lerden küçük olmalıdır.
Zaman damgası çakışması durumunda Event ID sıralaması kullanılır.

### EEC-005 — Görev Tamamlanma Kuralı

Bir görev için PASS Event'i (OLAY-072) oluşturulmadan önce aşağıdaki Event'lerin
tamamlanmış olması zorunludur:
- Constitution Scan (OLAY-098 + OLAY-099)
- Runtime Test (OLAY-100 + OLAY-101)
- Syntax Check (varsa) (OLAY-102 + OLAY-103)
Bu Event'ler tamamlanmadan PASS oluşturulamaz (MASTER-003 ve CEE-004 uyumluluğu).

---

## 14. Beklenen Sonuç

Bu dokümanın yürürlüğe girmesiyle birlikte:

- Executor'un her önemli işlemi gerçek zamanlı Event'e dönüştürülür.
- Tüm Event'ler PID ile ilişkilendirilerek izlenebilir hale gelir.
- Olay Kayıt Merkezi, Executor seviyesinde 28 yeni Event tipiyle genişler.
- LAC, gerçek Event'leri kronolojik olarak görüntüleyerek yöneticiye tam şeffaflık sağlar.
- Fake Progress mimari seviyede kesin olarak engellenir.
- Geliştirme süreci baştan sona izlenebilir ve denetlenebilir hale gelir.

---

_EEC, HLK'nın Executor üzerindeki gözüdür. Her işlem görünür, her adım kayıtlı, her sonuç denetlenebilir._
