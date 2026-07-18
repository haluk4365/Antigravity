# Sahne-2 Video Balloon Prototip — TR

## Amaç

Mevcut typewriter/editMessageText/delete_timer mekanizmaları olmadan,
tüm içeriğin (HLK + AHU + balon + metin) tek video renderı içinde
sunulduğu yeni Sahne-2 mimarisinin prototipi.

## Çalıştırma

```bash
# 1. Konuşma balonu PNG'sini üret
python generate_bubble.py

# 2. FFmpeg ile birleştir
python render_scene.py

# 3. Telegram'a gönder (test)
python send_test.py
```

## Gereksinimler

- Python 3.14+
- Pillow 11.3.0+
- FFmpeg 8.1+
- Segoe UI Bold font (Windows)
- python-telegram-bot v20+

## Çıktılar

| Dosya | Açıklama |
|-------|----------|
| `output/bubble.png` | Konuşma balonu PNG (720×550) |
| `output/scene2_tr_prototype.mp4` | Prototip video (720×1280, 12.88sn) |

## Pipeline

```
generate_bubble.py → output/bubble.png (720×550)
         ↓
render_scene.py   → hedra (720×730) + balon (720×550) + AHU ses
         ↓
output/scene2_tr_prototype.mp4 (720×1280, 12.88sn)
         ↓
send_test.py      → @hlk01_test_bot üzerinden Telegram'a gönder
```

## Geri Dönüş

```bash
rm -rf PROJELER/SCENE2_BALLOON_PROTOTYPE/
# Mevcut sistem etkilenmez
```
