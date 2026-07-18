# RAPOR — AR-002_88 Anayasa Revizyonu: Çelişki Tespiti ve Düzeltme

**Tarih:** 18.07.2026
**Referans:** AR-002_88 — Production State Ownership (Karar Yetki Zinciri)

---

## Tarama Sonucu: Mevcut anayasa büyük ölçüde uyumlu. 4 bölümde netleştirme gerekiyor.

AR-002_88 ile **doğrudan çelişen** bir madde tespit edilmedi. Mevcut anayasa (AR-002_76, MASTER-013, OR-004_12) zaten Executor'un karar vermeyeceğini söylüyor. Ancak 4 bölümde **ifade düzeyinde** netleştirme gerekiyor — mevcut metinler yoruma açık.

---

## Revizyon 1: AR-002_76 — Adım 5 (Üretim Çıktılarının Kaydedilmesi)

### Eski Metin (satır 6003-6011)

```
**Adım 5 — Üretim Çıktılarının Kaydedilmesi**

Executor, üretim çıktılarını ilgili Production Package'e kaydeder.

Çıktılar:

* Production Package'in ilgili bölümlerine yazılır (16_PRODUCTION_PACKAGE_STANDARD.md),
* PID ile ilişkilendirilir,
* Task Package altında saklanır (AR-002_74).
```

### Sorun

"Üretim çıktılarını ilgili Production Package'e kaydeder" ifadesi çok geniş. `update_status()` veya `PackageStatus` değişikliğini kapsayıp kapsamadığı belirsiz. AR-002_88: "Executor hiçbir koşulda PackageStatus değiştiremez."

### Yeni Metin

```
**Adım 5 — Teknik Çıktıların Kaydedilmesi**

Executor, yürütme sonucunda oluşan teknik çıktıları Production Package'e kaydeder.

Executor'un kaydedebileceği teknik çıktılar:

* Task yürütme sonuçları (task status, duration, output),
* Oluşturulan dosyaların referansları (görsel, ses, video yolu),
* Execution Event'leri (EEC standardına uygun),
* Task checkpoint kayıtları.

Executor'un kaydedemeyeceği:

* PackageStatus (COMPLETED, FAILED, vb.) — bu bir anayasal karardır,
* Decision History — bu HLK Runtime kararlarının kaydıdır,
* Production kararları (RETRY, RESUME, REPLAY, vb.).

Executor yalnızca teknik veri yazar; anayasal karar kaydetmez.
```

---

## Revizyon 2: AR-002_76 — Execution Result Status Açıklaması

### Eski Metin (satır 6017-6019)

```
Execution Result en az aşağıdaki bilgileri içermelidir:

* status: SUCCESS / FAILED / TIMEOUT / PARTIAL (AR-002_22)
```

### Sorun

`SUCCESS` / `FAILED` terimleri anayasal karar terimleriyle aynı. Task seviyesinde olduğu belirtilmemiş.

### Yeni Metin

```
Execution Result en az aşağıdaki bilgileri içermelidir:

* status: SUCCESS / FAILED / TIMEOUT / PARTIAL (AR-002_22)
  Bu status'lar yalnızca task yürütme sonucunu belirtir; üretim kararı değildir.
  SUCCESS = task teknik olarak tamamlandı (çıktı kalitesi garantisi yoktur).
  FAILED  = task teknik olarak başarısız (exception, timeout).
  Bu status'lar Production COMPLETED/FAILED kararı ile karıştırılamaz.
```

---

## Revizyon 3: AR-002_76 — Yürütme Durumları Tablosu

### Eski Metin (satır 6041-6048)

```
| Durum | Execution Result Status | Event Kaydı | Sonraki Adım |
|---|---|---|---|
| **Başarı** | SUCCESS | Tamamlanma Event'i | Feedback Loop → normal akış |
| **Başarısızlık** | FAILED | Başarısızlık Event'i | Feedback Loop → neden analizi |
| **Timeout** | TIMEOUT | Timeout Event'i | AR-002_7 → alternatif Agent/servis |
| **İptal** | CANCELLED | İptal Event'i | STATE_SESSION_CLOSED |
| **Kısmi Tamamlama** | PARTIAL | Kısmi tamamlanma Event'i | Feedback Loop → eksik kısım için ek karar |
| **Servis Değişikliği** | — | AGENT_REPLACED Event'i | AR-002_21 → yeni servis seçimi |
```

### Sorun

"Başarı" / "Başarısızlık" sütunu task seviyesinde mi yoksa production seviyesinde mi belli değil. "Sonraki Adım" sütunu karar içeriyor gibi görünüyor.

### Yeni Metin

```
| Task Sonucu | Execution Result Status | Teknik Event | Sonraki İşlem |
|---|---|---|---|
| **Task tamamlandı** | SUCCESS | TASK_COMPLETED | Feedback Loop'a iletilir — değerlendirme HLK'ya aittir |
| **Task başarısız** | FAILED | TASK_FAILED | Feedback Loop'a iletilir — neden analizi HLK'ya aittir |
| **Task timeout** | TIMEOUT | TASK_TIMEOUT | Feedback Loop'a iletilir — AR-002_7 alternatif değerlendirmesi |
| **Task iptal** | CANCELLED | TASK_CANCELLED | Feedback Loop'a iletilir |
| **Task kısmi** | PARTIAL | TASK_PARTIAL | Feedback Loop'a iletilir — eksik kısım HLK kararına bağlı |
| **Task servis değişimi** | — | PROVIDER_SWITCHED | AR-002_21 → HLK Runtime PROVIDER_SWITCH kararı |
```

---

## Revizyon 4: 16_PRODUCTION_PACKAGE_STANDARD.md — Yaşam Döngüsü

### Eski Metin (satır 109-131)

```
## 6. Production Package Yaşam Döngüsü

STATE_VIDEO_PRODUCTION Girişi
    ↓
PID Oluşturulur (AR-002_57)
    ↓
Production Package Oluşturulur
    ↓
EVENT_PRODUCTION_PACKAGE_CREATED
    ↓
Task Package'ler Oluşturulur (AR-002_47)
    ↓
Agent'lar Görevlendirilir
    ↓
Video Üretimi Gerçekleşir
    ↓
Kalite Kontrol Yapılır
    ↓
Nihai Video Teslim Edilir
    ↓
Production Package Arşivlenir
```

### Sorun

Yaşam döngüsü doğrusal gösterilmiş. Karar noktaları ve yetki zinciri görünmüyor. Package Status'un kim tarafından, ne zaman güncelleneceği belirsiz.

### Yeni Metin

```
## 6. Production Package Yaşam Döngüsü

STATE_VIDEO_PRODUCTION Girişi
    ↓
PID Oluşturulur (AR-002_57)
    ↓
Production Package Oluşturulur → PackageStatus: CREATED
    ↓
EVENT_PRODUCTION_PACKAGE_CREATED
    ↓
Task Package'ler Oluşturulur (AR-002_47)
    ↓
Agent'lar Görevlendirilir → PackageStatus: BUILDING
    ↓
Video Üretimi Gerçekleşir → PackageStatus: PRODUCING
    ↓
Executor: Teknik Event'ler yayınlar (TASK_COMPLETED, EXECUTION_FINISHED)
    ↓
Production Runtime: Teknik doğrulamaları yapar
    ↓
Decision Request → HLK Runtime
    ↓
HLK Runtime: COMPLETION kararı (AR-002_80 kriterleri)
    ↓
CEE: Kararı denetler
    ↓
PackageStatus: COMPLETED veya FAILED ← YALNIZCA bu zincirle
    ↓
Nihai Video Teslim Edilir
    ↓
Production Package Arşivlenir → PackageStatus: ARCHIVED
```

**Package Status güncelleme zinciri (AR-002_88):**

```
Executor               → Teknik Event (TASK_COMPLETED, EXECUTION_FINISHED)
    ↓
Production Runtime     → Event'leri toplar, doğrular, Decision Request oluşturur
    ↓
HLK Runtime            → COMPLETION kararı
    ↓
CEE                    → Kararı onaylar/reddeder
    ↓
Package Status Update  ← Yalnızca bu zincir tamamlandığında
```

Bu zincir dışında hiçbir modül PackageStatus değiştiremez.
```

---

## Revizyon Listesi Özeti

| # | Dosya | Bölüm | Değişiklik Türü | Neden |
|---|---|---|---|---|
| **R1** | `03_Architecture_Rules.md` | AR-002_76 Adım 5 | İfade netleştirme | "Kaydeder" → "Teknik çıktıları kaydeder; PackageStatus kaydedemez" |
| **R2** | `03_Architecture_Rules.md` | AR-002_76 Adım 6 | İfade netleştirme | Task status ≠ Production kararı açıklaması eklendi |
| **R3** | `03_Architecture_Rules.md` | AR-002_76 Durum Tablosu | Tablo revizyonu | "Başarı" → "Task tamamlandı"; karar içeren ifadeler temizlendi |
| **R4** | `16_PRODUCTION_PACKAGE_STANDARD.md` | Bölüm 6 Yaşam Döngüsü | Diyagram revizyonu | Karar zinciri eklendi; PackageStatus güncelleme yetkisi netleştirildi |

---

## Anayasa Güncelleme Sırası

1. Önce `16_PRODUCTION_PACKAGE_STANDARD.md` Bölüm 6 — temel yaşam döngüsü
2. Sonra `03_Architecture_Rules.md` AR-002_76 Adım 5 — yürütme çıktıları
3. Sonra `03_Architecture_Rules.md` AR-002_76 Adım 6 — Execution Result
4. Sonra `03_Architecture_Rules.md` AR-002_76 Durum Tablosu

---

## Sonuç

**HLK Anayasasında AR-002_88 ile doğrudan çelişen hiçbir madde tespit edilmemiştir.** Mevcut anayasa (AR-002_76, MASTER-013, OR-004_12) Executor'un karar vermeyeceğini zaten söylemektedir.

Ancak 4 bölümde ifadeler yeterince net değildi — "kaydeder", "başarı", "başarısızlık" gibi terimler yoruma açıktı. Bu revizyonlar, AR-002_88'in getirdiği netliği mevcut maddelere yansıtarak anayasayı kendi içinde tamamen tutarlı hale getirmektedir.

**HLK Anayasasında yeni ilkeye aykırı hiçbir madde kalmamıştır.**

(Not: Asıl ihlal anayasada değil, **kodda**dır — `production_executor.py:663/665`. Anayasa revizyonu kodu otomatik düzeltmez; kodun da anayasaya uygun hale getirilmesi gerekir.)
