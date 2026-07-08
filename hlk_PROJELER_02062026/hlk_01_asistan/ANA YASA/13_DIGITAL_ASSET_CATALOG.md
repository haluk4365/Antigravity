# 13 — Digital Asset Catalog

HLK tarafından arşivlenen tüm dijital varlıkların resmi katalog dosyasıdır.

---

## Amaç

Digital Asset Catalog;

HLK tarafından oluşturulan tüm dijital varlıkların aranabilir ve listelenebilir katalog kayıtlarını içerir.

Bu dosya medya dosyalarını içermez.

Bu dosya yalnızca katalog (metadata) kayıtlarını içerir.

---

## Katalog Kayıt Standardı

Her dijital varlık aşağıdaki bilgiler ile kataloglanır.

* Asset ID
* Video ID
* Kullanıcı Adı
* Kullanıcı Kimliği
* Telegram Kimliği
* Workflow
* Feature
* Ürün Adı
* Marka
* Ürün Linki
* Reklam Başlığı
* Reklam Dili
* Video Süresi
* Video Çözünürlüğü
* Dosya Boyutu
* Oluşturulma Tarihi
* Teslim Tarihi
* Revizyon Numarası
* Dosya Konumu
* SHA-256 Doğrulama Kodu
* Durum

---

## Arama Standardı

HLK aşağıdaki bilgilerden herhangi biri veya birkaçı ile katalog araması yapabilir.

* Asset ID
* Video ID
* Kullanıcı Adı
* Kullanıcı Kimliği
* Telegram Kimliği
* Ürün Adı
* Marka
* Ürün Linki
* Reklam Başlığı
* Workflow
* Feature
* Reklam Dili
* Video Süresi
* Video Çözünürlüğü
* Oluşturulma Tarihi
* Teslim Tarihi
* Revizyon Numarası

---

## Örnek Katalog Kaydı

Asset ID : ASSET-000001

Video ID : VIDEO-000001

Kullanıcı Adı : Haluk

Ürün Adı : Örnek Ürün

Marka : Örnek Marka

Reklam Dili : Türkçe

Video Süresi : 18 sn

Video Çözünürlüğü : 1080p

Oluşturulma Tarihi : 25.06.2026

Durum : TESLİM EDİLDİ

---

## Temel İlke

Digital Asset Catalog;

* Digital Asset Archive değildir.
* Workflow değildir.
* Feature Registry değildir.

Digital Asset Catalog, HLK'nın dijital kurumsal hafızasının aranabilir katalog katmanıdır.

Her dijital varlık için yalnızca bir katalog kaydı bulunur.

Katalog kayıtları fiziksel medya dosyalarının yerine geçmez; yalnızca onların bulunmasını, listelenmesini ve yönetilmesini sağlar.

---

## Production Package İlişkisi

Production Package (16_PRODUCTION_PACKAGE_STANDARD.md) içerisinde kullanılan tüm dijital varlıklar, Digital Asset Catalog'da **PID (Production ID)** üzerinden ilişkilendirilir.

Her katalog kaydı, bağlı olduğu Production Package'in PID'sini referans olarak içerir.

PID, katalog kayıtları için ortak arama anahtarı olarak kullanılabilir. Bir PID'ye ait tüm dijital varlıklar katalog üzerinden listelenebilir.

---

## Referans UI Tasarım Kayıtları

HLK'nın resmi kullanıcı arayüzü referans tasarımlarının katalog kayıtlarını içerir.

Bu katalogda yer alan referans tasarımlar;

- HLK içerisindeki ilgili form ve ekranların resmi tasarım standardıdır.
- Gelecekte oluşturulacak veya revize edilecek tüm ilgili form ve ekranlar bu referans tasarım esas alınarak geliştirilir.
- Yalnızca Proje Yöneticisinin onayı ile değiştirilebilir.

---

### REF-UI-005

| Alan | Değer |
|---|---|
| **Asset ID** | `REF-UI-005` |
| **Asset Türü** | Referans UI Tasarımı |
| **Tasarım Adı** | Live Activity Center (LAC) Referans Tasarımı |
| **İlgili Feature** | FEAT-015 — Live Activity Center (LAC Referans UI) |
| **İlgili State** | - |
| **Dosya Formatı** | PNG |
| **Dosya Adı** | `REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC).png` |
| **Dosya Konumu** | `FORMLAR/REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC).png` |
| **Versiyon** | v1.0 |
| **Oluşturulma Tarihi** | 01.07.2026 |
| **Durum** | AKTİF — Resmi Referans Tasarım |
| **Açıklama** | HLK Live Activity Center (LAC) için tek resmi referans kullanıcı arayüzü tasarımıdır. Bu tasarım; Desktop ve Mobile referans görünümlerini içerir. LAC; HLK sisteminin resmi Yönetici Operasyon Ekranı olup, kullanıcının `/start` komutundan oturum kapanışına kadar tüm Session Lifecycle'ı izleyen merkezi operasyon ekranıdır. LAC yalnızca Video Production sürecini değil; Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive olmak üzere 13 katmanı kapsar. Service katmanı; HLK tarafından kullanılan tüm harici ve dahili servislerin (OpenAI, Claude, Gemini, ElevenLabs, Hedra, FFmpeg, Telegram, Railway, PostgreSQL, Redis, Image API vb.) gerçek zamanlı operasyon durumunu gösterir. Yeni bir Workflow değildir; mevcut Workflow'ları izleyen bir operasyon izleme katmanıdır. PID tek referans olacak şekilde çalışır, yalnızca gerçek Event'leri gösterir, Fake Progress kullanmaz. LAC bileşenleri: Oturum Listesi, PID Listesi, Canlı İzleme Paneli, State Akışı, Workflow İlerleme Göstergesi, Açılır/Kapanır Adım Detayı, Event Akışı, Karar Gerekçesi Paneli, Ajan Seçim Paneli, Servis Durum Paneli, Dijital Varlık Paneli, Log Paneli, Durum Göstergesi, Arşiv Görünümü. LAC; HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanır. LAC yalnızca Yönetici Operasyon Ekranıdır, son kullanıcı tarafından kullanılmaz. Yönetici yalnızca izleyicidir; HLK karar mekanizmasına müdahale edemez. AR-002_59 (LAC Architecture) ile tanımlanmıştır. LAC Event'leri genişleyebilir yapıda olup 14_OLAY_KAYIT_MERKEZI.md içerisinde tanımlanmıştır. Yalnızca Proje Yöneticisinin onayı ile değiştirilebilir. |

---

### REF-UI-001

| Alan | Değer |
|---|---|
| **Asset ID** | `REF-UI-001` |
| **Asset Türü** | Referans UI Tasarımı |
| **Tasarım Adı** | Senaryo Onay Formu Referans Tasarımı |
| **İlgili Workflow** | WF-006 — Scenario Approval |
| **İlgili Feature** | FEAT-007 — Senaryo Üretimi (Senaryo Onay Formu Referans UI) |
| **İlgili State** | `STATE_SCENARIO_APPROVAL` |
| **Dosya Formatı** | PNG |
| **Dosya Adı** | `REFERANS_SENARYO_ONAY_FORMU.png` |
| **Dosya Konumu** | `FORMLAR/REFERANS_SENARYO_ONAY_FORMU.png` |
| **Oluşturulma Tarihi** | 29.06.2026 |
| **Durum** | AKTİF — Resmi Referans Tasarım |
| **Açıklama** | HLK tarafından kullanıcıya sunulacak tüm Senaryo Onay Formlarının resmi referans tasarımıdır. Gelecekte oluşturulacak veya revize edilecek tüm Senaryo Onay Formları bu referans tasarım esas alınarak geliştirilir. Bu referans tasarım yalnızca Proje Yöneticisinin onayı ile değiştirilebilir. |

---

### REF-UI-002

| Alan | Değer |
|---|---|
| **Asset ID** | `REF-UI-002` |
| **Asset Türü** | Referans UI Tasarımı |
| **Tasarım Adı** | Yönetici Fiyatlandırma Formu Referans Tasarımı |
| **İlgili Workflow** | WF-007 — Pricing |
| **İlgili Feature** | FEAT-011 — Yönetici Fiyatlandırma Formu (Yönetici Fiyatlandırma Formu Referans UI) |
| **İlgili State** | `STATE_PRICING` |
| **Dosya Formatı** | PNG |
| **Dosya Adı** | `REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.png` |
| **Dosya Konumu** | `FORMLAR/REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.png` |
| **Oluşturulma Tarihi** | 30.06.2026 |
| **Durum** | AKTİF — Resmi Referans Tasarım |
| **Açıklama** | HLK tarafından yöneticiye sunulacak tüm Yönetici Fiyatlandırma Formlarının resmi referans tasarımıdır. Bu dosya; yönetici fiyatlandırma ekranının resmi tasarım standardıdır, gelecekte yapılacak tüm revizyonların başlangıç noktasıdır, yeni bileşen ekleme, kaldırma ve güncelleme çalışmalarında ana referans olarak kullanılacaktır. HLK, yönetici fiyatlandırma ekranı ile ilgili tüm geliştirmelerde bu referans tasarımı esas alacaktır. Bu referans yalnızca Proje Yöneticisinin onayı ile değiştirilebilir. |

---

### REF-UI-003

| Alan | Değer |
|---|---|
| **Asset ID** | `REF-UI-003` |
| **Asset Türü** | Referans UI Tasarımı |
| **Tasarım Adı** | Kullanıcı Fiyat Teklif Formu Referans Tasarımı |
| **İlgili Workflow** | WF-007 — Pricing |
| **İlgili Feature** | FEAT-012 — Kullanıcı Fiyat Teklif Formu (Kullanıcı Fiyat Teklif Formu Referans UI) |
| **İlgili State** | `STATE_PRICING` |
| **Dosya Formatı** | PNG |
| **Dosya Adı** | `REFERANS_KULLANICI_FİYAT_TEKLİF_FORMU.png` |
| **Dosya Konumu** | `FORMLAR/REFERANS_KULLANICI_FİYAT_TEKLİF_FORMU.png` |
| **Versiyon** | v1.0 |
| **Oluşturulma Tarihi** | 30.06.2026 |
| **Durum** | AKTİF — Resmi Referans Tasarım |
| **Açıklama** | HLK Kullanıcı Fiyat Teklif Formunun resmi referans kullanıcı arayüzüdür. Bu form; Telegram kullanıcı ekranı, mobil telefon ekranı ve masaüstü ekranı uyumluluğu gözetilerek hazırlanmıştır. Bu referans tasarım; renk paleti, kart yapısı, ikon sistemi, tipografi, buton yerleşimi, açılır/kapanır panel yapısı, ödeme kartları, teklif alanı ve kullanıcı etkileşim yapısı için tek resmi referans kabul edilir. Gelecekte bu form üzerinde yapılacak tüm geliştirmeler, revizyonlar ve yeni sürümler bu referans tasarım esas alınarak hazırlanacaktır. Yalnızca Proje Yöneticisi tarafından onaylanan yeni referans tasarım bu kaydın yerine geçebilir. |

---

### REF-UI-004

| Alan | Değer |
|---|---|
| **Asset ID** | `REF-UI-004` |
| **Asset Türü** | Referans UI Tasarımı |
| **Tasarım Adı** | Yönetici Video Üretim Onay Formu Referans Tasarımı |
| **İlgili Workflow** | WF-008 — Video Production |
| **İlgili Feature** | FEAT-013 — Yönetici Video Üretim Onay Formu (Yönetici Video Üretim Onay Formu Referans UI) |
| **İlgili State** | `STATE_VIDEO_PRODUCTION` |
| **Dosya Formatı** | PNG |
| **Dosya Adı** | `REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU.png` |
| **Dosya Konumu** | `FORMLAR/REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU.png` |
| **Versiyon** | v1.0 |
| **Oluşturulma Tarihi** | 01.07.2026 |
| **Durum** | AKTİF — Resmi Referans Tasarım |
| **Açıklama** | Bu tasarım, HLK Video Production başlamadan önce kullanılan resmi Yönetici Video Üretim Onay Formunun tek referans kullanıcı arayüzüdür. Bu form; Video Production başlamadan önce çalışan son yönetici kontrol katmanıdır. Üretim paketini son kez doğrulamak, yanlış üretimi önlemek, gereksiz kredi tüketimini önlemek, üretim güvenliğini sağlamak, üretim referansını oluşturmak ve yöneticinin son kararını almak amacıyla kullanılır. Bu form tamamlanmadan HLK hiçbir şekilde Video Production sürecini başlatamaz. Form onaylandığında HLK tarafından benzersiz bir PID (Production ID) oluşturulur. Oluşturulan PID bu üretimin tek resmi üretim kimliğidir. PID standardı AR-002_57 ile tanımlanmıştır. Yalnızca Proje Yöneticisinin onayı ile değiştirilebilir. |

---
