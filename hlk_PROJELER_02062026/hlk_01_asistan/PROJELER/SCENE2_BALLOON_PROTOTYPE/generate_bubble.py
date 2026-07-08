#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sahne-2 Prototip v4.2 — Akıllı Metin Yönetimi (Smart Text Formatting)

Post-video baloncukla aynı tipografi:
  - **bold** → Candara Bold
  - *italic* → Candara Italic
  - ***bold+italic*** → Candara Bold Italic
  - HLK → her zaman mavi + bold

Renk Paleti:
  Balon zemini: #b9d7eb (pudra gökyüzü mavisi) alpha=170
  Ana yazı:     #282d46 (koyu çivit)
  HLK vurgusu:  #1e64c8 (canlı mavi)

Kullanım: python generate_bubble.py
Çıktı:    output/bubble.png (720x380, RGBA)
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

# ============================================================
# SABİTLER — v4.2 AKILLI METİN
# ============================================================

# Canvas
CANVAS_W = 720
CANVAS_H = 450
BG_RENK  = (0, 0, 0, 0)

# Renkler
BALON1_RENK  = (185, 215, 235, 170)  # pudra gökyüzü mavisi
BALON2_RENK  = (175, 205, 225, 160)  # pudra gökyüzü mavisi (biraz daha şeffaf)
METIN_RENK   = (40,  45,  70,  255)  # koyu çivit #282d46
HLK_RENK     = (30,  100, 200, 255)  # canlı mavi #1e64c8

# Layout
KOSA_YARI   = 28
PAD_X       = 24
PAD_Y       = 14
SATIR_ARASI = 8

# Simetrik balon — her iki tarafa eşit mesafe
BALON_MARGIN_LR = 16                    # canvas kenarından sağa/sola eşit boşluk
BALON_W = CANVAS_W - 2 * BALON_MARGIN_LR  # balon genişliği 720-32=688px
BALON_MAX_W = BALON_W - 2 * PAD_X         # metin alanı genişliği 688-48=640px

# Balon pozisyonları — simetrik merkez
BALON1_X = BALON_MARGIN_LR
BALON1_Y = 8
BALON2_X = BALON_MARGIN_LR
BALON2_Y = 320  # balon-1 altı + boşluk (308 + 12)

# Font boyutları — orta boy
BOYUT_NORMAL  = 36
BOYUT_BOLD    = 36
BOYUT_ITALIC  = 36
BOYUT_BOLDIT  = 36

# ============================================================
# FONT KAYNAKLARI (Candara — bold/italic varyantları mevcut)
# ============================================================

FONTS = {
    "normal":     "assets/candara.ttf",
    "bold":       "assets/candarab.ttf",
    "italic":     "assets/candarai.ttf",
    "bold_italic": "assets/candaraz.ttf",
}


# ============================================================
# TR METİNLER (post-video baloncukla aynı format)
# ***bold+italic*** = bold+italic, **bold** = bold, *italic* = italic
# ============================================================

MESAJ1 = (
    "Merhaba! Ben **HLK**, ***yapay zeka destekli*** "
    "reklam asistanınız. Ürününüz için "
    "**en iyi reklamı** üretmek üzereyim. "
    "Başlamadan önce size ***birkaç kısa sorum*** "
    "olacak."
)

MESAJ2 = (
    "Lütfen ürünün **web sitesi linkini** "
    "veya ***ürün linkini*** gönderin."
)


# ============================================================
# FONT YÜKLEME
# ============================================================

@dataclass
class FontSet:
    normal: ImageFont.FreeTypeFont
    bold: ImageFont.FreeTypeFont
    italic: ImageFont.FreeTypeFont
    bold_italic: ImageFont.FreeTypeFont


def font_yukle(key: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
    """Bir font tipini yükle."""
    path = FONTS.get(key)
    if not path:
        return None
    if not Path(path).exists():
        # assets/ altında değilse Windows Fonts'tan dene
        win_path = f"C:/Windows/Fonts/{Path(path).name}"
        if Path(win_path).exists():
            path = win_path
        else:
            return None
    try:
        font = ImageFont.truetype(path, size)
        print(f"  ✓ Font: {Path(path).name} ({size}px) [{key}]")
        return font
    except Exception:
        return None


def fontlari_yukle(size: int) -> FontSet:
    """4 font varyantını da yükle, düşen varsa fallback yap."""
    normal = font_yukle("normal", size)
    bold = font_yukle("bold", size) or normal
    italic = font_yukle("italic", size) or normal
    bold_italic = font_yukle("bold_italic", size) or bold

    if not normal:
        print("  ⚠ Hiçbir font yüklenemedi, varsayılan kullanılıyor")
        from PIL import ImageFont
        normal = ImageFont.load_default()
        bold = normal
        italic = normal
        bold_italic = normal

    return FontSet(normal=normal, bold=bold, italic=italic, bold_italic=bold_italic)


# ============================================================
# AKILLI METİN AYRIŞTIRMA
# ============================================================

@dataclass
class TextSegment:
    """Metin parçası: içerik + stil."""
    text: str
    style: str  # "normal", "bold", "italic", "bold_italic"
    is_hlk: bool = False


def metin_ayristir(satir: str) -> list[TextSegment]:
    """Satırdaki **bold**, *italic*, ***bold+italic*** ve HLK'yı ayrıştırır.

    Tek bir regex ile üç pattern birden (Python left-to-right alternation).
    Öncelik: *** > ** > *
    """
    segments = []

    # Tek pattern: önce ***, sonra **, sonra *
    # Python re alternation'ı soldan sağa dener, en uzun önce dener
    pattern = re.compile(
        r'\*\*\*(.+?)\*\*\*'   # ***bold italic***
        r'|\*\*(.+?)\*\*'       # **bold**
        r'|\*(.+?)\*'           # *italic*
    )

    pos = 0
    for match in pattern.finditer(satir):
        # Düz metin (pattern dışı)
        if match.start() > pos:
            segments.append(TextSegment(text=satir[pos:match.start()], style="normal"))

        # Hangi grup eşleşti?
        content = match.group(1) or match.group(2) or match.group(3)
        if match.group(1):
            style = "bold_italic"
        elif match.group(2):
            style = "bold"
        else:
            style = "italic"

        # İçerikte HLK var mı?
        if "HLK" in content:
            hlk_re = re.compile(r'\b(HLK)\b')
            hlk_pos = 0
            for hm in hlk_re.finditer(content):
                if hm.start() > hlk_pos:
                    segments.append(TextSegment(
                        text=content[hlk_pos:hm.start()],
                        style=style,
                    ))
                segments.append(TextSegment(text="HLK", style=style, is_hlk=True))
                hlk_pos = hm.end()
            if hlk_pos < len(content):
                segments.append(TextSegment(
                    text=content[hlk_pos:], style=style,
                ))
        else:
            segments.append(TextSegment(text=content, style=style))

        pos = match.end()

    # Kalan düz metin
    if pos < len(satir):
        segments.append(TextSegment(text=satir[pos:], style="normal"))

    if not segments:
        segments.append(TextSegment(text=satir, style="normal"))

    return segments


# ============================================================
# YARDIMCILAR
# ============================================================

def metin_genislik(metin: str, font) -> int:
    """Pillow ile metin genişliğini ölç (markerları temizler)."""
    # Markersız düz metni ölç
    plain = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', metin)
    plain = re.sub(r'\*\*(.+?)\*\*', r'\1', plain)
    plain = re.sub(r'\*(.+?)\*', r'\1', plain)
    bbox = font.getbbox(plain)
    return bbox[2] - bbox[0]


def _strip_markers(text: str) -> str:
    """Metin içindeki tüm markerları temizler, düz metin döndürür."""
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    return t


def satirlara_bol(metin: str, font, max_width: int) -> list[str]:
    """Metni max_width'e göre satırlara böler.

    Markerları (** **, * *, *** ***) korur, sadece genişlik ölçerken temizler.
    Token'ları regex ile ayırır: marker grupları tek token, normal kelimeler ayrı.
    """
    # Regex: ***...***, **...**, *...* (öncelik sırasıyla), veya normal kelime
    token_re = re.compile(
        r'\*\*\*.+?\*\*\*'        # ***bold italic*** (en yüksek öncelik)
        r'|\*\*.+?\*\*'           # **bold**
        r'|\*.+?\*'               # *italic*
        r'|[^\s]+'                # normal kelime
    )
    tokens = [m.group(0) for m in token_re.finditer(metin)]

    if not tokens:
        return [metin]

    satirlar = [tokens[0]]
    for token in tokens[1:]:
        test_raw = satirlar[-1] + " " + token
        test_plain = _strip_markers(test_raw)
        if metin_genislik(test_plain, font) <= max_width:
            satirlar[-1] = test_raw
        else:
            satirlar.append(token)

    return satirlar


def yuvarlak_dikdortgen_ciz(draw, xy, radius, fill):
    """Yuvarlak köşeli dikdörtgen çizer."""
    x1, y1, x2, y2 = xy

    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

    draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)


def _satir_genislik(segments: list[TextSegment], font_set: FontSet) -> int:
    """Bir satırdaki tüm segmentlerin toplam genişliğini hesaplar."""
    toplam = 0
    for seg in segments:
        f = _seg_font(seg, font_set)
        toplam += metin_genislik(seg.text, f)
    return toplam


def _seg_font(seg: TextSegment, font_set: FontSet):
    """Segment stilina göre font seçer."""
    if seg.style == "bold":
        return font_set.bold
    elif seg.style == "italic":
        return font_set.italic
    elif seg.style == "bold_italic":
        return font_set.bold_italic
    return font_set.normal


def balon_metni_ciz(draw, satirlar: list[str], x: int, y: int,
                    max_width: int, font_set: FontSet):
    """Akıllı metin çizici — bold/italic/HLK renk desteği ile (sola yaslı)."""
    suanki_y = y + PAD_Y

    for satir_idx, satir in enumerate(satirlar):
        segments = metin_ayristir(satir)
        satir_genislik = _satir_genislik(segments, font_set)
        bosluk = max_width - satir_genislik

        # Sola yasla (justify kullanılmıyor)
        suanki_x = x + PAD_X
        for seg in segments:
            f = _seg_font(seg, font_set)
            renk = HLK_RENK if seg.is_hlk else METIN_RENK
            draw.text((suanki_x, suanki_y), seg.text, fill=renk, font=f)
            suanki_x += metin_genislik(seg.text, f)

        suanki_y += font_set.normal.size + SATIR_ARASI


# ============================================================
# ANA FONKSİYON
# ============================================================

def main():
    print("🎨 Sahne-2 v4.2 AKILLI METİN YÖNETİMİ")
    print("=" * 45)
    print(f"  Boyut: {CANVAS_W}x{CANVAS_H}px RGBA")
    print(f"  Font: Candara (normal/bold/italic/bold_italic)")
    print()

    # 1. Kanvas
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG_RENK)
    draw = ImageDraw.Draw(canvas)
    print("  ✓ Kanvas hazır")

    # 2. Fontları yükle (4 varyant)
    font_set = fontlari_yukle(BOYUT_NORMAL)
    print()

    # 3. Satırlara böl (düz metin olarak)
    satirlar1 = satirlara_bol(MESAJ1, font_set.normal, BALON_MAX_W)
    satirlar2 = satirlara_bol(MESAJ2, font_set.normal, BALON_MAX_W)

    print(f"  ✓ Mesaj-1: {len(satirlar1)} satır")
    for s in satirlar1:
        # Görüntüleme için markerları temizle
        temiz = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', s)
        temiz = re.sub(r'\*\*(.+?)\*\*', r'\1', temiz)
        temiz = re.sub(r'\*(.+?)\*', r'\1', temiz)
        print(f'    "{temiz}"')
    print(f"  ✓ Mesaj-2: {len(satirlar2)} satır")
    for s in satirlar2:
        temiz = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', s)
        temiz = re.sub(r'\*\*(.+?)\*\*', r'\1', temiz)
        temiz = re.sub(r'\*(.+?)\*', r'\1', temiz)
        print(f'    "{temiz}"')

    # 4. Balon yükseklikleri
    balon1_h = 2 * PAD_Y + len(satirlar1) * font_set.normal.size + (len(satirlar1) - 1) * SATIR_ARASI
    balon2_h = 2 * PAD_Y + len(satirlar2) * font_set.normal.size + (len(satirlar2) - 1) * SATIR_ARASI
    print(f"  ✓ Balon-1: {balon1_h}px | Balon-2: {balon2_h}px")

    # 5. Balon-1 çiz — simetrik (her iki tarafa eşit mesafe)
    b1_x1 = BALON1_X
    b1_y1 = BALON1_Y
    b1_x2 = BALON1_X + BALON_W
    b1_y2 = BALON1_Y + balon1_h
    yuvarlak_dikdortgen_ciz(draw, (b1_x1, b1_y1, b1_x2, b1_y2), KOSA_YARI, BALON1_RENK)
    balon_metni_ciz(draw, satirlar1, b1_x1, b1_y1, BALON_MAX_W, font_set, )
    print("  ✓ Balon-1 çizildi (sola yasli)")

    # 6. Balon-2 çiz — simetrik (her iki tarafa eşit mesafe)
    b2_x1 = BALON2_X
    b2_y1 = BALON2_Y
    b2_x2 = BALON2_X + BALON_W
    b2_y2 = BALON2_Y + balon2_h
    yuvarlak_dikdortgen_ciz(draw, (b2_x1, b2_y1, b2_x2, b2_y2), KOSA_YARI, BALON2_RENK)
    balon_metni_ciz(draw, satirlar2, b2_x1, b2_y1, BALON_MAX_W, font_set, )
    print("  ✓ Balon-2 çizildi (son balon — sola yaslı)")

    # 7. PNG kaydet
    output_path = Path("output/bubble.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(output_path))
    print(f"\n  ✅ bubble.png: {CANVAS_W}x{CANVAS_H}, {os.path.getsize(output_path)//1024}KB")


if __name__ == "__main__":
    main()
