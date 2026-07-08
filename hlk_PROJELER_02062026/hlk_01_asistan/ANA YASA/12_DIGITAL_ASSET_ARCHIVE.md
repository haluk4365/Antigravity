# 12 — Digital Asset Archive

HLK tarafından üretilen veya kullanılan tüm dijital varlıkların resmi arşiv ve kayıt yönetim dosyasıdır.

---

## Amaç

Digital Asset Archive;

HLK'nın ürettiği tüm dijital varlıkların tek resmi arşiv yönetim standardıdır.

Bu dosya;

* dijital varlıkların nasıl saklanacağını,
* nasıl kayıt altına alınacağını,
* nasıl bulunacağını,
* nasıl korunacağını

tanımlar.

Bu dosya medya dosyalarının kendisini içermez.

---

## Arşiv Kapsamı

HLK aşağıdaki dijital varlıkları arşivleyebilir.

* Reklam Videoları
* Revizyon Videoları
* Ses Dosyaları
* Thumbnail Dosyaları
* Brief Dosyaları
* Senaryo Dosyaları
* Araştırma Çıktıları
* Metadata Dosyaları
* Render Bilgileri
* Sistem Logları

---

## Arşiv Kimliği

Arşive eklenen her dijital varlık benzersiz bir Arşiv Kimliği (Asset ID) alır.

Örnek:

ASSET-000001

---

## Kayıt Bilgileri

Her dijital varlık için en az aşağıdaki bilgiler kayıt altına alınır.

* Asset ID
* Asset Türü
* Kullanıcı
* Kullanıcı Kimliği
* Workflow
* Feature
* Ürün Adı
* Marka
* Ürün Linki
* Oluşturulma Tarihi
* Teslim Tarihi
* Dil
* Video Süresi
* Video Çözünürlüğü
* Revizyon Numarası
* Durum
* Dosya Konumu
* SHA-256 Doğrulama Kodu

---

## Arama Standardı

HLK arşivde bulunan dijital varlıkları aşağıdaki bilgilerden biri veya birkaçı kullanılarak bulabilir.

* Asset ID
* Kullanıcı Adı
* Kullanıcı Kimliği
* Telegram Kimliği
* Ürün Adı
* Marka
* Ürün Linki
* Workflow
* Tarih
* Tarih Aralığı
* Dil
* Video Çözünürlüğü
* Revizyon Numarası

---

## Ana Kopya (Master Copy)

HLK tarafından kullanıcıya teslim edilen ilk reklam videosu Ana Kopya olarak kabul edilir.

Ana Kopya;

* Değiştirilemez.
* Üzerine yazılamaz.
* Read Only olarak korunur.
* SHA-256 doğrulama kodu ile kayıt altına alınır.

---

## Revizyon Standardı

Revizyon oluşturulması gerektiğinde mevcut dosya değiştirilmez.

Her revizyon yeni bir dijital varlık olarak oluşturulur.

Ana Kopya her zaman korunur.

---

## Production Package İlişkisi

Production Package (16_PRODUCTION_PACKAGE_STANDARD.md), Digital Asset Archive için resmi üst referanstır.

Production Package içerisinde yer alan tüm dijital varlıklar (Nihai Video, Ses Dosyaları, Referans Görseller, vb.) Digital Asset Archive'de PID üzerinden ilişkilendirilerek saklanır.

Digital Asset Archive'deki her varlık kaydı, ilgili Production Package'in PID'sini referans alır.

Arşiv kimliği (Asset ID) ile PID arasındaki ilişki Digital Asset Catalog (13_DIGITAL_ASSET_CATALOG.md) üzerinden yönetilir.

Production Package, arşivlenen tüm dijital varlıkların ortak referans noktasıdır.

---

## Temel İlke

Digital Asset Archive;

Workflow değildir.

Feature Registry değildir.

Workflow Feature Map değildir.

Bu dosya HLK'nın dijital kurumsal hafızasını oluşturan resmi arşiv yönetim standardıdır.
