# 01 — Global Configuration

Proje genelinde geçerli yapılandırma kuralları.

---

## Parametreler

| Parametre | Değer | Açıklama |
|---|---|---|
| `GC_IMAGE_RESEARCH_TIMEOUT` | 20 saniye | Görsel araştırma zaman aşımı |
| `GC_IMAGE_MIN_COUNT` | 3 | Minimum görsel sayısı |
| `GC_IMAGE_MAX_COUNT` | 20 | Maksimum görsel sayısı |
| `GC_AGENT_TIMEOUT` | 5 saniye | Ajan zaman aşımı |
| `GC_AGENT_CACHE_DURATION` | 30 gün | Ajan önbellek süresi |
| `GC_MAX_PRODUCT_LINK_RETRY` | 5 | Kullanıcının ürün linki doğrulanmadan önce sahip olduğu maksimum yeniden deneme hakkı |
| `GC_MAX_AGENT_EXECUTION_TIME` | 5 saniye | Bir ajanın aynı görev için maksimum çalışma süresi; aşılırsa timeout uygulanır ve sıradaki aday devreye alınır |
| `GC_MAX_PRODUCT_DETAIL_IMAGE_COUNT` | 10 | Kullanıcının yükleyebileceği maksimum tamamlayıcı ürün görseli sayısı (üst sınır; hedef sayı değil) |
| `GC_PID_PREFIX` | `PID` | Production ID ön eki |
| `GC_PID_DATE_FORMAT` | `YYYYMMDD` | PID tarih formatı |
| `GC_PID_SEQUENCE_LENGTH` | 4 | PID sıra numarası basamak sayısı (sıfır dolgulu) |
| `GC_PID_SEQUENCE_START` | `0001` | PID günlük sıra numarası başlangıç değeri |
| `GC_SAHNE2_EXTRA_WAIT` | 5 saniye | SAHNE-2 video sonu ekstra bekleme süresi |
| `GC_LINK_PROCESSING_WAIT` | 4 saniye | Link işleme sonrası bekleme süresi |
| `GC_BALLOON_STAGGER_DELAY` | 1 saniye | Konuşma balonları arası gecikme |

---

## GC İlkesi

- Sayısal değerler kuralların içine yazılmaz.
- Kurallar yalnızca GC parametrelerine referans verir.
- Değişiklik gerektiğinde yalnızca bu dosya güncellenir.
- Aynı değer farklı yerlerde tekrar edilmez.
