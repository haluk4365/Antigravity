# 10 — Feature Registry

HLK içerisinde bulunan tüm sistem özelliklerinin (Feature) resmi kayıt dosyasıdır.

---

## Amaç

Feature Registry;

HLK'nın sahip olduğu tüm sistem özelliklerinin tek resmi kayıt noktasıdır.

Bu dosya yalnızca Feature kayıtlarını içerir.

Feature davranışları bu dosyada tanımlanmaz.

Feature davranışları ilgili Workflow, State Engine, Operational Rules, Module Rules ve diğer anayasal katmanlar tarafından yönetilir.

---

## Feature Kategorileri

### CORE

Türkçe Adı : Çekirdek Özellikler

HLK'nın çalışması için zorunlu temel yetenekleri içerir.

---

### RESEARCH

Türkçe Adı : Araştırma Özellikleri

Ürün, marka, görsel ve bilgi araştırma özelliklerini içerir.

---

### BRIEF

Türkçe Adı : Brief Özellikleri

Kullanıcıdan bilgi toplama süreçlerinde kullanılan özellikleri içerir.

---

### PRODUCTION

Türkçe Adı : Üretim Özellikleri

Senaryo, ses, video ve medya üretim özelliklerini içerir.

---

### QUALITY

Türkçe Adı : Kalite Özellikleri

Kalite kontrol ve doğrulama özelliklerini içerir.

---

### OPERATIONAL

Türkçe Adı : Operasyonel Özellikler

Cache, Retry, Log, Agent ve benzeri operasyonel özellikleri içerir.

---

### PRICING

Türkçe Adı : Fiyatlandırma Özellikleri

Fiyat teklifi, yönetici fiyatlandırma formu, kullanıcı teklif formu ve fiyatlandırma ile ilgili kullanıcı arayüzü özelliklerini içerir.

---

### SYSTEM

Türkçe Adı : Sistem Özellikleri

Oturum, kullanıcı, güvenlik ve sistem yönetimi özelliklerini içerir.

---

## İlk Feature Kayıtları

### FEAT-001

Türkçe Adı : Ürün Linki Doğrulama

İngilizce Adı : Product Link Validation

Kategori : CORE

Durum : AKTİF

---

### FEAT-002

Türkçe Adı : Karar Mekanizması

İngilizce Adı : Decision Engine

Kategori : CORE

Durum : AKTİF

---

### FEAT-003

Türkçe Adı : Durum Motoru

İngilizce Adı : State Engine

Kategori : CORE

Durum : AKTİF

---

### FEAT-004

Türkçe Adı : Arka Plan Araştırması

İngilizce Adı : Background Research

Kategori : RESEARCH

Durum : AKTİF

---

### FEAT-005

Türkçe Adı : Görsel Araştırması

İngilizce Adı : Image Research

Kategori : RESEARCH

Durum : AKTİF

---

### FEAT-006

Türkçe Adı : Marka Analizi

İngilizce Adı : Brand Analysis

Kategori : RESEARCH

Durum : AKTİF

---

### FEAT-007

Türkçe Adı : Senaryo Üretimi

İngilizce Adı : Scenario Generation

Kategori : PRODUCTION

Durum : AKTİF

---

### FEAT-008

Türkçe Adı : Ses Üretimi

İngilizce Adı : Voice Generation

Kategori : PRODUCTION

Durum : AKTİF

---

### FEAT-009

Türkçe Adı : Native Video Scene

İngilizce Adı : Native Video Scene

Kategori : PRODUCTION

Durum : AKTİF

---

### FEAT-010

Türkçe Adı : Kalite Kontrol

İngilizce Adı : Quality Control

Kategori : QUALITY

Durum : AKTİF

---

### FEAT-011

Türkçe Adı : Yönetici Fiyatlandırma Formu

İngilizce Adı : Admin Pricing Form

Kategori : PRICING

Tür : SCREEN

Durum : AKTİF

---

### FEAT-012

Türkçe Adı : Kullanıcı Fiyat Teklif Formu

İngilizce Adı : User Offer Form

Kategori : PRICING

Tür : SCREEN

Durum : AKTİF

---

### FEAT-013

Türkçe Adı : Yönetici Video Üretim Onay Formu

İngilizce Adı : Admin Video Production Approval Form

Kategori : QUALITY

Tür : SCREEN

Durum : AKTİF

Açıklama : Video üretimi başlamadan önce üretim paketinin yönetici tarafından doğrulanmasını sağlayan referans yönetici ekranıdır. Bu form; üretim paketini son kez doğrulamak, yanlış üretimi önlemek, gereksiz kredi tüketimini önlemek, üretim güvenliğini sağlamak, üretim referansını oluşturmak ve yöneticinin son kararını almak amacıyla kullanılır. Bu form tamamlanmadan HLK hiçbir şekilde Video Production sürecini başlatamaz. Form onaylandığında HLK tarafından benzersiz bir PID (Production ID) oluşturulur. PID standardı AR-002_57 ile tanımlanmıştır.

---

### FEAT-014

Türkçe Adı : Production Package Engine

İngilizce Adı : Production Package Engine

Kategori : PRODUCTION

Tür : ENGINE

Durum : AKTİF

Açıklama : PID oluşturulduktan sonra Production Package'in oluşturulmasından, yönetilmesinden ve arşivlenmesinden sorumlu motordur. Production Package; üretime ait tüm bilgi, dijital varlık, Task Package, log ve çıktıların ana kapsayıcısıdır. Production Package standardı AR-002_58 ve 16_PRODUCTION_PACKAGE_STANDARD.md ile tanımlanmıştır.

---

### FEAT-015

Türkçe Adı : Live Activity Center

İngilizce Adı : Live Activity Center

Kategori : OPERATIONAL

Tür : SCREEN

Durum : AKTİF

Açıklama : HLK Live Activity Center (LAC), HLK sisteminin resmi Yönetici Operasyon Ekranıdır. LAC; kullanıcının `/start` komutunu verdiği andan başlayarak oturum tamamen sonlanıncaya kadar HLK içerisinde oluşan tüm gerçek Event'leri canlı olarak izler. LAC yalnızca Video Production sürecini değil; Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive olmak üzere 13 katmanı kapsayan merkezi operasyon ekranıdır. Service katmanı; HLK tarafından kullanılan tüm harici ve dahili servislerin API durumu, kredi/kota, gecikme süresi ve hata bilgilerini gerçek zamanlı gösterir. PID tek referans olacak şekilde, Production Package ana veri kaynağı üzerinden, yalnızca gerçek Event'leri göstererek, Fake Progress kullanmadan HLK'nın tüm oturum yaşam döngüsünü (Session Lifecycle) canlı olarak izler. Yönetici yalnızca izleyicidir; HLK karar mekanizmasına müdahale edemez. LAC; Desktop ve Mobile referans tasarımlarını içeren tek resmi Referans UI Tasarımına sahiptir (REF-UI-005). LAC mimarisi AR-002_59 ile tanımlanmıştır.

---

### FEAT-019

Türkçe Adı : Constitution Enforcement Engine

İngilizce Adı : Constitution Enforcement Engine (CEE)

Kategori : ENFORCEMENT

Tür : ENGINE

Durum : AKTİF

Açıklama : Constitution Enforcement Engine (CEE), HLK'nın anayasal uygulatma katmanıdır. Executor'dan (Claude) önce anayasal görev paketini (CTP) oluşturur, Executor'dan sonra çıktıyı anayasal kurallara göre denetler, uygunsuzluğu REDDEDER ve yalnızca tam uyum sağlandığında PASS verir. CEE, 3 fazlı çalışır: PRE-CHECK (anayasal görev paketi oluşturma), EXECUTE (Executor denetimli çalışır), POST-CHECK (6 boyutlu anayasal denetim + PASS/FAIL). CEE, HLK içerisinde PASS/FAIL verme yetkisine sahip tek katmandır. CEE olmadan hiçbir geliştirme görevi tamamlanmış kabul edilemez. CEE mimarisi 21_CONSTITUTION_ENFORCEMENT_ENGINE.md ile tanımlanmıştır.

---

### FEAT-020

Türkçe Adı : Execution Event Collector

İngilizce Adı : Execution Event Collector (EEC)

Kategori : ENFORCEMENT

Tür : ENGINE

Durum : AKTİF

Açıklama : Execution Event Collector (EEC), Executor (Claude) işlemlerini gerçek zamanlı Event'lere dönüştüren, Olay Kayıt Merkezi'ne kaydeden ve Live Activity Center (LAC) tarafından anlık görüntülenebilmesini sağlayan Event toplama katmanıdır. EEC 3 aşamalı çalışır: LISTEN (Executor'u dinle), TRANSFORM (işlemi Event'e dönüştür), REGISTER (Olay Kayıt Merkezi'ne kaydet). 6 kategoride 28 Event tipi (OLAY-076 — OLAY-103) tanımlar. EEC hiçbir zaman Fake Progress üretmez. EEC mimarisi 22_EXECUTION_EVENT_COLLECTOR.md ile tanımlanmıştır.

---

Feature Registry;

* Workflow değildir.
* State Engine değildir.
* Operational Rules değildir.
* Module Rules değildir.

Bir Feature bir veya birden fazla Workflow tarafından kullanılabilir.

Workflow'lar değişebilir, ancak Feature'lar HLK'nın yeniden kullanılabilir sistem yeteneklerini temsil eder.
