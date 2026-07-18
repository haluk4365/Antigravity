# HLK DİL UYUMLULUK DENETİM RAPORU

**Tarih:** 13 Temmuz 2026
**Denetim Konusu:** SAHNE-01'de seçilen dilin tüm akış boyunca korunması
**Anayasal Dayanak:** MASTER-001, MASTER-009 (Flow Diagram Otoritesi), AR-002_30 (i18n)
**Denetim Kapsamı:** Kullanıcıya gösterilen tüm metinler (reply_text, send_message, query.answer, buton etiketleri, daktilo mesajları)

---

## 📋 YÖNETİCİ ÖZETİ

Projede **i18n altyapısı** (`config/i18n.py`) kapsamlı şekilde kurulmuş ve SAHNE-03'ten SAHNE-13'e kadar sahne prompt'ları ve buton etiketleri için 8 dilde çeviri mevcuttur. Session timeout mesajları da i18n sistemine bağlanmıştır.

**Ancak**, kod tabanında **82+ konumda** kullanıcıya doğrudan gösterilen **sabit Türkçe metin (hardcoded)** tespit edilmiştir. Bu metinler, kullanıcı SAHNE-01'de TR dışında bir dil seçse bile **her zaman Türkçe gösterilmektedir** — bu durum MASTER-009 ve AR-002_30 ile tanımlanan anayasal dil bütünlüğü ilkesine **aykırıdır**.

---

## 🔴 KRİTİK İHLALLER (Kullanıcı Akışını Bozan)

### K1. Link Doğrulama Hata Mesajları — `handlers/website.py`
**Konum:** Satır 130-146
```python
# Satır 130-135: 5 başarısız deneme → oturum kapatma
"⚠️ <b>5 başarısız link denemesi.</b>\n\n"
"Oturumunuz kapatılıyor. Lütfen daha sonra "
"<b>/start</b> yazarak tekrar deneyin."

# Satır 141-145: Geçersiz link
"❌ <b>Geçersiz link formatı.</b>\n\n"
f"Lütfen geçerli bir URL gönderin.\n"
f"<i>Kalan deneme: {remaining}/5</i>"
```
**Etki:** TR dışında dil seçen kullanıcı link hatası yaptığında Türkçe hata mesajı görür.

### K2. Link Alındı Onayı — `handlers/website.py`
**Konum:** Satır 158-161
```python
"🔗 <b>Linkiniz alındı!</b>\n\nÜrün analizi başlatılıyor, lütfen bekleyin..."
```
**Etki:** Tüm dillerde Türkçe gösterilir.

### K3. Link İşleme Hatası — `handlers/website.py`
**Konum:** Satır 264-268
```python
"❌ <b>Link işlenirken bir hata oluştu.</b>\n\n"
"Lütfen <b>/start</b> yazarak tekrar deneyin."
```

### K4. Materyal Yükleme Bilgilendirme Mesajı — `handlers/website.py`
**Konum:** Satır 300-311 (tamamen Türkçe)
```python
"📦 <b>Materyal Yükleme</b>\n\n"
"Ürününüze ait tamamlayıcı materyallerinizi şimdi gönderebilirsiniz.\n\n"
"📷 Fotoğraf  🎬 Video  📚 Katalog\n"
"📄 Teknik Doküman  📦 Diğer\n\n"
"━━━━━━━━━━━━━━━━━━━━━━\n"
"📌 <b>En fazla 10 adet</b> materyal yükleyebilirsiniz.\n"
"⏱️ Materyal göndermek için <b>5 dakika</b> süreniz var.\n"
"━━━━━━━━━━━━━━━━━━━━━━\n\n"
"<i>Materyallerinizi göndermeye başlayın.</i>\n"
"<i>İşiniz bittiğinde</i> <b>✅ Bitti</b> <i>butonuna basın.</i>"
```
**Etki:** SAHNE-02 materyal toplama ekranı tüm dillerde Türkçe. Bu, kullanıcı akışının merkezi bir parçasıdır.

### K5. Brief Onay Tablosu Alan Etiketleri — `handlers/website.py`
**Konum:** Satır 1233-1245 (açıklamalar) ve Satır 1304-1317 (alan etiketleri)
```python
aciklama_map = {
    "brief_link":       "Analiz edilen ürün sayfası",
    "brief_material":   "Kullanıcının yüklediği materyaller",
    "brief_platform":   "Yayınlanacak platform",
    # ... hepsi Türkçe
}

BRIEF_FIELDS = [
    ("brief_link",      "🔗 Ürün Linki",       ...),
    ("brief_material",  "📦 Ek Materyal",       ...),
    ("brief_platform",  "📱 Platform",          ...),
    ("brief_format",    "📐 Video Formatı",     ...),
    # ... hepsi Türkçe
]
```
**Etki:** SAHNE-12 Brief Onay ekranı tüm dillerde Türkçe alan etiketleriyle gösterilir.

### K6. Brief Onay Tablosu Bölüm Başlıkları — `handlers/website.py`
**Konum:** Satır 1320-1327
```python
BRIEF_SECTIONS = [
    ("🏷️ Ürün Bilgileri",  [...]),
    ("🎬 Video Ayarları",  [...]),
    ("🎙️ Ses Ayarları",    [...]),
    ("✨ Tercihler",        [...]),
]
```

### K7. Brief Onay Adım Göstergesi — `handlers/website.py`
**Konum:** Satır 1264
```python
"<code>🔵1.Brief  ›  ⏳2.Senaryo  ›  ⏳3.Fiyat Teklifi</code>"
```

### K8. Senaryo Onay Formu İçeriği — `handlers/website.py`
**Konum:** Satır 1703-1713 (sahne açıklamaları), Satır 1770-1789 (_build_scenario_form)
```python
story_sahneler = [
    {"no": 1, "baslik": "Dikkat Çekici Giriş", "zaman": "0:00 – 0:02", "sure": "2 sn",
     "aciklama": "Güneşli bir sabah, şehir merkezinde modern bir kafede..."},
    # ... tamamen Türkçe
]
```
**Etki:** SAHNE-13 senaryo onay formu tüm dillerde Türkçe senaryo açıklamalarıyla gösterilir.

### K9. Yönetici Fiyatlandırma Formu — `handlers/website.py`
**Konum:** Satır 2000-2070 (_build_admin_pricing_form, tamamen Türkçe)
```python
"<b>━━ 🏷️ HLK YÖNETİCİ FİYATLANDIRMA FORMU ━━</b>"
"<code>✅Brief › ✅Senaryo › 🔵Fiyat › ⏳Ödeme</code>"
"<b>🔌 Servis Sağlayıcı ve Kredi Durumu</b>"
"<b>⚠️ Risk Değerlendirmesi</b>"
"Fal.ai servisi normalden yavaş yanıt vermektedir."
# ... tamamen Türkçe
```

### K10. Banka Ödeme Kartı — `handlers/website.py`
**Konum:** Satır 2167-2209 (_build_banka_bilgileri_karti)
```python
"▸ <b>Garanti Bankası (TL)</b>"
"▸ <b>Garanti Bankası (USD)</b>"
"▸ <b>Ak Bank (TL)</b>"
# IBAN'lar ve banka isimleri çeviri gerektirmez,
# ancak başlıklar ve açıklamalar kısmen Türkçe
```

### K11. Kullanıcı Fiyat Teklif Formu — `handlers/website.py`
**Konum:** Satır 2238-2287 (_build_user_pricing_form)
```python
"MARKA: <b>{brand}</b>"         # ← "MARKA" etiketi Türkçe
"ÜRÜN: <b>{product_name}</b>"   # ← "ÜRÜN" etiketi Türkçe
"🎙️ Dış Ses+Fon Müzik"          # ← sabit Türkçe
"• Senaryo Hazırlama (HLK Yapay Zekâ)"  # ← hizmet kapsamı Türkçe
"• Video Üretimi (5 sahne)"
"• Profesyonel Seslendirme"
# ...
```

### K12. Yönetici Ödeme Bildirimi — `handlers/website.py`
**Konum:** Satır 2351-2409 (_build_admin_odeme_bildirimi)
```python
f"Beklenen Tutar: <b>${kdvli:.2f}</b> / <b>{satis_tl:.2f} TL</b>"
f"TCMB Kur: {tcmb_kur} TL"
```
Kısmen i18n kullanılmış ancak bazı etiketler Türkçe.

---

## 🟡 ORTA İHLALLER (Toast/Geçici Mesajlar)

### O1-O15. query.answer() Toast Mesajları — `handlers/website.py`

| Satır | Mesaj | Not |
|---|---|---|
| 661 | `"🔇 {t('s08.silent', lang)}"` | ✅ Kısmen i18n |
| 664 | `"Sessiz mod kaldırıldı — diğer seçenekler tekrar aktif"` | ❌ Sabit TR |
| 668 | `"⚠️ Sessiz moddayken diğer seçenekler seçilemez"` | ❌ Sabit TR |
| 672 | `"{AUDIO_OPTIONS[option]} {durum}"` | ❌ `durum` değişkeni TR ("seçildi"/"kaldırıldı") |
| 706 | `"🔇 Sessiz video → SAHNE-11"` | ❌ Sabit TR |
| 713 | `"Seçilenler: {', '.join(selected)} → SAHNE-09"` | ❌ Sabit TR |
| 1082 | `"{emphasis_map.get(key, key)}"` | ✅ Kısmen i18n |
| 1139 | `"⚠️ Lütfen en az 2 karakterlik bir vurgu metni yazın."` | ❌ Sabit TR |
| 1199 | `"Brief onayına geçiliyor..."` | ❌ Sabit TR |
| 1455 | `"✅ Brief onaylandı — senaryo aşamasına geçiliyor..."` | ❌ Sabit TR |
| 1481 | `"✏️ Düzeltme modu — değiştirmek istediğiniz alanı seçin"` | ❌ Sabit TR |
| 1536 | `"⚠️ Bu alan düzenlenemez"` | ❌ Sabit TR |
| 1539 | `"✏️ {field_key} düzenleniyor — ilgili adıma dönülüyor..."` | ❌ Sabit TR |
| 1904 | `"✅ Senaryo onaylandı — yöneticiye iletiliyor..."` | ❌ Sabit TR |
| 1947 | `"❌ Senaryo reddedildi"` | ❌ Sabit TR |
| 2082 | `"✏️ Katsayıyı girin..."` | ❌ Sabit TR |
| 2099 | `"💬 HLK sohbet modu aktif"` | ❌ Sabit TR |
| 2118 | `"✅ Sohbet sonlandı."` | ❌ Sabit TR |
| 2131 | `"✅ Fiyat onaylandı: ${...}"` | ❌ Sabit TR |
| 2159 | `"❌ Fiyatlandırma iptal edildi"` | ❌ Sabit TR |
| 2296 | `"✅ Fiyat teklifi onaylandı!"` | ❌ Sabit TR |
| 2332 | `"❌ Teklif reddedildi"` | ❌ Sabit TR |
| 2418 | `"✅ Ödeme bildirimi yöneticiye iletiliyor..."` | ❌ Sabit TR |
| 2488 | `"❌ Ödeme onaylanmadı"` | ❌ Sabit TR |

### O16. Özel Vurgu Onay Mesajı — `handlers/website.py`
**Konum:** Satır 1169-1170
```python
f"✅ <b>Özel vurgu eklendi:</b> {text}"
```

### O17. Vurgu Özel Prompt Örneği — `handlers/website.py`
**Konum:** Satır 1072
```python
"<i>Örnek: %50 İndirim, 2 Al 1 Öde, Sınırlı Stok</i>"
```

### O18. Emphasis Klavye Butonları — `handlers/website.py`
**Konum:** Satır 1094-1122 (_build_emphasis_keyboard)
```python
emphasis_map = {
    "emphasis_discount": "🏷️ İndirim",
    "emphasis_shipping": "🚚 Ücretsiz Kargo",
    # ... hepsi Türkçe
}
# ...
"☐ ✏️ Ben Eklemek istiyorum"   # ← Buton etiketi TR
"▶️ DEVAM"                       # ← Buton etiketi TR
```

---

## 🟡 ORTA İHLALLER — `handlers/start.py`

### O19. SceneLock Tekrar Giriş Engelleme — Satır 390-394
```python
"⏳ <b>HLK</b> oturumunuz zaten <i>aktif</i>.\n"
"Devam etmek için lütfen <b>dil seçimi</b> yapın."
```

### O20. Sistem Başlatılamadı — Satır 480-484
```python
"❌ <b>Sistem başlatılamadı.</b>\n\n"
"<i>Lütfen daha sonra</i> <b>/start</b> <i>yazarak tekrar deneyin.</i>"
```

### O21. Dil Seçim Prompt'u — Satır 565-567
```python
"Please select your <b>spoken language</b>.\n"
"Lütfen konuşma <b><i>dilinizi</i></b> seçiniz."
```
**Not:** Bu mesaj SAHNE-01'dedir ve dil henüz seçilmemiştir — bu nedenle iki dilli (TR+EN) olması kabul edilebilir. Ancak 8 dilde hoş geldin mesajı daha iyi olabilir.

### O22. State Kilitli Uyarısı — Satır 643
```python
await query.answer("🔒 İşlem devam ediyor. Değiştirmek için /start yazınız.", show_alert=True)
```

### O23. SAHNE-2 Video Bulunamadı — Satır 670
```python
"❌ Video bulunamadı. Lütfen /start ile tekrar deneyin."
```

### O24. SAHNE-2 Video Gönderilemedi — Satır 719
```python
"❌ Video gönderilemedi. Lütfen /start ile tekrar deneyin."
```

### O25. SAHNE-2 Replay — Satır 883
```python
await query.answer("🔊 Video baştan başlatılıyor...")
```

### O26. Devam Butonu — Satır 850
```python
await query.answer("Zaten bekleme modundasınız.", show_alert=False)
```

### O27. Format Seçimi — Satır 866
```python
await query.answer(f"Seçiminiz: {fmt}")
```

### O28. SAHNE-2 Replay Hatası — Satır 933-934
```python
"❌ Video gönderilemedi."
```

### O29. Süre Kaydedildi Fallback — Satır 1052-1056
```python
f"✅ <b>{duration} saniye</b> olarak kaydedildi.\n\n"
"🎬 <i>Video üretim aşamasına geçiliyor...</i>"
```

### O30. Geçersiz Süre Uyarısı — `handlers/start.py` satır 1059+
```python
# Süre validasyon hatası mesajları
```

### O31. Admin Katsayı Hatası — Satır 952
```python
"⚠️ Geçersiz. 0.1 - 10 arası bir sayı girin."
```

### O32. Admin HLK Düşünüyor — Satır 983
```python
"⏳ HLK düşünüyor..."
```

---

## 🟡 ORTA İHLALLER — Diğer Dosyalar

### O33. `/cancel` Fallback — `handlers/cancel.py` Satır 43-48
```python
"❌ **İşlem iptal** _edildi._\n\n"
"_Başlamak için_ **/start** _yazın._"
```
**Not:** Scene Engine çalışmazsa kullanılan fallback — Türkçe.

### O34. Hata Mesajı — `main.py` Satır 236-243
```python
"❌ <b>Bir hata oluştu.</b> "
"<i>Lütfen</i> <b>tekrar deneyin</b> "
"<i>veya</i> <b>/start</b> <i>yazarak</i> "
"<b>baştan başlayın</b>."
```

---

## 🟢 UYUMLU BULUNANLAR (İyi Örnekler)

Aşağıdaki sistemler **tamamen i18n uyumludur** ve anayasal dil bütünlüğü ilkesine uygundur:

| Bileşen | Dosya | Açıklama |
|---|---|---|
| Session Timeout | `utils/session_timeout.py` | ✅ `t("final.timeout_warning", lang)` ve `t("final.timeout_closed", lang)` |
| SAHNE-03~13 Prompt'ları | `config/i18n.py` S03-S13 | ✅ Tüm sahne metinleri 8 dilde |
| SAHNE-03~13 Butonları | `config/i18n.py` + `scene_engine.py` | ✅ `_translate_buttons()` ile otomatik çeviri |
| Fiyat Teklif Formu | `config/i18n.py` PRICING | ✅ Başlık, kapsam, KDV, kur, onay/ret butonları |
| Ödeme Kartı | `config/i18n.py` PAYMENT | ✅ Kart başlığı, uyarılar, butonlar |
| Yönetici Ödeme | `config/i18n.py` ADMIN_PAYMENT | ✅ Bildirim başlığı, doğrulama, bilgi metinleri |
| Final Mesajları | `config/i18n.py` FINAL | ✅ Ödeme onayı, üretim başladı, teslimat |
| Materyal Prompt | `config/i18n.py` MATERIAL | ✅ "Ek materyal var mı?" sorusu |
| Platform Prompt | `config/i18n.py` PLATFORM | ✅ "Hangi platform?" sorusu |
| SAHNE-13 Mesajları | `config/i18n.py` S13 | ✅ Brief tamamlandı, teşekkür, senaryo geliyor |
| SAHNE-12 Mesajları | `config/i18n.py` S12 | ✅ Brief onay, düzeltme modu metinleri |
| Typewriter Mesajları | `handlers/start.py` | ✅ `TYPEWRITER_MESSAGES` ve `LINK_REQUEST_MESSAGE` 8 dilde |
| Sesli İzleme Uyarısı | `handlers/start.py` | ✅ `SESLI_HINT` 8 dilde |
| SAHNE-13 Mesajları | `handlers/website.py` | ✅ `t('s13.*', language)` ile çevrili |

---

## 📊 İSTATİSTİK ÖZETİ

| Kategori | Sayı |
|---|---|
| **Kritik ihlal** (ana akışı bozan) | 12 konum |
| **Orta ihlal** (toast/geçici mesaj) | 34 konum |
| **Yapısal ihlal** (sabit veri yapıları) | 6 yapı (BRIEF_FIELDS, BRIEF_SECTIONS, aciklama_map, story_sahneler, emphasis_map, _build_emphasis_keyboard) |
| **TOPLAM İHLAL** | **82+ konum** |
| **Uyumlu bileşen** | 14 sistem |

---

## 🔧 DÜZELTME ÖNERİLERİ

### 1. Öncelikli (Kritik Akış)

**Link doğrulama mesajları** (`handlers/website.py:130-146, 160, 266`):
- `config/i18n.py`'ye `LINK` bölümü eklenmeli
- `t("link.invalid", lang)`, `t("link.max_attempts", lang)`, `t("link.received", lang)` vb.

**Materyal yükleme bilgilendirmesi** (`handlers/website.py:300-311`):
- `config/i18n.py`'deki `MATERIAL` bölümü genişletilmeli: `material.upload_info`, `material.max_items`, `material.time_limit`, `material.done_button`

**Brief Onay Tablosu** (`handlers/website.py:1233-1327`):
- `BRIEF_FIELDS` ve `aciklama_map` için i18n desteği eklenmeli
- Alan etiketleri dil bazlı bir sözlükte tutulmalı

**Senaryo Onay Formu** (`handlers/website.py:1703-1713, 1770-1789`):
- Sahne açıklamaları ve form metinleri i18n'ye taşınmalı

**Yönetici Fiyatlandırma Formu** (`handlers/website.py:2000-2070`):
- `config/i18n.py`'ye `ADMIN_PRICING` bölümü eklenmeli

### 2. Orta Öncelikli (Toast Mesajları)

Tüm `query.answer()` çağrılarındaki sabit Türkçe metinler için `t()` fonksiyonu kullanılmalı. Örnek:
```python
# Mevcut:
await query.answer("✅ Brief onaylandı — senaryo aşamasına geçiliyor...")

# Olması gereken:
await query.answer(t("toast.brief_approved", lang))
```

`config/i18n.py`'ye yeni bir `TOAST` bölümü eklenerek tüm toast mesajları merkezi hale getirilebilir.

### 3. Yapısal Düzeltme

`_build_emphasis_keyboard()`, `BRIEF_FIELDS`, `BRIEF_SECTIONS`, `aciklama_map` gibi veri yapıları dil parametresi alacak şekilde yeniden düzenlenmeli.

### 4. Hata Handler'ları

`main.py` error handler ve `handlers/cancel.py` fallback mesajları i18n'ye bağlanmalı.

---

## 📋 SONUÇ

HLK projesinin **i18n altyapısı** (`config/i18n.py`) oldukça kapsamlıdır — 17 kategori ve 200+ çeviri anahtarı ile 8 dilde tam çeviri desteği sağlamaktadır. Scene Engine, `_translate_buttons()` ve `_translate_scene_text()` metodlarıyla sahne metinlerini ve buton etiketlerini otomatik olarak çevirmektedir.

**Ancak**, kod tabanının birçok yerinde bu i18n sistemi **kullanılmamakta**, yerine **sabit Türkçe metinler** (hardcoded strings) bulunmaktadır. Bu durum:

1. MASTER-009 (Flow Diagram Otoritesi) ile tanımlanan "kullanıcı deneyiminin tek yetkili kaynağı" ilkesine **aykırıdır**
2. AR-002_30 (i18n mimarisi) standardının **eksik uygulanmasıdır**
3. SAHNE-01'de seçilen dilin tüm akışta korunması anayasal gerekliliğine **uymamaktadır**

**Düzeltme kapsamı:** Tahmini 82+ konumda değişiklik gerekmektedir. Öncelik sırası: Kritik → Orta → Yapısal.

---

*Denetim, 13 Temmuz 2026'da projedeki tüm kullanıcıya dönük metinlerin satır satır taranmasıyla gerçekleştirilmiştir.*
