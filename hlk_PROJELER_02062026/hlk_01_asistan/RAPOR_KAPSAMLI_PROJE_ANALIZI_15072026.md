# HLK AI REKLAM ASİSTANI — KAPSAMLI PROJE ANALİZ RAPORU

**Rapor Tarihi:** 15 Temmuz 2026
**Proje:** HLK_01_asistan (hlk_PROJELER_02062026/HLK_01_asistan)
**Analiz Kapsamı:** Tüm kaynak kod, konfigürasyon, anayasal dokümanlar, veri yapıları, test altyapısı

---

## İÇİNDEKİLER

1. [Proje Kimliği ve Amacı](#1-proje-ki̇mli̇ği̇-ve-amaci)
2. [Dizin Yapısı ve Dosya Envanteri](#2-di̇zi̇n-yapisi-ve-dosya-envanteri̇)
3. [Mimari Analiz](#3-mi̇mari̇-anali̇z)
4. [ANA YASA — Anayasal İşletim Sistemi](#4-ana-yasa--anayasal-i̇şleti̇m-si̇stemi̇)
5. [State Engine ve Sahne Akışı](#5-state-engine-ve-sahne-akişi)
6. [Servis Katmanı Detaylı Analizi](#6-servi̇s-katmani-detayli-anali̇zi̇)
7. [Handler Katmanı](#7-handler-katmani)
8. [Uluslararasılaştırma (i18n) Sistemi](#8-uluslararasilaştirma-i18n-si̇stemi̇)
9. [Harici API Entegrasyonları](#9-hari̇ci̇-api-entegrasyonlari)
10. [Form ve UI Sistemi](#10-form-ve-ui-si̇stemi̇)
11. [Production ve PID Sistemi](#11-production-ve-pi̇d-si̇stemi̇)
12. [Constitution Enforcement (CEE) ve Denetim](#12-constitution-enforcement-cee-ve-denetim)
13. [Test Altyapısı](#13-test-altyapisi)
14. [Güvenlik Değerlendirmesi](#14-güvenli̇k-değerlendi̇rmesi̇)
15. [Güçlü Yönler ve Yenilikçi Yaklaşımlar](#15-güçlü-yönler-ve-yeni̇li̇kçi̇-yaklaşimlar)
16. [İyileştirme Alanları ve Öneriler](#16-i̇yi̇leşti̇rme-alanlari-ve-öneri̇ler)
17. [Sonuç](#17-sonuç)

---

## 1. PROJE KİMLİĞİ VE AMACI

### 1.1 Genel Bakış

| Özellik | Değer |
|---------|-------|
| **Proje Adı** | HLK AI Reklam Asistanı |
| **Proje Dizini** | `hlk_PROJELER_02062026/HLK_01_asistan` |
| **Programlama Dili** | Python 3.14+ |
| **Platform** | Telegram Bot |
| **Framework** | `python-telegram-bot` (v21+) |
| **Botlar** | @hlk01_test_bot (Test), @hlk_reklam_asistani01_bot (Production) |
| **Sahip** | Haluk ARI |

### 1.2 Projenin Amacı

HLK AI Reklam Asistanı, Telegram üzerinden çalışan, **uçtan uca yapay zeka destekli reklam videosu üretim asistanıdır**. Kullanıcıdan aldığı ürün bilgileri, tercihler ve brief ile:

1. Ürün linkini analiz eder
2. Platform, format, çözünürlük, süre gibi teknik parametreleri toplar
3. Tanıtım tarzı, hedef kitle, ses tercihlerini belirler
4. Otomatik senaryo oluşturur
5. Fiyat teklifi sunar
6. Ödeme sonrası AI video üretimini başlatır
7. Üretilen videoyu kullanıcıya teslim eder

### 1.3 Kapsam

Proje **15.000+ satır** Python kodu, **22 anayasal doküman**, **8 dil desteği**, **7+ harici API entegrasyonu**, **6 referans form**, **14+ test dosyası** ve kapsamlı bir üretim altyapısından oluşmaktadır.

---

## 2. DİZİN YAPISI VE DOSYA ENVANTERİ

```
HLK_01_asistan/
├── main.py                     # Ana bot giriş noktası (579 satır)
├── .env                        # Ortam değişkenleri (API anahtarları dahil)
├── testi_baslat.bat            # Windows CMD başlatıcı
├── testi_baslat.ps1            # PowerShell başlatıcı
│
├── config/
│   ├── settings.py             # Merkezi konfigürasyon (50 satır)
│   ├── i18n.py                 # 8 dilli çeviri sistemi (1160 satır)
│   └── video_paths.py          # Video/ses dosya yolu yönetimi (111 satır)
│
├── handlers/
│   ├── __init__.py
│   ├── start.py                # Ana konuşma yönlendirici (1336 satır)
│   ├── website.py              # Tüm sahne handler'ları (2836 satır)
│   └── cancel.py               # İptal komutu (48 satır)
│
├── services/
│   ├── __init__.py
│   ├── scene_engine.py         # Konuşma akış orkestrasyonu (689 satır)
│   ├── scene_delivery.py       # Sahne/video teslimat (439 satır)
│   ├── scene_registry.py       # Sahne tanım kaydı (396 satır)
│   ├── research_orchestrator.py # Ürün araştırma motoru
│   ├── voice_generator.py      # ElevenLabs ses üretimi
│   ├── hedra_generator.py      # Hedra lip-sync video üretimi
│   ├── descript_generator.py   # Descript API entegrasyonu
│   ├── render_service.py       # Puppeteer form render
│   ├── lac.py                  # Live Activity Center
│   ├── constitution_cache.py   # Anayasal önbellek yöneticisi
│   ├── constitution_enforcement.py # Anayasal uyum denetim motoru (CEE)
│   ├── constitution_index.py   # Anayasal kural indeksi
│   ├── olay_kayit_merkezi.py   # Merkezi olay kayıt sistemi
│   ├── pid_runtime.py          # Production ID çalışma zamanı
│   ├── production_executor.py  # Üretim yürütücü
│   ├── production_package_runtime.py # Üretim paketi yönetimi
│   ├── production_runtime.py   # Üretim çalışma zamanı
│   └── execution_event_collector.py # Çalışma olayı toplayıcı (EEC)
│
├── utils/
│   ├── __init__.py
│   ├── state_engine.py         # Durum makinesi motoru
│   ├── session_timeout.py      # Oturum zaman aşımı
│   ├── scene_lock.py           # Sahne erişim kilidi
│   └── validators.py           # Girdi doğrulama
│
├── helpers/
│   └── typewriter_animation.py # Daktilo efekti animasyonu
│
├── ANA YASA/                   # 22 Anayasal doküman
│   ├── 00_HLK_MASTER_RULE_BOOK.md
│   ├── 01_Global_Configuration.md
│   ├── 02_General_Rules.md
│   ├── 03_Architecture_Rules.md
│   ├── 04_Operational_Rules.md
│   ├── 05_Quality_Rules.md
│   ├── 06_Module_Rule.md
│   ├── 07_HLK_STATE_ENGINE.md
│   ├── 08_HLK_FLOW_DIAGRAM.md
│   ├── 09_WORKFLOW_MANIFEST.md
│   ├── 10_FEATURE_REGISTRY.md
│   ├── 11_WORKFLOW_FEATURE_MAP.md
│   ├── 12_DIGITAL_ASSET_ARCHIVE.md
│   ├── 13_DIGITAL_ASSET_CATALOG.md
│   ├── 14_OLAY_KAYIT_MERKEZI.md
│   ├── 15_KARAR_GEREKCESI_STANDARDI.md
│   ├── 16_PRODUCTION_PACKAGE_STANDARD.md
│   ├── 17_SAHNE_KAYIT_DEFTERİ.md
│   ├── 18_CONSTITUTION_DIFF_ENGINE.md
│   ├── 19_CONSTITUTION_SCAN_ENGINE.md
│   ├── 20_TASK_ENGINE.md
│   ├── 21_CONSTITUTION_ENFORCEMENT_ENGINE.md
│   └── 22_EXECUTION_EVENT_COLLECTOR.md
│
├── FORMLAR/                    # Referans formlar ve HTML render
│   ├── REFERANS_Brief_Onay_Formu.png + klasörü
│   ├── REFERANS_SENARYO_ONAY_FORMU.png + klasörü
│   ├── REFERAN_KULLANICI FİYAT_TEKLİF_FORMU.png + klasörü
│   ├── REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.png + klasörü
│   ├── REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU.png + klasörü
│   ├── REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC).png + klasörü
│   └── shared/
│
├── data/
│   ├── enforcement/            # CEE denetim raporları (JSON)
│   ├── production_packages/    # Üretim paketleri
│   ├── pid_runtime.lock        # PID singleton kilidi
│   └── pid_runtime_state.json  # PID durum kaydı
│
├── VİDEO Dosyaları/
│   ├── sahne-1 giriş/          # Karşılama videoları
│   ├── sahne-2/                # Dile özel lip-sync videoları (8 dil)
│   └── sahne-13/               # Brief tamamlandı videoları (8 dil)
│
├── SES Dosyaları/
│   ├── hedra_SAHNE-2/          # SAHNE-2 ses dosyaları
│   ├── hedra_SAHNE-3/          # SAHNE-3 ses dosyaları
│   └── test/                   # Test sesleri
│
├── PROJELER/
│   └── SCENE2_BALLOON_PROTOTYPE/ # Sahne-2 konuşma balonu prototipi
│
├── NOTLAR/                     # Proje notları
├── logs/                       # Log dosyaları
└── *.md raporları              # 15+ detaylı rapor dokümanı
```

### 2.1 Dosya Sayıları

| Kategori | Sayı |
|----------|------|
| Python kaynak dosyası | 38 |
| Anayasal doküman (.md) | 22 |
| Test dosyası | 14 |
| Rapor dokümanı | 15+ |
| Referans form (.png) | 6 |
| HTML template | 4+ |
| Toplam Python satırı | ~15.000+ |

---

## 3. MİMARİ ANALİZ

### 3.1 Mimari Katmanlar

Proje **5 katmanlı** bir mimari üzerine inşa edilmiştir:

```
┌──────────────────────────────────────────────┐
│           TELEGRAM KULLANICI ARAYÜZÜ          │
├──────────────────────────────────────────────┤
│              HANDLER KATMANI                  │
│  start.py (yönlendirme) + website.py (sahne) │
├──────────────────────────────────────────────┤
│              SERVİS KATMANI                   │
│  17 modüler servis (scene, production, vb.)  │
├──────────────────────────────────────────────┤
│              UTILITY KATMANI                  │
│  state_engine, validators, timeout, lock     │
├──────────────────────────────────────────────┤
│              ANAYASAL KATMAN                  │
│  22 ANA YASA dokümanı + CEE + Cache          │
└──────────────────────────────────────────────┘
```

### 3.2 Anayasal Geliştirme Disiplini

Proje benzersiz bir **"Anayasa-Öncelikli Geliştirme"** disiplinine sahiptir:

1. **STATE → Anayasal Referans → Kod → Runtime → Telegram** sıralaması zorunludur
2. Her değişiklik önce ilgili ANA YASA dokümanında başlar
3. Kod hiçbir zaman başlangıç noktası değildir
4. Tüm geliştirmeler anayasal referanslarla doğrulanır

### 3.3 Bot Başlatma Akışı (Constitutional Boot)

Bot başlatıldığında aşağıdaki **18 katmanlı boot sequence** çalışır:

1. **FAZ 0**: Constitution Cache Manager — tüm ANA YASA dosyalarını tara, hash'le, önbellekle
2. **FAZ 1**: 18 Katmanlı Constitutional Boot — her katmanı yükle ve durumunu logla
3. **FAZ 2**: CONSTITUTION_READY kontrolü — tüm katmanlar aktif mi?
4. **CEE PRE-CHECK**: Anayasal görev paketi oluştur ve denetle
5. **EEC**: Bot başlangıç event'ini kaydet
6. **MASTER-003**: send_message monkey-patch ile tam stack trace aktif et

### 3.4 MASTER-003 Trace Sistemi

Her `send_message` çağrısı otomatik olarak trace edilir:
- Zaman damgası
- Mesaj içeriği (ilk 120 karakter)
- Chat ID
- Çağrı kaynağı (dosya, fonksiyon, satır)
- Tam stack trace (son 10 frame)

---

## 4. ANA YASA — ANAYASAL İŞLETİM SİSTEMİ

### 4.1 Genel Yapı

ANA YASA, projenin **değiştirilemez anayasal çerçevesidir**. 22 dokümandan oluşur ve aşağıdaki katmanlara ayrılmıştır:

| # | Doküman | Kategori | İçerik |
|---|---------|----------|--------|
| 00 | MASTER_RULE_BOOK | Temel | Analiz zorunluluğu, çalışma disiplini, MASTER-001/002/003 kuralları |
| 01 | Global_Configuration | Konfigürasyon | GC kuralları, global sabitler, ortam yapılandırması |
| 02 | General_Rules | Kurallar | GENEL_KURAL'lar, oturum yönetimi, hata handling |
| 03 | Architecture_Rules | Mimari | AR kuralları, katmanlar arası iletişim, modül bağımlılıkları |
| 04 | Operational_Rules | Operasyon | OR kuralları, çalışma prensipleri |
| 05 | Quality_Rules | Kalite | Kod kalitesi, test standartları, review süreçleri |
| 06 | Module_Rule | Modül | Modül geliştirme kuralları |
| 07 | STATE_ENGINE | State | SE-007 state tanımları, geçiş kuralları, event sistemi |
| 08 | FLOW_DIAGRAM | Akış | FD-008 tüm sahne akış diyagramları |
| 09 | WORKFLOW_MANIFEST | İş Akışı | WF tanımları ve iş akışı manifestosu |
| 10 | FEATURE_REGISTRY | Özellik | FEAT tanımları ve özellik kaydı |
| 11 | WORKFLOW_FEATURE_MAP | Eşleme | İş akışı-özellik eşleme tablosu |
| 12 | DIGITAL_ASSET_ARCHIVE | Dijital Varlık | Dijital varlık arşiv standardı |
| 13 | DIGITAL_ASSET_CATALOG | Katalog | Dijital varlık kataloğu |
| 14 | OLAY_KAYIT_MERKEZI | Olay | Merkezi olay kayıt sistemi standardı |
| 15 | KARAR_GEREKCESI_STANDARDI | Karar | Karar gerekçesi format standardı |
| 16 | PRODUCTION_PACKAGE_STANDARD | Üretim | Üretim paketi yapı standardı |
| 17 | SAHNE_KAYIT_DEFTERİ | Sahne | Sahne kayıt defteri standardı |
| 18 | CONSTITUTION_DIFF_ENGINE | Diff | Anayasa değişiklik takip motoru |
| 19 | CONSTITUTION_SCAN_ENGINE | Tarama | Anayasa tarama motoru |
| 20 | TASK_ENGINE | Görev | Görev motoru tanımı |
| 21 | CONSTITUTION_ENFORCEMENT_ENGINE | CEE | Anayasal uyum denetim motoru |
| 22 | EXECUTION_EVENT_COLLECTOR | EEC | Çalışma olayı toplama standardı |

### 4.2 Referans ID Sistemi

Tüm kurallar, sahneler, akışlar ve özellikler benzersiz referans ID'leri ile tanımlanır:

- **MASTER-XXX**: Ana kurallar (MASTER-001, MASTER-002, MASTER-003)
- **GC-XXX**: Global konfigürasyon kuralları
- **GENEL_KURAL_X**: Genel operasyonel kurallar
- **AR-XXX_XX**: Mimari kurallar (AR-002_28, AR-002_36, vb.)
- **OR-XXX_X**: Operasyonel kurallar
- **SE-007_X**: State Engine kuralları
- **FD-008_X**: Flow Diagram referansları
- **WF-XXX**: Workflow tanımları
- **FEAT-XXX**: Feature/Özellik tanımları

---

## 5. STATE ENGINE VE SAHNE AKIŞI

### 5.1 State Makinesi Mimarisi

State Engine (`utils/state_engine.py`), kullanıcı konuşma durumlarını yöneten merkezi bir durum makinesidir:

```
SE-007 State Modeli:
┌──────────────────────────────────────┐
│          USER STATES (18 Adet)        │
├──────────────────────────────────────┤
│ STATE_START                          │
│ STATE_LANGUAGE_SELECTION             │
│ STATE_PRODUCT_LINK                   │
│ STATE_MATERIAL_UPLOAD                │
│ STATE_PLATFORM_SELECTION             │
│ STATE_FORMAT_SELECTION               │
│ STATE_RESOLUTION_SELECTION           │
│ STATE_DURATION_SELECTION             │
│ STATE_STYLE_SELECTION                │
│ STATE_AUDIENCE_SELECTION             │
│ STATE_AUDIO_SELECTION                │
│ STATE_VOICE_LANGUAGE                 │
│ STATE_VOICE_CHARACTER                │
│ STATE_EMPHASIS                       │
│ STATE_BRIEF_APPROVAL                 │
│ STATE_SCENARIO_APPROVAL              │
│ STATE_PRICING                        │
│ STATE_PAYMENT                        │
│ STATE_PAYMENT_VERIFICATION           │
│ STATE_VIDEO_PRODUCTION               │
│ STATE_COMPLETED                      │
└──────────────────────────────────────┘
```

### 5.2 13 Sahnelik Akış (FD-008)

```
SAHNE-01: Dil Seçimi + Karşılama
    │
    ▼
SAHNE-02: Ürün Linki / Platform Seçimi
    │
    ▼
SAHNE-03: Video Formatı Seçimi (9:16 / 16:9 / 1:1)
    │
    ▼
SAHNE-04: Çözünürlük Seçimi (480p / 720p / 1080p)
    │
    ▼
SAHNE-05: Video Süresi (4-30 sn veya HLK'ya Bırak)
    │
    ▼
SAHNE-06: Tanıtım Tarzı (UGC / Geleneksel / Sinematik / Kendi / HLK)
    │
    ▼
SAHNE-07: Hedef Kitle (8 yaş grubu)
    │
    ▼
SAHNE-08: Ses Tercihleri (Seslendirme / Ortam / Müzik / Sessiz)
    │
    ▼
SAHNE-09: Seslendirme Dili (8 dil + özel dil)
    │
    ▼
SAHNE-10: Ses Karakteri (Kadın / Erkek / Çocuk)
    │
    ▼
SAHNE-11: Vurgulanacak Detaylar (İndirim / Kargo / Hediye / vb.)
    │
    ▼
SAHNE-12: Brief Onay Formu (Önizleme + Düzeltme)
    │
    ▼
SAHNE-13: Brief Tamamlandı → Senaryo → Fiyat → Ödeme → Üretim
```

### 5.3 Kullanıcı Deneyimi Detayları

Her sahne geçişinde:
- **Ekran temizleme**: Önceki butonlar silinir
- **Konuşma balonları**: Bilgilendirici metinler
- **Daktilo efekti**: Metin animasyonu (`helpers/typewriter_animation.py`)
- **Inline butonlar**: Telegram inline keyboard
- **State güncellemesi**: `state_engine` üzerinden state geçişi
- **Timeout**: Her sahnede oturum zaman aşımı kontrolü

---

## 6. SERVİS KATMANI DETAYLI ANALİZİ

### 6.1 Scene Engine (`services/scene_engine.py` — 689 satır)

Konuşma akışının orkestrasyonunu yönetir. Her sahne için:
- Sahne başlangıç mantığı
- Buton oluşturma
- Kullanıcı girdisi işleme
- Sonraki sahneye geçiş

### 6.2 Scene Delivery (`services/scene_delivery.py` — 439 satır)

Telegram'a sahne içeriği teslimatını yönetir:
- Video gönderme (file_id önbellekleme)
- Fotoğraf + caption gönderme
- Buton mesajları
- Ekran temizleme (önceki mesajları silme)
- Delivery status takibi (PENDING, SENT, FAILED)

### 6.3 Scene Registry (`services/scene_registry.py` — 396 satır)

Tüm sahnelerin merkezi kaydı:
- Her sahne için button tanımları
- Sahne geçiş kuralları
- State-Sahne eşlemesi
- `get_scene_for_state()` fonksiyonu

### 6.4 Research Orchestrator (`services/research_orchestrator.py`)

Ürün linkinden araştırma yapar:
- URL doğrulama
- Web scraping / içerik çıkarma
- Ürün bilgisi analizi
- Marka, ürün adı, kategori tespiti

### 6.5 Voice Generator (`services/voice_generator.py`)

ElevenLabs API ile ses üretimi:
- Çok dilli TTS desteği
- Ses klonlama
- Ses karakter profilleri (AHU sesi)
- Kalite parametreleri

### 6.6 Hedra Generator (`services/hedra_generator.py`)

Hedra API ile lip-sync video üretimi:
- Karakter görseli + ses → konuşan avatar videosu
- Asset yükleme ve yönetme
- Generation job takibi
- Video indirme

5 farklı versiyonu (`_hedra_runner.py` - `_hedra_v5_runner.py`), API endpoint'lerindeki değişikliklere adaptasyonu gösterir.

### 6.7 Live Activity Center — LAC (`services/lac.py`)

FEAT-015: Canlı aktivite merkezi:
- Kullanıcı aktivite akışı
- Telegram HTML formatında panel
- Olay Kayıt Merkezi ile entegrasyon
- PID bazlı filtreleme

### 6.8 Constitution Cache (`services/constitution_cache.py`)

Anayasal önbellek yöneticisi:
- Tüm ANA YASA dosyalarını tara
- Hash tabanlı değişiklik tespiti
- 18 katmanlı boot manifest'i oluşturma
- `is_valid()` ile CONSTITUTION_READY kontrolü
- Telegram HTML durum paneli

### 6.9 Render Service (`services/render_service.py`)

Puppeteer ile HTML form render:
- Referans form şablonlarını PNG'e render etme
- `template.html` + `sample-data.json` + `render.js` işleme

### 6.10 Olay Kayıt Merkezi (`services/olay_kayit_merkezi.py`)

14_OLAY_KAYIT_MERKEZI standardına uygun:
- Tüm sistem olaylarının merkezi kaydı
- EEC entegrasyonu
- Event filtreleme ve sorgulama

---

## 7. HANDLER KATMANI

### 7.1 start.py (1336 satır)

Ana konuşma yönlendiricisi:
- `start_handler`: /start komutu — dil seçimi ve karşılama
- `button_handler`: Dil seçimi callback'leri (`lang_`)
- `message_handler`: **SE-007_3** uyumlu state tabanlı mesaj yönlendirme
  - Her state için ayrı işleme mantığı
  - Metin, fotoğraf, video, doküman mesajları
- `handle_devam_button`: DEVAM butonu işleme
- `handle_format_selection`: Format seçimi (scout modu)
- `handle_duration_hlk`: "HLK'ya Bırak" süre seçimi
- `validate_language_support`: Dil desteği doğrulama (AR-002_37)

### 7.2 website.py (2836 satır)

Tüm sahne callback handler'ları:
- `handle_material_choice`: Materyal yükleme/seçme
- `handle_platform_selection`: Platform seçimi
- `handle_format_selection`: Format seçimi
- `handle_resolution_selection`: Çözünürlük seçimi
- `handle_audio_toggle` / `handle_audio_devam`: Ses toggle ve devam
- `handle_style_selection`: Tanıtım tarzı
- `handle_audience_selection`: Hedef kitle
- `handle_voice_language`: Seslendirme dili
- `handle_voice_character`: Ses karakteri
- `handle_emphasis` / `handle_emphasis_done`: Vurgulama
- `handle_scenario_approve` / `handle_scenario_reject`: Senaryo onay/ret
- `handle_pricing_approve` / `handle_pricing_reject`: Fiyat onay/ret
- `handle_payment_declared` / `handle_payment_cancel`: Ödeme bildirim/iptal
- `handle_admin_pricing_submit`: Yönetici fiyatlandırma
- `handle_admin_payment_approve` / `handle_admin_payment_ret`: Yönetici ödeme onay
- `handle_brief_approve` / `handle_brief_edit` / `handle_brief_edit_field`: Brief yönetimi

### 7.3 cancel.py (48 satır)

`/cancel` komutu: Oturum temizleme, timer iptali, state sıfırlama.

---

## 8. ULUSLARARASILAŞTIRMA (i18n) SİSTEMİ

### 8.1 Desteklenen Diller

| Kod | Dil | Kapsam |
|-----|-----|--------|
| TR | Türkçe | Tam (fallback) |
| EN | İngilizce | Tam |
| DE | Almanca | Tam |
| FR | Fransızca | Kısmi |
| ES | İspanyolca | Kısmi |
| AR | Arapça | Kısmi |
| RU | Rusça | Kısmi |
| KR | Kürtçe (Kurmanci) | Kısmi |

### 8.2 i18n Mimarisi

- **1160 satır** merkezi çeviri dosyası
- **19 bölüm**: Her sahne ve form için ayrı çeviri grupları
- `t(key, lang)` fonksiyonu: `"s03.title"` formatında key ile çeviri
- Otomatik TR fallback (geçersiz dil durumunda)
- `get_lang(user_data)`: Kullanıcı dilini session'dan okur

### 8.3 Çeviri Kapsamı

| Bölüm | Açıklama | Anahtar Sayısı |
|-------|----------|----------------|
| S03-S13 | Sahne metinleri | ~100+ |
| COMMON | Ortak butonlar/mesajlar | ~10 |
| PRICING | Fiyat teklif formu | ~25 |
| PAYMENT | Ödeme kartı | ~15 |
| ADMIN_PAYMENT | Yönetici ödeme bildirimi | ~15 |
| FINAL | Final mesajları | ~10 |
| MATERIAL | Materyal mesajları | ~5 |
| PLATFORM | Platform seçimi | ~3 |
| LINK | Link/araştırma mesajları | ~5 |
| SCENARIO | Senaryo onay formu | ~30 |

---

## 9. HARİCİ API ENTEGRASYONLARI

### 9.1 Entegrasyon Haritası

```
┌─────────────────────────────────────────────────────────┐
│                   HLK AI REKLAM ASİSTANI                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐            │
│  │ ElevenLabs│  │  Hedra    │  │ Descript │            │
│  │ (TTS)    │  │ (Lip-Sync)│  │ (Video)  │            │
│  └──────────┘  └───────────┘  └──────────┘            │
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐            │
│  │ Higgsfield│  │  Kie AI   │  │  Fal.ai  │            │
│  │ (Video)  │  │ (Görsel)  │  │ (Img2Vid)│            │
│  └──────────┘  └───────────┘  └──────────┘            │
│                                                         │
│  ┌──────────┐  ┌───────────┐                           │
│  │ OpenAI   │  │   TCMB    │                           │
│  │ (TTS)    │  │ (Döviz)   │                           │
│  └──────────┘  └───────────┘                           │
│                                                         │
│  ┌──────────────────────────┐                          │
│  │   Telegram Bot API       │                          │
│  └──────────────────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

### 9.2 API Detayları

| API | Kullanım | API Key Durumu |
|-----|----------|---------------|
| **Telegram** | Bot iletişimi, medya gönderimi | `.env`'de 2 token (test + prod) |
| **ElevenLabs** | Ses üretimi (TTS) | Aktif |
| **Hedra** | Lip-sync karakter videosu | Aktif, 5 versiyon adaptasyon |
| **Descript** | Video/ses düzenleme, sentetik ses | Aktif |
| **Higgsfield AI** | AI video üretimi | Aktif |
| **Kie AI** | Görsel üretimi | Aktif |
| **Fal.ai** | Seedance image-to-video | Aktif |
| **OpenAI** | TTS (yedek) | Aktif |
| **TCMB** | Döviz kuru (fiyat teklifinde TL karşılığı) | Ücretsiz |

---

## 10. FORM VE UI SİSTEMİ

### 10.1 Referans Form Mimarisi

FORMLAR dizini iki katmanlı bir mimari kullanır:

1. **Referans UI** (`.png` dosyaları): Proje Yöneticisi tarafından onaylanan değiştirilemez görsel standart
2. **Çalışan UI** (HTML/JS klasörleri): Referans UI'ın platforma uyarlanmış uygulaması

### 10.2 Form Listesi

| Form | PNG Boyutu | Amaç |
|------|-----------|------|
| Brief Onay Formu | 1.4 MB | Kullanıcının tüm seçimlerini önizleme ve onaylama |
| Senaryo Onay Formu | 1.5 MB | AI tarafından üretilen senaryonun onayı |
| Kullanıcı Fiyat Teklif Formu | 1.4 MB | Fiyat teklifinin kullanıcıya sunumu |
| Yönetici Fiyatlandırma Formu | 1.3 MB | Admin fiyat belirleme arayüzü |
| Yönetici Video Üretim Onay Formu | 1.3 MB | Admin video prodüksiyon onayı |
| HLK Live Activity Center | 1.6 MB | Canlı aktivite izleme paneli |

### 10.3 Puppeteer Render

Her form klasörü şunları içerir:
- `template.html`: Form şablonu
- `sample-data.json`: Örnek veri
- `render.js`: Puppeteer render scripti

`services/render_service.py` bu şablonları kullanarak dinamik olarak form görüntüleri üretir.

---

## 11. PRODUCTION VE PID SİSTEMİ

### 11.1 PID Runtime

Her üretim işlemine benzersiz bir **Production ID (PID)** atanır:

```
PID Formatı: PID-YYYYMMDD-NNNN
Örnek: PID-20260715-0001

Yapı:
  - PID: Prefix (gc_prefix)
  - 20260715: Tarih
  - 0001: Günlük sayaç (gc_sequence_length = 4)
```

### 11.2 PID Özellikleri

- **Singleton zorlaması**: `pid_runtime.lock` dosyası ile aynı anda tek PID aktif
- **Durum kalıcılığı**: `pid_runtime_state.json` ile tüm PID'ler kaydedilir
- **Günlük sayaç**: Her gün sıfırlanan sayaç (20260713: 1, 20260714: 2, 20260715: 1)
- **Aktif/Pasif durumu**: Her PID `is_active` flag'i taşır

### 11.3 Production Executor

`services/production_executor.py`:
- Üretim iş akışını başlatır
- CEE denetimi sonrası üretime geçer
- PID ataması yapar
- Production package oluşturur

### 11.4 Production Package Runtime

`services/production_package_runtime.py`:
- 16_PRODUCTION_PACKAGE_STANDARD uyumlu paket yönetimi
- Paket oluşturma, arşivleme, durum takibi

---

## 12. CONSTITUTION ENFORCEMENT (CEE) VE DENETİM

### 12.1 CEE Mimarisi

Constitution Enforcement Engine (CEE), **6 boyutlu** anayasal uyum denetimi yapar:

```
CEE Denetim Boyutları:
┌─────────────────────────────────────┐
│ 1. code_anayasa_check               │
│    Kod ↔ Anayasa uyumu              │
├─────────────────────────────────────┤
│ 2. flow_compliance                  │
│    Flow Diagram uyumu               │
├─────────────────────────────────────┤
│ 3. state_compliance                 │
│    State Engine uyumu               │
├─────────────────────────────────────┤
│ 4. operational_compliance           │
│    Operational Rules uyumu          │
├─────────────────────────────────────┤
│ 5. architectural_integrity          │
│    Mimari bütünlük                  │
├─────────────────────────────────────┤
│ 6. runtime_behavior                 │
│    Çalışma zamanı davranışı         │
└─────────────────────────────────────┘
```

### 12.2 CEE Rapor Formatı

Her denetim JSON formatında kaydedilir (`data/enforcement/CEE-*.json`):

```json
{
  "report_id": "CEE-20260715-08FE",
  "verdict": "PASS" | "FAIL",
  "attempt": 2,
  "deficiencies": [],
  "violations": [],
  "justification": {
    "DecisionID": "DEC-...",
    "ConfidenceLevel": "HIGH",
    "DecisionOutcomes": [...]
  }
}
```

### 12.3 Karar Gerekçesi Standardı (15_KARAR_GEREKCESI_STANDARDI)

Her CEE kararı şu alanları içermek zorundadır:
- DecisionID, DecisionName, DecisionDescription
- DecisionMaker, DecisionTimestamp
- SourceState, WorkflowID, FeatureID
- Justifications (gerekçeler listesi)
- Alternatives (alternatifler)
- ConfidenceLevel (HIGH/MEDIUM/LOW)
- DecisionOutcomes (sonuçlar)

---

## 13. TEST ALTYAPISI

### 13.1 Test Dosyaları (14 adet)

| Test Dosyası | Kapsam | Satır |
|-------------|-------|-------|
| `test_banka_karti.py` | Banka ödeme kartı görüntüsü | ~50 |
| `test_constitution_enforcement.py` | CEE denetim motoru | ~250 |
| `test_fiyat_teklif.py` | Fiyat teklif formu | ~70 |
| `test_i18n_check.py` | i18n dil kontrolleri | ~80 |
| `test_kullanici_fiyat.py` | Kullanıcı fiyat akışı | ~100 |
| `test_odeme_bildirim.py` | Ödeme bildirim akışı | ~120 |
| `test_odeme_karti.py` | Ödeme kartı render | ~60 |
| `test_photo_inline.py` | Fotoğraf inline gönderimi | ~150 |
| `test_pid_multiprocess.py` | PID çoklu proses testi | ~140 |
| `test_production_executor.py` | Production executor | ~400 |
| `test_production_package_runtime.py` | Package runtime | ~330 |
| `test_production_runtime.py` | Production runtime | ~300 |
| `test_sahne12.py` | SAHNE-12 brief onay | ~90 |
| `test_sahne13.py` | SAHNE-13 brief tamamlandı | ~120 |
| `test_yonetici_fiyat.py` | Yönetici fiyatlandırma | ~250 |

### 13.2 Test Yaklaşımı

- Testler Telegram bot'una gerçek API çağrıları yapmaz
- Mock ve simülasyon kullanılmaz
- Testler doğrudan servis fonksiyonlarını çağırır
- Her test bağımsız çalıştırılabilir
- `if __name__ == "__main__"` pattern'i ile hem import hem direkt çalıştırma

---

## 14. GÜVENLİK DEĞERLENDİRMESİ

### 14.1 Bulgular

| Risk | Şiddet | Açıklama |
|------|--------|----------|
| **.env dosyasında API anahtarları** | ⚠️ YÜKSEK | Tüm API anahtarları (ElevenLabs, Hedra, OpenAI, Fal.ai, Descript, Higgsfield) düz metin olarak `.env` dosyasında saklanıyor. Bu dosya repoya commit edilmiş durumda. |
| **Production token'ı repoda** | ⚠️ YÜKSEK | Production bot token'ı (8866104400:...) repoda görünür durumda |
| **ALLOWED_USERS=*** | ⚠️ ORTA | Tüm kullanıcılar bot'a erişebilir |
| **Hata mesajlarında bilgi sızıntısı** | ⚠️ DÜŞÜK | `error_handler` ham hataları log'a yazıyor |
| **API anahtarları kod içinde** | ⚠️ DÜŞÜK | Hedra runner dosyalarında hardcoded asset ID'leri var |

### 14.2 Öneriler

1. `.env` dosyası `.gitignore`'a eklenmeli
2. Production token'ı rotate edilmeli
3. `.env.example` oluşturulmalı (zaten mevcut: `hlk_PROJELER_02062026/.env.example`)
4. API anahtarları için secret manager kullanımı değerlendirilmeli

---

## 15. GÜÇLÜ YÖNLER VE YENİLİKÇİ YAKLAŞIMLAR

### 15.1 Mimari İnovasyonlar

1. **Anayasal İşletim Sistemi**: 22 dokümanlık ANA YASA ile codebase'den bağımsız, değiştirilemez kurallar bütünü
2. **Constitutional Boot Sequence**: Bot başlangıcında 18 katmanlı anayasa yükleme ve doğrulama
3. **CEE (Constitution Enforcement Engine)**: 6 boyutlu otomatik anayasal uyum denetimi
4. **EEC (Execution Event Collector)**: Merkezi olay toplama ve izleme
5. **MASTER-003 Trace**: Her send_message'un tam stack trace ile loglanması
6. **Karar Gerekçesi Standardı**: Her önemli kararın yapılandırılmış gerekçelendirme formatı

### 15.2 Teknik Güçlü Yönler

1. **8 dil desteği**: Kapsamlı i18n altyapısı (1160 satır)
2. **13 sahnelik akış**: Kullanıcıyı adım adım yönlendiren kompleks konuşma tasarımı
3. **Referans UI / Çalışan UI ayrımı**: Tasarım ve uygulama katmanlarının net ayrımı
4. **PID sistemi**: Production ID ile iş takibi ve singleton zorlaması
5. **15+ rapor**: Detaylı proje dokümantasyonu
6. **5 Hedra API adaptasyonu**: API değişikliklerine karşı esneklik
7. **Monkey-patch trace**: Debugging için yenilikçi yaklaşım

### 15.3 Operasyonel Güçlü Yönler

1. **Çift bot yapısı**: Test (@hlk01_test_bot) ve Production (@hlk_reklam_asistani01_bot) ayrı
2. **Environment-based token seçimi**: `ENV=test` ile otomatik test token'ı
3. **PowerShell + CMD başlatıcı**: Her iki platform için başlatma scriptleri
4. **Drop pending updates**: Bot başlangıcında eski güncellemelerin temizlenmesi
5. **Timeout yönetimi**: Her sahnede oturum zaman aşımı ve otomatik temizlik

---

## 16. İYİLEŞTİRME ALANLARI VE ÖNERİLER

### 16.1 Mimari Öneriler

| Öneri | Öncelik | Açıklama |
|-------|---------|----------|
| Asenkron HTTP client | ORTA | `requests` (senkron) yerine `httpx` veya `aiohttp` kullanımı |
| Dependency injection | DÜŞÜK | Servisler arası bağımlılıkların daha gevşek olması |
| Circuit breaker | ORTA | Harici API çağrılarında hata toleransı |

### 16.2 Kod Kalitesi

| Öneri | Öncelik | Açıklama |
|-------|---------|----------|
| Type hint'lerin tamamlanması | ORTA | Bazı servislerde eksik tip belirteçleri |
| Docstring standardizasyonu | DÜŞÜK | Tüm fonksiyonlara Google/NumPy style docstring |
| Test coverage artırımı | ORTA | Mevcut testler fonksiyonel, birim test coverage düşük |
| Log seviyesi ayarları | DÜŞÜK | Bazı yerlerde INFO yerine DEBUG kullanımı |

### 16.3 Güvenlik

| Öneri | Öncelik | Açıklama |
|-------|---------|----------|
| `.env` gitignore | ⚠️ ACİL | API anahtarlarının repodan çıkarılması |
| Token rotasyonu | ⚠️ ACİL | Production token'ının değiştirilmesi |
| Input validasyonu | ORTA | Kullanıcı girdilerinde daha sıkı doğrulama |
| Rate limiting | DÜŞÜK | API çağrılarında rate limiting |

### 16.4 Operasyonel

| Öneri | Öncelik | Açıklama |
|-------|---------|----------|
| Docker container | ORTA | Taşınabilir deployment |
| CI/CD pipeline | ORTA | Otomatik test ve deployment |
| Monitoring/Alerting | DÜŞÜK | Bot sağlığı için izleme |
| Backup stratejisi | DÜŞÜK | Veri ve state yedekleme |

### 16.5 i18n

| Öneri | Öncelik | Açıklama |
|-------|---------|----------|
| Eksik çeviriler | ORTA | FR, ES, AR, RU, KR dillerinde bazı metinler eksik |
| Çeviri dosyası ayırma | DÜŞÜK | 1160 satırlık tek dosya yerine dil başına JSON |
| Profesyonel çeviri | DÜŞÜK | Google Translate yerine native speaker review |

---

## 17. SONUÇ

### 17.1 Genel Değerlendirme

HLK AI Reklam Asistanı, **benzersiz bir anayasal mimari** üzerine inşa edilmiş, **15.000+ satırlık** kapsamlı bir Telegram bot projesidir. Proje:

- **Yenilikçi** bir "Constitution-First" geliştirme yaklaşımı benimsemiştir
- **8 dilde** hizmet verebilen kompleks bir konuşma akışına sahiptir
- **7+ harici API** ile entegredir
- **6 boyutlu otomatik denetim** mekanizması ile kod kalitesini güvence altına alır
- **Uçtan uca** reklam videosu üretim sürecini yönetir

### 17.2 Olgunluk Seviyesi

| Boyut | Seviye | Not |
|-------|--------|-----|
| Mimari Tasarım | ⭐⭐⭐⭐⭐ | Olağanüstü — Anayasal sistem benzersiz |
| Kod Organizasyonu | ⭐⭐⭐⭐ | İyi — Modüler ama bazı büyük dosyalar var |
| Dokümantasyon | ⭐⭐⭐⭐⭐ | Mükemmel — 22 anayasa + 15+ rapor |
| Test Kapsamı | ⭐⭐⭐ | Orta — Fonksiyonel testler var, birim test eksik |
| Güvenlik | ⭐⭐ | Geliştirilmeli — API anahtarları repoda |
| i18n | ⭐⭐⭐⭐ | İyi — 8 dil, bazı çeviriler eksik |
| Hata Yönetimi | ⭐⭐⭐⭐ | İyi — Trace sistemi ve loglama güçlü |
| Ölçeklenebilirlik | ⭐⭐⭐ | Orta — Monolitik yapı, servis ayrımı başlamış |

### 17.3 Nihai Değerlendirme

HLK AI Reklam Asistanı, **tek kişilik bir ekip tarafından** geliştirilmiş olmasına rağmen, kurumsal ölçekte bir yazılım projesinin tüm katmanlarını barındırmaktadır. Anayasal mimari yaklaşımı, özellikle AI/LLM destekli geliştirme süreçlerinde tutarlılığı sağlamak için yenilikçi bir çözümdür.

Proje, **üretim kalitesinde** bir Telegram bot'u olarak çalışmakta ve gerçek kullanıcılara hizmet vermeye hazır durumdadır. Güvenlik iyileştirmeleri (API anahtarı yönetimi) ve test kapsamının artırılması ile kurumsal kullanıma tamamen hazır hale gelecektir.

---

**Raporu Hazırlayan:** Claude Code (DeepSeek V4 Pro)
**Analiz Tarihi:** 15 Temmuz 2026
**Toplam İncelenen Dosya:** 50+
**Analiz Süresi:** Kapsamlı derinlemesine inceleme
