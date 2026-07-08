# Sahne-2 Video Balloon Prototip Planı — TR

> **Durum:** Plan aşaması — kod yazılmadı
> **Kapsam:** Sadece TR, sadece Sahne-2, sadece prototip
> **Mevcut sistem korunacak, değiştirilmeyecek**

---

## 1. Dosya Yapısı — Yeni Prototip Dizini

```
hlk_PROJELER_02062026/HLK_01_asistan/
├── PROJELER/                          ← YENİ: prototip dizini
│   └── SCENE2_BALLOON_PROTOTYPE/      ← YENİ: bu prototip
│       ├── README.md                  ← çalıştırma talimatı
│       ├── assets/                    ← girdi dosyaları
│       │   ├── hedra_tr.mp4           ← mevcut Sahne-2 small videosu (kopya)
│       │   ├── ahu_tr.mp3             ← mevcut TR AHU MP3 (kopya)
│       │   └── arial.ttf              ← font (C:\Windows\Fonts\arial.ttf)
│       ├── output/                    ← çıktı dosyaları
│       │   ├── bubble.png              ← konuşma balonu PNG
│       │   └── scene2_tr_prototype.mp4 ← nihai video
│       ├── generate_bubble.py         ← YENİ: PNG balon üretici
│       ├── render_scene.py            ← YENİ: FFmpeg pipeline
│       └── send_test.py              ← YENİ: Telegram'a gönderme testi
```

**Mevcut sisteme dokunulmaz.** Tüm prototip `PROJELER/` altında izole çalışır.

---

## 2. Yeni Oluşturulacak Dosyalar

| # | Dosya | Amaç | Tahmini Satır |
|---|-------|------|--------------|
| 1 | `generate_bubble.py` | Python/Pillow ile konuşma balonu PNG'si üretir. TR metnini balon içine yerleştirir, Türkçe karakter desteği, premium görünüm. | ~120 |
| 2 | `render_scene.py` | FFmpeg pipeline: Hedra video + AHU ses + balon PNG'sini tek MP4'te birleştirir. vstack + overlay + drawtext. | ~80 |
| 3 | `send_test.py` | Telegram bot token'ını kullanarak `scene2_tr_prototype.mp4`'yi @hlk01_test_bot üzerinden gönderir. | ~60 |
| 4 | `README.md` | Çalıştırma adımları, bağımlılıklar, geri dönüş planı. | ~40 |
| **Toplam** | | | **~300 satır** |

---

## 3. Kullanılacak Pipeline

```
ADIM-1: Girdileri hazırla
─────────────────────────────────────────
  kaynak/hedefler:
    VİDEO Doyaları/hedra_sahne-2_small/hedra_video_tr_small_v2.mp4
      → PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/hedra_tr.mp4

    SES Dosyaları/hedra_SAHNE-2/hedra_ses_tr.mp3
      → PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/ahu_tr.mp3

    C:/Windows/Fonts/arial.ttf
      → PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/arial.ttf

ADIM-2: Konuşma balonu PNG'si üret
─────────────────────────────────────────
  python generate_bubble.py
    → output/bubble.png  (720x550, RGBA, şeffaf arkaplan)
    - Balon-1 (karşılama): 3 satır
    - Balon-2 (link istek): 2 satır
    - Aynı PNG içinde alt alta iki balon

ADIM-3: FFmpeg ile birleştir
─────────────────────────────────────────
  python render_scene.py
    → output/scene2_tr_prototype.mp4
    - Hedra video 720x730 ölçeklenir (üst kısım)
    - Balon PNG'si 720x550 alt kısım
    - vstack ile dikey birleştirme
    - AHU ses MP3 eklenir
    - H.264 CRF 23, 30fps, 44100Hz stereo

ADIM-4: Telegram'a gönder (test)
─────────────────────────────────────────
  python send_test.py
    → @hlk01_test_bot üzerinden sendVideo
    - 9:16 format
    - supports_streaming=True
    - duration parametresi
```

---

## 4. FFmpeg Yaklaşımı

### Seçilen Yöntem: **vstack + overlay hibrit**

```
Gerekçe:
  - vstack: iki videoyu (Hedra + balon) dikey birleştirme
  - overlay: ikinci bir geçişte metin düzeltmesi
  - drawtext: sadece HLK vurgusu için (opsiyonel)
```

### FFmpeg Komutu (Taslak)

```bash
ffmpeg -i assets/hedra_tr.mp4 -i output/bubble.png -i assets/ahu_tr.mp3 \
       -filter_complex "
         [0:v]scale=720:730[face];
         [1:v]scale=720:550[bubble];
         [face][bubble]vstack=inputs=2[final]
       " \
       -map "[final]" -map 2:a \
       -c:v libx264 -preset fast -crf 23 \
       -c:a aac -b:a 128k \
       -pix_fmt yuv420p \
       -t 12.880 \
       output/scene2_tr_prototype.mp4
```

### Neden vstack?

| Yöntem | Açıklama | Karar |
|--------|----------|-------|
| **vstack** | İki videoyu dikey birleştirir, en hızlı | ✅ SEÇİLDİ |
| overlay | PNG'yi video üstüne bindirir, daha esnek | 🟡 Yedek |
| drawtext | Metni doğrudan render eder, çok satır zor | ❌ Elendi |
| ASS subtitle | Altyazı dosyası, her istemcide farklı görünür | ❌ Elendi |

### TR Video Süre Yönetimi

```
Hedra small video:    12.880 sn
AHU MP3:              12.771 sn
Hedef prototip süre:  12.880 sn (video süresi)
```

**Karar:** Prototip süresi = video süresi (12.880sn). AHU ses MP3'ü video süresine kırpılır (`-t 12.880`). Video bittiğinde her şey biter → AR-002_39 otomatik uyumlu.

---

## 5. PNG Balon Üretimi — detay

### Kullanılacak Teknoloji

```
Python 3.14 + Pillow (PIL) 11.3.0
Font: Arial Bold (arialbd.ttf) — Türkçe karakter desteği ✅
```

### Balon Tasarımı

```
┌──────────────────────────────────────┐  ← 720px
│  ┌────────────────────────────────┐  │
│  │  Merhaba! Ben HLK, yapay      │  │  ← Balon-1 (karşılama)
│  │  zeka destekli reklam         │  │     3 satır
│  │  asistanınız.                 │  │     y=30 — y=200
│  │                                │  │
│  │  Ürününüz için en iyi         │  │
│  │  reklamı üretmek üzereyim.    │  │
│  │                                │  │
│  │  Başlamadan önce size          │  │
│  │  birkaç kısa sorum olacak.     │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │  Lütfen ürünün web sitesi     │  │  ← Balon-2 (link istek)
│  │  linkini veya ürün linkini    │  │     2 satır
│  │  gönderin.                    │  │     y=260 — y=380
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │        [ 🔗 Link gönder ]     │  │  ← İlerleme göstergesi
│  └────────────────────────────────┘  │     y=420 — y=470
│                                      │
└──────────────────────────────────────┘  ← 550px
```

### Renk Paleti

| Öğe | Renk Kod | Açıklama |
|-----|---------|----------|
| Arkaplan | `#0d0d1a` (şeffaf) | Siyah-mavi ton, premium |
| Balon-1 dolgu | `#1a1a2e` opak 0.90 | Koyu lacivert |
| Balon-2 dolgu | `#16213e` opak 0.90 | Biraz daha açık |
| Metin rengi | `#ffffff` | Beyaz |
| HLK vurgusu | `#e8b84b` | Altın sarısı (HLK marka rengi) |
| Gönderge oku | `#4a4a6a` | Nötr gri-mavi |

### Metin Bölme (Word Wrap)

```python
# TR karşılama (22 kelime) → 3 satır
satir1 = "Merhaba! Ben HLK, yapay zeka"
satir2 = "destekli reklam asistanınız."
satir3 = "Ürününüz için en iyi reklamı"
satir4 = "üretmek üzereyim. Başlamadan"
satir5 = "önce size birkaç kısa sorum"
satir6 = "olacak."

# TR link istek (9 kelime) → 2 satır
satir1 = "Lütfen ürünün web sitesi"
satir2 = "linkini veya ürün linkini"
satir3 = "gönderin."
```

**Font size:** 30px (satır başına ~25-28 karakter, 3 satır → ~90 karakter)
**HLK vurgusu:** Ayrı `drawtext` katmanı ile altın renk

---

## 6. Metin Yerleşimi

### Koordinat Sistemi (PNG 720×550)

```
X=0                  X=360               X=720
  ┌──────────────────────────────────────┐  Y=0
  │  ┌────────────────────────────────┐  │
  │  │   Merhaba! Ben HLK...         │  │  Y=30 — Y=210
  │  │   (3 satır, 30px font)        │  │  ← 1. balon
  │  └────────────────────────────────┘  │
  │                                      │  Y=230
  │  ┌────────────────────────────────┐  │
  │  │   Lütfen ürün linkini...       │  │  Y=260 — Y=400
  │  │   (2 satır, 28px font)         │  │  ← 2. balon
  │  └────────────────────────────────┘  │
  │                                      │  Y=420
  │  ┌────────────────────────────────┐  │
  │  │   ── ── ── ── ── ──          │  │  Y=480 — Y=520
  │  └────────────────────────────────┘  │  ← animasyon çizgisi
  └──────────────────────────────────────┘  Y=550
```

### HLK Vurgusu

"HLK" kelimesi metin içinde **altın rengi (#e8b84b)** ile vurgulanacak. Bu, mevcut HTML `<b>HLK</b>` formatının PNG karşılığıdır. İki yöntem:

1. **Ayrı metin katmanı:** "Merhaba! Ben " + "HLK" (altın) + ", yapay zeka..."
2. **Renk değiştirme:** Aynı satırda farklı renkte `drawtext`

**Öneri:** Yöntem-1, Pillow `textbbox` ile hassas konumlandırma.

---

## 7. Test Planı

### Aşama-1: Birim Test (offline)

```
1. python generate_bubble.py
   → output/bubble.png oluşur
   → Kontrol: 720x550, RGBA, şeffaf
   → Kontrol: Türkçe karakterler (ü,ğ,şı,ö,ç)
   → Kontrol: HLK vurgusu altın renk

2. python render_scene.py
   → output/scene2_tr_prototype.mp4 oluşur
   → Kontrol: 720x1280, 9:16
   → Kontrol: Süre = 12.880sn
   → Kontrol: Ses var (AAC, stereo)
   → Kontrol: HLK yüzü merkezde
   → Kontrol: Balon alt kısımda okunabilir
```

### Aşama-2: Telegram Testi (canlı)

```
3. python send_test.py
   → Bot: @hlk01_test_bot
   → sendVideo(scene2_tr_prototype.mp4)
   → Kontrol: Video oynuyor mu?
   → Kontrol: Ses var mı?
   → Kontrol: Metin okunuyor mu?
   → Kontrol: Video bittiğinde ne oluyor?
   → Kontrol: Replay var mı?
```

### Aşama-3: Karşılaştırma

```
4. Mevcut Sahne-2 vs Prototip:
   - API çağrısı sayısı
   - Toplam süre (kullanıcı bekleme)
   - Flood control
   - Kullanıcı deneyimi (gözlem)
```

---

## 8. Riskler

| # | Risk | Olasılık | Etki | Önlem |
|---|------|---------|------|-------|
| 1 | **Türkçe karakterler bozuk görünür** | 🟢 Düşük | 🔴 Yüksek | Arial Bold fontu test et, `encoding='unic'` kullan |
| 2 | **Balon pozisyonu HLK yüzüyle çakışır** | 🟡 Orta | 🟡 Orta | Hedra video kırpma sınırını dene |
| 3 | **Renk/profil uyumsuzluğu** | 🟡 Orta | 🟡 Orta | 2 geçişli render (önce vstack, sonra renk düzeltme) |
| 4 | **Video boyutu artar** | 🟢 Düşük | 🟢 Düşük | Hedef: mevcut ~2MB altı |
| 5 | **FFmpeg pipeline hatası** | 🟡 Orta | 🟡 Orta | Her adımda çıktı kontrolü |
| 6 | **Telegram video reddeder** | 🟢 Düşük | 🔴 Yüksek | 50MB limit, 720p, H.264 |
| 7 | **Mevcut sistem karışır** | 🔴 Yüksek | 🔴 Yüksek | Prototip TAMAMEN AYRI dizinde |

### Geri Dönüş Planı

```bash
# Herhangi bir sorunda:
rm -rf PROJELER/SCENE2_BALLOON_PROTOTYPE/
# Mevcut sistem etkilenmez.
```

---

## 9. Tahmini Geliştirme Süresi

| Adım | İş | Süre |
|------|----|------|
| 1 | Dizin yapısını oluştur, girdi dosyalarını kopyala | 5 dk |
| 2 | `generate_bubble.py` — PNG balon üretici | 45 dk |
| 3 | `render_scene.py` — FFmpeg pipeline | 30 dk |
| 4 | İlk test: PNG + render doğrulama | 15 dk |
| 5 | `send_test.py` — Telegram gönderme | 20 dk |
| 6 | Telegram'da görsel test ve düzeltme | 30 dk |
| 7 | Dokümantasyon (`README.md`) | 15 dk |
| **Toplam** | | **~2.5 saat** |

---

## 10. Başarı Kriterleri

✅ Prototip video başarıyla oluşur
✅ Telegram'da 9:16 formatında oynar
✅ AHU sesi net duyulur
✅ Konuşma balonu okunabilir (Türkçe karakterler dahil)
✅ HLK yüzü merkezde
✅ Video bittiğinde doğal olarak durur (replay yok)
✅ Flood control hatası oluşmaz
✅ Mevcut sistem etkilenmez

---

## 11. Mevcut Sistem ile Karşılaştırma

| Metrik | Mevcut | Prototip | Fark |
|--------|--------|----------|------|
| Telegram API çağrısı | ~70 | **1** (sendVideo) | **%98 az** |
| Dosya sayısı | 4 (video+hint+2balon) | **1 video** | **-3 dosya** |
| Flood control riski | Yüksek | **%0** | **Tamamen kalktı** |
| Senkron sorunu | sleep + timer + delay | **FFmpeg doğal** | **%0** |
| Replay riski | Var (delete timer) | **Yok** | **Tamamen kalktı** |
| Tasarım esnekliği | Telegram HTML limitli | **Pixel-perfect** | **Arttı** |
| Render süresi | 0sn | **~3sn** | **+3sn** (offline) |

---

## Onay Beklenen

Plan hazır. İstersen:

1. **Onayla** → `SCENE2_TR_PROTOTYPE_IMPLEMENTATION.md` oluşturup kod yazmaya başlayayım
2. **Düzelt** → planda değişiklik istersen belirt
3. **İptal** → prototipi başlatma

Ne yapalım?
