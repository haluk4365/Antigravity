# 07_HLK_STATE_ENGINE

> Bu dosya HLK'nın resmi STATE (Durum) yönetim dokümanıdır.
> Bu dosya ANA KURALLAR'ın, Akış Diyagramının, GENEL KURALLAR'ın ve Global Configuration'ın
> yerine geçmez; yalnızca STATE yönetimini tanımlar.
>
> ⚠️ İSKELET — Bu aşamada yalnızca yapı oluşturulmuştur. Bölümler bir sonraki aşamada
> mevcut ANA KURALLAR ve HLK Akış Diyagramı referans alınarak doldurulacaktır.
>
> Not: Timeout süreleri, ajan timeout değerleri, oturum timeout kuralları, fotoğraf yükleme
> süreleri ve diğer sayısal parametreler bu dosyada TEKRAR tanımlanmaz; gerektiğinde yalnızca
> ANA KURALLAR içindeki ilgili kurallara referans verilir.

---

## 1. Amaç

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 2. Kapsam

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 3. Temel İlkeler

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 4. State Tanımlama Standardı

### SE-007_1 — Ajan Durum Sınıflandırma Sistemi (Agent State Classification System)

HLK, her ajanın yaşam döngüsünü standart durumlar üzerinden takip eder.

Bu durumlar yalnızca iç operasyonel yönetim amacıyla kullanılır.

HLK, ihtiyaç duyduğunda aşağıdaki durumları kullanabilir:

* `AGENT_CREATED`
* `AGENT_QUEUED`
* `AGENT_ACTIVE`
* `AGENT_SUCCESS`
* `AGENT_FAILED`
* `AGENT_TIMEOUT`
* `AGENT_NO_CREDITS`
* `AGENT_API_KEY_MISSING`
* `AGENT_SERVICE_UNAVAILABLE`
* `AGENT_ACCESS_DENIED`
* `AGENT_DISABLED`
* `AGENT_PLACEHOLDER`
* `AGENT_REPLACED`
* `AGENT_CANCELLED`

Bu liste başlangıç referansıdır.

HLK, sistem geliştikçe yeni durumlar ekleyebilir, bazı durumları birleştirebilir veya kullanım dışı bırakabilir.

Her ajan aynı anda yalnızca bir ana duruma sahip olabilir.

Bir ajanın durumu değiştiğinde HLK, gerekli durum geçiş kurallarını uygular.

Operasyonel bildirimler, yönetici raporları ve ajan eskalasyon mekanizmaları mümkün olan durumlarda bu standart durumları kullanmalıdır.

HLK'nin amacı yalnızca bir ajanın başarılı veya başarısız olduğunu belirtmek değil, operasyonel durumun gerçek nedenini mümkün olan en doğru şekilde sınıflandırabilmektir.

Örnek:

* `AGENT_PLACEHOLDER` ≠ `AGENT_FAILED`
* `AGENT_NO_CREDITS` ≠ `AGENT_TIMEOUT`
* `AGENT_API_KEY_MISSING` ≠ `AGENT_SERVICE_UNAVAILABLE`

Bu nedenle farklı operasyonel nedenler mümkün olduğu ölçüde farklı durumlar olarak yönetilmelidir.

---

## 5. State Geçiş Kuralları

### SE-007_2 — Ajan State Geçiş Kuralları (Agent State Transition Rules)

HLK içerisinde her state'den her state'e geçiş yapılamaz.

Her durum yalnızca tanımlanmış geçiş yollarını kullanmalıdır.

#### Normal Akış

```
AGENT_CREATED → AGENT_QUEUED → AGENT_ACTIVE → AGENT_SUCCESS
```

#### Başarısızlık Akışı

```
AGENT_ACTIVE → AGENT_FAILED
```

#### Timeout Akışı

```
AGENT_ACTIVE → AGENT_TIMEOUT
```

#### API Problemi Akışı

```
AGENT_QUEUED → AGENT_API_KEY_MISSING
AGENT_QUEUED → AGENT_SERVICE_UNAVAILABLE
AGENT_QUEUED → AGENT_ACCESS_DENIED
```

#### Kredi Problemi Akışı

```
AGENT_QUEUED → AGENT_NO_CREDITS
```

#### Placeholder Akışı

```
AGENT_CREATED → AGENT_PLACEHOLDER
```

#### Ajan Değiştirme Akışı

```
AGENT_FAILED → AGENT_REPLACED → AGENT_ACTIVE
AGENT_TIMEOUT → AGENT_REPLACED → AGENT_ACTIVE
```

#### İptal Akışı

```
AGENT_CREATED → AGENT_CANCELLED
AGENT_QUEUED → AGENT_CANCELLED
AGENT_ACTIVE → AGENT_CANCELLED
```

#### Devre Dışı Bırakma Akışı

```
AGENT_FAILED → AGENT_DISABLED
AGENT_PLACEHOLDER → AGENT_DISABLED
```

Bu akışlar başlangıç referansıdır.

HLK, sistem geliştikçe yeni geçişler ekleyebilir, bazı geçişleri kaldırabilir veya yeni state'lere uygun geçiş yolları tanımlayabilir.

Ancak her state değişikliği açık kurallarla tanımlanmalıdır.

HLK'nin amacı yalnızca ajan durumlarını saklamak değil, ajan yaşam döngüsünü tutarlı ve denetlenebilir şekilde yönetmektir.

---

### SE-007_3 — User Conversation State Architecture

Kullanıcı ile yürütülen konuşma akışının hangi durumlar üzerinden yönetileceğini tanımlar.

HLK içerisinde kullanıcı ile yürütülen oturum yönetimi, ajan yaşam döngüsünden bağımsız olarak ayrı bir Kullanıcı Durum Makinesi (User Conversation State Machine) tarafından yönetilir.

HLK aşağıdaki kullanıcı durumlarını kullanabilir:

`STATE_START`

`STATE_SCENE_1`

`STATE_LANGUAGE_SELECTION`

`STATE_SCENE_2`

`STATE_WAIT_PRODUCT_LINK`

`STATE_LINK_VALIDATION`

`STATE_LINK_VALIDATED`

`STATE_BACKGROUND_RESEARCH_RUNNING`

`STATE_COLLECT_PRODUCT_MATERIALS`

`STATE_PLATFORM_SELECTION`

`STATE_VIDEO_RESOLUTION_SELECTION`

`STATE_VIDEO_DURATION_SELECTION`

`STATE_AUDIO_SELECTION`

`STATE_BRIEF_COMPLETED`

`STATE_SCENARIO_APPROVAL`

`STATE_PRICING`

`STATE_PAYMENT_VERIFICATION`

`STATE_VIDEO_PRODUCTION`

`STATE_SESSION_COMPLETED`

`STATE_SESSION_TIMEOUT`

`STATE_SESSION_CLOSED`

Bu liste başlangıç referansıdır.

HLK sistem geliştikçe yeni kullanıcı durumları ekleyebilir, bazı durumları birleştirebilir veya kullanım dışı bırakabilir.

Her kullanıcı oturumu aynı anda yalnızca bir ana kullanıcı durumunda bulunabilir.

Kullanıcı durumları, ajan durumlarından bağımsız olarak yönetilir.

HLK bulunduğu kullanıcı durumuna göre;

• Active Conversation Screen'i çalıştırabilir.

• Conversation Scene Engine'i çalıştırabilir.

• Kullanıcıdan bilgi isteyebilir.

• Brief toplama sürecini yönetebilir.

• Sonraki duruma geçebilir.

Bu mimarinin amacı kullanıcı akışını açık, yönetilebilir ve denetlenebilir hale getirmektir.

Örnek Akış:

```
STATE_START
↓
STATE_SCENE_1
↓
STATE_LANGUAGE_SELECTION
↓
STATE_SCENE_2
↓
STATE_WAIT_PRODUCT_LINK
↓
STATE_LINK_VALIDATION
↓
STATE_LINK_VALIDATED
↓
STATE_BACKGROUND_RESEARCH_RUNNING
↓
STATE_COLLECT_PRODUCT_MATERIALS
↓
STATE_PLATFORM_SELECTION
↓
STATE_VIDEO_RESOLUTION_SELECTION
↓
STATE_VIDEO_DURATION_SELECTION
↓
STATE_AUDIO_SELECTION
↓
STATE_BRIEF_COMPLETED
↓
STATE_SCENARIO_APPROVAL
↓
STATE_PRICING
↓
STATE_PAYMENT_VERIFICATION
↓
STATE_VIDEO_PRODUCTION
↓
STATE_SESSION_COMPLETED
```

Beklenen Sonuç:

AR-002_27 Active Conversation Screen Architecture kuralının hangi durumda çalışacağı tanımlanmış olur.

AR-002_28 Conversation Scene Engine Architecture kuralının hangi durumda çalışacağı tanımlanmış olur.

AR-002_35 Research-Conversation Parallel Execution Architecture kuralının hangi aşamada devreye gireceği tanımlanmış olur.

HLK'nin kullanıcı tarafındaki Telegram akışı ilk kez resmi state yapısı içerisinde tanımlanmış olur.

---

### SE-007_4 — User Conversation State Transition Rules

Kullanıcı durumları arasındaki izin verilen geçişleri tanımlar.

HLK içerisinde kullanıcı durumları arasında rastgele geçiş yapılamaz.

Her kullanıcı durumu yalnızca tanımlanmış geçiş yollarını kullanmalıdır.

```
Normal Kullanıcı Akışı

STATE_START
→ STATE_SCENE_1
→ STATE_LANGUAGE_SELECTION
→ STATE_SCENE_2
→ STATE_WAIT_PRODUCT_LINK
→ STATE_LINK_VALIDATION
→ STATE_LINK_VALIDATED
→ STATE_BACKGROUND_RESEARCH_RUNNING
→ STATE_COLLECT_PRODUCT_MATERIALS
→ STATE_PLATFORM_SELECTION
→ STATE_VIDEO_RESOLUTION_SELECTION
→ STATE_VIDEO_DURATION_SELECTION
→ STATE_AUDIO_SELECTION
→ STATE_BRIEF_COMPLETED
→ STATE_SCENARIO_APPROVAL
→ STATE_PRICING
→ STATE_PAYMENT_VERIFICATION
→ STATE_VIDEO_PRODUCTION
→ STATE_SESSION_COMPLETED

Ödeme Doğrulama Akışı

STATE_PAYMENT_VERIFICATION
→ STATE_VIDEO_PRODUCTION

STATE_PAYMENT_VERIFICATION
→ STATE_SESSION_CLOSED

Oturum Zaman Aşımı Akışı

STATE_WAIT_PRODUCT_LINK
→ STATE_SESSION_TIMEOUT

STATE_LANGUAGE_SELECTION
→ STATE_SESSION_TIMEOUT

STATE_COLLECT_PRODUCT_MATERIALS
→ STATE_SESSION_TIMEOUT

STATE_PLATFORM_SELECTION
→ STATE_SESSION_TIMEOUT

STATE_VIDEO_RESOLUTION_SELECTION
→ STATE_SESSION_TIMEOUT

STATE_VIDEO_DURATION_SELECTION
→ STATE_SESSION_TIMEOUT

STATE_AUDIO_SELECTION
→ STATE_SESSION_TIMEOUT

Timeout Sonrası Akış

STATE_SESSION_TIMEOUT
→ STATE_SESSION_CLOSED

Link Doğrulama Başarısız Akışı

STATE_LINK_VALIDATION
→ STATE_WAIT_PRODUCT_LINK

Materyal Toplama Tamamlama Akışı

STATE_COLLECT_PRODUCT_MATERIALS
→ STATE_PLATFORM_SELECTION

Senaryo Onay Akışı

STATE_BRIEF_COMPLETED
→ STATE_SCENARIO_APPROVAL

STATE_SCENARIO_APPROVAL
→ STATE_PRICING

STATE_SCENARIO_APPROVAL
→ STATE_SESSION_CLOSED

Fiyat Teklifi Akışı

STATE_PRICING
→ STATE_PAYMENT_VERIFICATION

STATE_PRICING
→ STATE_SESSION_CLOSED

Ödeme Doğrulama Akışı

STATE_PAYMENT_VERIFICATION
→ STATE_VIDEO_PRODUCTION

STATE_PAYMENT_VERIFICATION
→ STATE_SESSION_CLOSED
```

Bu akışlar başlangıç referansıdır.

HLK sistem geliştikçe yeni kullanıcı durumları ekleyebilir, bazı geçişleri değiştirebilir veya yeni geçiş yolları tanımlayabilir.

Ancak her kullanıcı durumu geçişi açık kurallarla tanımlanmalıdır.

HLK'nin amacı yalnızca mevcut state'i saklamak değil, kullanıcı oturum yaşam döngüsünü tutarlı ve denetlenebilir şekilde yönetmektir.

Beklenen Sonuç:

SE-007_3 ile tanımlanan kullanıcı state'leri arasındaki resmi geçiş kuralları tanımlanmış olur.

AR-002_27 Active Conversation Screen Architecture için gerekli state geçişleri tanımlanmış olur.

AR-002_28 Conversation Scene Engine Architecture için gerekli state geçişleri tanımlanmış olur.

AR-002_35 Research-Conversation Parallel Execution Architecture için gerekli state geçişleri tanımlanmış olur.

HLK kullanıcı oturum yaşam döngüsü ilk kez resmi geçiş kuralları ile yönetilebilir hale gelir.

---

### SE-007_5 — State Event Trigger Architecture

State değişimlerini başlatan olayların (event) nasıl yönetileceğini tanımlar.

HLK içerisinde hiçbir state değişimi sebepsiz veya rastgele gerçekleşemez.

Her state değişimi bir olay (event) tarafından tetiklenmelidir.

HLK kullanıcı etkileşimleri, sistem kararları, araştırma sonuçları veya operasyonel olaylar sonucunda state değişikliği başlatabilir.

HLK'nin amacı yalnızca mevcut state'i takip etmek değil, state değişiminin neden gerçekleştiğini de kayıt altına alabilmektir.

---

**Event Ownership (MASTER-001):**

HLK içerisinde kullanılan tüm Event'lerin tek resmi tanım kaynağı **14_OLAY_KAYIT_MERKEZI.md** dosyasıdır.

Bu dosya (07_HLK_STATE_ENGINE.md), Event tanımlamaz. Yalnızca State geçişlerinde hangi resmi Event'in tetikleyici olarak kullanıldığını referans gösterir.

---

**State → Event → Sonraki State Referans Tablosu:**

Her state geçişi, 14_OLAY_KAYIT_MERKEZI.md içerisinde tanımlı bir Event tarafından tetiklenir. Aşağıdaki tablo, SE-007_4'te tanımlanan state geçişlerinin hangi Event'ler ile tetiklendiğini gösterir.

| Kaynak State | Tetikleyici Event (14_OLAY referanslı) | Hedef State |
|---|---|---|
| `STATE_START` | `EVENT_SESSION_STARTED` (OLAY-001) | `STATE_SCENE_1` |
| `STATE_SCENE_1` | `EVENT_SCENE_1_COMPLETED` | `STATE_LANGUAGE_SELECTION` |
| `STATE_LANGUAGE_SELECTION` | `EVENT_LANGUAGE_SELECTED` (OLAY-002) | `STATE_SCENE_2` |
| `STATE_SCENE_2` | `EVENT_SCENE_2_COMPLETED` | `STATE_WAIT_PRODUCT_LINK` |
| `STATE_WAIT_PRODUCT_LINK` | `EVENT_PRODUCT_LINK_RECEIVED` (OLAY-003) | `STATE_LINK_VALIDATION` |
| `STATE_LINK_VALIDATION` | `EVENT_PRODUCT_LINK_VALIDATED` (OLAY-004) | `STATE_LINK_VALIDATED` |
| `STATE_LINK_VALIDATION` | `EVENT_PRODUCT_LINK_REJECTED` (OLAY-005) | `STATE_WAIT_PRODUCT_LINK` |
| `STATE_LINK_VALIDATED` | `EVENT_PRODUCT_ANALYSIS_STARTED` (OLAY-006) | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| `STATE_BACKGROUND_RESEARCH_RUNNING` | `EVENT_MATERIAL_REQUEST_STARTED` | `STATE_COLLECT_PRODUCT_MATERIALS` |
| `STATE_COLLECT_PRODUCT_MATERIALS` | `EVENT_MATERIAL_COLLECTION_COMPLETED` | `STATE_PLATFORM_SELECTION` |
| `STATE_PLATFORM_SELECTION` | `EVENT_PLATFORM_SELECTED` | `STATE_VIDEO_RESOLUTION_SELECTION` |
| `STATE_VIDEO_RESOLUTION_SELECTION` | `EVENT_RESOLUTION_SELECTED` | `STATE_VIDEO_DURATION_SELECTION` |
| `STATE_VIDEO_DURATION_SELECTION` | `EVENT_DURATION_SELECTED` | `STATE_AUDIO_SELECTION` |
| `STATE_AUDIO_SELECTION` | `EVENT_AUDIO_OPTION_SELECTED` | `STATE_BRIEF_COMPLETED` |
| `STATE_BRIEF_COMPLETED` | `EVENT_BRIEF_APPROVED` | `STATE_SCENARIO_APPROVAL` |
| `STATE_SCENARIO_APPROVAL` | `EVENT_SCENARIO_APPROVED` (OLAY-011) | `STATE_PRICING` |
| `STATE_SCENARIO_APPROVAL` | `EVENT_SCENARIO_REJECTED` (OLAY-012) | `STATE_SESSION_CLOSED` |
| `STATE_PRICING` | `EVENT_PRICE_APPROVED` (OLAY-014) | `STATE_PAYMENT_VERIFICATION` |
| `STATE_PRICING` | `EVENT_PRICE_REJECTED` (OLAY-015) | `STATE_SESSION_CLOSED` |
| `STATE_PAYMENT_VERIFICATION` | `EVENT_PAYMENT_DECLARED` (OLAY-029) | `STATE_PAYMENT_VERIFICATION` |
| `STATE_PAYMENT_VERIFICATION` | `EVENT_PAYMENT_APPROVED` (OLAY-030) | `STATE_VIDEO_PRODUCTION` |
| `STATE_VIDEO_PRODUCTION` | `EVENT_VIDEO_PRODUCTION_COMPLETED` (OLAY-024) | `STATE_SESSION_COMPLETED` |
| `STATE_VIDEO_PRODUCTION` | `EVENT_VIDEO_PRODUCTION_STARTED` (OLAY-023) | `STATE_VIDEO_PRODUCTION` |
| `STATE_VIDEO_PRODUCTION` | `EVENT_PRODUCTION_PACKAGE_CREATED` (OLAY-031) | `STATE_VIDEO_PRODUCTION` |
| Kullanıcı cevap bekleyen tüm state'ler | `EVENT_TIMEOUT_REACHED` | `STATE_SESSION_TIMEOUT` |
| `STATE_SESSION_TIMEOUT` | `EVENT_SESSION_CLOSED` (OLAY-028) | `STATE_SESSION_CLOSED` |

> **Referans Zinciri:** Bu tabloda listelenen Event'lerin tamamının resmi tanımları (Teknik Sabit, Event Adı, Açıklama, Kaynak Durum, Hedef Durum, Üreten Bileşen, Tetikleyici, Öncelik, Bildirim Hedefleri, Kayıt Politikası ve diğer tüm alanlar) yalnızca **14_OLAY_KAYIT_MERKEZI.md** içerisinde yer almaktadır.

> **Not:** Bu tabloda referans verilen tüm Event'ler 14_OLAY_KAYIT_MERKEZI.md içerisinde kayıt altına alınmıştır (OLAY-001 — OLAY-044). OLAY numarası belirtilmeyen satır bulunmamaktadır.

---

**Temel İlke:**

14_OLAY_KAYIT_MERKEZI.md → Event'leri tanımlar (Single Source of Truth)

07_HLK_STATE_ENGINE.md → Event'leri referans gösterir (State tetikleyici haritası)

Bu iki dosya arasındaki ilişki MASTER-001 Karar Hiyerarşisi'ne tabidir. Event tanımı ile referans arasında çelişki oluşursa 14_OLAY_KAYIT_MERKEZI.md esas alınır.

---

Beklenen Sonuç:

SE-007_3 ile tanımlanan kullanıcı state'lerinin hangi Event'lerle başlatılacağı referans tablosu oluşturulmuş olur.

SE-007_4 ile tanımlanan state geçişlerinin tetikleyicileri, 14_OLAY_KAYIT_MERKEZI.md referanslarıyla ilişkilendirilmiş olur.

HLK state yönetimi; durum, geçiş ve resmi Event referanslarından oluşan tam bir yaşam döngüsüne kavuşmuş olur.

MASTER-001 Single Source of Truth prensibi Event mimarisinde uygulanmış olur.

---

### SE-007_6 — State Action Mapping Architecture

State ile sistem davranışları arasındaki ilişkiyi tanımlar.

HLK içerisinde her state yalnızca bir durum bilgisini temsil etmez.

Her state aynı zamanda belirli modüllerin, servislerin veya sistem davranışlarının çalıştırılmasını tetikleyebilir.

Bir state aktif hale geldiğinde HLK ilgili state için tanımlanmış modülleri devreye alabilir.

State Engine, modül seçimleri için merkezi referans noktası olarak kullanılabilir.

Örnek State → Modül İlişkileri

```
STATE_START
↓
Oturumu başlat
Sistem başlangıç kontrollerini çalıştır
```

```
STATE_SCENE_1
↓
SAHNE-1 karşılama videosunu oynat
Sahne tamamlanmasını bekle
```

```
STATE_LANGUAGE_SELECTION
↓
Dil seçim ekranını göster
Kullanıcı seçimini bekle
```

```
STATE_SCENE_2
↓
SAHNE-2 konuşma videosunu oynat
Kullanıcıyı ürün linki aşamasına hazırla
```

```
STATE_WAIT_PRODUCT_LINK
↓
Ürün linki bekle
Kullanıcı girişini dinle
```

```
STATE_LINK_VALIDATION
↓
Ürün linki doğrulama işlemini başlat
Link analiz görevini çalıştır
```

```
STATE_LINK_VALIDATED
↓
Link doğrulama sonucunu kaydet
Sonraki iş akışını hazırla
```

```
STATE_BACKGROUND_RESEARCH_RUNNING
↓
Arka plan araştırmasını başlat
Ajan görevlerini oluştur
```

```
STATE_COLLECT_PRODUCT_MATERIALS
↓
Tamamlayıcı materyal talep et
Materyal yüklemelerini yönet
```

```
STATE_PLATFORM_SELECTION
↓
Platform seçeneklerini göster
Kullanıcı seçimini kaydet
```

```
STATE_VIDEO_RESOLUTION_SELECTION
↓
Video çözünürlük seçeneklerini göster
Kullanıcı seçimini kaydet
```

```
STATE_VIDEO_DURATION_SELECTION
↓
Video süresi seçeneklerini göster
Kullanıcı seçimini kaydet
```

```
STATE_AUDIO_SELECTION
↓
Ses seçeneklerini göster
Kullanıcı seçimini kaydet
```

```
STATE_BRIEF_COMPLETED
↓
Brief toplama sürecini tamamla
Senaryo onayına hazırlık yap
```

```
STATE_SCENARIO_APPROVAL
↓
Senaryo paketini hazırla
Kullanıcıya sun
ONAY / RET kararını bekle
```

```
STATE_PRICING
↓
Fiyat teklifini hazırla
HLK Yönetici Fiyatlandırma Formu (Yöneticiye özel)
HLK Kullanıcı Fiyat Teklif Formu (Kullanıcıya özel)
ONAY / RET kararını bekle
```

STATE_PRICING aşamasında iki resmi operasyon ekranı bulunur.

**HLK Yönetici Fiyatlandırma Formu** — Yalnızca yönetici tarafından görüntülenebilir. Operasyon özeti, ürün bilgileri, senaryo özeti, kullanılan/kullanılmayan ajan ve servis bilgileri, API durumları, Servis Güven Skorları, kredi durumları, risk analizi, tahmini maliyet ve süre bilgilerini gösterir. Yönetici satış fiyatını girer, kampanya veya indirim uygulayabilir, teklifi onaylar veya iptal eder.

> 📐 **Referans UI Tasarımı:** HLK Yönetici Fiyatlandırma Formu'nun resmi referans tasarımı `REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.png` dosyasıdır. Bu dosya Digital Asset Catalog içerisinde `REF-UI-002` Asset ID'si ile kayıtlıdır ve `FORMLAR/REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.png` konumunda bulunur. STATE_PRICING aşamasında HLK tarafından oluşturulacak tüm Yönetici Fiyatlandırma Formları bu referans tasarım esas alınarak geliştirilir. Bu referans tasarım AR-002_55 (Referans UI Tasarım Mimarisi) kapsamında yönetilir ve yalnızca Proje Yöneticisinin onayı ile değiştirilebilir.

**HLK Kullanıcı Fiyat Teklif Formu** — Yalnızca kullanıcı tarafından görüntülenebilir. Yönetici tarafından belirlenen satış teklifini profesyonel teklif formu olarak sunar. Ürün özeti, platform, video süresi, çözünürlük, teslim süresi, hizmet kapsamı, satış fiyatı, vergi bilgisi, teklif geçerlilik süresi ve ödeme bilgilerini içerir. Kullanıcı teklifi onaylar veya reddeder.

Her iki ekran HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanır.

Ekran geçiş sırası:

STATE_SCENARIO_APPROVAL
→ EVENT_SCENARIO_APPROVED
→ HLK Yönetici Fiyatlandırma Formu
→ HLK Kullanıcı Fiyat Teklif Formu
→ EVENT_PRICING_APPROVED / EVENT_PRICING_REJECTED
→ STATE_PAYMENT_VERIFICATION / STATE_SESSION_CLOSED
→ EVENT_PAYMENT_DECLARED (Kullanıcı)
→ Yönetici Ödeme Onay Formu
→ EVENT_PAYMENT_APPROVED (Yönetici)
→ STATE_VIDEO_PRODUCTION

```
STATE_PAYMENT_VERIFICATION
↓
Yönetici Ödeme Onay Formunu göster
Banka hesabı kontrolünü bekle
ÖDEMEYİ ONAYLA / RET kararını bekle
```

STATE_PAYMENT_VERIFICATION aşamasında bir resmi operasyon ekranı bulunur.

**Yönetici Ödeme Onay Formu** — Yalnızca yönetici tarafından görüntülenebilir. Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" bildirimi gönderdiğinde yöneticiye iletilir. Form başlığı: ÖDEME DOĞRULAMA. Açıklama: Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" bildirimi göndermiştir. Lütfen banka hesabınızı kontrol ediniz. Ödeme hesabınıza ulaştıysa aşağıdaki butona basınız. Yönetici banka hesabını kontrol eder ve ÖDEMEYİ ONAYLA butonuna basar. Yalnızca EVENT_PAYMENT_APPROVED sonrasında STATE_VIDEO_PRODUCTION başlatılır.

Yönetici Ödeme Onay Formu, HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanır.

STATE_PAYMENT_VERIFICATION aşamasında timeout kuralları geçerlidir. Bekleme ve timeout davranışları OR-004_9 kurallarına tabidir.

```
STATE_VIDEO_PRODUCTION
↓
PID oluştur (Production ID — AR-002_57 standardı)
Üretim paketini PID ile ilişkilendir
Video üretim sürecini başlat
Üretim görevlerini yönet
```

STATE_VIDEO_PRODUCTION state'ine girişte, Video Production başlamadan hemen önce HLK tarafından benzersiz bir **PID (Production ID)** oluşturulur.

PID oluşturulduktan hemen sonra HLK tarafından **Production Package** oluşturulur. Production Package, bu üretime ait tüm bilgi, varlık ve Task Package'lerin ana kapsayıcısıdır (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md).

PID formatı: `PID-YYYYMMDD-NNNN` (Global Configuration: `GC_PID_PREFIX`, `GC_PID_DATE_FORMAT`, `GC_PID_SEQUENCE_LENGTH`, `GC_PID_SEQUENCE_START` tarafından yönetilir).

PID ve Production Package, bu üretime ait tüm event, log, maliyet, servis ve kalite kayıtlarının ortak referansıdır. PID alanı üretim event'lerinde zorunludur (AR-002_57).

```
STATE_SESSION_COMPLETED
↓
Sonuçları kullanıcıya sun
Oturumu başarıyla kapat
```

```
STATE_SESSION_TIMEOUT
↓
Timeout işlemlerini uygula
Oturum sonlandırma sürecini başlat
```

```
STATE_SESSION_CLOSED
↓
Oturumu kapat
Kaynak temizleme işlemlerini tamamla
```

Bu eşleştirmeler başlangıç referansıdır.

HLK sistem geliştikçe yeni state-modül ilişkileri ekleyebilir, mevcut eşleştirmeleri değiştirebilir veya kullanım dışı bırakabilir.

Ancak her modül aktivasyonu mümkün olduğunca bir state ile ilişkilendirilmelidir.

Beklenen Sonuç:

SE-007_3 ile tanımlanan kullanıcı state'lerinin hangi modülleri çalıştıracağı tanımlanmış olur.

SE-007_4 ile tanımlanan kullanıcı geçişlerinin hangi sistem davranışlarını başlatacağı tanımlanmış olur.

SE-007_5 ile tanımlanan event'lerin sonuç olarak hangi modülleri çalıştıracağı tanımlanmış olur.

HLK State Engine yapısı yalnızca durum ve geçişleri yöneten bir sistem olmaktan çıkar, iş akışını yöneten merkezi karar mekanizmasına dönüşür.

Telegram testlerinde görülen "state oluştu fakat beklenen modül çalışmadı" problemleri daha kolay analiz edilebilir hale gelir.

---

## 6. İzin Verilen Geçişler

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 7. Yasak Geçişler

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 8. State Güvenlik İlkeleri

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 9. State Devralma Kuralları

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 10. State Kurtarma Kuralları

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 11. Genel Kurallarla İlişki

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 12. Global Configuration ile İlişki

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 13. Akış Diyagramı ile İlişki

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 14. State Diyagramı

*(Bir sonraki aşamada doldurulacaktır.)*

---

## 15. Kanonik State Listesi

*(Bir sonraki aşamada doldurulacaktır.)*
