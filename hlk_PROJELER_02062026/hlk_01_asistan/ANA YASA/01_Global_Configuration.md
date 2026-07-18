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
| `GC_MAX_RE_EVALUATION_COUNT` | 3 | Feedback Loop maksimum yeniden değerlendirme sayısı (AR-002_22 §6.3) |
| `GC_PRODUCTION_TIMEOUT` | 3600 saniye | Production Runtime toplam üretim zaman aşımı (AR-002_70) |
| `GC_PRODUCTION_STEP_TIMEOUT` | 300 saniye | Production Runtime adım zaman aşımı — PID/Package oluşturma (AR-002_70) |
| `GC_EXECUTOR_MAX_RETRY` | 3 | Production Executor görev başına maksimum deneme sayısı (AR-002_76) |
| `GC_EXECUTOR_TASK_TIMEOUT` | 300 saniye | Production Executor tek görev zaman aşımı (AR-002_76) |
| `GC_EXECUTOR_RETRY_DELAY` | 0.5 saniye | Production Executor yeniden deneme öncesi bekleme süresi (AR-002_76) |
| `GC_EXECUTOR_STATE_DIR` | `data` | Production Executor durum dosyaları dizini (AR-002_76) |
| `GC_RUNTIME_HEARTBEAT_INTERVAL` | 60 saniye | Runtime aktiflik kanıt sinyali (heartbeat) aralığı (MASTER-011) |
| `GC_PROVIDER_HTTP_TIMEOUT` | 30 saniye | Provider API istek zaman aşımı (AR-002_81) |
| `GC_PROVIDER_STATUS_TIMEOUT` | 10 saniye | Provider durum sorgusu zaman aşımı (AR-002_81) |
| `GC_PROVIDER_POLL_COUNT` | 10 | Provider sonuç bekleme maksimum durum sorgusu sayısı (AR-002_81) |
| `GC_IMAGE_POLL_INTERVAL` | 3 saniye | Görsel üretim durum sorgusu aralığı (AR-002_81) |
| `GC_VIDEO_POLL_INTERVAL` | 5 saniye | Video üretim durum sorgusu aralığı (AR-002_81) |
| `GC_REPRODUCE_SEARCH_LIMIT` | 20 | Yeniden üretim paket aramasında taranacak maksimum package dosyası sayısı (AR-002_84) |
| `GC_REPRODUCE_MAX_CANDIDATES` | 5 | Yeniden üretim paket aramasında değerlendirilecek maksimum aday sayısı (AR-002_84) |

---

## GC İlkesi

- Sayısal değerler kuralların içine yazılmaz.
- Kurallar yalnızca GC parametrelerine referans verir.
- Değişiklik gerektiğinde yalnızca bu dosya güncellenir.
- Aynı değer farklı yerlerde tekrar edilmez.
