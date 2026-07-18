# HLK AI REKLAM ASİSTANI — KAPSAMLI PROJE İNCELEME RAPORU

**Rapor Tarihi:** 13 Temmuz 2026
**Proje:** HLK_01_asistan (hlk_PROJELER_02062026)
**İnceleme Kapsamı:** Tam proje (kod, mimari, anayasal sistem, formlar, testler, raporlar)
**Metodoloji:** 4 paralel araştırma agent'ı + doğrudan kod incelemesi

---

## İÇİNDEKİLER

1. [Proje Kimliği ve Amacı](#1-proje-kimliği-ve-amacı)
2. [Dizin Yapısı ve Dosya Envanteri](#2-dizin-yapısı-ve-dosya-envanteri)
3. [Mimari Katmanlar](#3-mimari-katmanlar)
4. [State Machine ve Scene Management](#4-state-machine-ve-scene-management)
5. [Kullanıcı Akışı (SAHNE-01 → SAHNE-13)](#5-kullanıcı-akışı)
6. [Handler Analizi](#6-handler-analizi)
7. [Servis Katmanı Analizi](#7-servis-katmanı-analizi)
8. [ANA YASA — Anayasal İşletim Sistemi](#8-ana-yasa--anayasal-i̇şletim-sistemi)
9. [FORMLAR — Referans UI Sistemi](#9-formlar--referans-ui-sistemi)
10. [Çoklu Dil Desteği (i18n)](#10-çoklu-dil-desteği-i18n)
11. [Harici API Entegrasyonları](#11-harici-api-entegrasyonları)
12. [Test Altyapısı](#12-test-altyapısı)
13. [Kod Kalitesi Değerlendirmesi](#13-kod-kalitesi-değerlendirmesi)
14. [Raporlar ve Uyumluluk Durumu](#14-raporlar-ve-uyumluluk-durumu)
15. [Güçlü Yönler](#15-güçlü-yönler)
16. [Eksiklikler ve İyileştirme Alanları](#16-eksiklikler-ve-i̇yileştirme-alanları)
17. [Özet Metrikler](#17-özet-metrikler)
18. [Sonuç ve Öneriler](#18-sonuç-ve-öneriler)

---

## 1. PROJE KİMLİĞİ VE AMACI

| Özellik | Değer |
|---|---|
| **Proje Adı** | HLK AI Reklam Asistanı (HLK AI Advertising Assistant) |
| **Ana Dizin** | `hlk_PROJELER_02062026/hlk_01_asistan/` |
| **Platform** | Telegram Bot |
| **Programlama Dili** | Python 3.14 |
| **Framework** | python-telegram-bot v21+ |
| **Çalışma Modu** | Long-polling (webhook kullanmaz) |
| **Prodüksiyon Botu** | @hlk_reklam_asistani01_bot |
| **Test Botu** | @hlk01_test_bot |
| **Toplam Commit** | 7 (tamamı haluk4365 tarafından) |
| **Geliştirme Dönemi** | Mayıs — Temmuz 2026 |

**Temel Amaç:** Kullanıcıların ürünleri için AI destekli reklam videoları üretmek. Kullanıcıdan ürün linki, platform, format, çözünürlük, süre, tanıtım tarzı, hedef kitle, ses tercihleri gibi bilgileri toplayarak reklam videosu üretim sürecini yönetir.

---

## 2. DİZİN YAPISI VE DOSYA ENVANTERİ

### 2.1 Ana Dizin Yapısı

```
hlk_01_asistan/
├── main.py                         (578 satır) — Ana bot giriş noktası
├── .env                            — Ortam değişkenleri & API anahtarları
│
├── ANA YASA/                       — 23 belgelik anayasal sistem (~872 KB)
├── handlers/                       — Telegram bot handler'ları (3 dosya)
│   ├── start.py                    (1,226 satır) — /start, dil, SAHNE-1/2
│   ├── website.py                  (2,531 satır) — SAHNE-02…13 + fiyatlandırma
│   └── cancel.py                   (49 satır) — /cancel işlemi
│
├── services/                       — İş mantığı servis katmanı (16 modül)
│   ├── scene_registry.py           — FD-008_1 sahne tanımları
│   ├── scene_engine.py             — AR-002_28 Conversation Scene Engine
│   ├── scene_delivery.py           — AR-002_36 sahne teslim modülü
│   ├── voice_generator.py          — AHU Voice Generator (ElevenLabs TTS)
│   ├── research_orchestrator.py    — AR-002 ürün araştırma
│   ├── hedra_generator.py          — Hedra API lip-sync video
│   ├── descript_generator.py       — Descript API TTS
│   ├── constitution_cache.py       — Anayasal Cache Manager (SHA-256)
│   ├── constitution_enforcement.py — CEE: Constitution Enforcement Engine
│   ├── constitution_index.py       — Generic Constitutional Rule Index
│   ├── execution_event_collector.py— EEC: Execution Event Collector
│   ├── olay_kayit_merkezi.py       — Olay Kayıt Merkezi (Event Registry)
│   ├── lac.py                      — LAC: Live Activity Center
│   ├── render_service.py           — Referans Form PNG render (Puppeteer)
│   └── __init__.py
│
├── utils/                          — Yardımcı araçlar (4 modül)
│   ├── state_engine.py             (641 satır) — State Machine (SE-007)
│   ├── scene_lock.py               — AR-002_44 SAHNE-1 kilit mekanizması
│   ├── session_timeout.py          — GENEL_KURAL_1 zaman aşımı
│   └── validators.py               — URL ve kullanıcı ID validasyonu
│
├── helpers/                        — Yardımcılar
│   └── typewriter_animation.py     — Daktilo yazı efekti
│
├── config/                         — Konfigürasyon (3 modül)
│   ├── settings.py                 — Merkezi ayarlar
│   ├── i18n.py                     (895 satır) — 8 dil desteği
│   └── video_paths.py              — Merkezi video path yapılandırması
│
├── FORMLAR/                        — Referans UI formları
│   ├── REFERANS_Brief_Onay_Formu/
│   ├── REFERANS_SENARYO_ONAY_FORMU/
│   ├── REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC)/
│   ├── REFERAN_KULLANICI FİYAT_TEKLİF_FORMU/
│   ├── REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU/
│   ├── REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU/
│   └── shared/ (base.css + render-common.js)
│
├── VİDEO Dosyaları/                — Sahne videoları
├── SES Dosyaları/                  — Ses dosyaları
├── FOTOGRAF Dosyaları/             — Fotoğraf dosyaları
├── logs/                           — Bot log dizini
│
├── test_*.py                       — 10 test script'i
├── _hedra_runner*.py               — 5 Hedra test script'i
├── testi_baslat.bat / .ps1         — Test başlatma komutları
└── *.md                            — Proje raporları (~15 adet)
```

### 2.2 Sayısal Envanter

| Metrik | Değer |
|---|---|
| Python dosyası | 48 |
| Toplam Python kodu | ~14,621 satır |
| Markdown dosyası (toplam) | 74 |
| Markdown dokümantasyonu | ~1.29 MB |
| ANA YASA belgesi | 23 |
| Handler dosyası | 3 |
| Servis modülü | 16 |
| En büyük dosya | `handlers/website.py` (2,531 satır) |

---

## 3. MİMARİ KATMANLAR

### 3.1 Katmanlı Mimari

Proje **Anayasal İşletim Sistemi (Constitutional Operating System)** adı verilen benzersiz bir mimariye sahiptir:

```
                         ┌─────────────────────────┐
                         │   ANA YASA (Anayasa)     │
                         │  00_HLK_MASTER_RULE_BOOK  │
                         │  23 .md belge, ~872 KB    │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
    │ Constitution Cache │  │ Constitution Index│  │  CEE (Enforcement │
    │ (SHA-256 hash)     │  │ (Rule ayrıştırma) │  │   Engine)         │
    │ 18 katman Boot     │  │ Generic Validator │  │   PRE/POST-CHECK  │
    └────────────────────┘  └────────────────────┘  └────────────────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
          ┌─────────▼─────────┐ ┌────▼──────┐ ┌────────▼─────────┐
          │ EEC (Event        │ │   LAC     │ │ Olay Kayıt       │
          │ Collector)        │ │ (İzleyici)│ │ Merkezi          │
          │ 28 Event tipi     │ │ Salt okur │ │ (Event Registry) │
          └────────────────────┘ └───────────┘ └──────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                    ┌─────▼─────┐          ┌──────▼──────┐
                    │  Handlers │          │   Services  │
                    │ (Telegram │◄────────►│ (İş mantığı)│
                    │  olayları)│          │             │
                    └───────────┘          └─────────────┘
                          │                       │
                          └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │   Telegram Bot API    │
                          │ (python-telegram-bot) │
                          └───────────────────────┘
```

### 3.2 Karar Hiyerarşisi (MASTER-001)

```
1. HLK MASTER RULE BOOK  ← En üst otorite
2. Global Configuration (GC)
3. General Rules (GK)
4. Architecture Rules (AR)
5. State Engine (SE)
6. Flow Diagram (FD)
7. Operational Rules (OR)
8. Quality Rules (QR)
9. Module Rules (MR)
10. Kod (Python)
```

### 3.3 12 MASTER Kuralı Özeti

| Kural | İlke |
|---|---|
| MASTER-001 | ANA YASA üstünlüğü — anayasa en üst otoritedir |
| MASTER-002 | Aktif Proje Sınırı — yalnızca aktif proje klasörü çalışma alanıdır |
| MASTER-003 | ANA YASA/Kod Uyumluluk Denetimi — kural + kod uyumu zorunlu |
| MASTER-004 | Karar Mekanizması — HLK karar verir, katmanlar yönlendirir |
| MASTER-005 | V1 Mimari Dondurma — değişiklikler Proje Yöneticisi onayına tabi |
| MASTER-006 | Modüler ve Öğrenen YZ Asistanı |
| MASTER-007 | Geliştirici Çalışma Metodolojisi — AI Geliştirici vs HLK denetleyici |
| MASTER-008 | Bütüncül Anayasal Model — her görev öncesi tüm kaynaklar okunur |
| MASTER-009 | Flow Diagram Otoritesi — UX'in tek yetkili kaynağı |
| MASTER-010 | Referans Form Kullanım Otoritesi — .png UI'in anayasal otoritesidir |
| MASTER-011 | Runtime Aktiflik Doğrulama — 4 şartlı doğrulama |
| MASTER-012 | Hedef Çalışma Ortamı Doğrulama — Telegram'da doğrulama zorunlu |

---

## 4. STATE MACHINE VE SCENE MANAGEMENT

### 4.1 State Engine (SE-007)

**Dosya:** `utils/state_engine.py` (641 satır)

Projenin kalbi olan State Engine, 4 bileşenden oluşur:

- **UserState** (str, Enum): 27 state tanımlı. `STATE_START` → `SCENE_1` → … → `SESSION_COMPLETED`
- **UserEvent** (str, Enum): 50+ event tanımı. OLAY-001'den OLAY-103'e kadar
- **STATE_TRANSITIONS**: `dict[UserState, dict[UserEvent, UserState]]` — tüm geçerli geçişler
- **STATE_ACTION_MAP**: Her state için aktif modüllerin listesi

**StateEngine Sınıfı:**
- `fire(event)` → geçiş varsa uygular, yoksa "blocked" olarak kaydeder
- `can_transition(event)` → geçiş kontrolü
- `get_allowed_events()` → mevcut state'de izin verilen event'ler
- `get_active_modules()` → mevcut state'in aktif modülleri
- `reset()` → oturumu sıfırlar

### 4.2 Scene Registry (FD-008_1)

**Dosya:** `services/scene_registry.py` (397 satır)

`SceneDefinition` dataclass'ı ile her sahne tanımlanır:
- `scene_id`, `scene_name`, `state`, `text`, `parse_mode`
- `next_state`, `trigger_event`, `buttons`, `timeout_seconds`, `voice_enabled`

14 sahne tanımı içerir (SAHNE-01…SAHNE-13 + Senaryo Onay Formu).

### 4.3 Scene Engine (AR-002_28)

**Dosya:** `services/scene_engine.py` (689 satır)

`ConversationSceneEngine` — 6 adımlı yaşam döngüsü:
1. STATE'i belirle
2. FD-008_1'den sahne kaydını bul
3. Flow Diagram davranışlarını Constitution Cache'ten oku
4. Scene içeriğini oluştur (i18n çeviri + ses üretimi)
5. ScenePayload üret
6. scene_delivery.deliver() ile teslim et

### 4.4 Scene Delivery (AR-002_36)

**Dosya:** `services/scene_delivery.py` (434 satır)

- `ScenePayload`: scene_id, chat_id, text, video_path/ID, audio_path/ID, buttons
- 3 denemeli retry mekanizması
- `cleanup_chat()`: Önceki sahneye ait tüm mesajları siler
- `replace_ui_component()`: Aktif UI bileşenini yerinde günceller
- `send_and_track()`: Mesaj gönderir ve cleanup havuzuna kaydeder

### 4.5 Scene Lock (AR-002_44)

**Dosya:** `utils/scene_lock.py` (127 satır)

SAHNE-1 için oturum başına tek seferlik çalışma garantisi.
Zorunlu geçiş zinciri: `IDLE → LOCKED → PLAYING → COMPLETED → CLEANUP → DONE` (terminal)

---

## 5. KULLANICI AKIŞI (SAHNE-01 → SAHNE-13)

```
/start
  │
  ├─ SAHNE-01: HLK Karşılama Videosu (hlk_sahne1.mp4, 8sn)
  │   └─ Scene Lock: IDLE → LOCKED → PLAYING → COMPLETED → CLEANUP → DONE
  │
  ├─ Dil Seçimi: 8 dil butonu (TR, EN, DE, FR, ES, AR, RU, KR/Kürtçe)
  │
  ├─ SAHNE-02: Dile Özel AHU Lip-Sync Video (SAHNE-2_{LANG}_alt.mp4, 16-24sn)
  │   └─ Daktilo animasyonu ile karşılama mesajı + link isteği
  │
  ├─ Ürün Linki: Kullanıcı link gönderir
  │   ├─ Link Doğrulama (URL regex + erişim kontrolü)
  │   ├─ Arka Plan Araştırması (web scraping, 8 modül)
  │   └─ 5 başarısız deneme → oturum kapatma
  │
  ├─ SAHNE-01 (Materyal): Tamamlayıcı Materyal Bilgilendirmesi
  │   └─ [📤 Materyal Yükle] / [⏭️ Geç]
  │
  ├─ SAHNE-02: Platform Seçimi
  │   └─ TikTok / Instagram Reels / YouTube / Diğer
  │
  ├─ SAHNE-03: Video Formatı
  │   └─ Dikey 9:16 / Yatay 16:9 / Kare 1:1
  │
  ├─ SAHNE-04: Çözünürlük
  │   └─ 480p / 720p HD ⭐ / 1080p Full HD
  │
  ├─ SAHNE-05: Video Süresi (4-30 sn veya HLK'ya Bırak)
  │
  ├─ SAHNE-06: Tanıtım Tarzı
  │   └─ UGC / Geleneksel / Sinematik / Kendim Yazacağım / HLK'ya Bırak
  │
  ├─ SAHNE-07: Hedef Kitle (8 yaş grubu)
  │
  ├─ SAHNE-08: Ses Tercihleri (multi-select toggle)
  │   └─ Dış Seslendirme / Ortam Sesleri / Fon Müziği / 🔇 SESSİZ
  │
  ├─ SAHNE-09: Seslendirme Dili (8 dil)
  │
  ├─ SAHNE-10: Ses Karakteri (Kadın / Erkek / Çocuk)
  │
  ├─ SAHNE-11: Vurgulanacaklar (multi-select + özel metin)
  │   └─ İndirim / Ücretsiz Kargo / Hediye Paket / Yeni Sezon / Yerli Üretim
  │
  ├─ SAHNE-12: Brief Onay Formu (PNG render + [✅ ONAYLIYORUM / ✏️ DÜZELT])
  │
  ├─ SAHNE-13: Brief Tamamlandı + Senaryo Onayı
  │   └─ Video + [✅ ONAYLA / ❌ REDDET]
  │
  ├─ STATE_PRICING: Yönetici Fiyatlandırma → Kullanıcı Fiyat Teklifi
  │   └─ Katsayı girişi, HLK sohbet, fiyat onay/ret
  │
  ├─ STATE_PAYMENT_VERIFICATION: Ödeme Doğrulama
  │   └─ Banka bilgileri → [ÖDEME YAPTIM] → Yönetici onayı
  │
  └─ STATE_VIDEO_PRODUCTION: Video Üretimi → STATE_SESSION_COMPLETED
```

---

## 6. HANDLER ANALİZİ

### 6.1 handlers/start.py (1,226 satır)

En kritik handler. Temel fonksiyonlar:

| Fonksiyon | Görev |
|---|---|
| `start_handler` | SAHNE-01: Karşılama videosu + 8 dil seçimi |
| `handle_language_selection` | SAHNE-02: Lip-sync video + daktilo + link isteği |
| `message_handler` | State tabanlı mesaj yönlendirme merkezi |
| `handle_devam_button` | Devam butonu |
| `handle_format_selection` | SCOUT format seçimi (test) |
| `handle_duration_hlk` | SAHNE-05 "HLK'ya Bırak" — dinamik süre |
| `validate_language_support` | 8 dil video+ses+metin varlık doğrulaması |

**8 dilde karşılama mesajı:** `TYPEWRITER_MESSAGES` dict'i (TR, EN, DE, FR, ES, AR, RU, KR)
**8 dilde link isteği:** `LINK_REQUEST_MESSAGE` dict'i

### 6.2 handlers/website.py (2,531 satır)

**Projenin en büyük dosyası.** Tüm SAHNE-02…SAHNE-13 handler'larını ve fiyatlandırma/ödeme işlemlerini içerir:

| Grup | Fonksiyonlar |
|---|---|
| Link ve Materyal | `handle_website_link`, `handle_material_choice`, `handle_material_upload` |
| SAHNE-02…05 | `handle_platform_selection`, `handle_format_selection`, `handle_resolution_selection` |
| SAHNE-06…08 | `handle_style_selection`, `handle_audience_selection`, `handle_audio_toggle`, `handle_audio_devam` |
| SAHNE-09…11 | `handle_voice_language`, `handle_voice_character`, `handle_emphasis`, `handle_emphasis_done` |
| SAHNE-12…13 | `handle_brief_approve`, `handle_brief_edit`, `handle_brief_edit_field`, `handle_scenario_approve`, `handle_scenario_reject` |
| Fiyatlandırma | `handle_admin_pricing_submit`, `handle_pricing_approve`, `handle_pricing_reject` |
| Ödeme | `handle_payment_declared`, `handle_payment_cancel`, `handle_admin_payment_approve`, `handle_admin_payment_ret` |
| HTML Üreticiler | `_build_brief_html`, `_build_senaryo_html`, `_build_admin_pricing_form`, `_build_user_pricing_form`, `_build_banka_bilgileri_karti`, `_build_admin_odeme_bildirimi` |

### 6.3 handlers/cancel.py (49 satır)

`handle_cancel()`: `/cancel` komutu. SceneLock'u IDLE'a sıfırlar, user_data'yı temizler.

---

## 7. SERVİS KATMANI ANALİZİ

### 7.1 Scene ve Konuşma Yönetimi

| Servis | Satır | Açıklama |
|---|---|---|
| `scene_registry.py` | 397 | FD-008_1: 14 sahne tanımı, `SceneDefinition` dataclass |
| `scene_engine.py` | 689 | AR-002_28: ConversationSceneEngine, 6 adımlı yaşam döngüsü |
| `scene_delivery.py` | 434 | AR-002_36: 3 denemeli retry, cleanup, UI component replace |

### 7.2 Anayasal İşletim Sistemi

| Servis | Satır | Açıklama |
|---|---|---|
| `constitution_cache.py` | 545 | SHA-256 hash + önbellek, 18 katmanlı Boot manifest'i |
| `constitution_enforcement.py` | 383 | CEE: PRE-CHECK → EXECUTE → POST-CHECK (6 boyutlu denetim) |
| `constitution_index.py` | 621 | ANA YASA'dan kural ayrıştırma, Generic Runtime Validation |
| `execution_event_collector.py` | 359 | EEC: 28 Event tipi, 6 kategori, 3 faz |
| `olay_kayit_merkezi.py` | 199 | Merkezi Event Registry, PID/kategori/sonuç bazlı sorgulama |
| `lac.py` | 259 | Live Activity Center: salt izleyici, Telegram HTML rapor |

### 7.3 Medya Üretim Servisleri

| Servis | Satır | Açıklama |
|---|---|---|
| `voice_generator.py` | 144 | AHU Voice: ElevenLabs TTS, multilingual_v2 model, dosya cache |
| `research_orchestrator.py` | 676 | AR-002: 8 modüllü araştırma, BeautifulSoup scraping, aday puanlama |
| `hedra_generator.py` | 153 | Hedra API: görsel + ses → lip-sync video |
| `descript_generator.py` | 458 | Descript API: Overdub TTS, proje yönetimi, AI Agent düzenleme |
| `render_service.py` | 162 | Node.js + Puppeteer ile Referans Form → PNG render |

### 7.4 Yardımcı Modüller (utils/)

| Modül | Satır | Açıklama |
|---|---|---|
| `state_engine.py` | 641 | SE-007: 27 state, 50+ event, tüm geçiş kuralları |
| `scene_lock.py` | 127 | AR-002_44: 6 aşamalı kilit, terminal DONE state |
| `session_timeout.py` | 71 | 5dk + 2dk uyarı = 7dk sonra oturum kapatma |
| `validators.py` | 48 | URL regex doğrulama, Telegram kullanıcı ID kontrolü |

---

## 8. ANA YASA — ANAYASAL İŞLETİM SİSTEMİ

### 8.1 Belge Envanteri

`ANA YASA/` dizini 23 belgeden oluşur:

| # | Dosya | Boyut | Açıklama |
|---|---|---|---|
| 1 | `00_HLK_MASTER_RULE_BOOK.md` | 45.8 KB | En üst otorite, 12 MASTER kuralı, karar hiyerarşisi |
| 2 | `01_Global_Configuration.md` | 1.7 KB | 16 GC parametresi |
| 3 | `02_General_Rules.md` | 5.5 KB | 12 GK kuralı |
| 4 | `03_Architecture_Rules.md` | 301.8 KB | **En büyük dosya**. 77+ AR kuralı |
| 5 | `04_Operational_Rules.md` | 36.6 KB | 16 OR kuralı |
| 6 | `05_Quality_Rules.md` | 9.8 KB | 8 QR kuralı |
| 7 | `06_Module_Rule.md` | 14.7 KB | 6 MR kuralı |
| 8 | `07_HLK_STATE_ENGINE.md` | 23.2 KB | SE-007 serisi state tanımları |
| 9 | `08_HLK_FLOW_DIAGRAM.md` | 31.9 KB | FD-008_1: 13 sahnelik kullanıcı akışı |
| 10 | `09_WORKFLOW_MANIFEST.md` | 2.6 KB | Workflow manifestosu |
| 11 | `10_FEATURE_REGISTRY.md` | 7.8 KB | Özellik kayıtları |
| 12 | `11_WORKFLOW_FEATURE_MAP.md` | 6.9 KB | Workflow-özellik eşleştirmesi |
| 13 | `12_DIGITAL_ASSET_ARCHIVE.md` | 3.0 KB | Dijital varlık arşivi |
| 14 | `13_DIGITAL_ASSET_CATALOG.md` | 10.5 KB | Dijital varlık kataloğu |
| 15 | `14_OLAY_KAYIT_MERKEZI.md` | 77.2 KB | Olay Kayıt Merkezi (OLAY-001…OLAY-103) |
| 16 | `15_KARAR_GEREKCESI_STANDARDI.md` | 11.3 KB | Karar gerekçesi standardı |
| 17 | `16_PRODUCTION_PACKAGE_STANDARD.md` | 10.3 KB | Üretim paketi standardı |
| 18 | `17_SAHNE_KAYIT_DEFTERI.md` | 9.2 KB | Sahne kayıt defteri |
| 19 | `18_CONSTITUTION_DIFF_ENGINE.md` | 53.1 KB | CDE: Anayasa-Kod karşılaştırma |
| 20 | `19_CONSTITUTION_SCAN_ENGINE.md` | 42.5 KB | CSE: Anayasal veri toplama |
| 21 | `20_TASK_ENGINE.md` | 50.9 KB | Task Engine |
| 22 | `21_CONSTITUTION_ENFORCEMENT_ENGINE.md` | 41.0 KB | CEE spesifikasyonu |
| 23 | `22_EXECUTION_EVENT_COLLECTOR.md` | 18.1 KB | EEC spesifikasyonu |

### 8.2 Constitutional Boot Sequence (18 Katman)

Bot başlangıcında `post_init()` tarafından çalıştırılan 18 katmanlı boot sırası:

```
FAZ 0: Constitution Cache taraması (SHA-256)
FAZ 1: 18 katman sırayla yüklenir:
  01_Global_Configuration → 02_General_Rules → 03_Architecture_Rules →
  04_Operational_Rules → 05_Quality_Rules → 06_Module_Rule →
  07_HLK_STATE_ENGINE → 08_HLK_FLOW_DIAGRAM → 09_WORKFLOW_MANIFEST →
  10_FEATURE_REGISTRY → 11_WORKFLOW_FEATURE_MAP → 12_DIGITAL_ASSET_ARCHIVE →
  13_DIGITAL_ASSET_CATALOG → 14_OLAY_KAYIT_MERKEZI →
  18_CONSTITUTION_DIFF_ENGINE → 19_CONSTITUTION_SCAN_ENGINE →
  20_TASK_ENGINE → 00_HLK_MASTER_RULE_BOOK
FAZ 2: CONSTITUTION_READY doğrulaması + CEE PRE-CHECK
```

### 8.3 Anayasal Denetim Katmanları

| Katman | Görev | PASS/FAIL Yetkisi |
|---|---|---|
| **CSE** (Constitution Scan Engine) | Veri toplama | ❌ Yok |
| **CDE** (Constitution Diff Engine) | Anayasa-Kod karşılaştırma | ❌ Yok |
| **Task Engine** | Görev önceliklendirme | ❌ Yok |
| **CEE** (Constitution Enforcement Engine) | **PASS/FAIL kararı** | ✅ Tek yetkili |
| **EEC** (Execution Event Collector) | Event toplama | ❌ Yok |
| **LAC** (Live Activity Center) | Salt izleme | ❌ Yok |

---

## 9. FORMLAR — REFERANS UI SİSTEMİ

### 9.1 İki Katmanlı UI Mimarisi

Proje, **Referans UI** ve **Çalışan UI** olmak üzere iki katmanlı bir mimari kullanır:

1. **Referans UI (FORMLAR/):** Proje Yöneticisi tarafından onaylanan .png referansları. HTML/CSS/JS + Puppeteer ile yeniden üretilebilir. Tasarım otoritesidir.

2. **Çalışan UI (Python/Telegram):** Referans UI'nin Telegram platformundaki uygulanabilir en yakın karşılığı. PNG kullanılmaz; Telegram HTML + InlineKeyboardButton kullanılır.

### 9.2 Form Envanteri

| # | Form | Kullanıcı/Rol | Component Sayısı | PNG Boyutu |
|---|---|---|---|---|
| 1 | REFERAN_KULLANICI FİYAT_TEKLİF_FORMU | Son Kullanıcı | 0 (Basit) | 1.45 MB |
| 2 | REFERANS_Brief_Onay_Formu | Son Kullanıcı | 0 (Basit) | 1.48 MB |
| 3 | REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC) | Yönetici | 5 | 1.64 MB |
| 4 | REFERANS_SENARYO_ONAY_FORMU | Son Kullanıcı | 0 (Basit) | 1.51 MB |
| 5 | REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU | Yönetici | 6 | 1.34 MB |
| 6 | REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU | Yönetici | 0 (Basit) | 1.31 MB |

### 9.3 Form-State İlişkisi

| STATE | Form | Handler |
|---|---|---|
| STATE_BRIEF_REVIEW | Brief Onay Formu | `handle_brief_approve` / `handle_brief_edit` |
| STATE_SCENARIO_APPROVAL | Senaryo Onay Formu | `handle_scenario_approve` / `handle_scenario_reject` |
| STATE_PRICING (Admin) | Yönetici Fiyatlandırma | `handle_admin_pricing_submit` |
| STATE_PRICING (User) | Kullanıcı Fiyat Teklifi | `handle_pricing_approve` / `handle_pricing_reject` |
| STATE_PAYMENT_VERIFICATION | Yönetici Ödeme Onayı | `handle_admin_payment_approve` / `handle_admin_payment_ret` |

### 9.4 Shared Kaynaklar

- **`base.css`** (V1.1): HLK Design System token'ları (renkler, grid, kartlar, butonlar, badge'ler)
- **`render-common.js`** (V1.0): Puppeteer tabanlı render motoru — `injectData()`, `loadComponents()`, `renderForm()`, CSS inline mekanizması

### 9.5 Render Mimarisi

```
sample-data.json → render.js → render-common.js → injectData() →
  template.html ({{DATA_JSON}} çözülür) → Puppeteer → PNG çıktısı
```

**Not:** Telegram WebApp API (Telegram.WebApp) hiçbir yerde kullanılmaz. Tüm etkileşimler InlineKeyboardButton ve HTML parse_mode ile sağlanır.

---

## 10. ÇOKLU DİL DESTEĞİ (i18n)

### 10.1 Desteklenen Diller

| Kod | Dil | Bayrak |
|---|---|---|
| tr | Türkçe | 🇹🇷 |
| en | English | EN |
| de | Deutsch | 🇩🇪 |
| fr | Français | 🇫🇷 |
| es | Español | 🇪🇸 |
| ar | العربية | AR |
| ru | Русский | 🇷🇺 |
| kr | Kürtçe (Kurdî) | ☀️ |

**Önemli:** "kr" kodu sistemde Kürtçe anlamına gelir (uluslararası standart "ku"dur). Bu geriye dönük uyumluluk için korunur. UI'da Kore bayrağı ile gösterilemez; ☀️ KU olarak gösterilmelidir (MR-0005_2).

### 10.2 i18n Altyapısı

- **`config/i18n.py`** (895 satır): 17 kategori, 200+ çeviri anahtarı, 8 dil
- `t("section.key", lang)` formatı ile çeviri lookup
- SAHNE-03…SAHNE-13 arası tüm prompt ve buton etiketleri 8 dilde mevcut
- `SceneEngine._translate_buttons()` ve `_translate_scene_text()` ile otomatik çeviri

### 10.3 i18n İhlal Durumu

**82+ konumda** sabit Türkçe metin (hardcoded) tespit edilmiştir:

| Seviye | Sayı | Örnek Konumlar |
|---|---|---|
| **Kritik** | 12 | Link doğrulama hata mesajları, materyal yükleme, brief onay tablosu, senaryo onay formu |
| **Orta** | 34 | query.answer() toast mesajları, hata mesajları |
| **Yapısal** | 6 | BRIEF_FIELDS, aciklama_map, story_sahneler, emphasis_map veri yapıları |
| **Uyumlu** | 14 | Session timeout, SAHNE-03~13 prompt'ları, typewriter mesajları |

---

## 11. HARİCİ API ENTEGRASYONLARI

| Servis | API | Kullanım |
|---|---|---|
| **Telegram** | Bot API | İki token: @hlk_reklam_asistani01_bot (prod), @hlk01_test_bot (test) |
| **Anthropic** | Claude API | Admin fiyatlandırma sohbet modu (Claude Haiku 4.5) |
| **ElevenLabs** | TTS API | AHU ses üretimi (eleven_multilingual_v2) |
| **Hedra** | Lip-Sync API | Görsel + ses → lip-sync video |
| **Descript** | Overdub API | TTS, proje yönetimi, AI Agent düzenleme |
| **Higgsfield AI** | Video API | Video üretimi (fiyatlandırma formunda referans) |
| **Kie AI** | Görsel API | Görsel üretimi |
| **Fal.ai** | Seedance API | Image-to-video |
| **OpenAI** | TTS API | Yedek ses üretimi |

---

## 12. TEST ALTYAPISI

### 12.1 Test Script'leri (10 adet)

| Test | Boyut | Test Edilen |
|---|---|---|
| `test_photo_inline.py` | 5.9 KB | Brief Onay Formu HTML + InlineKeyboard |
| `test_sahne12.py` | 3.4 KB | SAHNE-12 Brief Onay Formu |
| `test_sahne13.py` | 4.6 KB | SAHNE-13 Senaryo Onay Formu |
| `test_yonetici_fiyat.py` | 9.7 KB | Yönetici Fiyatlandırma + HLK Sohbet |
| `test_fiyat_teklif.py` | 2.7 KB | Kullanıcı Fiyat Teklif Formu |
| `test_kullanici_fiyat.py` | 3.9 KB | Kullanıcı fiyat gösterme |
| `test_odeme_bildirim.py` | 4.8 KB | Yönetici Ödeme Onay Formu |
| `test_odeme_karti.py` | 2.3 KB | Ödeme kartı gösterme |
| `test_banka_karti.py` | 1.9 KB | Banka Bilgileri Kartı |
| `test_i18n_check.py` | 3.1 KB | i18n dil desteği kontrolü |

### 12.2 Test Başlatma

- `testi_baslat.bat`: Eski process'leri öldürür, `ENV=test`, `TEST_MODE=true` ile başlatır
- `testi_baslat.ps1`: PowerShell alternatifi
- Tüm testler `@hlk01_test_bot` üzerinde çalışır

**Not:** pytest framework kullanılmaz. Her test bağımsız bir Telegram bot script'idir.

---

## 13. KOD KALİTESİ DEĞERLENDİRMESİ

### 13.1 Güçlü Yönler

1. **Kapsamlı State Machine Mimarisi:** StateEngine + STATE_TRANSITIONS + STATE_ACTION_MAP üçgeni, tüm kullanıcı akışını merkezi ve izlenebilir şekilde yönetir.

2. **Scene Engine ve Registry Ayırımı:** SceneDefinition veri yapısı ile sahne tanımları koddan ayrıştırılmış, merkezi olarak toplanmıştır.

3. **Hata Yönetimi:** error_handler stale callback'leri ayırt eder. scene_delivery 3 denemeli retry mekanizması içerir. SceneLock eşzamanlı ikinci oturumu engeller.

4. **Defansif Programlama:** Birçok yerde try/except ile graceful degradation. Typewriter 3 aşamalı fallback ile çalışır.

5. **Loglama:** Kapsamlı debug log'ları. SENDMESSAGE TRACE monkey-patch tüm mesaj gönderimlerini kaydeder.

6. **Mimari Desenler:** Singleton, State Machine, Registry, Strategy, Observer/Event, Template Method, Chain of Responsibility, Proxy/Cache, Facade desenleri başarıyla uygulanmıştır.

### 13.2 Zayıf Yönler

1. **Kod Tekrarı (DRY İhlali):**
   - Tüm SAHNE handler'ları (SAHNE-03…SAHNE-11) aynı şablonu tekrar eder: query.answer(), state geçişi, mesaj silme, cleanup, scene engine, start_timer. Bir **dekoratör veya base class** ile soyutlanabilir.
   - `_get_brief_value()` ve `_build_senaryo_html()` içinde aynı `lang_names` dict'i en az 3 kez tekrar ediliyor.

2. **Aşırı Büyük Dosyalar:**
   - `handlers/website.py` **2,531 satır** — en az 3-4 dosyaya bölünmeli: `pricing.py`, `brief.py`, `scenario.py`, `scenes.py`.
   - `handlers/start.py` **1,226 satır**.

3. **SOLID İhlalleri:**
   - **Single Responsibility:** website.py hem link doğrulama, hem materyal, hem tüm sahne geçişleri, hem brief, hem senaryo, hem fiyatlandırma, hem ödeme işlemlerini yönetiyor.
   - **Dependency Inversion:** Servisler doğrudan singleton olarak import ediliyor. DI kullanılmaması test edilebilirliği düşürür.

4. **Tip Güvenliği:**
   - `bot` parametresi çoğu fonksiyonda tip hint'siz.
   - `user_data: dict` tipi çok geniş — TypedDict veya Pydantic model kullanılmalı.

5. **Hata Yönetimi:**
   - Çoğu `try/except` bloğu `except Exception: pass` şeklinde — gerçek hataları gizler.
   - `asyncio.create_task()` ile başlatılan arka plan görevlerinde hata yakalama eksik.

6. **Test Edilebilirlik:**
   - Singleton kullanımı (10+ global singleton) test etmeyi zorlaştırır.
   - Hiçbir birim test (unit test) yok. Mevcut testler yalnızca manuel Telegram test script'leri.

7. **Performans:**
   - `get_scene_for_state()` linear arama (O(n)) kullanır.
   - Typewriter animasyonu her 4 kelimede bir API çağrısı yapar — rate limiting riski.

8. **Veri Kalıcılığı Yok:**
   - Tüm durum bellekte (`context.user_data`) tutulur.
   - Bot restart'ta tüm oturum verileri ve olay kayıtları kaybolur.
   - `DATABASE_URL=sqlite:///data/bot.db` tanımlı ancak kullanılmaz.

9. **Anayasa-Kod Uçurumu:**
   - CEE (Constitution Enforcement Engine) kodu yazılmış fakat **runtime'da hiçbir yerde çağrılmaz.**
   - 11 AR kuralı (AR-002_67…AR-002_77) uyumsuz veya eksik.

---

## 14. RAPORLAR VE UYUMLULUK DURUMU

### 14.1 Mevcut Raporlar

| Rapor | Tarih | Odak |
|---|---|---|
| RAPOR_PROJE_INCELEME_13072026.md | 13 Tem | Kapsamlı proje inceleme |
| RAPOR_PROJE_INCELEME_08072026.md | 8 Tem | Anayasal mimari, CEE/EEC denetim |
| RAPOR_DIL_UYUMLULUK_DENETIMI_13072026.md | 13 Tem | i18n uyumluluk (82+ ihlal) |
| RAPOR_ANAYASAL_UYUMLULUK_AR67_77_13072026.md | 13 Tem | AR-002_67…77 uyumluluk |
| HLK_CONSTITUTION_AUDIT_RAPORU.md | 3 Tem | Anayasal denetim |
| HLK_ANAYASAL_KANIT_RAPORU.md | 3 Tem | Davranış modeli kanıt |
| HLK_BEHAVIOR_MODEL_ANALYSIS.md | — | Davranış model analizi |
| HLK_RAPOR_ASISTAN_PROJESI.md | — | Genel proje raporu |

### 14.2 Kritik Uyumluluk Bulguları

#### AR-002_67…77 Uyumluluk

| Kural | Durum | Risk |
|---|---|---|
| AR-002_67 (Referans Form Runtime Render) | UYUMSUZ | YÜKSEK |
| AR-002_68 (DATA CONTRACT) | UYUMSUZ | YÜKSEK |
| AR-002_69 (Component Independence) | UYUMSUZ | ORTA |
| AR-002_70 (STATE_VIDEO_PRODUCTION Runtime) | **KOD YOK** | KRİTİK |
| AR-002_71 (PID Runtime) | UYUMSUZ | YÜKSEK |
| AR-002_72 (Production Package) | **KOD YOK** | KRİTİK |
| AR-002_73 (Production Event) | KISMİ | YÜKSEK |
| AR-002_74 (Task Package) | **KOD YOK** | YÜKSEK |
| AR-002_75 (Production Service Selection) | UYUMSUZ | ORTA |
| AR-002_76 (Üretim Yürütme Mimarisi) | **KOD YOK** | KRİTİK |
| AR-002_77 (Yaratıcı İçerik Üretim) | UYUMSUZ | YÜKSEK |

**11 kuralın tamamı uyumsuz veya eksik. 3 kural için kod hiç yok.**

#### CEE ve EEC Runtime Eksikliği

- **CEE:** Kod mevcut (383 satır) ancak **hiçbir yerde çağrılmıyor.** Handler'larda import veya çağrı yok.
- **EEC:** Kod mevcut (359 satır) ancak **sadece main.py post_init()'te** kullanılıyor.
- **Olay Kayıt Merkezi:** Kod mevcut ancak handler'lardan çağrılmıyor.

#### Davranış Modeli İhlalleri

- **Karar Akışı Ters:** Handler'lar karar veriyor, CEE yalnızca sonucu onaylıyor (MASTER-004 ihlali)
- **CEE Zorunlu Geçiş Noktası Değil:** CEE PRE-CHECK ve POST-CHECK bypass edilebiliyor
- **Runtime Aktiflik Doğrulama Eksik:** MASTER-011'in 4 şartlı doğrulaması uygulanmıyor

---

## 15. GÜÇLÜ YÖNLER

1. **Benzersiz Anayasal Sistem:** 23 belgelik ANA YASA mimarisi, AI destekli geliştirmede tutarlılık için yenilikçi bir yaklaşım.

2. **Katmanlı Dokümantasyon:** Her katmanın sorumluluğu net. MASTER → GC → GK → AR → OR → QR → MR hiyerarşisi belirgin.

3. **Single Source of Truth Prensibi:** Event'ler Olay Kayıt Merkezi'nde, sayısal değerler GC'de, kullanıcı akışı Flow Diagram'da.

4. **Kapsamlı State Machine:** 27 state, 50+ event, merkezi geçiş kuralları ile tam akış yönetimi.

5. **8 Dil Desteği:** Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, Arapça, Rusça, Kürtçe.

6. **Referans UI Sistemi:** Her form için .png referans + HTML/CSS/JS implementasyonu + Puppeteer render.

7. **Detaylı Raporlama Kültürü:** 8+ rapor dosyası, her rapor ANA YASA referanslı, kanıt temelli.

8. **Scene Lock Mekanizması:** 6 aşamalı kilit ile eşzamanlı çalışma ve tekrarlı oynatma engelleme.

9. **Typewriter Animation:** 3 aşamalı garantili teslimat ile doğal konuşma deneyimi.

10. **Constitutional Boot Sequence:** 18 katmanlı sistematik başlangıç süreci.

---

## 16. EKSİKLİKLER VE İYİLEŞTİRME ALANLARI

### 16.1 Kritik (Hemen Ele Alınmalı)

1. **STATE_VIDEO_PRODUCTION Runtime yok** — AR-002_70 kod implementasyonu tamamen eksik
2. **Production Package yok** — AR-002_72 hiç implemente edilmemiş
3. **Production Executor yok** — AR-002_76 karar-yürütme ayırımı eksik
4. **CEE runtime'da çalışmıyor** — kod mevcut ama çağrılmıyor

### 16.2 Yüksek Öncelikli

5. **PID formatı ANA YASA ile çelişiyor:** Kod `PID-YYYYMMDD-HHMMSS` üretiyor, ANA YASA `PID-YYYYMMDD-NNNN` istiyor
6. **82+ i18n ihlali** — hardcoded Türkçe metinler
7. **Handler dosyaları aşırı büyük** — website.py 2,531 satır
8. **AR-002_67…77 uyumluluğu** — 11 kuraldan 11'i uyumsuz

### 16.3 Orta Öncelikli

9. **Test altyapısı zayıf** — pytest yok, CI/CD entegrasyonu yok
10. **Veri kalıcılığı yok** — bot restart'ta tüm veriler kayboluyor
11. **State Engine eksik bölümleri** — SE-007_6…15 arası boş
12. **Dokümantasyon dili tutarsız** — Türkçe/İngilizce karışık

### 16.4 Düşük Öncelikli

13. **get_scene_for_state()** O(n) linear arama
14. **Singleton bağımlılığı** test edilebilirliği azaltıyor
15. **CSS inline regex'i kırılgan** — tek tırnak/farklı attribute sıralamasında çalışmayabilir
16. **try/except pass** pattern'i hata ayıklamayı zorlaştırıyor

---

## 17. ÖZET METRİKLER

| Metrik | Değer |
|---|---|
| Python dosyası | 48 |
| Toplam Python kodu | ~14,621 satır |
| ANA YASA belgesi | 23 (~872 KB) |
| Markdown dosyası (toplam) | 74 (~1.29 MB) |
| MASTER kuralı | 12 |
| AR kuralı | 77+ |
| Desteklenen dil | 8 |
| State sayısı | 27 |
| Event sayısı | 44 kayıtlı (50+ toplam) |
| Sahne sayısı | 13 |
| Entegre harici servis | 9 |
| Handler dosyası | 3 |
| Servis modülü | 16 |
| Test script'i | 10 |
| Referans Form | 6 |
| Component (form) | 11 |
| i18n hardcoded ihlali | 82+ konum |
| Anayasa-kod uyumsuz AR kuralı | 11 |
| Kritik eksik modül | 4 |
| Geliştirici | haluk4365 (tek) |
| Commit sayısı | 7 |
| Geliştirme dönemi | Mayıs — Temmuz 2026 |

---

## 18. SONUÇ VE ÖNERİLER

### 18.1 Genel Değerlendirme

HLK AI Reklam Asistanı, **benzersiz bir anayasal mimari** üzerine inşa edilmiş, kapsamlı bir Telegram bot projesidir. Projenin en güçlü yanı, **ANA YASA** adı verilen 23 belgelik anayasal sistem ve bu sistemi koda bağlayan **Constitution Cache + CEE + EEC + Olay Kayıt Merkezi** zinciridir.

Ancak proje şu anda bir **geçiş aşamasındadır:** ANA YASA belgeleri ileri seviyede detaylandırılmış olmasına rağmen, bu kuralların kod karşılıkları henüz tam olarak inşa edilmemiştir. Özellikle **STATE_PRICING sonrası akışlar** (STATE_VIDEO_PRODUCTION, ödeme doğrulama, PID, Production Package) büyük ölçüde eksiktir.

### 18.2 Önerilen 3 Fazlı İyileştirme Planı

**FAZ 1 — Temel Altyapı (Kritik):**
1. `services/production_runtime.py` — STATE_VIDEO_PRODUCTION Runtime (AR-002_70)
2. `services/pid_runtime.py` — PID oluşturma ve yönetimi (AR-002_71)
3. `services/production_package_runtime.py` — Üretim paketi altyapısı (AR-002_72)
4. `services/production_executor.py` — Karar-yürütme ayırımı (AR-002_76)
5. CEE'nin handler akışına entegrasyonu

**FAZ 2 — Event ve Entegrasyon (Yüksek):**
6. `services/production_event_runtime.py` (AR-002_73)
7. `services/task_package_runtime.py` (AR-002_74)
8. `services/reference_form_resolver.py` (AR-002_67)
9. `services/data_contract_validator.py` (AR-002_68)
10. `services/creative_content_engine.py` (AR-002_77)
11. Handler dosyalarının bölünmesi (website.py → pricing/brief/scenario/scenes)
12. 82+ i18n ihlalinin giderilmesi

**FAZ 3 — Optimizasyon (Orta):**
13. `services/service_selection_engine.py` (AR-002_75)
14. pytest tabanlı test altyapısı
15. Veri kalıcılığı (SQLite/PostgreSQL)
16. Tip güvenliği iyileştirmeleri (TypedDict/Pydantic)
17. get_scene_for_state() → dict lookup optimizasyonu
18. Kod tekrarlarının giderilmesi (DRY)

---

**Hazırlayan:** Claude Code (DeepSeek V4 Pro) — 4 paralel araştırma agent'ı + doğrudan kod incelemesi ile
**İnceleme Kapsamı:** 48 Python dosyası, 14,621 satır kod, 74 Markdown dosyası, 23 ANA YASA belgesi
