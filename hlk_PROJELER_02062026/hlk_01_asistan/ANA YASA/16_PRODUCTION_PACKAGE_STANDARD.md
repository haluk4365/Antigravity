# 16 — Production Package Standard

HLK içerisinde oluşturulan her üretim için tek resmi ana kapsayıcı olan Production Package'in mimari standardıdır.

---

## 1. Amaç

HLK içerisinde oluşturulan her PID için tek bir Production Package oluşturulur.

Production Package; o üretime ait tüm bilgi, dijital varlık, görev paketleri, loglar ve çıktıların resmi ana kapsayıcısıdır.

Bu dosyanın amacı;

* Production Package'in yapısını, içeriğini ve yaşam döngüsünü standart hale getirmek,
* PID ile Production Package arasındaki birebir ilişkiyi tanımlamak,
* Task Package'lerin Production Package altındaki konumunu belirlemek,
* Üretime ait tüm bileşenlerin tek bir kapsayıcı altında toplanmasını sağlamak,
* Digital Asset Archive ve diğer sistem bileşenleri ile entegrasyonu tanımlamaktır.

---

## 2. Kapsam

Bu standart aşağıdaki tüm üretim süreçlerinde kullanılır:

* İlk üretim (Initial Production)
* Revizyon üretimi (Revision Production)
* Gelecekte eklenecek tüm üretim türleri

Her üretim türü için ayrı bir Production Package oluşturulur.

---

## 3. Temel İlkeler

1. Her PID yalnızca bir adet Production Package oluşturabilir.
2. Her Production Package yalnızca bir PID'ye bağlıdır.
3. Production Package silinemez.
4. Production Package arşivlenebilir.
5. Production Package, üretime ait tüm bileşenlerin tek resmi ana kapsayıcısıdır.
6. Task Package yapısı korunur; Production Package, Task Package'lerin üst katmanı olarak çalışır.
7. Hiçbir Agent Production Package'in tamamına erişemez; yalnızca kendisine atanan Task Package'e erişebilir.

---

## 4. Hiyerarşi

```
PID (Production ID)
    ↓
Production Package
    ↓
    ├── Task Package 1 (Agent 1)
    ├── Task Package 2 (Agent 2)
    ├── Task Package 3 (Agent 3)
    ├── ...
    └── Task Package N (Agent N)
```

### PID

Production ID (PID), HLK tarafından STATE_VIDEO_PRODUCTION girişinde oluşturulan benzersiz üretim kimliğidir. PID standardı AR-002_57 ile tanımlanmıştır.

### Production Package

PID oluşturulduktan hemen sonra HLK tarafından oluşturulur. Üretime ait tüm bilgi, varlık ve kayıtların ana kapsayıcısıdır.

### Task Package

Task Package yapısı AR-002_47 (Task Package Engine Architecture) ile tanımlanmıştır ve değiştirilmemiştir.

Task Package'ler Production Package'in alt bileşeni olarak çalışır.

Her Agent yalnızca kendisine atanan Task Package'e erişebilir. Production Package'in tamamına erişemez.

---

## 5. Production Package Bölümleri

Production Package aşağıdaki ana bölümleri içerir.

| # | Bölüm | Açıklama | Zorunluluk |
|---|-------|----------|:----------:|
| 1 | **PID** | Production ID — bu paketin bağlı olduğu benzersiz üretim kimliği | Zorunlu |
| 2 | **Production Metadata** | Üretim tarihi, türü, durumu, sürüm bilgisi | Zorunlu |
| 3 | **Brief** | Kullanıcıdan toplanan tüm brief verileri | Zorunlu |
| 4 | **Senaryo** | Onaylanmış reklam senaryosu | Zorunlu |
| 5 | **Storyboard** | Sahne planı ve görsel akış şeması | İsteğe Bağlı |
| 6 | **Prompt Setleri** | Video üretimi için hazırlanan prompt'lar | Zorunlu |
| 7 | **Task Package Listesi** | Bu üretim için oluşturulan tüm Task Package'ler | Zorunlu |
| 8 | **Araştırma Sonuçları** | Ürün, marka, rakip, fiyat ve hedef kitle analizleri | Zorunlu |
| 9 | **Referans Görseller** | Araştırma sırasında toplanan ve doğrulanan referans görseller | Zorunlu |
| 10 | **Kullanıcı Dosyaları** | Kullanıcı tarafından yüklenen tamamlayıcı materyaller | İsteğe Bağlı |
| 11 | **Dijital Varlıklar** | Üretim sürecinde kullanılan tüm dijital varlıklar | Zorunlu |
| 12 | **Ses Dosyaları** | AHU seslendirme ve diğer ses çıktıları | İsteğe Bağlı |
| 13 | **Video Parametreleri** | Format, çözünürlük, süre, platform bilgileri | Zorunlu |
| 14 | **Servis Kullanımları** | Kullanılan servis sağlayıcılar ve tüketim bilgileri | Zorunlu |
| 15 | **Agent Logları** | Tüm agent'ların çalışma log'ları | Zorunlu |
| 16 | **Event Logları** | Üretim sürecinde oluşan tüm event kayıtları | Zorunlu |
| 17 | **Kalite Raporları** | Kalite kontrol sonuçları ve değerlendirmeler | Zorunlu |
| 18 | **Revizyon Geçmişi** | Varsa revizyon talepleri ve sonuçları | İsteğe Bağlı |
| 19 | **Teslim Bilgileri** | Kullanıcıya teslim tarihi, yöntemi ve durumu | Zorunlu |
| 20 | **Karar Gerekçeleri (Decision History)** | Yönetici kararları ve HLK karar gerekçeleri | Zorunlu |
| 21 | **Nihai Video** | Teslim edilen nihai reklam videosu | Zorunlu |

---

## 6. Production Package Yaşam Döngüsü

```
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

---

## 7. Production Package Oluşturulma Anı

Production Package, STATE_VIDEO_PRODUCTION state'ine girişte, PID oluşturulduktan hemen sonra HLK tarafından otomatik olarak oluşturulur.

Production Package oluşturulduğunda:

1. PID, Production Package'e yazılır.
2. EVENT_PRODUCTION_PACKAGE_CREATED event'i oluşturulur.
3. Production Metadata bölümü doldurulur.
4. Task Package Engine, Production Package altında Task Package'leri oluşturmaya başlar.
5. Production Package, Olay Kayıt Merkezi'ne kaydedilir.

---

## 8. Digital Asset Archive İlişkisi

Production Package, Digital Asset Archive (12_DIGITAL_ASSET_ARCHIVE.md) için resmi üst referanstır.

Production Package içerisinde yer alan tüm dijital varlıklar (Nihai Video, Ses Dosyaları, Referans Görseller, vb.) Digital Asset Archive'de PID üzerinden ilişkilendirilerek saklanır.

Digital Asset Archive'deki her varlık kaydı, ilgili Production Package'in PID'sini referans alır.

Arşiv kimliği (Asset ID) ile PID arasındaki ilişki Digital Asset Catalog (13_DIGITAL_ASSET_CATALOG.md) üzerinden yönetilir.

---

## 9. Digital Asset Catalog İlişkisi

Production Package içerisinde kullanılan tüm dijital varlıklar, Digital Asset Catalog'da PID üzerinden ilişkilendirilir.

Her katalog kaydı, bağlı olduğu Production Package'in PID'sini içerir.

PID, katalog kayıtları için ortak arama anahtarı olarak kullanılabilir.

---

## 10. Olay Kayıt Merkezi İlişkisi

Production Package oluşturulduğunda EVENT_PRODUCTION_PACKAGE_CREATED event'i tetiklenir.

Bu event, Olay Kayıt Merkezi'nde (14_OLAY_KAYIT_MERKEZI.md) OLAY-031 olarak kayıtlıdır.

Production Package ile ilgili tüm event'ler PID alanını zorunlu olarak içerir.

---

## 11. Karar Gerekçesi Standardı İlişkisi

Production Package'in **Karar Gerekçeleri (Decision History)** bölümü, Karar Gerekçesi Standardı (15_KARAR_GEREKCESI_STANDARDI.md) ile uyumludur.

Bu bölümde aşağıdaki kararlar saklanır:

* Yönetici fiyatlandırma kararı
* Yönetici ödeme onay kararı
* Yönetici video üretim onay kararı
* HLK servis seçim kararları
* HLK ajan seçim kararları
* Revizyon kararları
* Üretim sürecinde alınan diğer tüm kritik kararlar

Her karar; gerekçesi, alternatifleri, güven seviyesi ve sonuçları ile birlikte kaydedilir.

---

## 12. Task Package İlişkisi

Task Package yapısı (AR-002_47) değiştirilmemiştir.

Production Package ile Task Package arasındaki ilişki:

```
Production Package (Ana Kapsayıcı)
    ↓ içerir
Task Package 1 (Agent 1 için)
Task Package 2 (Agent 2 için)
Task Package N (Agent N için)
```

Her Task Package:
* Yalnızca bir Production Package'e aittir.
* Yalnızca bir Agent'a atanır.
* Kendi Production Package'inin PID'sini referans olarak taşır.

Her Agent:
* Yalnızca kendisine atanan Task Package'e erişebilir.
* Production Package'in tamamına erişemez.
* Diğer Task Package'lere erişemez.

---

## 13. Erişim ve Güvenlik

1. Production Package'in tamamına yalnızca HLK erişebilir.
2. Agent'lar yalnızca kendi Task Package'lerine erişebilir.
3. Yönetici, Yönetici formları aracılığıyla Production Package özetine erişebilir.
4. Kullanıcı yalnızca nihai çıktılara (video, teklif, senaryo) erişebilir.
5. Production Package kayıtları değiştirilemez.
6. Production Package silinemez; yalnızca arşivlenebilir.

---

## 14. State Engine İlişkisi

Production Package, STATE_VIDEO_PRODUCTION state'i ile doğrudan ilişkilidir (07_HLK_STATE_ENGINE.md).

STATE_VIDEO_PRODUCTION girişinde:
1. PID oluşturulur.
2. Production Package oluşturulur.
3. Task Package'ler oluşturulur.
4. Video üretim süreci başlatılır.

---

## 15. Workflow İlişkisi

Production Package, WF-008 (Video Production) workflow'u kapsamında oluşturulur (11_WORKFLOW_FEATURE_MAP.md).

Production Package Engine (FEAT-014), Production Package'in oluşturulmasından ve yönetilmesinden sorumlu Feature'dır.

---

## 16. Gelecekte Genişletilebilirlik

Bu dosya başlangıç standardıdır.

HLK sistem geliştikçe aşağıdaki durumlarda Production Package yapısı genişletilebilir:

* Yeni bir üretim türü eklendiğinde,
* Yeni bir dijital varlık türü eklendiğinde,
* Yeni bir Task Package türü eklendiğinde,
* Yeni bir karar noktası tanımlandığında,
* Yeni bir kalite kontrol aşaması eklendiğinde.

Genişletme kuralları:

1. Mevcut bölümler değiştirilmez; yalnızca yeni bölümler eklenir.
2. Yeni bölümler mevcut numaralandırma sistemine uygun olmalıdır.
3. Zorunluluk durumu her yeni bölüm için açıkça belirtilmelidir.

---

## 17. Temel İlke

Bu standart;

* PID standardını (AR-002_57) değiştirmez.
* Task Package mimarisini (AR-002_47) değiştirmez.
* Digital Asset Archive standardını değiştirmez.
* Karar Gerekçesi Standardını değiştirmez.

Bu standart yalnızca;

PID ile başlayan üretim sürecinin tüm bileşenlerini tek bir ana kapsayıcı altında toplayan,
Task Package'leri bu kapsayıcının alt bileşeni olarak konumlandıran,
ve tüm sistem bileşenleri arasındaki ilişkiyi PID üzerinden kuran

resmi Production Package mimarisini tanımlar.
