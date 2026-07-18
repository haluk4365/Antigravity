#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.5 MULTI-LANGUAGE BUILD — 8 dil için overlay video üretimi.

Her dil için:
  1. Kaynak video + ses assets'e kopyalanır
  2. HTML metin → marker formatına çevrilir
  3. Bubble PNG (Pillow ile) üretilir
  4. FFmpeg ile overlay video render edilir (+5sn donuk son kare)
"""

import os, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Langs ──
LANGUAGES = ["tr", "en", "de", "fr", "es", "ar", "ru", "kr"]

# ── Paths ──
BASE = Path(__file__).parent.resolve()
PROJE = BASE.parent.parent
ASSETS = BASE / "assets"
OUTPUT = BASE / "output"

# GC-001: Merkezi path yapılandırması (config/video_paths.py)
sys.path.insert(0, str(PROJE))
from config.video_paths import (
    SAHNE2_DIR, SAHNE2_VIDEO_TEMPLATE,
    SES_SAHNE2_DIR, SES_SAHNE2_TEMPLATE,
)
VIDEO_SRC = SAHNE2_DIR
AUDIO_SRC = SES_SAHNE2_DIR

# ── Text constants (from handlers/start.py) ──
TYPEWRITER_MESSAGES = {
    "tr": "Merhaba! Ben <b>HLK</b>, <b><i>yapay zeka destekli</i></b> reklam asistanınız. Ürününüz için <b>en iyi reklamı</b> üretmek üzereyim. Başlamadan önce size <b><i>birkaç kısa sorum</i></b> olacak.",
    "en": "Hello! I'm <b>HLK</b>, your <b><i>AI-powered</i></b> ad assistant. I'm here to create the <b>best ads</b> for your products. Before we start, I have a <b><i>few quick questions</i></b> for you.",
    "fr": "Bonjour! Je suis <b>HLK</b>, votre assistant publicitaire <b><i>alimenté par l'IA</i></b>. Je suis là pour créer les <b>meilleures publicités</b> pour vos produits. Avant de commencer, j'ai <b><i>quelques questions rapides</i></b> pour vous.",
    "de": "Hallo! Ich bin <b>HLK</b>, Ihr <b><i>KI-gestützter</i></b> Werbeassistent. Ich bin hier, um die <b>besten Anzeigen</b> für Ihre Produkte zu erstellen. Bevor wir beginnen, habe ich <b><i>ein paar schnelle Fragen</i></b> für Sie.",
    "es": "¡Hola! Soy <b>HLK</b>, tu asistente publicitario <b><i>impulsado por IA</i></b>. Estoy aquí para crear los <b>mejores anuncios</b> para tus productos. Antes de comenzar, tengo <b><i>algunas preguntas rápidas</i></b> para ti.",
    "ar": "مرحبا! أنا <b>HLK</b>، مساعدك الإعلاني <b><i>المدعوم بالذكاء الاصطناعي</i></b>. أنا هنا لإنشاء <b>أفضل الإعلانات</b> لمنتجاتك. قبل أن نبدأ، لدي <b><i>بعض الأسئلة السريعة</i></b> لك.",
    "ru": "Привет! Я <b>HLK</b>, ваш рекламный ассистент <b><i>на основе ИИ</i></b>. Я здесь, чтобы создать <b>лучшую рекламу</b> для ваших продуктов. Прежде чем начать, у меня есть <b><i>несколько быстрых вопросов</i></b> для вас.",
    "kr": "Merheba! Ez <b>HLK</b> me, <b><i>AI-ê rênivîsbariya</i></b> reklamê alîkarê we me. Ez li vir im ji bo hilberîna we <b>baştirîn reklamê</b> çêdikim. Berî ku em dest pê bikin, <b><i>çend pirsên kurt</i></b> hene.",
}

LINK_REQUEST_MESSAGE = {
    "tr": "Lütfen ürünün <b>web sitesi linkini</b> veya <b><i>ürün linkini</i></b> gönderin.",
    "en": "Please send your <b>product website link</b> or <b><i>product link</i></b>.",
    "fr": "Veuillez envoyer le <b>lien du site Web</b> de votre produit ou le <b><i>lien du produit</i></b>.",
    "de": "Bitte senden Sie den <b>Link der Produktwebsite</b> oder den <b><i>Produktlink</i></b>.",
    "es": "Por favor, envía el <b>enlace del sitio web</b> del producto o el <b><i>enlace del producto</i></b>.",
    "ar": "يرجى إرسال <b>رابط موقع المنتج</b> أو <b><i>رابط المنتج</i></b>.",
    "ru": "Пожалуйста, отправьте <b>ссылку на сайт товара</b> или <b><i>ссылку на продукт</i></b>.",
    "kr": "Ji kerema xwe <b>rêjeya malpera hilberînê</b> an <b><i>rêjeya hilberînê</i></b> bişînin.",
}

# ── Bubble constants ──
CANVAS_W = 720
CANVAS_H = 450
BG_RENK  = (0, 0, 0, 0)
BALON1_RENK  = (185, 215, 235, 170)
BALON2_RENK  = (175, 205, 225, 160)
METIN_RENK   = (40,  45,  70,  255)
HLK_RENK     = (30,  100, 200, 255)
KOSA_YARI   = 28
PAD_X = 24
PAD_Y = 14
SATIR_ARASI = 8
BALON_MARGIN_LR = 16
BALON_W = CANVAS_W - 2 * BALON_MARGIN_LR
BALON_MAX_W = BALON_W - 2 * PAD_X
BALON1_X, BALON1_Y = BALON_MARGIN_LR, 8
BALON2_X, BALON2_Y = BALON_MARGIN_LR, 252
FONT_SIZE = 36

# ── Fonts ├─
FONT_DIR = ASSETS
# Dil bazında font seçimi: Arapça için Tahoma (Arapça glif desteği)
FONT_MAP = {
    "ar": {
        "normal": "C:/Windows/Fonts/tahoma.ttf",
        "bold":   "C:/Windows/Fonts/tahomabd.ttf",
        "italic": "C:/Windows/Fonts/tahoma.ttf",
        "bold_italic": "C:/Windows/Fonts/tahomabd.ttf",
    },
}
_DEFAULT_FONTS = {
    "normal": str(FONT_DIR / "candara.ttf"),
    "bold":   str(FONT_DIR / "candarab.ttf"),
    "italic": str(FONT_DIR / "candarai.ttf"),
    "bold_italic": str(FONT_DIR / "candaraz.ttf"),
}

def get_font_paths(lang: str) -> dict:
    return FONT_MAP.get(lang, _DEFAULT_FONTS)


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def html_to_markers(text: str) -> str:
    """Convert HTML bold/italic to marker format."""
    t = text
    t = re.sub(r'<b><i>(.*?)</i></b>', r'***\1***', t)
    t = re.sub(r'</?b>', '**', t)
    t = re.sub(r'</?i>', '*', t)
    return t


def strip_markers(text: str) -> str:
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    return t


def get_duration(filepath):
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(filepath)],
                          capture_output=True,text=True,timeout=15)
        if r.stdout.strip():
            return float(r.stdout.strip())
    except: pass
    return 0.0


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size) if Path(path).exists() else ImageFont.load_default()
    except:
        return ImageFont.load_default()


def text_width(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


# Font cache per language
_font_cache: dict[str, dict] = {}

def get_fonts_for_lang(lang: str):
    if lang not in _font_cache:
        paths = get_font_paths(lang)
        _font_cache[lang] = {
            "normal": load_font(paths["normal"], FONT_SIZE),
            "bold": load_font(paths["bold"], FONT_SIZE),
            "italic": load_font(paths["italic"], FONT_SIZE),
            "bold_italic": load_font(paths["bold_italic"], FONT_SIZE),
        }
    return _font_cache[lang]


# ═══════════════════════════════════════════════════════════
# BUBBLE GENERATION
# ═══════════════════════════════════════════════════════════

def split_lines(text, font, max_w):
    """Split text into lines respecting max width (preserves markers)."""
    token_re = re.compile(r'\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|[^\s]+')
    tokens = [m.group(0) for m in token_re.finditer(text)]
    if not tokens:
        return [text]

    lines = [tokens[0]]
    for tok in tokens[1:]:
        test = lines[-1] + " " + tok
        if text_width(strip_markers(test), font) <= max_w:
            lines[-1] = test
        else:
            lines.append(tok)
    return lines


def parse_text(line):
    """Parse line into segments with style info."""
    segments = []
    pat = re.compile(r'\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*')
    pos = 0
    for m in pat.finditer(line):
        if m.start() > pos:
            segments.append((line[pos:m.start()], "normal"))
        content = m.group(1) or m.group(2) or m.group(3)
        style = "bold_italic" if m.group(1) else ("bold" if m.group(2) else "italic")
        # Check for HLK inside content
        hlk_parts = re.split(r'\b(HLK)\b', content)
        for part in hlk_parts:
            if part == "HLK":
                segments.append(("HLK", style, True))
            elif part:
                segments.append((part, style, False))
        pos = m.end()
    if pos < len(line):
        segments.append((line[pos:], "normal", False))
    if not segments:
        segments.append((line, "normal", False))
    return segments


def get_font(style, lang="tr"):
    fonts = get_fonts_for_lang(lang)
    if style == "bold": return fonts["bold"]
    if style == "italic": return fonts["italic"]
    if style == "bold_italic": return fonts["bold_italic"]
    return fonts["normal"]


def rounded_rect(draw, xy, r, fill):
    x1,y1,x2,y2 = xy
    draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
    draw.pieslice([x1, y1, x1+2*r, y1+2*r], 180, 270, fill=fill)
    draw.pieslice([x2-2*r, y1, x2, y1+2*r], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*r, x1+2*r, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*r, y2-2*r, x2, y2], 0, 90, fill=fill)


def draw_bubble_text(draw, lines, x, y, max_w, lang="tr"):
    cy = y + PAD_Y
    for line in lines:
        segments = parse_text(line)
        cx = x + PAD_X
        for seg in segments:
            text, style = seg[0], seg[1]
            is_hlk = seg[2] if len(seg) > 2 else False
            font = get_font(style, lang)
            color = HLK_RENK if is_hlk else METIN_RENK
            draw.text((cx, cy), text, fill=color, font=font)
            cx += text_width(text, font)
        cy += FONT_SIZE + SATIR_ARASI


def generate_bubble(lang: str, text1: str, text2: str) -> Path:
    """Generate bubble PNG for a language. Returns path."""
    fonts = get_fonts_for_lang(lang)
    font = fonts["normal"]

    lines1 = split_lines(text1, font, BALON_MAX_W)
    lines2 = split_lines(text2, font, BALON_MAX_W)

    balon1_h = 2*PAD_Y + len(lines1)*FONT_SIZE + (len(lines1)-1)*SATIR_ARASI
    balon2_h = 2*PAD_Y + len(lines2)*FONT_SIZE + (len(lines2)-1)*SATIR_ARASI

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG_RENK)
    draw = ImageDraw.Draw(canvas)

    # Balon 1
    b1 = (BALON1_X, BALON1_Y, BALON1_X+BALON_W, BALON1_Y+balon1_h)
    rounded_rect(draw, b1, KOSA_YARI, BALON1_RENK)
    draw_bubble_text(draw, lines1, BALON1_X, BALON1_Y, BALON_MAX_W, lang)

    # Balon 2
    b2 = (BALON2_X, BALON2_Y, BALON2_X+BALON_W, BALON2_Y+balon2_h)
    rounded_rect(draw, b2, KOSA_YARI, BALON2_RENK)
    draw_bubble_text(draw, lines2, BALON2_X, BALON2_Y, BALON_MAX_W, lang)

    out = OUTPUT / f"bubble_{lang}.png"
    canvas.save(str(out))
    print(f"  ✓ Bubble {lang}: {lines1}, {lines2}, {out.name} ({out.stat().st_size//1024}KB)")
    return out


# ═══════════════════════════════════════════════════════════
# MAIN BUILD
# ═══════════════════════════════════════════════════════════

def main():
    print("="*55)
    print("V3.5 MULTI-LANGUAGE BUILD — 8 Dil")
    print("="*55)

    ASSETS.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)

    for lang in LANGUAGES:
        print(f"\n--- [{lang.upper()}] {'='*45}")
        ulang = lang.upper()

        # ── ADIM 1: Assets ──
        print("  ADIM 1: Assets...")
        src_v = VIDEO_SRC / SAHNE2_VIDEO_TEMPLATE.format(LANG=lang.upper())
        dst_v = ASSETS / f"hedra_{lang}.mp4"
        if src_v.exists():
            shutil.copy2(src_v, dst_v)
            print(f"  ✓ Video: {src_v.name}")
        else:
            print(f"  ✗ Video YOK: {src_v.name}")

        src_a = AUDIO_SRC / SES_SAHNE2_TEMPLATE.format(lang=lang)
        dst_a = ASSETS / f"ahu_{lang}.mp3"
        if src_a.exists():
            shutil.copy2(src_a, dst_a)
            print(f"  ✓ Audio: {src_a.name}")
        else:
            print(f"  ✗ Audio YOK: {src_a.name}")

        # ── ADIM 2: Bubble PNG ──
        print("  ADIM 2: Bubble PNG...")
        text1 = html_to_markers(TYPEWRITER_MESSAGES[lang])
        text2 = html_to_markers(LINK_REQUEST_MESSAGE[lang])
        generate_bubble(lang, text1, text2)

        # ── ADIM 3: Video Render ──
        print("  ADIM 3: Video Render...")
        vid = ASSETS / f"hedra_{lang}.mp4"
        bub = OUTPUT / f"bubble_{lang}.png"
        aud = ASSETS / f"ahu_{lang}.mp3"
        out = OUTPUT / f"scene2_{lang}_prototype.mp4"

        if not all(p.exists() for p in [vid, bub, aud]):
            print(f"  ✗ Eksik dosya, atlanıyor")
            continue

        dur = get_duration(vid)
        total_dur = round(dur + 5.0, 3)

        cmd = [
            "ffmpeg",
            "-i", str(vid), "-i", str(bub), "-i", str(aud),
            "-filter_complex",
            "[1:v]format=rgba[balloon];"
            "[0:v][balloon]overlay=0:830:format=auto[overlayed];"
            "[overlayed]tpad=stop_mode=clone:stop_duration=5[final_v]",
            "-map", "[final_v]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-af", "apad=pad_dur=5",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p", "-t", str(total_dur),
            "-movflags", "+faststart", "-y", str(out)
        ]

        print(f"  Rendering: {dur:.1f}s → {total_dur}s (+5s freeze)")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, stderr = proc.communicate(timeout=180)
            if proc.returncode != 0:
                errs = [l for l in stderr.split('\n') if 'error' in l.lower()][:3]
                for e in errs: print(f"  ✗ {e.strip()}")
                continue
            size_kb = out.stat().st_size // 1024
            print(f"  ✅ {out.name}: {total_dur}s, {size_kb}KB")
        except Exception as e:
            print(f"  ✗ Hata: {e}")

    print(f"\n{'='*55}")
    print("✅ ALL DONE — 8 dil V3.5 video hazir!")
    print("="*55)


if __name__ == "__main__":
    main()
