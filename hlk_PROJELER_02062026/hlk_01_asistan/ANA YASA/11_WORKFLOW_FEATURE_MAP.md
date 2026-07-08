# 11 — Workflow Feature Map

HLK içerisinde bulunan Workflow'lar ile Feature'lar arasındaki ilişkiyi gösteren resmi kayıt dosyasıdır.

---

## Amaç

Workflow Feature Map;

Workflow'ların hangi Feature'ları kullandığını gösteren tek resmi kayıt noktasıdır.

Bu dosya yalnızca ilişki bilgilerini içerir.

Workflow davranışları bu dosyada tanımlanmaz.

Feature davranışları bu dosyada tanımlanmaz.

---

## Workflow - Feature İlişkileri

### WF-001

Türkçe Adı : Ürün Linki Doğrulama

Kullandığı Feature'lar

* FEAT-001 Ürün Linki Doğrulama
* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru

---

### WF-002

Türkçe Adı : Arka Plan Araştırması

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-004 Arka Plan Araştırması
* FEAT-005 Görsel Araştırması
* FEAT-006 Marka Analizi

---

### WF-003

Türkçe Adı : Brief Toplama

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru

---

### WF-004

Türkçe Adı : Brief Onayı

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru

---

### WF-005

Türkçe Adı : Senaryo Üretimi

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-007 Senaryo Üretimi

---

### WF-006

Türkçe Adı : Senaryo Onayı

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru

---

### WF-007

Türkçe Adı : Fiyatlandırma

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-011 Yönetici Fiyatlandırma Formu
* FEAT-012 Kullanıcı Fiyat Teklif Formu
* FEAT-013 Yönetici Video Üretim Onay Formu

#### Kullanıcı Arayüzü Ekranları

**HLK Yönetici Fiyatlandırma Formu**

Görevi

Kullanıcının senaryoyu onaylamasından sonra HLK tarafından otomatik oluşturulur.

Bu ekran yalnızca yöneticiye gönderilir.

Bu ekranın amacı yöneticinin satış fiyatını belirlemesini sağlamaktır.

Gösterilecek Bilgiler

* Ürün özeti
* Marka bilgisi
* Platform
* Video süresi
* Çözünürlük
* Teslim süresi
* Senaryo özeti

Operasyon Bilgileri

* Kullanılan ajanlar
* Kullanılan servis sağlayıcılar
* Kullanılmayan servis sağlayıcılar
* Kullanılmama nedenleri

Servis Sağlık Bilgileri

Her servis için;

* API durumu
* Servis Güven Skoru
* Mevcut kredi
* Tahmini kredi tüketimi
* Üretim sonrası tahmini kredi
* Kota durumu
* Risk seviyesi

Risk Analizi

* API problemleri
* Kritik kredi seviyeleri
* Kota problemleri
* Alternatif servis kullanımı
* Yönetici müdahalesi gerektiren durumlar

Tahmini Üretim

* Tahmini maliyet
* Tahmini üretim süresi
* Tahmini kredi tüketimi

Yönetici İşlemleri

* Satış fiyatı giriş alanı
* Fiyatı Onayla
* Düzenle
* İptal

Yönetici fiyatı onayladıktan sonra workflow otomatik olarak HLK Kullanıcı Fiyat Teklif Formu ekranına geçer.

Tasarım Standardı: HLK Premium Card Architecture, HLK UI Component Library, HLK Design Token Architecture

---

**HLK Kullanıcı Fiyat Teklif Formu**

Görevi

Yönetici tarafından belirlenen satış fiyatını kullanıcıya profesyonel teklif formu olarak sunar.

Bu ekran yalnızca kullanıcıya gönderilir.

Gösterilecek Bilgiler

Ürün Bilgileri

* Ürün adı
* Platform
* Video süresi
* Çözünürlük
* Teslim süresi

Hizmet İçeriği

* Senaryo hazırlama
* Yapay zekâ reklam üretimi
* Video üretimi
* Seslendirme
* Kurgu
* Teslim

Teklif Bilgisi

* Yönetici tarafından belirlenen satış fiyatı
* Para birimi
* Vergi bilgisi
* Teklif geçerlilik süresi

Bilgilendirme

* Ödeme alındıktan sonra üretimin başlayacağı bilgisi
* Üretim süreci hakkında kısa açıklama

Kullanıcı İşlemleri

* Teklifi Onayla
* Teklifi Reddet

Kullanıcı teklifi onayladığında workflow ödeme sürecine geçer.

Kullanıcı teklifi reddederse workflow mevcut operasyon kurallarına göre sonlandırılır veya revizyon sürecine yönlendirilir.

Tasarım Standardı: HLK Premium Card Architecture, HLK UI Component Library, HLK Design Token Architecture

---

Ekran Geçiş Sırası

Senaryo Onay Formu

↓

HLK Yönetici Fiyatlandırma Formu

↓

HLK Kullanıcı Fiyat Teklif Formu

↓

Ödeme Süreci

↓

Reklam Üretim Süreci

---

### WF-008

Türkçe Adı : Video Üretimi

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-008 Ses Üretimi
* FEAT-009 Native Video Scene
* FEAT-013 Yönetici Video Üretim Onay Formu
* FEAT-014 Production Package Engine

#### PID (Production ID) Oluşturulma Aşaması

WF-008 kapsamında, STATE_VIDEO_PRODUCTION girişinde HLK tarafından benzersiz bir **PID (Production ID)** oluşturulur.

PID formatı: `PID-YYYYMMDD-NNNN` (AR-002_57, GC_PID_PREFIX, GC_PID_DATE_FORMAT, GC_PID_SEQUENCE_LENGTH, GC_PID_SEQUENCE_START).

Oluşturulan PID; Production Package, Workflow, Event logları, Agent logları, Video dosyaları, Kalite raporları, Servis kullanımları, Kredi tüketimi ve Teslim kayıtları için ortak referans anahtarı olarak kullanılır.

PID oluşturulduktan hemen sonra Production Package Engine (FEAT-014) devreye girer ve Production Package'i oluşturur. Production Package, Task Package'lerin üst katmanı olarak çalışır (AR-002_58).

PID alanı üretim event'lerinde (OLAY-023, OLAY-024, OLAY-025, OLAY-026, OLAY-027, OLAY-031) zorunludur.

#### Yönetici Video Üretim Onay Formu

Bu form, WF-007 (Pricing) ile STATE_VIDEO_PRODUCTION arasında çalışan son yönetici kontrol katmanıdır.

Video Production başlamadan önce HLK, oluşturduğu üretim paketini bu form üzerinden Proje Yöneticisinin onayına sunar.

Yönetici onayı alınmadan hiçbir Video Production süreci başlatılamaz.

Bu formun görevi:

* Üretim paketini son kez doğrulamak,
* Yanlış üretimi önlemek,
* Gereksiz kredi tüketimini önlemek,
* Üretim güvenliğini sağlamak,
* Üretim referansını oluşturmak,
* Yöneticinin son kararını almaktır.

---

### WF-009

Türkçe Adı : Kalite Kontrol

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-010 Kalite Kontrol

---

### WF-010

Türkçe Adı : Teslim

Kullandığı Feature'lar

* FEAT-002 Karar Mekanizması
* FEAT-003 Durum Motoru
* FEAT-010 Kalite Kontrol

---

### WF-015

Türkçe Adı : Constitution Enforcement

Kullandığı Feature'lar

* FEAT-019 Constitution Enforcement Engine (CEE)

---

### WF-016

Türkçe Adı : Execution Event Collection

Kullandığı Feature'lar

* FEAT-020 Execution Event Collector (EEC)

---


## Temel İlke

Workflow Feature Map yalnızca Workflow ile Feature arasındaki ilişkiyi gösterir.

Bu dosya;

* Workflow değildir.
* Feature Registry değildir.
* State Engine değildir.
* Flow Diagram değildir.

Bu dosya yalnızca HLK'nın Workflow-Feature bağımlılık haritasının resmi kayıt defteridir.
