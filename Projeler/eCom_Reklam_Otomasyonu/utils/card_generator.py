"""
card_generator.py — Telegram-Optimized Only
Dikey format, 800px sabit genişlik, Telegram mobil için optimize edilmiş teklif kartı.
01 -> 02 -> 03 bölümleri tam alt alta, tek sütun.
"""
import os, re
from PIL import Image, ImageDraw, ImageFont

# ── Renkler ─────────────────────────────────────────────────────────────────
NAVY      = "#07182E"
RED       = "#D32F2F"
WHITE     = "#FFFFFF"
DARK_TEXT = "#1C2B3A"
MID_GREY  = "#78909C"
DIVIDER   = "#CFD8DC"
PRICE_RED = "#E53935"

_TG_CARD_W  = 800     # Telegram mobil ekran genişliği
_TG_M       = 28      # Kenar boşluğu
_TG_FOOT_BG = "#0A1929"
_TG_OFF_W   = "#F5F7FA"

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Yardımcılar ──────────────────────────────────────────────────────────────

def _lf(bold_nt, reg_nt, size, bold=True):
    """Font yükle (Windows/Linux uyumlu)."""
    name = bold_nt if bold else reg_nt
    alt  = "LiberationSans-Bold.ttf" if bold else "LiberationSans.ttf"
    extras = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in ([name, alt] if os.name == "nt" else [alt, name]) + extras:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _tw(draw, text, font):
    try:
        return int(draw.textlength(text, font=font))
    except Exception:
        try:
            bb = draw.textbbox((0, 0), text, font=font)
            return bb[2] - bb[0]
        except Exception:
            return len(text) * 10


def _wrap(text, max_chars):
    words = text.split()
    lines, cur = [], []
    for w in words:
        if len(" ".join(cur + [w])) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _rr(draw, xy, r=12, fill=None, outline=None, lw=2):
    try:
        if fill:
            draw.rounded_rectangle(xy, radius=r, fill=fill)
        if outline:
            draw.rounded_rectangle(xy, radius=r, outline=outline, width=lw)
    except AttributeError:
        if fill:
            draw.rectangle(xy, fill=fill)
        if outline:
            draw.rectangle(xy, outline=outline, width=lw)


def _tg_lf(bold_name, reg_name, size, bold=True):
    return _lf(bold_name, reg_name, size, bold)


def _tg_tw(draw, text, font):
    return _tw(draw, text, font)


def _tg_th(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]
    except Exception:
        return 20


def _tg_section_card(draw, x0, y0, x1, y1, radius=14):
    """Telegram kartı beyaz kutusu — hafif gölge + kenarlık."""
    _rr(draw, [x0+2, y0+2, x1+3, y1+3], r=radius, fill="#E2E8EF")
    _rr(draw, [x0, y0, x1, y1], r=radius, fill=WHITE)
    _rr(draw, [x0, y0, x1, y1], r=radius, outline="#D0D7DE", lw=1)


def _tg_section_header(draw, img, x, y, number, label, font_title, font_badge):
    """Kırmızı badge + başlık + kırmızı alt çizgi (Telegram boyutu)."""
    badge_path = os.path.join(_HERE, "..", "assets", "parts", f"badge_{number:02d}.png")
    badge_w = 0
    if os.path.exists(badge_path):
        b = Image.open(badge_path).convert("RGBA")
        bw, bh = b.size
        scale = 56 / bh
        new_w = int(bw * scale)
        b = b.resize((new_w, 56), Image.LANCZOS)
        img.paste(b, (x, y), b)
        badge_w = new_w + 10
    else:
        draw.rectangle([x, y, x+52, y+52], fill=RED)
        draw.text((x+10, y+8), f"{number:02d}", fill=WHITE, font=font_badge)
        badge_w = 62

    tx = x + badge_w
    draw.text((tx, y + 6), label, fill=DARK_TEXT, font=font_title)
    tw = _tg_tw(draw, label, font_title)
    line_y = y + 50
    draw.line([tx, line_y, tx + tw, line_y], fill=RED, width=3)
    draw.ellipse([tx + tw - 2, line_y - 4, tx + tw + 7, line_y + 4], fill=RED)
    return badge_w


def generate_telegram_proposal_card(scenario: dict, price: float) -> str:
    """
    Telegram ekranı için optimize edilmiş HLK Senaryo Hazır-Onay Formu.
    • Genişlik : 800 px sabit (Telegram mobil)
    • Yükseklik: dinamik — sahne sayısına göre (1-5 sahne)
    • Düzen    : 01 → 02 → 03 bölümleri TAM alt alta, tek sütun
    • Footer   : tek satır, iki yana yaslanmış — stiller korunmuş
    """
    B, R = "arialbd.ttf", "arial.ttf"
    W = _TG_CARD_W
    M = _TG_M

    # Fontlar
    f_sec_title = _tg_lf(B, R, 34, bold=True)
    f_badge_num = _tg_lf(B, R, 28, bold=True)
    f_field_lbl = _tg_lf(B, R, 24, bold=True)
    f_field_val = _tg_lf(B, R, 22, bold=True)
    f_small     = _tg_lf(R, R, 19, bold=False)
    f_scene_t   = _tg_lf(B, R, 21, bold=True)
    f_footer_l  = _tg_lf(B, R, 24, bold=True)
    f_price     = _tg_lf(B, R, 60, bold=True)
    f_price_sub = _tg_lf(B, R, 24, bold=True)
    f_price_tag = _tg_lf(B, R, 22, bold=True)
    f_slogan    = _tg_lf(R, R, 20, bold=False)
    f_slogan_b  = _tg_lf(B, R, 20, bold=True)
    f_quote     = _tg_lf(B, R, 72, bold=True)

    # Veri
    brand    = scenario.get("brand",   "—")
    product  = scenario.get("product", "—")
    duration = scenario.get("duration", 15)
    scenes   = scenario.get("scenes", [])[:5]
    raw_vo   = scenario.get("voiceover_text", "")
    vo_text  = re.sub(r"\[[^\]]+\]", "", raw_vo).strip()

    # ─── YÜKSEKLIK HESABI ──────────────────────────────────────────
    HEADER_H = 320
    SEC_GAP  = 16
    PAD      = 14

    # 01 — Ürün Bilgisi
    S1_H = PAD + 60 + (3 * 52) + PAD

    # 02 — Senaryo Kurgusu
    DESC_CHARS = 52
    scene_row_heights = []
    scene_wrapped = []
    for sc in scenes:
        raw = sc.get("voiceover_segment") or sc.get("video_prompt") or ""
        desc = re.sub(r"\[[^\]]+\]", "", raw).strip()
        lines = _wrap(desc, DESC_CHARS)[:3]
        scene_wrapped.append(lines)
        h = max(54, 28 + len(lines) * 22 + 8)
        scene_row_heights.append(h)

    S2_INNER = sum(scene_row_heights) + max(0, len(scenes) - 1) * 10 if scenes else 80
    S2_H = PAD + 60 + S2_INNER + PAD

    # 03 — Dış Ses
    VO_CHARS = 56
    vo_lines = _wrap(vo_text, VO_CHARS)[:10] if vo_text else ["(Voiceover metni yok)"]
    VO_TEXT_H = len(vo_lines) * 26 + 40
    S3_H = PAD + 60 + max(120, VO_TEXT_H) + PAD

    # Footer
    FOOTER_H = 88

    TOTAL_H = (HEADER_H + SEC_GAP + S1_H + SEC_GAP
               + S2_H + SEC_GAP + S3_H + SEC_GAP + FOOTER_H)

    # ─── CANVAS ────────────────────────────────────────────────────
    img  = Image.new("RGB", (W, TOTAL_H), _TG_OFF_W)
    draw = ImageDraw.Draw(img)

    # ══ HEADER ═════════════════════════════════════════════════════
    header_path = os.path.join(_HERE, "..", "assets", "parts", "header.png")
    if os.path.exists(header_path):
        hdr = Image.open(header_path).convert("RGB")
        hdr = hdr.resize((W, HEADER_H), Image.LANCZOS)
        img.paste(hdr, (0, 0))
    else:
        draw.rectangle([0, 0, W, HEADER_H], fill=NAVY)
        draw.text((M, 80), "HLK AI REKLAM", fill=WHITE, font=f_sec_title)

    # Slogan şeridi (header alt kenarı)
    draw.rectangle([0, HEADER_H - 50, W, HEADER_H], fill=_TG_OFF_W)
    slogan_y = HEADER_H - 38
    s1 = "Yaratici fikirler, "
    s2 = "etkili senaryolar,"
    s3 = " guclu sonuclar."
    sx = M
    draw.text((sx, slogan_y), s1, fill=DARK_TEXT, font=f_slogan)
    sx += _tg_tw(draw, s1, f_slogan)
    draw.text((sx, slogan_y), s2, fill=RED, font=f_slogan_b)
    sx += _tg_tw(draw, s2, f_slogan_b)
    draw.text((sx, slogan_y), s3, fill=DARK_TEXT, font=f_slogan)

    # ══ 01 — ÜRÜN BİLGİSİ ═════════════════════════════════════════
    S1_Y = HEADER_H + SEC_GAP
    _tg_section_card(draw, M, S1_Y, W - M, S1_Y + S1_H)
    _tg_section_header(draw, img, M + 12, S1_Y + PAD, 1, "URUN BILGISI", f_sec_title, f_badge_num)

    row_y = S1_Y + PAD + 62
    icon_files = ["sec1_icon_1.png", "sec1_icon_2.png", "sec1_icon_3.png"]
    f_labels   = ["Marka", "Urun", "Sure (sn)"]
    f_values   = [
        brand[:42] + "..." if len(brand) > 42 else brand,
        product[:42] + "..." if len(product) > 42 else product,
        f"{duration} sn",
    ]
    for i in range(3):
        icon_path = os.path.join(_HERE, "..", "assets", "parts", icon_files[i])
        ix = M + 18
        if os.path.exists(icon_path):
            ic = Image.open(icon_path).convert("RGBA")
            ic = ic.resize((36, 36), Image.LANCZOS)
            img.paste(ic, (ix, row_y + 4), ic)
        lx = ix + 46
        draw.text((lx, row_y), f_labels[i], fill=DARK_TEXT, font=f_field_lbl)
        colon_x = lx + 130
        draw.text((colon_x, row_y), ":", fill=DARK_TEXT, font=f_field_lbl)
        val_x = colon_x + 18
        draw.text((val_x, row_y + 2), f_values[i], fill=DARK_TEXT, font=f_field_val)
        dot_s = val_x + _tg_tw(draw, f_values[i], f_field_val) + 8
        for dx in range(dot_s, W - M - 20, 9):
            draw.ellipse([dx, row_y + 20, dx + 3, row_y + 23], fill=DIVIDER)
        row_y += 52

    # ══ 02 — SENARYO KURGUSU ══════════════════════════════════════
    S2_Y = S1_Y + S1_H + SEC_GAP
    _tg_section_card(draw, M, S2_Y, W - M, S2_Y + S2_H)
    _tg_section_header(draw, img, M + 12, S2_Y + PAD, 2, "SENARYO KURGUSU", f_sec_title, f_badge_num)

    sc_content_y = S2_Y + PAD + 66
    TL_X = M + 32  # timeline x

    if len(scenes) > 1:
        first_dy = sc_content_y + scene_row_heights[0] // 2
        last_dy  = sc_content_y + sum(scene_row_heights[:len(scenes)-1]) + (len(scenes)-1)*10 + scene_row_heights[-1]//2
        draw.line([TL_X, first_dy, TL_X, last_dy], fill=DIVIDER, width=3)

    sc_y = sc_content_y
    default_names = ["Sahne Adi 1", "Sahne Adi 2", "Sahne Adi 3", "Sahne Adi 4", "Sahne Adi 5"]
    for si, sc in enumerate(scenes):
        sname = sc.get("scene_name", default_names[si])
        sdur  = sc.get("duration_seconds", sc.get("duration", 5))
        dot_y = sc_y + scene_row_heights[si] // 2

        draw.ellipse([TL_X-9, dot_y-9, TL_X+9, dot_y+9], fill=RED, outline=WHITE, width=2)

        icon_num = (si % 3) + 1
        icon_path = os.path.join(_HERE, "..", "assets", "parts", f"sec2_icon_{icon_num}.png")
        icon_col_x = TL_X + 18
        if os.path.exists(icon_path):
            ic2 = Image.open(icon_path).convert("RGBA")
            ic2 = ic2.resize((44, 44), Image.LANCZOS)
            img.paste(ic2, (icon_col_x, sc_y + (scene_row_heights[si] - 44) // 2), ic2)

        text_x = icon_col_x + 52
        title_str = f"Sahne {si+1}: {sname}"
        draw.text((text_x, sc_y + 4), title_str, fill=DARK_TEXT, font=f_scene_t)
        dur_str = f" ({sdur}s)"
        dur_x = text_x + _tg_tw(draw, title_str, f_scene_t)
        draw.text((dur_x, sc_y + 4), dur_str, fill=RED, font=f_scene_t)

        for li, line in enumerate(scene_wrapped[si]):
            draw.text((text_x, sc_y + 28 + li * 22), line, fill=MID_GREY, font=f_small)

        sc_y += scene_row_heights[si] + 10

    # ══ 03 — DIŞ SES (VOICEOVER) ══════════════════════════════════
    S3_Y = S2_Y + S2_H + SEC_GAP
    _tg_section_card(draw, M, S3_Y, W - M, S3_Y + S3_H)

    mic_path = os.path.join(_HERE, "..", "assets", "parts", "mic.png")
    mic_col_x = M + 12
    if os.path.exists(mic_path):
        mic = Image.open(mic_path).convert("RGBA")
        mic = mic.resize((68, 68), Image.LANCZOS)
        img.paste(mic, (mic_col_x, S3_Y + PAD + 62), mic)

    header_x3 = mic_col_x + 76
    _tg_section_header(draw, img, header_x3, S3_Y + PAD, 3, "DIS SES (VOICEOVER)", f_sec_title, f_badge_num)

    draw.text((header_x3, S3_Y + PAD + 48), "\u201c", fill=RED, font=f_quote)
    vo_y = S3_Y + PAD + 62
    vo_x = header_x3 + 38
    for ln in vo_lines:
        draw.text((vo_x, vo_y), ln, fill=DARK_TEXT, font=f_small)
        vo_y += 26
    draw.text((W - M - 54, vo_y + 4), "\u201d", fill=RED, font=f_quote)

    # ══ FOOTER — TOPLAM FATURA (tek satır, iki yana yaslanmış) ═════
    FOOT_Y = S3_Y + S3_H + SEC_GAP
    # Koyu lacivert arka plan + kırmızı kenarlık
    _rr(draw, [M, FOOT_Y, W - M, FOOT_Y + FOOTER_H], r=14, fill=_TG_FOOT_BG)
    _rr(draw, [M, FOOT_Y, W - M, FOOT_Y + FOOTER_H], r=14, outline=RED, lw=2)

    # Sol — "TOPLAM FATURA"
    label_y = FOOT_Y + (FOOTER_H - _tg_th(draw, "TOPLAM FATURA", f_footer_l)) // 2
    draw.text((M + 24, label_y), "TOPLAM FATURA", fill=WHITE, font=f_footer_l)

    # Sağ — Fiyat + USD + KDV (sağa yaslanmış, tek satır)
    price_whole = int(price)
    price_dec   = int(round((price - price_whole) * 100))
    p_main = f"${price_whole:,}"
    p_sub  = f".{price_dec:02d}"
    p_tag  = "  USD + KDV"

    pm_w = _tg_tw(draw, p_main, f_price)
    ps_w = _tg_tw(draw, p_sub,  f_price_sub)
    pt_w = _tg_tw(draw, p_tag,  f_price_tag)
    price_start_x = W - M - 20 - (pm_w + ps_w + pt_w)
    pc_y = FOOT_Y + FOOTER_H // 2

    main_y = pc_y - _tg_th(draw, p_main, f_price) // 2
    sub_y  = pc_y - _tg_th(draw, p_sub,  f_price_sub) // 2 + 10
    tag_y  = pc_y - _tg_th(draw, p_tag,  f_price_tag) // 2 + 10

    draw.text((price_start_x,            main_y), p_main, fill=PRICE_RED, font=f_price)
    draw.text((price_start_x + pm_w,     sub_y),  p_sub,  fill=PRICE_RED, font=f_price_sub)
    draw.text((price_start_x + pm_w + ps_w, tag_y), p_tag, fill=WHITE,    font=f_price_tag)

    # Alt not görseli
    note_path = os.path.join(_HERE, "..", "assets", "parts", "footer_note.png")
    if os.path.exists(note_path):
        note = Image.open(note_path).convert("RGBA")
        note = note.resize((W, 52), Image.LANCZOS)
        img.paste(note, (0, FOOT_Y + FOOTER_H - 2),
                  note.split()[3] if note.mode == "RGBA" else None)

    # ── Kaydet ────────────────────────────────────────────────────
    out_dir = os.path.join(_HERE, "..", "assets", "cards")
    os.makedirs(out_dir, exist_ok=True)
    sc_id = scenario.get("id", "telegram")
    out_path = os.path.join(out_dir, f"proposal_tg_{sc_id}.png")
    img.save(out_path, "PNG")
    return out_path
