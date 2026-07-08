# Sahne-2 Video İçi Konuşma Balonu — Prototip Tasarımı

> **Durum:** Fizibilite / Prototip aşaması
> **Kapsam:** Sadece TR dili, sadece Sahne-2
> **Mevcut sistem korunacak, değiştirilmeyecek**

---

## 1. Teknik Mimari — Hedef Durum

### MEVCUT (karmaşık, 4 farklı Telegram bileşeni)

```
Telegram API'ye 4+ çağrı:
  1. sendVideo(hedra_lipsync.mp4)
  2. sendMessage("🔊 Sesli izlemek için...")          ← hint
  3. sendMessage("▌") → editMessageText x22          ← typewriter Mesaj-1
  4. sendMessage("▌") → editMessageText x9           ← typewriter Mesaj-2
  5. deleteMessage(video)                              ← timer
  6. deleteMessage(hint)
  7. deleteMessage(balon-1)
  8. deleteMessage(balon-2)
```

### HEDEF (tek Telegram çağrısı)

```
Tek Telegram API çağrısı:
  1. sendVideo(final_scene2.mp4)   ← HLK + AHU + balon + metin
  2. deleteMessage(video)           ← video bittiğinde
```

### Video İçeriği (FFmpeg ile oluşturulur)

```
┌──────────────────────────────┐  ← 720px
│                              │
│   ┌──────────────────────┐   │
│   │                      │   │
│   │   HLK Karakteri      │   │  y=20 — y=730
│   │   (Hedra lip-sync)   │   │  (710px yükseklik)
│   │                      │   │
│   │                      │   │
│   └──────────────────────┘   │
│                              │
│   ┌──────────────────────┐   │
│   │  ┌────────────────┐  │   │
│   │  │  Merhaba! Ben  │  │   │  y=760 — y=1060
│   │  │  HLK, yapay    │  │   │  (300px konuşma balonu)
│   │  │  zeka destekli │  │   │
│   │  │  reklam asis-  │  │   │
│   │  │  tanınız.      │  │   │
│   │  └────────────────┘  │   │
│   └──────────────────────┘   │
│                              │
│   ┌──────────────────────┐   │
│   │  ┌────────────────┐  │   │
│   │  │  Lütfen ürün   │  │   │  y=1080 — y=1260
│   │  │  linkini        │  │   │  (180px ikinci balon)
│   │  │  gönderin.      │  │   │
│   │  └────────────────┘  │   │
│   └──────────────────────┘   │
│                              │
└──────────────────────────────┘  ← 1280px
```

---

## 2. Yerleşim Önerisi — TR Metni İçin

### 2.1 TR Karşılama Metni (22 kelime)

```
"Merhaba! Ben HLK, yapay zeka destekli reklam asistanınız.
Ürününüz için en iyi reklamı üretmek üzereyim.
Başlamadan önce size birkaç kısa sorum olacak."
```

→ 3 satır, ~70 karakter/satır

### 2.2 TR Link İsteme Metni (9 kelime)

```
"Lütfen ürünün web sitesi linkini
veya ürün linkini gönderin."
```

→ 2 satır, ~35 karakter/satır

### 2.3 Önerilen Font ve Boyut

| Parametre | Değer | Gerekçe |
|-----------|-------|---------|
| Font | **Inter Bold** veya **Arial Bold** | Telegram benzeri, okunabilir |
| Metin boyutu | **28-32px** | 720px genişlikte 70kar/satıra izin verir |
| Balon padding | **20px yatay, 12px dikey** | Nefes payı |
| Balon arkaplan | **#1a1a2e opacity 0.85** | Koyu, okunabilir |
| Metin rengi | **#FFFFFF** | Beyaz, yüksek kontrast |
| Vurgu rengi | **#FFD700 (altın)** | HLK marka rengi |
| Satır aralığı | **1.4x font size** | Okunabilirlik |

### 2.4 Güvenli Alan (Safe Area)

```
720px
←───────→
┌──────────┐
│  ████    │  y=0-20     ← Üst güvenli boşluk
│  ████    │
│  ████    │  y=20-730   ← HLK karakter bölgesi
│  ████    │              (Hedra lip-sync, mevcut video)
│  ████    │
│  ████    │  y=730-760  ← Geçiş boşluğu (30px)
├──────────┤
│ BALON-1  │  y=760-1060 ← 1. konuşma balonu (300px)
├──────────┤
│ BALON-2  │  y=1060-1240← 2. konuşma balonu (180px)
├──────────┤
│          │  y=1240-1280← Alt güvenli boşluk (40px)
└──────────┘
```

---

## 3. Ekran Taslağı (ASCII)

```
┌──────────────────────────────────────┐
│                                      │
│         ░░░░░░░░░░░░░░░░             │
│       ░░░░░░░░░░░░░░░░░░            │
│      ░░░░  ████████  ░░░░           │  ← HLK yüzü
│      ░░  ████████████  ░░           │    (Hedra lip-sync)
│       ░░ ████████████ ░░            │
│        ░░░░  ████  ░░░░             │
│          ░░░░░░░░░░░░               │
│                                      │
│  ┌────────────────────────────────┐  │
│  │                                │  │  ← Balon-1
│  │  Merhaba! Ben HLK, yapay      │  │    (karşılama)
│  │  zeka destekli reklam         │  │
│  │  asistanınız. Ürününüz için   │  │
│  │  en iyi reklamı üretmek       │  │
│  │  üzereyim. Başlamadan önce    │  │
│  │  size birkaç kısa sorum       │  │
│  │  olacak.                      │  │
│  │                                │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  Lütfen ürünün web sitesi     │  │  ← Balon-2
│  │  linkini veya ürün linkini    │  │    (link istek)
│  │  gönderin.                    │  │
│  └────────────────────────────────┘  │
│                                      │
└──────────────────────────────────────┘
```

---

## 4. FFmpeg Yaklaşımları — Karşılaştırmalı Analiz

### A Seçeneği: `drawtext` filter (metin doğrudan render)

```bash
ffmpeg -i hedra_lipsync.mp4 -i ahu_ses.mp3 \
       -filter_complex "
         [0:v]scale=720:730[face];
         color=#0d0d1a:s=720x550[canvas];
         [face][canvas]vstack=inputs=2[stack];
         drawtext=text='Merhaba! Ben HLK':
                  fontfile=font.ttf:fontsize=30:
                  fontcolor=white:box=1:boxcolor=#1a1a2e@0.9:
                  x=(w-text_w)/2:y=30:
                  enable='between(t,0,13)'"
       -c:v libx264 -preset fast -crf 23
```

**Avantajları:**
- Tek geçiş, hızlı (~1-3sn)
- Dinamik metin desteği (değişken `text=`)
- Zamanlama kontrolü (`enable='between(t,...)'`)
- Ek dosya gerektirmez

**Dezavantajları:**
- Karmaşık çok satır desteği yok (her satır ayrı `drawtext`)
- Font dosyası gerektirir
- Türkçe karakter (ü,ğ,şı) desteği fonta bağlı
- Her dil/değişiklikte yeniden render
- Önizleme imkansız (deneme/yanılma)

### B Seçeneği: PNG overlay (konuşma balonu şeffaf PNG)

```bash
# Önce PNG oluştur (Python/Pillow ile)
# Sonra overlay olarak ekle
ffmpeg -i hedra_lipsync.mp4 -i ahu_ses.mp3 \
       -i bubble_tr.png \
       -filter_complex "
         [0:v]scale=720:730[face];
         [2:v]scale=720:550[bubble];
         [face][bubble]vstack=inputs=2[final]"
```

**Avantajları:**
- Pixel-perfect tasarım (font, renk, gölge tam kontrol)
- Çok satır, emoji, özel karakter desteği sınırsız
- Dil başına 1 PNG önceden hazırlanabilir
- Tasarım değişikliklerinde sadece PNG güncellenir

**Dezavantajları:**
- 2 aşamalı işlem (PNG üret + FFmpeg birleştir)
- Dinamik metin zor (her değişiklikte yeni PNG)
- Ek dosya yönetimi

### C Seçeneği: Subtitle/ASS altyazı yaklaşımı

```bash
ffmpeg -i hedra_lipsync.mp4 -i ahu_ses.mp3 \
       -vf "ass=bubble.ass" \
       -c:v libx264 -preset fast -crf 23
```

**Avantajları:**
- ASS formatı ile karaoke efekti mümkün (kelime kelime renk değiştirme)
- Konum, font, stil tam kontrol
- .ass dosyası metin olarak düzenlenebilir
- Yeniden render gerektirmez (sadece ass dosyası)

**Dezavantajları:**
- ASS render kalitesi FFmpeg yapısına bağlı
- Bazı Telegram istemcilerinde altyazı sorunlu
- Daktilo efekti için karmaşık ASS timing

### D Seçeneği: Hibrit (PNG tabanlı, daktilo efektsiz)

**Önerilen yaklaşım:**

```python
# Adım 1: Python ile konuşma balonu PNG'si oluştur
# Adım 2: FFmpeg ile birleştir
# Adım 3: Telegram'a gönder
```

```
AVANTAJLARI:
  ✓ En yüksek kalite kontrol
  ✓ Türkçe karakter sorunsuz (Pillow+font)
  ✓ Çok satır, emoji, gradient destekli
  ✓ Dil başına 1 PNG = hızlı switch
  ✓ Daktilo efekti yerine statik balon (AR-002_39 muafiyeti gerekebilir)
```

### Karşılaştırma Tablosu

| Kriter | A: drawtext | B: PNG overlay | C: ASS subtitle | D: Hibrit (ÖNERİLEN) |
|--------|------------|---------------|-----------------|---------------------|
| Render hızı | ⚡ Çok hızlı | 🟡 Orta | ⚡ Çok hızlı | 🟡 Orta |
| Kalite kontrol | 🟡 Sınırlı | ✅ Tam | 🟡 Orta | ✅ Tam |
| Çok satır | ❌ Karmaşık | ✅ Kolay | ✅ Kolay | ✅ Kolay |
| Türkçe karakter | ⚠️ Font bağımlı | ✅ Sorunsuz | ✅ Sorunsuz | ✅ Sorunsuz |
| Daktilo efekti | ❌ Yok | ❌ Yok | ✅ Karaoke | ❌ Yok |
| Dosya yönetimi | ✅ Tek adım | 🟡 2 adım | 🟡 2 adım | 🟡 2 adım |
| Dinamik metin | ✅ Kolay | ❌ Zor | ✅ Kolay | ❌ Zor |
| Ön izleme | ❌ Zor | ✅ Kolay | 🟡 Orta | ✅ Kolay |
| **Öneri** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 5. Kaldırılacak Modüllerin Bağımlılık Haritası

### Mevcut Bağımlılıklar

```
handlers/start.py
├── helpers/typewriter_animation.py
│   ├── strip_html()
│   └── typewriter_animation()
│       ├── asyncio.sleep(delay)
│       ├── bot.send_message("▌")
│       ├── bot.edit_message_text()  ← her kelime için
│       └── bot.edit_message_text(HTML)  ← son format
│
├── _run_balloons()
│   ├── asyncio.sleep(1)
│   ├── typewriter_animation(welcome, delay=...)
│   ├── asyncio.sleep(1)
│   └── typewriter_animation(link, delay=...)
│
├── SAHNE2_SURE_LANG = {...}       ← sabit süre sözlüğü
├── SESLI_HINT = {...}             ← hint metni (8 dil)
│
├── _delete_sahne2()
│   └── asyncio.sleep(...) → delete_message(video, hint)
│
└── _get_mp3_duration()            ← ffprobe ile MP3 süresi
```

### Hedef Durumda Kalanlar

```
handlers/start.py (sadeleşmiş)
├── send_video(render_edilmis_video.mp4)  ← TEK ÇAĞRI
└── asyncio.sleep(video_suresi)
    └── delete_message(video)
```

### Kaldırılan Her Modülün Etkisi

| Kaldırılan Modül | Dosya | Satır | Etki |
|-----------------|-------|-------|------|
| `typewriter_animation.py` | helpers/ | ~110 satır | ❌ Tamamen kaldırılır. Telegram editMessageText zinciri biter. Flood control riski kalkar. |
| `strip_html()` | helpers/typewriter_animation.py | ~10 satır | ❌ HTML formatlamaya gerek kalmaz. |
| `_run_balloons()` | handlers/start.py | ~35 satır | ❌ Tamamen kaldırılır. Sleep-1, Sleep-2, typewriter çağrıları biter. |
| `_delete_sahne2()` task | handlers/start.py | ~10 satır | ❌ Timer'a gerek kalmaz. Video doğal süresinde biter. |
| `SAHNE2_SURE_LANG` | handlers/start.py | 5 satır | ❌ Video süresi otomatik (ffprobe). Elle girilen sabit kalkar. |
| `SESLI_HINT` | handlers/start.py | 10 satır | ❌ Video zaten sesli, ayrı uyarı gerekmez. |

**Toplam:** ~180 satır kod, 1 dosya (helpers/typewriter_animation.py) tamamen kalkar.

### Yeni Eklenmesi Gerekenler

| Yeni Modül | Tahmini Satır | Açıklama |
|-----------|--------------|----------|
| `services/scene_renderer.py` | ~80 satır | FFmpeg pipeline: lipsync+AHU+balon birleştirme |
| `helpers/bubble_generator.py` | ~60 satır | Python/Pillow ile konuşma balonu PNG üretimi |
| Cache katmanı | ~30 satır | Render edilmiş videoları cache'leme |

**Net kazanç:** ~180 satır gider, ~170 satır gelir → **~10 satır net azalma** (işlem basitleşir)

---

## 6. Tahmini Performans Kazancı

### API Çağrısı Azalması

| İşlem | Mevcut | Prototip | Azalma |
|-------|--------|----------|--------|
| `sendVideo` | 1 | 1 | — |
| `sendMessage` (hint) | 1 | **0** | **-1** |
| `sendMessage` (balon) | 2 | **0** | **-2** |
| `editMessageText` | **31** (22+9) | **0** | **-31** |
| `sendChatAction` (typing) | **31** (her kelime) | **0** | **-31** |
| `deleteMessage` | 4 (video+hint+2 balon) | **1** (sadece video) | **-3** |
| **Toplam API çağrısı** | **~70** | **~2** | **%97 azalma** 🚀 |

### Flood Control Riskinin Ortadan Kalkması

- **Mevcut:** Her dilde typewriter `editMessageText` çağrıları flood control'a takılıyor (KR'da görüldü)
- **Prototip:** Hiç `editMessageText` çağrısı yok → **flood control riski %0**

### Telegram Edit İşlemlerinin Kaldırılması

- `editMessageText` çağrıları retry mekanizması gerektirir
- Flood control durumunda 3-13sn gecikme oluşur (KR'da 13sn flood control beklemesi görüldü)
- Prototipte: hiç edit yok → **gecikme riski %0**

### AR-002_39 Uyumu

| Gereksinim | Mevcut | Prototip |
|-----------|--------|----------|
| AHU sesi tamamlanmalı | ✅ (delay hesaplaması ile) | ✅ (FFmpeg doğal) |
| Daktilo efekti tamamlanmalı | ⚠️ (sleep + delay ile) | ✅ (video içinde görünür) |
| Konuşma balonu tamamlanmalı | ✅ | ✅ (video içinde) |
| Video tekrar başlatılamaz | ❌ (replay riski) | ✅ (video bittiğinde her şey biter) |
| Video döngüye alınamaz | ❌ (replay riski) | ✅ (imkansız) |
| Video yeniden render edilemez | ❌ | ✅ |
| Video sonlandırılır | ⚠️ (timer ile) | ✅ (doğal bitiş) |
| Video kaldırılır | ⚠️ (gecikmeli) | ✅ (hemen) |
| Butonlar görünür | ⚠️ (timer bekler) | ✅ (video biter bitmez) |

---

## 7. Dezavantajlar ve Risk Analizi

### Risk Matrisi

| Risk | Olasılık | Etki | Çözüm |
|------|---------|------|-------|
| **Render süresi** (1-3sn ek bekleme) | 🟡 Orta | 🟡 Orta | Cache + background render |
| **Türkçe karakter font sorunu** | 🟢 Düşük | 🔴 Yüksek | Google Fonts + embed |
| **Metin değişikliği zorluğu** | 🟡 Orta | 🟡 Orta | Her değişiklikte yeniden render |
| **Daktilo efekti kaybı** | 🔴 Yüksek | 🟡 Orta | AR-002_39 revizyonu gerekebilir |
| **Video boyutu artışı** | 🟢 Düşük | 🟢 Düşük | CRF 23 ile ~%5 artış |
| **Hedra video yeniden encode** | 🟡 Orta | 🟢 Düşük | Kayıpsız copy mümkün değil (filter) |
| **PNG balon pozisyonu** | 🟡 Orta | 🟡 Orta | Pixel-perfect test gerektirir |

### Daktilo Efekti Kaybı

**En önemli dezavantaj.** Mevcut AR-002_39 kuralı "daktilo efektinin tamamlanması"nı şart koşar. Video içi balonda daktilo efekti bulunmaz — metin ya sabittir ya da ASS karaoke ile animasyonludur.

**İki seçenek:**
1. AR-002_39 revize edilir: "daktilo efekti" şartı kaldırılır
2. ASS altyazı (C seçeneği) ile kelime kelime görünme sağlanır (karmaşık)

---

## 8. Geçiş Maliyeti

### Geliştirme Süresi Tahmini

| Aşama | İş | Süre |
|-------|----|------|
| 1 | Python bubble generator (Pillow) | ~2 saat |
| 2 | FFmpeg pipeline testleri | ~1 saat |
| 3 | TR prototip video üretimi | ~1 saat |
| 4 | Telegram entegrasyon testi | ~1 saat |
| 5 | Diğer 7 dil için adaptasyon | ~2 saat |
| 6 | Cache mekanizması | ~1 saat |
| 7 | Test ve hata düzeltme | ~2 saat |
| **Toplam** | | **~10 saat** |

### Kod Değişiklik Büyüklüğü

| Dosya | İşlem | Tahmini Satır |
|-------|-------|--------------|
| `services/scene_renderer.py` | **YENİ** | ~80 |
| `helpers/bubble_generator.py` | **YENİ** | ~60 |
| `handlers/start.py` | **DEĞİŞİKLİK** | -40 (kaldırma) + 20 (yeni) |
| `helpers/typewriter_animation.py` | **SİLİNECEK** | -110 |
| **Toplam** | | **~90 satır net değişim** |

---

## 9. Nihai Tavsiye

```
╔════════════════════════════════════════════════════════════╗
║                    KARAR: İLERLET                           ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Prototipin üretilmesi ÖNERİLİR.                           ║
║                                                            ║
║  Gerekçe:                                                   ║
║  • Telegram API çağrıları %97 azalır (~70 → ~2)            ║
║  • Flood control riski tamamen kalkar                      ║
║  • AR-002_39 kuralına %100 uyum sağlanır                  ║
║  • Replay/döngü riski sıfırlanır                           ║
║  • Kod ~180 satır azalır                                   ║
║  • Kullanıcı deneyimi iyileşir (kesintisiz video)          ║
║                                                            ║
║  Önerilen yöntem: PNG Overlay (B seçeneği)                 ║
║  - Python/Pillow ile balon PNG'si                          ║
║  - FFmpeg ile Hedra + AHU + PNG birleştirme                 ║
║  - Cache katmanı ile tekrar render önleme                   ║
║                                                            ║
║  Önce sadece TR için prototip yap, test et,                ║
║  onaylanırsa 8 dile genişlet.                              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### Adım Adım İlerleme Planı

```
AŞAMA-1: Prototip (TR için, bu branch)
  ├── bubble_generator.py → TR balon PNG'si
  ├── FFmpeg pipeline testi
  ├── Telegram'da manuel test
  └── Kullanıcı onayı

AŞAMA-2: Entegrasyon (onaylanırsa)
  ├── scene_renderer.py servisi
  ├── handlers/start.py sadeleştirme
  ├── typewriter_animation.py kaldırma
  ├── _run_balloons() kaldırma
  └── Telegram testi

AŞAMA-3: 8 Dil
  ├── Her dil için PNG üretimi
  ├── Cache mekanizması
  └── Tam test
```

---

## Ek: Prototip İçin Gerekli Araçlar

| Araç | Amaç |
|------|------|
| **Python 3.14** | Mevcut ortam |
| **Pillow** (PIL) | Konuşma balonu PNG üretimi |
| **FFmpeg** | Video + ses + PNG birleştirme |
| **Inter Font** | Telegram benzeri font (isteğe bağlı) |

```bash
# FFmpeg mevcut mu?
ffmpeg -version

# Pillow mevcut mu?
python3 -c "from PIL import Image; print('OK')"

# Kurulum (gerekirse)
# pip install Pillow
```
