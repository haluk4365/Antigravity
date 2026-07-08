# Sahne-2 Video Render İçi Konuşma Balonu — Fizibilite Analizi

## 1. Mevcut Durum

### Video Özellikleri (Tüm Diller)

| Parametre | Değer |
|-----------|-------|
| Çözünürlük | **720 x 1280** (9:16 dikey) |
| Codec | H.264 High Profile, Level 31 |
| Bitrate | ~900-1100 kbps |
| Ses | AAC, 44100 Hz, Stereo |
| İçerik | Hedra AI lip-sync (konuşan kafa) |
| Format | Portrait / Telegram Story uyumlu |

### Video Kompozisyonu (Tahmini)

```
720px
←───────→
┌──────────┐  y=0    ← Siyah çerçeve (Hedra output padding)
│  ░░░░░░  │
│  ░░░░░░  │  y≈200
│   ┌──┐   │
│   │HLK│   │  y≈300-600  ← Yüz bölgesi (lip-sync)
│   │   │   │
│   └──┘   │
│          │
│          │
│          │  y≈900-1280  ← Alt boşluk (şu an boş / koyu)
│          │
│          │
└──────────┘  y=1280
```

Hedra AI lip-sync çıktılarında:
- Yüz **merkezde** (y≈300-700)
- Üst ve alt kısımda **doğal boşluk** bulunur (koyu/kontrastsız alan)
- Alt kısım yüzün altından itibaren ~400-500px boşluk içerir

---

## 2. Analiz Sorularına Cevaplar

### S1: HLK karakteri merkeze alınabilir mi?

**Evet.** Mevcut yapıda HLK karakteri zaten merkezdedir (lip-sync için yüz merkezde olmalıdır). Hedra AI'nın çıktısı standart portrait formatında olduğu için yüz doğal olarak frame'in üst-orta kısmında konumlanır.

**Ancak:** Şu anki lip-sync videosu yalnızca kafa/hareket içeriyor. Karakterin tam gövdesi veya sahne tasarımı yok. "HLK karakterini merkeze almak" için:
- Mevcut Hedra videosu üst kısma yerleştirilir (y=0-800)
- Alt kısım (y=800-1280) konuşma balonu için ayrılır
- Veya: yeni bir render katmanı eklenir (HLK karakteri + arka plan + konuşma balonu)

### S2: Alt boşluk konuşma balonu için yeterli mi?

**Evet, yeterlidir.** 

| Alan | px | Kullanım |
|------|----|----------|
| Toplam frame | 1280px | |
| Yüz bölgesi | ~500px (y=200-700) | Mevcut Hedra lip-sync |
| Alt boşluk | **~580px** (y=700-1280) | Konuşma balonu için kullanılabilir |

580px ≈ 720px genişliğinde bir alan. Bu alana:
- **2 satır metin:** ~120px (font 36px ile)
- **Bubble arkaplanı:** ~200px (padding + rounded rect)
- **HLK avatar/mini gösterge:** ~50px
- **Kalan boşluk:** ~210px (nefes payı)

**Bu yeterlidir.** Türkçe karşılama mesajı 22 kelime, İngilizce 28 kelime — 2-3 satıra sığar.

### S3: 9:16 format korunur mu?

**Evet.** 720x1280 çözünürlük ve 9:16 en-boy oranı aynen korunur. Konuşma balonu alt kısma eklendiğinde frame boyutları değişmez. Video, Telegram'da `supports_streaming=True` ile aynı şekilde gönderilmeye devam eder.

### S4: Konuşma balonu videoya gömülürse mimari nasıl sadeleşir?

**ÖNCE (mevcut mimari):**

```
Dil Seçimi
    ↓
send_video(hedra_lipsync.mp4)
    ↓
asyncio.create_task(_delete_sahne2())  ← MP3 süresi kadar bekle, sonra sil
    ↓
_run_balloons():
    asyncio.sleep(1)
    typewriter_animation(Mesaj-1)    ← Telegram mesajı, kelime kelime
    asyncio.sleep(1)
    typewriter_animation(Mesaj-2)    ← Telegram mesajı, kelime kelime
    ↓
delete_message(video)
delete_message(hint)
delete_message(balon-1)
delete_message(balon-2)
    ↓
WAIT_PRODUCT_LINK state
```

**SONRA (render içi balon ile):**

```
Dil Seçimi
    ↓
render_bubble_video(tr, "Merhaba...", "Link gönderin...")
    ├── Hedra lip-sync katmanı (mevcut video)
    ├── Konuşma balonu SVG/metin katmanı (alt kısım)
    ├── AHU ses katmanı (mevcut MP3)
    └── FFmpeg ile tek videoda birleştir
    ↓
send_video(render_edilmis_tek_video.mp4)
    ↓
asyncio.create_task(_delete_sahne2())  ← video süresi kadar bekle
    ↓
delete_message(video)
    ↓
WAIT_PRODUCT_LINK state
```

**Sadeleşen noktalar:**

| Modül/İşlem | Mevcut | Render içi | Tasarruf |
|------------|--------|-----------|----------|
| `typewriter_animation.py` | ✅ Karmaşık kelime kelime edit | ❌ **KALDIRILIR** | ~100 satır |
| `_run_balloons()` | ✅ 2 mesaj, sleep, senkron | ❌ **KALDIRILIR** | ~30 satır |
| Flood control yönetimi | ✅ Telegram limitiyle uğraş | ❌ **KALDIRILIR** | Sürekli hata takibi |
| `deleteMessage` × 4 | ✅ video, hint, balon-1, balon-2 | ❌ **SADECE 1** | 4 API çağrısı → 1 |
| AHU ses senkronu | ✅ Daktilo hızı MP3'e göre hesaplanır | ❌ **FFMPEG halleder** | Karmaşık mantık |
| SAHNE2_SURE_LANG | ✅ 8 dil için elle girilmiş | ❌ **KALDIRILIR** | Otomatik |
| Delete timer gecikmesi | ✅ Event loop scheduling sorunu | ❌ **KALDIRILIR** | Video bittiğinde biter |
| AR-002_39 | ✅ Kısmen implemente | ✅ **OTOMATİK** | Video+ses+metin aynı anda |

### S5: Hangi mevcut modüller tamamen kaldırılabilir?

| Modül | Dosya | Kaldırılma Sebebi |
|-------|-------|-------------------|
| **typewriter_animation** | `helpers/typewriter_animation.py` | Metin artık videonun içinde render edilir, Telegram mesajı olarak gönderilmez |
| **strip_html** | `helpers/typewriter_animation.py` | HTML formatlamaya gerek kalmaz (video içi düz metin) |
| **run_balloons()** | `handlers/start.py:326-358` | Balon gönderme mantığı tamamen kalkar |
| **SAHNE2_SURE_LANG** | `handlers/start.py:48-51` | Video süresi otomatik, elle girilen sabite gerek yok |
| **SESLI_HINT** | `handlers/start.py:55-64` | Video zaten sesli, ayrı uyarı gerekmez |
| **delete_sahne2 task** | `handlers/start.py:314-322` | Video doğal süresinde biter, ek timer gerekmez |

**Yaklaşık ~150 satır kod ve 4 dosya azalır.**

---

## 3. Yeni Mimari Akışı

```
Dil Seçimi (lang_tr)
    ↓
1. AHU MP3 üret (veya cache'den al)
2. Hedra lip-sync video al (mevcut)
3. Metinleri hazırla (welcome + link_request)
4. FFmpeg ile birleştir:
   ┌──────────────────────────┐
   │    720x1280 frame        │
   │                          │
   │   ┌────────────────┐     │
   │   │  Hedra lip-sync│     │  y=0-750
   │   │  (HLK anlatıyor)│     │
   │   └────────────────┘     │
   │                          │
   │   ┌────────────────┐     │
   │   │ ┌──────────┐   │     │
   │   │ │ Merhaba! │   │     │  y=800-1100
   │   │ │ Ben HLK, │   │     │  (konuşma balonu)
   │   │ └──────────┘   │     │
   │   └────────────────┘     │
   │                          │
   └──────────────────────────┘
    ↓
send_video(render_edilmis_video.mp4)
    ↓
asyncio.sleep(video_suresi)
    ↓
delete_message(video)
    ↓
WAIT_PRODUCT_LINK
```

### FFmpeg Birleştirme Komutu (Tahmini)

```bash
ffmpeg -i hedra_lipsync.mp4 -i ahu_ses.mp3 \
       -filter_complex "
         [0:v]scale=720:750[face];
         color=#1a1a2e:s=720x530[canvas];
         [face][canvas]vstack=inputs=2[stack];
         drawtext=text='Merhaba! Ben HLK':
                  fontsize=32:
                  fontcolor=white:
                  box=1:
                  boxcolor=black@0.6:
                  x=(w-text_w)/2:
                  y=h-200:
                  enable='between(t,0,3)'
       " -c:v libx264 -preset fast -crf 23 \
       -c:a aac -b:a 128k \
       -t 13 final_scene2.mp4
```

---

## 4. Riskler ve Dezavantajlar

| Risk | Seviye | Açıklama |
|------|--------|----------|
| **Render süresi** | 🟡 Orta | FFmpeg birleştirme ~1-3sn sürebilir, kullanıcı bekleme süresi artar |
| **Cache stratejisi** | 🟡 Orta | Her dil için render önceden yapılmalı veya cache'lenmeli |
| **Metin değişikliği** | 🟢 Düşük | Metin değişirse video yeniden render edilmeli |
| **Kalite kaybı** | 🟢 Düşük | H.264 re-encode kalitesi, CRF 18-23 ile ihmal edilebilir |
| **Boyut artışı** | 🟡 Orta | Metin katmanı eklenince dosya boyutu ~%5-10 artabilir |
| **Esneklik kaybı** | 🟡 Orta | Telegram bubble'a tıklama/etkileşim kaybolur (callback data) |

---

## 5. Nihai Karar

| Kriter | Değerlendirme | Puan |
|--------|--------------|------|
| Teknik fizibilite | ✅ Mümkün, FFmpeg ile 1 adımda | 10/10 |
| Mimari sadeleşme | ✅ ~150 satır kod, 4 dosya azalır | 9/10 |
| Senkron sorunları | ✅ FFmpeg ses+görüntü+metni kendisi senkronize eder | 10/10 |
| AR-002_39 uyumu | ✅ Video içinde olduğu için otomatik uyumlu | 10/10 |
| Render süresi | ⚠️ ~1-3sn ek süre (cache ile minimize edilir) | 7/10 |
| Esneklik | ⚠️ Dinamik metin değişikliklerinde yeniden render gerekir | 6/10 |
| **TOPLAM** | | **52/60** |

**Öneri:** Render içi konuşma balonu **teknik olarak mümkün** ve mevcut mimariyi önemli ölçüde sadeleştirir. Ancak render süresi ve cache stratejisi dikkatlice tasarlanmalıdır.
