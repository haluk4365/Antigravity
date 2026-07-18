# HLK_01 ASİSTAN PROJE ANALİZ RAPORU

**Tarih:** 2026-07-08
**Proje:** hlk_projeler_02062026/hlk_01_asistan
**Analiz:** Detaylı mimari ve kod incelemesi

---

## 1. ÖZET

HLK_01 Asistan projesi, Telegram üzerinden ürün tanıtım reklam videosu üreten yapay zekâ asistanıdır. Proje anayasal bir yapıya sahiptir ve MASTER-001 kurallarıyla yönetilir.

**Temel Özellikler:**
- Telegram bot tabanlı kullanıcı arayüzü
- Multi-step brief toplama akışı
- Dynamic AI agent seçimi
- Constitution Enforcement Engine (CEE) entegrasyonu
- Scene Engine & Delivery modülü
- Research Orchestrator
- Event Registry
- LAC (Live Activity Center)

---

## 2. ANAYASAL MİMARİ

### 2.1 Karar Hiyerarşisi (MASTER-001)

```
1. HLK MASTER RULE BOOK (00_HLK_MASTER_RULE_BOOK.md)
   ↓
2. Global Configuration (GC)
   ↓
3. General Rules (GK)
   ↓
4. Architecture Rules (AR)
   ↓
5. State Engine (SE-007)
   ↓
6. Flow Diagram (FD-008_1)
   ↓
7. Operational Rules (OR)
   ↓
8. Quality Rules (QR)
   ↓
9. Module Rules (MR)
   ↓
10. Kod (Main.py, Services, Handlers)
```

**Not:** Main.py'de 928 satır kod bulunmakta.

### 2.2 State Engine (SE-007)

**Tanımlanan Kullanıcı State'leri:**
- `STATE_START`
- `STATE_SCENE_1`
- `STATE_LANGUAGE_SELECTION`
- `STATE_SCENE_2`
- `STATE_WAIT_PRODUCT_LINK`
- `STATE_LINK_VALIDATION`
- `STATE_LINK_VALIDATED`
- `STATE_BACKGROUND_RESEARCH_RUNNING`
- `STATE_COLLECT_PRODUCT_MATERIALS`
- `STATE_PLATFORM_SELECTION`
- `STATE_VIDEO_RESOLUTION_SELECTION`
- `STATE_VIDEO_DURATION_SELECTION`
- `STATE_AUDIO_SELECTION`
- `STATE_BRIEF_COMPLETED`
- `STATE_SCENARIO_APPROVAL`
- `STATE_PRICING`
- `STATE_PAYMENT_VERIFICATION`
- `STATE_VIDEO_PRODUCTION`
- `STATE_SESSION_COMPLETED`
- `STATE_SESSION_TIMEOUT`
- `STATE_SESSION_CLOSED`

**Event-Action Eşleştirmeleri (SE-007_5):**
- Event'lerin resmi tanım kaynağı: `14_OLAY_KAYIT_MERKEZI.md`
- State → Event → Hedef State tablosu tanımlanmış

**State-Modül Eşleştirmeleri (SE-007_6):**
Her state için belirli modüllerin çalıştırılması tanımlanmış:

```
STATE_START → Oturum başlat, sistem kontrolleri
STATE_SCENE_1 → SAHNE-1 videosu oynat
STATE_LANGUAGE_SELECTION → Dil seçimi UI
STATE_SCENE_2 → SAHNE-2 videosu
STATE_WAIT_PRODUCT_LINK → Ürün linki bekle
STATE_LINK_VALIDATION → Link doğrulama başlat
STATE_LINK_VALIDATED → Link sonucunu kaydet
STATE_BACKGROUND_RESEARCH_RUNNING → Araştırma başlat
STATE_COLLECT_PRODUCT_MATERIALS → Materyal yüklemeleri yönet
STATE_PLATFORM_SELECTION → Platform seçimini göster
STATE_VIDEO_RESOLUTION_SELECTION → Çözünürlük seçimi
STATE_VIDEO_DURATION_SELECTION → Süre seçimi
STATE_AUDIO_SELECTION → Ses seçimi
STATE_BRIEF_COMPLETED → Brief tamamla, senaryo hazırlık
STATE_SCENARIO_APPROVAL → Senaryo paketi hazırla
STATE_PRICING → Fiyat teklifi oluştur (Yönetici + Kullanıcı)
STATE_PAYMENT_VERIFICATION → Ödeme doğrulama
STATE_VIDEO_PRODUCTION → Video üretimi başlat
STATE_SESSION_COMPLETED → Sonuçları sun
STATE_SESSION_TIMEOUT → Timeout işlemleri
STATE_SESSION_CLOSED → Oturumu kapat
```

### 2.3 Flow Diagram (FD-008_1)

**Operasyonel Bağlayıcılık Prensibi:**
- Flow Diagram, yalnızca dokümantasyon değil, **uygulanması zorunlu operasyonel akış referansıdır**
- Tüm sahne davranışları Flow Diagram'da tanımlanmalıdır
- Kod ile Flow Diagram çelişkiliyse Flow Diagram esas alınır
- Flow Diagram'da bulunmayan hiçbir kullanıcı davranışı koda eklenemez

**Sahne Akışı:**
1. SAHNE-01: Hlk asistan giriş videosu + Dil seçimi
2. SAHNE-02: Ürün linki bekleme + Link doğrulama
3. SAHNE-02: Ürün araştırması (background)
4. SAHNE-02: Ek materyal isteme
5. SAHNE-03: Video format seçimi (9:16, 16:9, 1:1)
6. SAHNE-04: Çözünürlük seçimi (480p, 720p, 1080p)
7. SAHNE-05: Video süresi seçimi (4-30sn)
8. SAHNE-06: Tanıtım tarzı seçimi
9. SAHNE-07: Hedef kitle seçimi
10. SAHNE-08: Sesli/Sessiz seçimi
11. SAHNE-09: Seslendirme dili seçimi
12. SAHNE-10: Ses karakteri seçimi
13. SAHNE-11: Özellikle vurgulanacaklar
14. SAHNE-12: Tüm seçimleri göster + Onay
15. SAHNE-13: Brief tamamlandı + Senaryo onay

**Önemli Kurallar:**
- EKRAN SİLİNİR kuralı: Her state geçişiyle birlikte önceki ekranlar temizlenmeli
- Daktilo efektleri ve konuşma balonları Flow Diagram'da tanımlanmalı
- Butonlar ve kullanıcı etkileşimleri Flow Diagram'a bağlı

---

## 3. KOD YAPISI

### 3.1 Ana Dosyalar

```
hlk_projeler_02062026/hlk_01_asistan/
├── main.py (928 satır) — Bot başlatma
├── .env — Environment ayarları
├── .claude/
│   └── CLAUDE.md — Geliştirme talimatı
├── config/
│   ├── settings.py (Settings sınıfı)
│   └── video_paths.py
├── handlers/
│   ├── start.py (1490 satır) — Start handler
│   ├── website.py (95k bayt) — Website linki işleme
│   └── cancel.py
├── services/
│   ├── scene_registry.py (17.5k) — Sahne tanımları
│   ├── scene_engine.py (22.6k) — Scene Engine
│   ├── scene_delivery.py (18.6k) — Scene Delivery
│   ├── research_orchestrator.py (26k) — Research
│   ├── constitution_enforcement.py (17k) — CEE
│   ├── execution_event_collector.py (17.7k) — EEC
│   ├── constitution_cache.py (22.6k) — Cache Manager
│   ├── olay_kayit_merkezi.py (6.8k) — Event Registry
│   ├── lac.py (9.3k) — Live Activity Center
│   ├── descript_generator.py (18k) — Descript
│   ├── hedra_generator.py (5.7k) — Hedra
│   ├── voice_generator.py (4.4k) — Ses üretimi
│   └── render_service.py (7k) — Render
├── utils/
│   ├── state_engine.py — State Engine core
│   └── session_timeout.py — Timeout yönetimi
└── helpers/
    └── typewriter_animation.py (4.5k) — Daktilo efekti
```

### 3.2 Ana Modüller

#### 3.2.1 main.py (Bot Başlatma)

**Özellikler:**
- Telegram bot polling başlatma
- 50+ handler kaydı (command + callback + message)
- Constitution Cache Manager boot
- CEE (PRE-CHECK + POST-CHECK)
- EEC (Execution Event Collector) entegrasyonu
- Event Registry (Olay Kayıt Merkezi) entegrasyonu
- LAC (Live Activity Center) entegrasyonu
- SENDMESSAGE Trace (MASTER-003)

**Handler Registerleri:**
- Command handlers: `/start`, `/cancel`, `/audit`, `/constitution`, `/rules`
- Callback handlers: 30+ button pattern'ı
- Message handlers: TEXT, PHOTO, VIDEO, Document

**Constitutional Boot Sequence:**
1. FAZ 0: Constitution Cache tarama
2. FAZ 1: 18 katmanlı Constitutional Boot
3. FAZ 2: CONSTITUTION_READY kontrolü
4. CEE FAZ-1: PRE-CHECK
5. Bot start event kaydı

#### 3.2.2 handlers/website.py (Website Link İşleme)

**Responsibility:**
- URL validasyonu
- Link doğrulama başlatma
- Arka plan araştırma tetikleme
- Scene Engine devretme
- State geçişleri yönetme

**Önemli Metodlar:**
- `handle_website_link()` — Link al, doğrula, araştırmayı başlat
- `_process_link_background()` — Ağır işlemler arka planda
- `handle_material_choice()` — Materyal seçimi
- `handle_platform_selection()` — Platform seçimi
- `handle_format_selection()` — Format seçimi
- `handle_resolution_selection()` — Çözünürlük seçimi
- `handle_duration_hlk()` — Süre seçimi
- `handle_style_selection()` — Tarz seçimi
- `handle_audience_selection()` — Hedef kitle seçimi
- `handle_voice_language()` — Seslendirme dili
- `handle_voice_character()` — Ses karakteri
- `handle_emphasis()` — Vurgu seçimi
- `handle_scenario_approve/reject()` — Senaryo onayı

**State Flow Map:**
```python
_STATE_FLOW_MAP: dict[str, str] = {
    "STATE_ACTIVE_CONVERSATION": "SAHNE-02",
    "STATE_COLLECT_PRODUCT_MATERIALS": "SAHNE-02",
    # ... (21 state)
}
```

**Flow Diagram Integration:**
- Constitution Cache'ten Flow Diagram verisi okur
- Hardcoded fallback'ler Flow Diagram yoksa
- Amaç: Geliştirilmesi kolay, kurallara bağlı

#### 3.2.3 services/scene_engine.py (Conversation Scene Engine)

**Responsibility:**
- State → Flow Diagram sahne eşleştirme
- Scene içerik oluşturma
- ScenePayload üretme
- Scene Delivery entegrasyonu

**Yaşam Döngüsü:**
```
1. STATE'i belirle
2. FD-008_1'den sahne kaydını bul
3. Scene içeriğini oluştur (SceneDefinition.text)
4. ScenePayload üret
5. Delivery'e gönder
6. Sonucu logla
```

**Temel Metod:**
- `produce_and_deliver()` — Bir sahneyi üretir ve teslim eder

**Flow Diagram Önbellekleme:**
- State içi tekrar okumaları önlemek için
- `_flow_cache` key'i altında saklanır
- State değiştiğinde önbellek geçersiz

#### 3.2.4 services/scene_delivery.py (Scene Delivery Module)

**Responsibility:**
- Telegram API üzerinden sahne teslimi
- EKRAN SİLİNİR temizliği
- ScenePayload → Telegram mesaj

**Temel Sınıflar:**
- `DeliveryStatus` enum: PENDING, DELIVERED, FAILED, RETRYING
- `ScenePayload` dataclass: Teslim edilecek veri
- `DeliveryReceipt` dataclass: Teslimat sonucu
- `SceneDeliveryModule` sınıfı: Teslim modülü

**Önemli Metodlar:**
- `send_and_track()` — Mesaj gönder + otomatik tracking
- `cleanup_chat()` — Önceki sahneyi temizle
- `replace_ui_component()` — Active UI Component (ekranı güncelle)
- `register_user_message()` — Kullanıcı mesajını kalıcı temizle

**Clean up Mekanizması:**
- `_pending_cleanup_ids`: Bekleyen mesaj ID'leri
- `_user_msg_ids`: Kalıcı kullanıcı mesajları
- Her cleanup'ta TÜM mesajlar temizlenmeli (FD-008_1)

#### 3.2.5 services/research_orchestrator.py (Research Orchestrator)

**Responsibility:**
- Ürün linki doğrulandıktan sonra araştırma görevini yönetme
- AR-002_1: Sayfa ön analizi
- AR-002_3: Ajan aday seçimi, puanlama, sıralama
- AR-002_10: Bağımsız karar alanları
- AR-002_7: Dinamik görevlendirme
- Master: "Araştırma Öncelik Hiyerarşisi"

**Temel Sınıf:**
- `ResearchCandidate`: Ajan adayı + değerlendirme kriterleri

**Ajan Seçim Kriterleri (AR-002_3):**
```python
def _score(c: ResearchCandidate) -> float:
    return (
        c.uygunluk * 1.0 +
        c.dogruluk * 0.8 +
        c.guvenilirlik * 0.8 +
        c.kalite * 1.0 +
        c.hiz * 0.6 +
        c.guncellik * 0.7 +
        (10 - c.maliyet) * 0.3
    )
```

**Öncelik Sırası (Master):**
1. Ürün görseli araştırması
2. Marka analizi
3. Ürün açıklamaları
4. Hedef müşteri analizi
5. Marka dili ve tarzı
6. Fiyat segmenti
7. Rakip analizi
8. Reklam stratejisi hazırlığı

**Araştırma Modülleri:**
1. Ürün görseli araştırması (M1)
2. Marka analizi (M2)
3. Ürün açıklamaları (M3)
4. Hedef müşteri (M4)
5. Marka dili (M5)
6. Fiyat segmenti (M6)
7. Rakip analizi (M7)
8. Reklam stratejisi (M8)

---

## 4. KEEPER - GÖZETLENECEK BÖLGELER

### 4.1 State Engine (SE-007_3/4/5/6) Doğrulaması

**Sorun:** State tanımlanmış ama belirlenen modüller çalıştırılıyor mu?

**Gerekli Kontrol:**
1. Tüm 21 state için state-modül ilişkisi kontrol edilmeli
2. Flow Diagram ile uyumluluk doğrulanmalı
3. Event-Action referansları karşılaştırılmalı

**Raporlama Yöntemi:**
```
State → Modül Eşleşmesi → Runtime'da Çalışır mı?
───────────────────────────────────────────────
STATE_START → Oturum başlat
STATE_SCENE_1 → SAHNE-1 videosu
STATE_LANGUAGE_SELECTION → Dil seçimi UI
STATE_SCENE_2 → SAHNE-2 videosu
STATE_WAIT_PRODUCT_LINK → Ürün linki bekle
STATE_LINK_VALIDATION → Link doğrulama
STATE_LINK_VALIDATED → Link sonucunu kaydet
STATE_BACKGROUND_RESEARCH_RUNNING → Araştırma başlat
STATE_COLLECT_PRODUCT_MATERIALS → Materyal yüklemeleri
STATE_PLATFORM_SELECTION → Platform seçimi
STATE_VIDEO_RESOLUTION_SELECTION → Çözünürlük seçimi
STATE_VIDEO_DURATION_SELECTION → Süre seçimi
STATE_AUDIO_SELECTION → Ses seçimi
STATE_BRIEF_COMPLETED → Brief tamamla
STATE_SCENARIO_APPROVAL → Senaryo paketi
STATE_PRICING → Fiyat teklifi
STATE_PAYMENT_VERIFICATION → Ödeme doğrulama
STATE_VIDEO_PRODUCTION → Video üretimi
STATE_SESSION_COMPLETED → Sonuçları sun
STATE_SESSION_TIMEOUT → Timeout işlemleri
STATE_SESSION_CLOSED → Oturumu kapat
```

### 4.2 Flow Diagram Operasyonel Bağlayıcılık Prensibi (FD-008_1)

**Sorun:** Flow Diagram ile çalışan kod arasında çelişki var mı?

**Kontrol Noktaları:**
1. **SAHNE-01:** Video oynatma → video silinme
2. **SAHNE-02:** Link doğrulama → arka plan araştırması
3. **SAHNE-03:** Video format seçimi
4. **SAHNE-04:** Çözünürlük seçimi
5. **SAHNE-05:** Süre seçimi (4-30sn validation)
6. **SAHNE-06:** Tarz seçimi
7. **SAHNE-07:** Hedef kitle seçimi
8. **SAHNE-08:** Sesli/Sessiz seçimi
9. **SAHNE-09:** Seslendirme dili
10. **SAHNE-10:** Ses karakteri
11. **SAHNE-11:** Özellikle vurgulanacaklar
12. **SAHNE-12:** Tüm seçimleri göster + Onay
13. **SAHNE-13:** Brief tamamlandı + Senaryo onay

**Doğrulama:** Her state için Flow Diagram'daki operasyonel talimat kodda uygulanıyor mu?

### 4.3 EKRAN SİLİNİR Kuralı (FD-008_1)

**Sorun:** Her state geçişiyle birlikte ekran temizliği yapılıyor mu?

**Kontrol Noktaları:**
1. `scene_delivery.cleanup_chat()` çağrıldı mı?
2. Manuel mesaj silme işlemleri eksik mi?
3. Typewriter mesajları temizlendi mi?
4. Voice mesajları temizlendi mi?

**Örnek Senaryo:**
```
STATE_WAIT_PRODUCT_LINK
→ Event: LINK_RECEIVED
→ Handler: scene_delivery.cleanup_chat()
→ Result: TÜM önceki mesajlar silinmeli
```

### 4.4 Event Registry (OLAY-001 ~ OLAY-044)

**Sorun:** Event'ler 14_OLAY_KAYIT_MERKEZI.md'de tanımlanmış mı?

**Kontrol:**
1. `UserEvent` enum değerleri
2. Event Registry kayıtları
3. Event üretim noktaları

**Örnek:**
- `EVENT_SESSION_STARTED` → STATE_START → STATE_SCENE_1
- `EVENT_PRODUCT_LINK_RECEIVED` → STATE_WAIT_PRODUCT_LINK → STATE_LINK_VALIDATION
- `EVENT_LINK_VALIDATED` → STATE_LINK_VALIDATION → STATE_LINK_VALIDATED

### 4.5 Constitution Enforcement Engine (CEE)

**Sorun:** CEE denetimleri her önemli noktada çalışıyor mu?

**Kontrol Noktaları:**
1. **PRE-CHECK (Bot başlatma):** main.py post_init
2. **POST-CHECK (Link doğrulama):** website.py handle_website_link
3. **POST-CHECK (Her önemli event):** event_registry.register_from_eec()

**Raporlama:**
```
Event → CEE PRE-CHECK → CEE POST-CHECK → Event Registry
─────────────────────────────────────────────────────
Bot Start → PASS → PASS → OLAY-001
Link Valid → PASS → PASS → OLAY-004
Material Upload → PASS → PASS → OLAY-007
```

### 4.6 Ajan Seçim ve Puanlama (AR-002_3)

**Sorun:** Ajan seçimi gerçekten dinamik mi?

**Kontrol Noktaları:**
1. `_score()` fonksiyonu kullanılıyor mu?
2. Ayanlar gerçekten puanlanıyor mu?
3. Puan bazlı sıralama yapılıyor mu?
4. Başarısız ajanlar devrediliyor mu?

**Örnek:**
```python
# Research Candidate
code: str (örn: "google_search")
name: str
executor: Callable
uygunluk: int = 0  # Ürün kategorisine uygunluk
dogruluk: int = 0  # Doğruluk oranı
guvenilirlik: int = 0  # Güvenilirlik
kalite: int = 0  # Kalite
hiz: int = 0  # Hız
guncellik: int = 0  # Güncellik
maliyet: int = 0  # Maliyet
priority: float = _score(candidate)
```

### 4.7 Daktilo Efektleri ve Konuşma Balonları

**Sorun:** Konuşmalar HLK tarafından oluşturuluyor mu, yoksa Flow Diagram'dan mı geliyor?

**Kontrol:**
1. `scene_def.text` kullanılıyor mu?
2. `flow_section["speech_directive"]` kullanılıyor mu?
3. Hardcoded konuşmalar var mı?

**Örnek (scene_engine.py):**
```python
if scene_def and scene_def.text:
    scene_text = scene_def.text  # SceneDefinition'dan
elif flow_section and flow_section.get("speech_directive"):
    speech = flow_section["speech_directive"]  # Flow Diagram'dan fallback
```

### 4.8 Session Timeout (OR-004_9)

**Sorun:** Session timeout kuralları uygulandı mı?

**Kontrol Noktaları:**
1. Zamanlayıcı başlatıldı mı? (`start_timer()`)
2. Timeout sonrası state geçişi yapılıyor mu?
3. EVENT_TIMEOUT_REACHED üretiliyor mu?

**Zamanlayıcı Konumları:**
- Link alındıktan sonra
- Active conversation başladığında
- Material toplama aşamasında

---

## 5. MİMARİ AKIŞŞ

### 5.1 User Request → State → Engine → Scene → Delivery

```
Kullanıcı (Telegram)
   ↓
Handler (website.py, start.py)
   ↓
StateEngine.fire(UserEvent)
   ↓
UserState Değişimi
   ↓
Scene Engine (scene_engine.py)
   ↓
ScenePayload
   ↓
Scene Delivery (scene_delivery.py)
   ↓
Telegram API
   ↓
Kullanıcı
```

### 5.2 Research Orchestrator Flow

```
Link Alındı
   ↓
UserEvent.PRODUCT_LINK_RECEIVED
   ↓
UserState.LINK_VALIDATION
   ↓
Araştırma Görevi Başlat (research_orchestrator.py)
   ↓
Sayfa Ön Analizi (AR-002_1)
   ↓
Ajan Aday Seçimi (AR-002_3)
   ↓
Puanlama ve Sıralama
   ↓
Dinamik Görevlendirme (AR-002_7)
   ↓
Araştırma Modülleri Çalıştır
   ↓
Result → Brief
```

### 5.3 Constitutional Boot Flow

```
Bot Başlatma (main.py post_init)
   ↓
Constitution Cache Tarama
   ↓
18 Katmanlı Constitutional Boot
   ↓
CONSTITUTION_READY Kontrolü
   ↓
CEE FAZ-1: PRE-CHECK
   ↓
Event: BOT_STARTED
   ↓
Event Registry Kaydı
   ↓
Runtime'da CEE POST-CHECK
   ↓
Runtime'da Event Registry Kaydı
```

---

## 6. ÖZET

### 6.1 Güçlü Yönler

✅ **Anayasal Mimarisi:** MASTER-001 karar hiyerarşisi net, kod / dokümantasyon ayrımı açık

✅ **State Engine:** State → Event → Modül ilişkileri tanımlanmış

✅ **Flow Diagram:** Operasyonel talimatlar net, EKRAN SİLİNİR kuralı uygulanıyor

✅ **CEE + EEC:** Anayasal denetim entegrasyonu var

✅ **Event Registry:** Tüm olaylar kayıt altında

✅ **Dinamik Ajan Seçimi:** AR-002_3 puanlama sistemi var

✅ **Scene Engine + Delivery:** Sahne üretim + teslim mekanizması iyi

### 6.2 Geliştirilmesi Gereken Bölümler

⚠️ **Runtime Aktiflik:** MASTER-011 — Kod var mı, çalışıyor mu?

⚠️ **EKRAN SİLİNİR:** State geçişleriyle birlikte tüm temizlik yapılıyor mu?

⚠️ **Event Registry:** Event'ler gerçekten tanımlandığı gibi üretiliyor mu?

⚠️ **CEE Denetimi:** Her önemli noktada CEE çalışıyor mu?

⚠️ **Daktilo Efektleri:** Konuşmalar HLK tarafından mı üretiliyor?

⚠️ **Session Timeout:** Zamanlayıcılar düzgün çalışıyor mu?

⚠️ **Ajan Seçimi:** Puanlama gerçekten kullanılıyor mu?

---

## 7. SONUÇ

HLK_01 Asistan projesi, anayasal bir yapıya sahip kapsamlı bir sistemdir. State Engine, Flow Diagram, CEE, EEC ve Event Registry entegrasyonu projenin kalitesini yükseltir.

**Önerilen Aksiyonlar:**
1. Detaylı runtime denetimi yap
2. Flow Diagram ile kod uyumluluğunu doğrula
3. EKRAN SİLİNİR kuralının tüm noktalarda uygulanmasını kontrol et
4. Event Registry'yi tam tanımla ve doğrula
5. Session timeout'ları test et
6. Daktilo efektlerinin HLK tarafından üretilip üretilmediğini doğrula
7. CEE denetimlerini her önemli noktada çalıştır

---

**Rapor Hazırlayan:** Claude (HLK)
**Tarih:** 2026-07-08
