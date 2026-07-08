# Sahne-2 Video Balloon Prototip — Uygulama Planı

> **Durum:** Uygulama planı — kod yazılmadı, dosya oluşturulmadı
> **Kapsam:** Sadece TR, sadece Sahne-2, sadece prototip
> **Mevcut sistem korunacak, değiştirilmeyecek**
> 
> **Onay:** ✅ SCĖNE2_TR_PROTOTYPE_PLAN.md onaylandı
> **Sonraki adım:** Bu plan okunup onaylandıktan sonra kod yazılacak

---

## İçindekiler

1. [Uygulama Adımları](#1-uygulama-adımları)
2. [Dizin Yapısı](#2-dizin-yapısı)
3. [Pipeline Diagramı](#3-pipeline-diagramı)
4. [Dosya Detayları](#4-dosya-detayları)
5. [Girdi Dosyaları](#5-girdi-dosyaları)
6. [Pipeline Adım Adım](#6-pipeline-adım-adım)
7. [Test Senaryosu](#7-test-senaryosu)
8. [Başarı Kriterleri](#8-başarı-kriterleri)
9. [Karşılaştırma Tablosu](#9-karşılaştırma-tablosu)
10. [Geri Dönüş Planı](#10-geri-dönüş-planı)
11. [Riskler ve Önlemler](#11-riskler-ve-önlemler)
12. [Zaman Tahmini](#12-zaman-tahmini)

---

## 1. Uygulama Adımları

### Aşama-0: Hazırlık (5 dk)

```
Adım 0.1 — Dizin yapısını oluştur
Adım 0.2 — Girdi dosyalarını kopyala
Adım 0.3 — Font dosyasını kopyala
```

**Yapılacaklar:**
```bash
mkdir -p PROJELER/SCENE2_BALLOON_PROTOTYPE/assets
mkdir -p PROJELER/SCENE2_BALLOON_PROTOTYPE/output

# Girdi dosyalarını kopyala (mevcut sistemden)
cp "VİDEO Doyaları/hedra_sahne-2_small/hedra_video_tr_small_v2.mp4" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/hedra_tr.mp4"

cp "SES Dosyaları/hedra_SAHNE-2/hedra_ses_tr.mp3" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/ahu_tr.mp3"

# Font kopyala
cp "C:/Windows/Fonts/arialbd.ttf" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/arialbd.ttf"
```

**Kontrol:** Dosyalar var mı? Boyutları doğru mu?

---

### Aşama-1: PNG Balon Üretici — `generate_bubble.py` (45 dk)

```
Adım 1.1 — Sabitleri tanımla (renk, font, boyut)
Adım 1.2 — Metin satırlarına bölme fonksiyonu (word wrap)
Adım 1.3 — HLK vurgusu için ayırma fonksiyonu
Adım 1.4 — Yuvarlak dikdörtgen balon çizimi
Adım 1.5 — Balon-1 (karşılama) metin yerleşimi
Adım 1.6 — Balon-2 (link istek) metin yerleşimi
Adım 1.7 — İlerleme çizgisi (isteğe bağlı animasyon efekti)
Adım 1.8 — PNG çıktı (720x550, RGBA)
```

**Detaylı fonksiyon listesi:**

```python
# generate_bubble.py — Taslak yapı

FONKSİYONLAR:
  load_font(path, size)                    → ImageFont
  word_wrap(text, font, max_width)         → [str]  (satır listesi)
  split_hlk_vurgusu(satir)                 → [("HLK", True), (" metni", False)]
  draw_rounded_rect(draw, xy, radius, fill)→ None
  draw_ballon(draw, metin_satirlari,       → None
              pos_x, pos_y, max_width,
              font, vurgu_font)
  main()                                   → None (PNG kaydet)

SABİTLER:
  W, H        = 720, 550    # PNG boyutu
  BG_RENK     = (0, 0, 0, 0)  # şeffaf
  BALON1_RENK = (26, 26, 46, 230)  # #1a1a2e
  BALON2_RENK = (22, 33, 62, 230)  # #16213e
  METIN_RENK  = (255, 255, 255)    # beyaz
  HLK_RENK    = (232, 184, 75)     # altın sarısı
  FONT_YOLU   = "assets/arialbd.ttf"
  FONT_BOYUT  = 30
  KOSA_YARI   = 20           # rounded corner radius
  PADDING_X   = 30
  PADDING_Y   = 20
  SATIR_ARASI = 8             # px

KONUMLAR:
  BALON1_Y    = 30    # Balon-1 üst kenar
  BALON2_Y    = 270   # Balon-2 üst kenar
  BALON_MAX_W = 660   # maksimum genişlik (720 - 2x30)

METİNLER (HTML'den arındırılmış):
  mesaj1 = "Merhaba! Ben HLK, yapay zeka destekli reklam asistanınız. Ürününüz için en iyi reklamı üretmek üzereyim. Başlamadan önce size birkaç kısa sorum olacak."
  mesaj2 = "Lütfen ürünün web sitesi linkini veya ürün linkini gönderin."
```

**Python importları:**
```python
from PIL import Image, ImageDraw, ImageFont
import textwrap, os, re
```

---

### Aşama-2: FFmpeg Pipeline — `render_scene.py` (30 dk)

```
Adım 2.1 — Video süresini al (ffprobe)
Adım 2.2 — Balon PNG'sini yükle
Adım 2.3 — FFmpeg komutunu oluştur (vstack + ses)
Adım 2.4 — Pipeline'ı çalıştır
Adım 2.5 — Çıktıyı doğrula (süre, boyut, çözünürlük)
```

**Detaylı fonksiyon listesi:**

```python
# render_scene.py — Taslak yapı

FONKSİYONLAR:
  get_duration(filepath)                   → float (sn)
  build_ffmpeg_cmd(hedra_video, bubble_png,  → [str] (komut listesi)
                   ahu_mp3, output_mp4,
                   duration)
  run_pipeline(cmd)                        → bool
  validate_output(filepath)                → dict {süre, boyut, w, h}
  main()                                   → None

VARSAYILANLAR:
  HEDRA_VIDEO  = "assets/hedra_tr.mp4"
  BUBBLE_PNG   = "output/bubble.png"
  AHU_MP3      = "assets/ahu_tr.mp3"
  OUTPUT_MP4   = "output/scene2_tr_prototype.mp4"
  FPS          = 30
  VIDEO_W      = 720
  VIDEO_H      = 1280
  FACE_H       = 730  # Hedra kırpma yüksekliği
  BUBBLE_H     = 550  # Balon yüksekliği
```

**FFmpeg komutu (tam):**

```bash
ffmpeg -i assets/hedra_tr.mp4 \
       -i output/bubble.png \
       -i assets/ahu_tr.mp3 \
       -filter_complex "                                      
         [0:v]scale=720:730:force_original_aspect_ratio=decrease,
               setsar=1[face];
         [1:v]scale=720:550[balloon];
         [face][balloon]vstack=inputs=2[final]
       " \
       -map "[final]" \
       -map 2:a \
       -c:v libx264 \
       -preset fast \
       -crf 23 \
       -c:a aac \
       -b:a 128k \
       -pix_fmt yuv420p \
       -r 30 \
       -t 12.880 \
       -movflags +faststart \
       output/scene2_tr_prototype.mp4
```

**Komut parametre açıklamaları:**

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `-i hedra_tr.mp4` | 1. girdi | HLK lip-sync videosu |
| `-i bubble.png` | 2. girdi | Konuşma balonu PNG |
| `-i ahu_tr.mp3` | 3. girdi | AHU ses dosyası |
| `scale=720:730` | video kırpma | Hedra'yı 720x730'a ölçekler (üst kısım) |
| `vstack=inputs=2` | dikey birleştirme | Face(730) + Balon(550) = 1280px |
| `-crf 23` | kalite | 18=kayıpsız, 23=iyi, 28=düşük |
| `-preset fast` | hız/kalite dengesi | fast, medium, slow |
| `-t 12.880` | süre | Video süresi (MP3'ten uzun) |
| `-movflags +faststart` | web optimizasyonu | Telegram için gerekli |

---

### Aşama-3: Telegram Gönderme — `send_test.py` (20 dk)

```
Adım 3.1 — .env'den bot token'ını oku
Adım 3.2 — Hedef chat_id'yi belirle (test botu)
Adım 3.3 — Video süresini al (ffprobe)
Adım 3.4 — sendVideo ile Telegram'a gönder
Adım 3.5 — Yanıtı yazdır (başarılı mı?)
```

**Detaylı fonksiyon listesi:**

```python
# send_test.py — Taslak yapı

FONKSİYONLAR:
  load_token()                              → str
  get_hedef_chat()                          → int (test)
  get_duration(filepath)                    → float
  send_video(token, chat_id, video_path,     → bool
             duration)
  main()                                     → None

VARSAYILANLAR:
  VIDEO_PATH  = "output/scene2_tr_prototype.mp4"
  TEST_BOT    = @hlk01_test_bot

AKIŞ:
  1. .env dosyasından TELEGRAM_TOKEN_TEST oku
  2. Bot = Application.builder().token(TEST_TOKEN).build()
  3. send_video(video, supports_streaming=True, 
                width=720, height=1280, duration=sure)
  4. print("✅ Video gönderildi: msg_id=X")
```

**İmportlar:**
```python
import asyncio, logging, os, sys
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot, InputFile
import subprocess
```

---

### Aşama-4: Entegrasyon Testi (30 dk)

```
Adım 4.1 — generate_bubble.py çalıştır
Adım 4.2 — render_scene.py çalıştır
Adım 4.3 — Çıktıyı ffprobe ile doğrula
Adım 4.4 — send_test.py çalıştır
Adım 4.5 — Telegram'da görsel inceleme
Adım 4.6 — Gerekirse düzeltme yap
```

---

## 2. Dizin Yapısı (Tam)

```
hlk_PROJELER_02062026/HLK_01_asistan/
│
├── (mevcut tüm dosyalar — DEĞİŞMEZ)
│   ├── main.py
│   ├── handlers/start.py
│   ├── helpers/typewriter_animation.py
│   ├── services/scene_*.py
│   ├── VİDEO Doyaları/...
│   ├── SES Dosyaları/...
│   └── ANA YASA/...
│
├── PROJELER/                                     ← YENİ
│   └── SCENE2_BALLOON_PROTOTYPE/                 ← YENİ
│       │
│       ├── README.md                             ← YENİ: ~40 satır
│       │   - Proje amacı
│       │   - Çalıştırma talimatı (4 adım)
│       │   - Bağımlılıklar
│       │   - Geri dönüş talimatı
│       │
│       ├── assets/                               ← YENİ: girdi dosyaları
│       │   ├── hedra_tr.mp4                      ← kopya (mevcut sistemden)
│       │   ├── ahu_tr.mp3                        ← kopya (mevcut sistemden)
│       │   └── arialbd.ttf                       ← kopya (Windows Fonts)
│       │
│       ├── output/                               ← YENİ: çıktı dosyaları
│       │   ├── bubble.png                        ← generate_bubble.py çıktısı
│       │   └── scene2_tr_prototype.mp4           ← render_scene.py çıktısı
│       │
│       ├── generate_bubble.py                    ← YENİ: ~120 satır
│       ├── render_scene.py                       ← YENİ: ~80 satır
│       └── send_test.py                          ← YENİ: ~60 satır
│
├── SCENE2_TR_PROTOTYPE_PLAN.md                   ← (plan belgesi)
├── SCENE2_TR_PROTOTYPE_IMPLEMENTATION.md          ← (bu dosya)
├── SCENE2_VIDEO_BALLOON_PROTOTYPE.md             ← (fizibilite raporu)
├── VIDEO_DELETE_TIMER_ANALYSIS.md
└── VIDEO_LIFECYCLE_ANALYSIS.md
```

---

## 3. Pipeline Diagramı (Tam)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SCENE2 BALLOON PROTOTYPE PIPELINE                │
│                          TR DİLİ — SADECE TEST                       │
└─────────────────────────────────────────────────────────────────────┘

ADIM-1                    ADIM-2                    ADIM-3
─────────                ─────────                 ─────────
GİRDİLER                 PNG ÜRETİMİ               FFMPEG BİRLEŞTİRME

assets/                  generate_bubble.py        render_scene.py
│                        │                         │
├── hedra_tr.mp4         ├── word_wrap()           ├── scale hedra → 720x730
├── ahu_tr.mp3           ├── split_hlk()           ├── load bubble.png → 720x550
└── arialbd.ttf          ├── draw_rounded_rect()   ├── vstack[face][balloon]
                         ├── draw text line-1      ├── add AHU MP3 audio
                         ├── draw text line-2      └── -t 12.880, crf 23, yuv420p
                         ├── draw text line-3      │
                         ├── draw HLK in gold      └── output/scene2_tr_prototype.mp4
                         ├── draw balon-2          │
                         └── output/bubble.png     │
                                                   │
                      ADIM-4                      ADIM-5
                      ──────────                  ──────────
                      DOĞRULAMA                   TELEGRAM TESTİ
                      │                           │
                      ffprobe:                    send_test.py
                      ├── süre=12.880sn           │
                      ├── w=720, h=1280           ├── .env'den token oku
                      ├── codec=h264              ├── sendVideo(prototype.mp4)
                      ├── ses=AAC stereo          ├── supports_streaming=True
                      └── boyut<10MB              └── msg_id al

                      ┌─────────────────────────────────────┐
                      │         BAŞARI KRİTERLERİ            │
                      │  ✓ 720x1280, 9:16                   │
                      │  ✓ HLK yüzü merkezde                │
                      │  ✓ Balon okunabilir                 │
                      │  ✓ AHU sesi net                     │
                      │  ✓ Flood control YOK                │
                      │  ✓ 1 API çağrısı (sendVideo)        │
                      └─────────────────────────────────────┘
```

---

## 4. Dosya Detayları

### 4.1 `generate_bubble.py` — Detaylı Tasarım

```python
#!/usr/bin/env python3
"""
Sahne-2 Prototip — Konuşma Balonu PNG Üretici

TR dili için 720x550px konuşma balonu PNG'si üretir.
İçerik: 2 adet konuşma balonu (karşılama + link istek)
+ ilerleme göstergesi.

Kullanım: python generate_bubble.py
Çıktı:   output/bubble.png
"""

# ============================================================
# SABİTLER
# ============================================================
# PNG boyutu
CANVAS_W = 720
CANVAS_H = 550

# Renk paleti (RGBA)
BG_RENK      = (0, 0, 0, 0)        # şeffaf
BALON1_RENK  = (26, 26, 46, 230)   # #1a1a2e
BALON2_RENK  = (22, 33, 62, 230)   # #16213e
METIN_RENK   = (255, 255, 255)      # beyaz
HLK_RENK     = (232, 184, 75)       # altın sarısı
ILERLEME_RENK = (74, 74, 106)       # #4a4a6a

# Font
FONT_YOLU  = "assets/arialbd.ttf"
FONT_BOYUT = 30
FONT_KUCUK  = 26  # balon-2 için

# Yerleşim
KOSA_YARI   = 22       # yuvarlak köşe yarıçapı
PADDING_X   = 30       # yatay iç boşluk
PADDING_Y   = 22       # dikey iç boşluk
SATIR_ARASI = 6        # satırlar arası boşluk
BALON_MAX_W = CANVAS_W - 2 * PADDING_X  # 660px

# Balon pozisyonları
BALON1_X = PADDING_X
BALON1_Y = 30
BALON2_X = PADDING_X
BALON2_Y = 280

# İlerleme çizgisi
ILERLEME_Y = 490

# ============================================================
# METİNLER (HTML etiketlerinden arındırılmış, TR)
# ============================================================
MESAJ1 = ("Merhaba! Ben HLK, yapay zeka destekli "
          "reklam asistanınız. Ürününüz için "
          "en iyi reklamı üretmek üzereyim. "
          "Başlamadan önce size birkaç kısa "
          "sorum olacak.")

MESAJ2 = ("Lütfen ürünün web sitesi linkini "
          "veya ürün linkini gönderin.")

# ============================================================
# FONKSİYONLAR
# ============================================================

def load_font(path=FONT_YOLU, size=FONT_BOYUT):
    """Font dosyasını yükle. Bulunamazsa varsayılan kullan."""
    ...

def split_hlk_emphasis(text):
    """Metindeki 'HLK' kelimesini ayır, vurgu işareti döndür.
    
    Örnek: "Merhaba! Ben HLK, yapay..." 
    → [("Merhaba! Ben ", False), ("HLK", True), (", yapay...", False)]
    """
    ...

def word_wrap(text, font, max_width):
    """Metni max_width genişliğine göre satırlara böl.
    
    font.getbbox() veya textbbox() kullanarak 
    her satırın piksel genişliğini hesapla.
    """
    ...

def draw_rounded_rect(draw, xy, radius, fill):
    """Yuvarlak köşeli dikdörtgen çiz.
    
    xy: (x1, y1, x2, y2) — sol üst, sağ alt
    radius: köşe yarıçapı
    """
    ...

def draw_balloon_content(draw, lines, x, y, 
                          max_width, font, 
                          vurgu_font=None):
    """Bir balonun metin içeriğini çiz.
    
    Her satır için:
      - split_hlk_emphasis() ile HLK'yı ayır
      - Normal metni METIN_RENK ile çiz
      - HLK'yı HLK_RENK ile çiz
      - Satırları SATIR_ARASI ile aşağı kaydır
    """
    ...

def draw_progress_bar(draw):
    """Alt kısımda ilerleme çizgisi çiz."""
    ...

def main():
    """Ana fonksiyon: tüm balon PNG'sini oluştur."""
    
    # 1. Şeffaf kanvas oluştur
    # 2. Fontları yükle
    # 3. Metinleri satırlara böl
    # 4. Balon-1 arkaplan (yuvarlak dikdörtgen)
    # 5. Balon-1 metin (HLK vurgusu ile)
    # 6. Balon-2 arkaplan
    # 7. Balon-2 metin
    # 8. İlerleme çizgisi
    # 9. PNG olarak kaydet
    ...

if __name__ == "__main__":
    main()
```

---

### 4.2 `render_scene.py` — Detaylı Tasarım

```python
#!/usr/bin/env python3
"""
Sahne-2 Prototip — FFmpeg Video Render

Hedra lip-sync videosu + AHU ses + konuşma balonu PNG'sini
tek MP4 video dosyasında birleştirir.

Pipeline:
  1. Hedra video → scale 720:730 (üst kısım)
  2. Balon PNG → scale 720:550 (alt kısım)
  3. vstack → dikey birleştir → 720x1280
  4. AHU MP3 → ses olarak ekle

Kullanım: python render_scene.py
Çıktı:   output/scene2_tr_prototype.mp4
"""

import subprocess, logging, json, sys
from pathlib import Path

# ============================================================
# SABİTLER
# ============================================================
HEDRA_VIDEO = "assets/hedra_tr.mp4"
BUBBLE_PNG  = "output/bubble.png"
AHU_MP3     = "assets/ahu_tr.mp3"
OUTPUT      = "output/scene2_tr_prototype.mp4"

FACE_H    = 730   # Hedra video yüksekliği (kırpılmış)
BUBBLE_H  = 550   # Balon PNG yüksekliği
VIDEO_W   = 720   # Çıktı genişliği
VIDEO_H   = 1280  # Çıktı yüksekliği

FFMPEG    = "ffmpeg"
FFPROBE   = "ffprobe"

# ============================================================
# FONKSİYONLAR
# ============================================================

def get_duration(filepath):
    """ffprobe ile video/ses süresini al."""
    ...

def build_ffmpeg_cmd(duration):
    """FFmpeg komutunu oluştur.
    
    Kullanılacak parametreler:
      - scale=720:730 (Hedra)
      - scale=720:550 (balon)
      - vstack=inputs=2 (dikey birleştirme)
      - preset=fast, crf=23 (h264 kalite)
      - aac@128k (ses codec)
      - yuv420p (pixel format)
      - t={duration} (video süresi)
      - movflags +faststart (web optimizasyonu)
    """
    ...

def run_command(cmd):
    """FFmpeg komutunu çalıştır, çıktıyı logla."""
    ...

def validate_output(filepath):
    """Çıktı dosyasını ffprobe ile doğrula.
    
    Kontrol edilecekler:
      - Dosya var mı?
      - Süre = 12.880sn ± 0.1
      - Çözünürlük = 720x1280
      - Codec = h264
      - Ses var mı (AAC)?
      - Boyut < 50MB
    """
    ...

def main():
    """Pipeline'ı çalıştır."""
    
    # 1. Süreyi al
    # 2. FFmpeg komutunu oluştur
    # 3. Pipeline'ı çalıştır
    # 4. Çıktıyı doğrula
    # 5. Sonucu yazdır
    ...

if __name__ == "__main__":
    main()
```

---

### 4.3 `send_test.py` — Detaylı Tasarım

```python
#!/usr/bin/env python3
"""
Sahne-2 Prototip — Telegram Gönderme Testi

scene2_tr_prototype.mp4'yi @hlk01_test_bot üzerinden
Telegram'a gönderir.

Kullanım: python send_test.py
"""

import asyncio, logging, subprocess
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# SABİTLER
# ============================================================
ENV_PATH    = "../../../.env"  # proje kökündeki .env
VIDEO_PATH  = "output/scene2_tr_prototype.mp4"
HEDEF_CHAT  = None  # test eden kullanıcının chat_id'si

# ============================================================
# FONKSİYONLAR
# ============================================================

def load_token():
    """Proje .env dosyasından TELEGRAM_TOKEN_TEST oku."""
    ...

def get_duration(filepath):
    """Video süresini ffprobe ile al."""
    ...

async def send_test_video(token, chat_id, video_path, duration):
    """Video'yu Telegram'a gönder.
    
    python-telegram-bot veya doğrudan HTTP API kullanılabilir.
    
    Parametreler:
      - video: InputFile(video_path)
      - supports_streaming=True
      - width=720, height=1280
      - duration=duration
    """
    ...

async def main():
    """Token al → chat_id al → video gönder."""
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 4.4 `README.md` — İçerik Taslağı

```markdown
# Sahne-2 Video Balloon Prototip — TR

## Amaç
Mevcut typewriter/editMessageText/delete_timer mekanizmaları 
olmadan, tüm içeriğin (HLK + AHU + balon + metin) tek video 
renderı içinde sunulduğu yeni Sahne-2 mimarisinin prototipi.

## Çalıştırma

# 1. Konuşma balonu PNG'sini üret
python generate_bubble.py

# 2. FFmpeg ile birleştir
python render_scene.py

# 3. Telegram'a gönder (test)
python send_test.py

## Gereksinimler
- Python 3.14
- Pillow 11.3.0+
- FFmpeg 8.1+
- Arial Bold font (Windows)

## Geri Dönüş
rm -rf PROJELER/SCENE2_BALLOON_PROTOTYPE/
Mevcut sistem etkilenmez.
```

---

## 5. Girdi Dosyaları

| Dosya | Kaynak | Boyut (yaklaşık) | Açıklama |
|-------|--------|-----------------|----------|
| `assets/hedra_tr.mp4` | `VİDEO Doyaları/hedra_sahne-2_small/hedra_video_tr_small_v2.mp4` | ~2.0 MB | TR lip-sync video, 720x1280, 12.880sn |
| `assets/ahu_tr.mp3` | `SES Dosyaları/hedra_SAHNE-2/hedra_ses_tr.mp3` | ~200 KB | TR AHU ses, 44100Hz, stereo, 12.771sn |
| `assets/arialbd.ttf` | `C:/Windows/Fonts/arialbd.ttf` | ~400 KB | Arial Bold font (Türkçe karakter desteği) |

### Süre Uyumluluğu

```
Video:  12.880 sn
MP3:    12.771 sn
Fark:   +0.109 sn (video MP3'ten uzun ✅ — video sonunda ses kesilmez)
Hedef:  12.880 sn (video süresi baz alınır)
```

---

## 6. Pipeline Adım Adım

### Adım-0: Hazırlık

```bash
cd hlk_PROJELER_02062026/HLK_01_asistan

# Dizinleri oluştur
mkdir -p PROJELER/SCENE2_BALLOON_PROTOTYPE/assets
mkdir -p PROJELER/SCENE2_BALLOON_PROTOTYPE/output

# Girdileri kopyala
cp "VİDEO Doyaları/hedra_sahne-2_small/hedra_video_tr_small_v2.mp4" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/hedra_tr.mp4"

cp "SES Dosyaları/hedra_SAHNE-2/hedra_ses_tr.mp3" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/ahu_tr.mp3"

cp "C:/Windows/Fonts/arialbd.ttf" \
   "PROJELER/SCENE2_BALLOON_PROTOTYPE/assets/arialbd.ttf"

cd PROJELER/SCENE2_BALLOON_PROTOTYPE
```

### Adım-1: Balon PNG Üretimi

```bash
python generate_bubble.py
```

**Beklenen çıktı:**
```
✅ Font yüklendi: arialbd.ttf (30px)
📝 Mesaj-1: 6 satır
📝 Mesaj-2: 2 satır
🖼️  bubble.png kaydedildi: 720x550, RGBA
```

**Doğrulama:**
```bash
ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 output/bubble.png
# → width=720 height=550
```

### Adım-2: Video Render

```bash
python render_scene.py
```

**Beklenen çıktı:**
```
🎬 Pipeline başladı...
   Girdi: assets/hedra_tr.mp4 (12.880sn)
   PNG:   output/bubble.png (720x550)
   Ses:   assets/ahu_tr.mp3 (12.771sn)
✅ Render tamamlandı: output/scene2_tr_prototype.mp4

Doğrulama:
   Süre:       12.880 sn
   Çözünürlük: 720x1280
   Codec:      h264
   Ses:        aac, stereo, 128kbps
   Boyut:      ~2.4 MB
```

**Doğrulama:**
```bash
ffprobe -v error -show_entries format=duration,size,bit_rate \
  -of default=noprint_wrappers=1 output/scene2_tr_prototype.mp4
```

### Adım-3: Telegram Testi

```bash
python send_test.py
```

**Beklenen çıktı:**
```
🔐 Token yüklendi: TELEGRAM_TOKEN_TEST (bot: @hlk01_test_bot)
📤 Video gönderiliyor: scene2_tr_prototype.mp4 (12.880sn)
✅ Video gönderildi: message_id=XXXX
```

---

## 7. Test Senaryosu

### Test-1: Balon PNG Doğrulama (offline)

| Test | Beklenen | Kontrol |
|------|---------|---------|
| `bubble.png` boyutu | 720x550 | ffprobe |
| Şeffaf arkaplan | RGBA, alpha=0 | Python kontrol |
| Türkçe karakterler | "ü", "ğ", "ş", "ı", "ö", "ç" okunur | Görsel inceleme |
| HLK vurgusu | Altın rengi (#e8b84b) | Pixel değeri |
| Balon-1 pozisyonu | y=30 başlar | Pixel kontrol |
| Balon-2 pozisyonu | y=280 başlar | Pixel kontrol |
| İlerleme çizgisi | y=490, #4a4a6a | Pixel kontrol |

### Test-2: Video Doğrulama (offline)

| Test | Beklenen | Kontrol |
|------|---------|---------|
| Çözünürlük | 720x1280 | ffprobe |
| Süre | 12.880sn (±0.1) | ffprobe |
| En-boy oranı | 9:16 (0.5625) | ffprobe |
| Codec | h264 | ffprobe |
| Pixel format | yuv420p | ffprobe |
| Ses codec | aac | ffprobe |
| Ses kanal | stereo | ffprobe |
| Ses bitrate | ~128kbps | ffprobe |
| Dosya boyutu | < 10MB | ls |
| HLK yüzü | Merkezde, kesilmiş değil | Görsel |
| Balon okunabilir | Metin net, taşma yok | Görsel |
| Vurgu rengi | HLK altın renk | Görsel |

### Test-3: Telegram Gönderimi (canlı)

| Test | Beklenen | Kontrol |
|------|---------|---------|
| sendVideo 200 OK | HTTP 200 | Log |
| Video oynuyor | Telegram'da görüntülenir | Gözlem |
| Ses var | Hoparlör simgesi, ses duyulur | Gözlem |
| 9:16 format | Dikey, tam ekran | Gözlem |
| Streaming | Anında oynatma başlar | Gözlem |
| Video bitişi | Doğal durur, replay butonu | Gözlem |
| Flood control | Hata yok | Log |

### Test-4: Karşılaştırma (Mevcut Sistem vs Prototip)

| Metrik | Mevcut | Prototip | Sonuç |
|--------|--------|----------|-------|
| API çağrısı sayısı | ~70 | **1** | ➡️ Ölç |
| Toplam süre | ~20sn | **12.88sn** | ➡️ Ölç |
| Flood control | Var | **Yok** | ➡️ Gözlem |
| Kullanıcı deneyimi | Karmaşık | **Basit** | ➡️ Değerlendir |

---

## 8. Başarı Kriterleri

### Zorunlu (Hepsi karşılanmalı)

- [ ] **P1:** `generate_bubble.py` çalışır, 720x550 PNG üretir
- [ ] **P2:** `render_scene.py` çalışır, 720x1280 MP4 üretir
- [ ] **P3:** TR karakterler (ü,ğ,şı,ö,ç) PNG'de okunabilir
- [ ] **P4:** HLK vurgusu altın renk (#e8b84b) olarak görünür
- [ ] **P5:** Video Telegram'da 9:16 formatında oynar
- [ ] **P6:** AHU sesi net duyulur
- [ ] **P7:** HLK yüzü merkezde, taşma yok
- [ ] **P8:** Flood control hatası oluşmaz
- [ ] **P9:** Hiçbir mevcut dosya değişmez
- [ ] **P10:** Geri dönüş planı çalışır (silince sistem etkilenmez)

### İsteğe Bağlı (Varsa daha iyi)

- [ ] **P11:** Video boyutu < 3MB (mevcut ~2MB)
- [ ] **P12:** Render süresi < 5sn
- [ ] **P13:** İlerleme çizgisi animasyonu görünür
- [ ] **P14:** Balon gölge efekti (premium görünüm)

---

## 9. Karşılaştırma Tablosu

### Telegram API Çağrıları

| # | İşlem | Mevcut | Prototip | Kazanç |
|---|-------|--------|----------|--------|
| 1 | `sendVideo` | 1 | 1 | — |
| 2 | `sendMessage` (hint) | 1 | **0** | -1 |
| 3 | `sendMessage` (balon-1) | 1 | **0** | -1 |
| 4 | `editMessageText` (balon-1 × 22 kelime) | 22 | **0** | -22 |
| 5 | `sendMessage` (balon-2) | 1 | **0** | -1 |
| 6 | `editMessageText` (balon-2 × 9 kelime) | 9 | **0** | -9 |
| 7 | `sendChatAction` (typing) | 31 | **0** | -31 |
| 8 | `deleteMessage` (video) | 1 | 1 | — |
| 9 | `deleteMessage` (hint) | 1 | **0** | -1 |
| 10 | `deleteMessage` (balon-1) | 1 | **0** | -1 |
| 11 | `deleteMessage` (balon-2) | 1 | **0** | -1 |
| | **Toplam** | **~70** | **~2** | **-68 (%97)** |

### Kod Satır Sayısı

| Dosya | Mevcut | Prototip |
|-------|--------|----------|
| `helpers/typewriter_animation.py` | ~110 | — |
| `handlers/start.py` (_run_balloons kısmı) | ~40 | — |
| `handlers/start.py` (delete_sahne2) | ~12 | — |
| `handlers/start.py` (SAHNE2_SURE_LANG) | ~5 | — |
| `handlers/start.py` (SESLI_HINT) | ~10 | — |
| `generate_bubble.py` (yeni) | — | +120 |
| `render_scene.py` (yeni) | — | +80 |
| `send_test.py` (yeni) | — | +60 |
| **Toplam** | **~180** | **~260** |

*Not: Prototip fazladan kod içerir. Gerçek entegrasyonda bu ~70 satıra düşer.*

---

## 10. Geri Dönüş Planı

### Anlık Geri Dönüş (test sırasında sorun olursa)

```bash
# Prototip dizinini tamamen sil
cd hlk_PROJELER_02062026/HLK_01_asistan
rm -rf PROJELER/SCENE2_BALLOON_PROTOTYPE/

# Mevcut sistem aynen çalışmaya devam eder
# testi başlat → @hlk01_test_bot → /start → mevcut Sahne-2
```

### Kısmi Geri Dönüş (sadece bir dosyada sorun varsa)

```bash
# Sadece PNG'yi yeniden üret
cd PROJELER/SCENE2_BALLOON_PROTOTYPE
python generate_bubble.py  # düzeltilmiş versiyon

# Sadece video'yu yeniden render et
python render_scene.py

# Sadece Telegram testini tekrarla
python send_test.py
```

### Kalıcı Geri Dönüş (prototip tamamen iptal)

```bash
# Tüm prototip izlerini temizle
rm -rf PROJELER/SCENE2_BALLOON_PROTOTYPE/
rm -f SCENE2_TR_PROTOTYPE_PLAN.md
rm -f SCENE2_TR_PROTOTYPE_IMPLEMENTATION.md
rm -f SCENE2_VIDEO_BALLOON_PROTOTYPE.md

# Mevcut sistem etkilenmez
# testi başlat → Sahne-2 eskisi gibi çalışır
```

---

## 11. Riskler ve Önlemler

| # | Risk | Olasılık | Etki | Önlem | Acil Durum |
|---|------|---------|------|-------|-----------|
| 1 | **Türkçe karakterler bozuk** | 🟢 Düşük | 🔴 Yüksek | Arial Bold font testi, `encoding='unic'` | Font değiştir (Segoe UI, Tahoma) |
| 2 | **HLK yüzü kırpılır** | 🟡 Orta | 🔴 Yüksek | scale=720:730 ile üst kısmı koru | scale değerini 700 veya 760 dene |
| 3 | **Balon metni taşar** | 🟡 Orta | 🟡 Orta | word_wrap testi, font size küçült | Fontu 28px yap, PADDING'i artır |
| 4 | **FFmpeg vstack hatası** | 🟢 Düşük | 🟡 Orta | overlay yöntemine geç | `overlay=0:730` |
| 5 | **Ses/video senkron kayar** | 🟢 Düşük | 🟡 Orta | `-t video_suresi` ile kırp | MP3 süresini video süresine eşitle |
| 6 | **Telegram video reddeder** | 🟢 Düşük | 🔴 Yüksek | 50MB limit altında kal, 720p | CRF 26'ya çek, boyutu küçült |
| 7 | **Renk profili farklı** | 🟡 Orta | 🟢 Düşük | `-pix_fmt yuv420p` | `-colorspace bt709` ekle |
| 8 | **Mevcut sistem karışır** | 🔴 Yüksek | 🔴 Yüksek | Tamamen ayrı dizin | `rm -rf PROJELER/` |

---

## 12. Zaman Tahmini

| Aşama | İş | Süre | Bağımlılık |
|-------|----|------|-----------|
| 0 | Dizin oluşturma, dosya kopyalama | 5 dk | — |
| 1 | `generate_bubble.py` yazma | 45 dk | Aşama-0 |
| 2 | Ara test: PNG doğrulama | 5 dk | Aşama-1 |
| 3 | Hata düzeltme (font, renk) | 15 dk | Aşama-2 |
| 4 | `render_scene.py` yazma | 30 dk | Aşama-1 |
| 5 | Ara test: video doğrulama | 5 dk | Aşama-4 |
| 6 | Hata düzeltme (boyut, codec) | 10 dk | Aşama-5 |
| 7 | `send_test.py` yazma | 20 dk | Aşama-5 |
| 8 | Telegram testi | 15 dk | Aşama-7 |
| 9 | Düzeltme döngüsü | 20 dk | Aşama-8 |
| 10 | `README.md` yazma | 10 dk | Aşama-9 |
| | **Toplam** | **~3 saat** | |

---

## Uygulama Sırası (Özet)

```
SIRALI ÇALIŞMA AKIŞI:

  Adım    İşlem                      Süre    Durum
  ────    ──────────────────────     ────    ─────
  0       Dizin + kopyalama          5dk     ⏳
  ════════════════════════════════════════════════
  1       generate_bubble.py         45dk    ⏳
  2       Doğrulama (PNG)            5dk     ⏳
  3       Gerekirse düzelt           15dk    ⏳
  ════════════════════════════════════════════════
  4       render_scene.py            30dk    ⏳
  5       Doğrulama (video)          5dk     ⏳
  6       Gerekirse düzelt           10dk    ⏳
  ════════════════════════════════════════════════
  7       send_test.py               20dk    ⏳
  8       Telegram testi             15dk    ⏳
  9       Düzeltme döngüsü           20dk    ⏳
  ════════════════════════════════════════════════
  10      README.md                  10dk    ⏳
  ────    ──────────────────────     ────    
          TOPLAM:                    ~3 saat
```

> **Notlar:**
> - Her aşamadan sonra test yapılır, hata varsa düzeltilir
> - Mevcut sisteme ASLA dokunulmaz
> - Sorun çıkarsa `rm -rf PROJELER/` ile geri dönülür
> - Bu plan onaylandıktan sonra kod yazma aşamasına geçilir

---

## Onay

Plan tamamlandı. Onaylıyor musun?

- **Onayla →** Kod yazma aşamasına geç
- **Düzelt →** Plana değişiklik öner
- **İptal →** Prototipi başlatma
