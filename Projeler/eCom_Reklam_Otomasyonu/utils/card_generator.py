"""
card_generator.py — v4 Referans Uyumlu
Dikey 1080x1920 format, örnek_seneryo hazır formu.png'e birebir uygun.
• Lacivert köşegen header band
• HLK logosu + kırmızı çizgi aksanı
• Kırmızı kare bölüm badge'leri (01, 02, 03)
• Gerçek ikonlar yerine PIL ile çizilmiş geometrik ikonlar
• Film makarası (02) ve mikrofon (03) görsel vurguları
• Lacivert footer + kırmızı fiyat
• Dinamik: admin fiyatı ve senaryo verisi
"""
import os, re
from PIL import Image, ImageDraw, ImageFont

# ── Renkler ─────────────────────────────────────────────────────────────────
NAVY      = "#07182E"
RED       = "#D32F2F"
RED_DARK  = "#B71C1C"
WHITE     = "#FFFFFF"
OFF_WHITE = "#F5F5F5"
LIGHT_GR  = "#F0F2F5"
DARK_TEXT = "#1C2B3A"
MID_GREY  = "#78909C"
DIVIDER   = "#CFD8DC"
GOLD      = "#FFFFFF"   # Fiyat beyaz (referansta beyaz)
PRICE_RED = "#E53935"   # Fiyat kırmızı

CARD_W = 1080
# CARD_H dinamik olarak içeriğe göre hesaplanır

# Template (arka plan) — varsa yükle
_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_WIDE = os.path.join(_HERE, "..", "assets", "hlk_form_template_wide.png")


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


def _card(draw, xy, radius=18):
    """Gölgeli beyaz kart (yumuşak kenarlık ve gölge)."""
    x0, y0, x1, y1 = xy
    # Draw soft shadow layers
    _rr(draw, [x0+1, y0+1, x1+3, y1+3], r=radius, fill="#E4E8EE")
    _rr(draw, [x0+2, y0+2, x1+2, y1+2], r=radius, fill="#ECEFF3")
    _rr(draw, xy, r=radius, fill=WHITE)
    _rr(draw, xy, r=radius, outline="#D0D7DE", lw=2)


def _section_badge(img, x, y, number):
    """Kırmızı kare badge — referans formdan kesilmiş yüksek kaliteli görsel."""
    badge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "parts", f"badge_{number:02d}.png")
    if os.path.exists(badge_path):
        badge_img = Image.open(badge_path)
        img.paste(badge_img, (x - 10, y - 10), badge_img.convert("RGBA") if badge_img.mode != "RGBA" else badge_img)


def _icon_circle(draw, cx, cy, color=None):
    """Koyu daire ikon zemini."""
    r = 34
    c = color or NAVY
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)
    return r


def _draw_tag_icon(draw, cx, cy):
    """Etiket ikonu (marka)."""
    _icon_circle(draw, cx, cy)
    # Basit etiket şekli
    draw.polygon(
        [(cx-14, cy-10), (cx+10, cy-10), (cx+18, cy), (cx+10, cy+10), (cx-14, cy+10)],
        fill=WHITE
    )
    draw.ellipse([cx+8, cy-4, cx+16, cy+4], fill=NAVY)


def _draw_box_icon(draw, cx, cy):
    """Kutu ikonu (ürün)."""
    _icon_circle(draw, cx, cy)
    draw.rectangle([cx-14, cy-12, cx+14, cy+12], outline=WHITE, width=3)
    draw.line([cx-14, cy-4, cx+14, cy-4], fill=WHITE, width=2)
    draw.line([cx, cy-12, cx, cy-4], fill=WHITE, width=2)


def _draw_film_icon(draw, cx, cy):
    """Film/kamera ikonu (süre)."""
    _icon_circle(draw, cx, cy)
    draw.ellipse([cx-14, cy-14, cx+14, cy+14], outline=WHITE, width=3)
    draw.polygon([(cx-5, cy-9), (cx+12, cy), (cx-5, cy+9)], fill=WHITE)


def _draw_person_icon(draw, cx, cy):
    """İnsan silueti (sahne)."""
    draw.ellipse([cx-14, cy-22, cx+14, cy+22], fill="#E0E0E0")
    draw.ellipse([cx-10, cy-20, cx+10, cy], fill=DARK_TEXT)
    draw.ellipse([cx-14, cy-5, cx+14, cy+22], fill=DARK_TEXT)


def _draw_mic_icon(draw, cx, cy, size=1.0):
    """Mikrofon ikonu — referans formdaki büyük mikrofon."""
    s = size
    r_body = int(28 * s)
    # Dış çember (kırmızı, geniş)
    outer_r = int(58 * s)
    draw.ellipse([cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r],
                 outline=RED, width=int(4*s))
    # Mikrofon gövdesi
    _rr(draw, [cx - int(20*s), cy - int(50*s), cx + int(20*s), cy + int(15*s)],
        r=int(20*s), fill=NAVY)
    # Mikrofon kolu
    draw.line([cx, cy + int(15*s), cx, cy + int(42*s)], fill=NAVY, width=int(6*s))
    draw.line([cx - int(22*s), cy + int(42*s), cx + int(22*s), cy + int(42*s)],
              fill=NAVY, width=int(5*s))
    # Ses dalgaları (kırmızı)
    for wr in [35, 46]:
        wr = int(wr * s)
        draw.arc([cx-wr, cy-wr+int(8*s), cx+wr, cy+wr+int(8*s)],
                 start=210, end=330, fill=RED, width=int(3*s))


def _draw_film_reel(draw, cx, cy, r=90):
    """Film makarası (02 bölümü sağ kısım)."""
    # Dış çember
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill="#1C1C2E", outline="#333", width=2)
    # İç çember
    ir = r // 3
    draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], fill="#2C2C3E")
    # Şerit delikleri
    for angle_deg in range(0, 360, 60):
        import math
        a = math.radians(angle_deg)
        hx = cx + int((r * 0.65) * math.cos(a))
        hy = cy + int((r * 0.65) * math.sin(a))
        draw.ellipse([hx-12, hy-12, hx+12, hy+12], fill="#111")
    # Kırmızı play butonu
    draw.ellipse([cx-24, cy-24, cx+24, cy+24], fill=RED)
    draw.polygon([(cx-8, cy-14), (cx+16, cy), (cx-8, cy+14)], fill=WHITE)


# ── Ana Üretici ──────────────────────────────────────────────────────────────

def generate_a6_proposal_card(scenario: dict, price: float) -> str:
    """
    Örnek forma birebir uygun HLK teklif kartı üretir.
    Dikey 1080x1920. Dinamik senaryo + admin fiyatı.
    """
    # ── VERİ ────────────────────────────────────────────────────────────────
    brand    = scenario.get("brand",   "—")
    product  = scenario.get("product", "—")
    duration = scenario.get("duration", 15)
    scenes   = scenario.get("scenes",  [])[:6]
    raw_vo   = scenario.get("voiceover_text", "")
    vo_text  = re.sub(r"\[[^\]]+\]", "", raw_vo).strip()

    # ═══════════════════════════════════════════════════════════════════════
    # GEÇİŞ 1 — İçerik ölçümü ve dinamik yükseklik hesabı
    # ═══════════════════════════════════════════════════════════════════════

    DESC_MAX_CHARS = 38   # Açıklama satır uzunluğu
    VO_WRAP_LIMIT  = 48   # Voiceover satır uzunluğu

    # --- S1 (Ürün Bilgisi) yüksekliği ---
    S1_H = 370

    # --- S2 (Senaryo Kurgusu) yüksekliği ---
    S2_HEADER = 96
    scene_heights = []
    scene_wrapped_descs = []
    
    default_names = ["Kizla Aksam", "Kardes Yuruyusu", "Evdey Geldin"]
    
    for si, scene in enumerate(scenes):
        sname = scene.get("scene_name", default_names[si] if si < len(default_names) else f"Sahne {si+1}")
        raw = scene.get("voiceover_segment") or scene.get("video_prompt") or ""
        sdesc = re.sub(r"\[[^\]]+\]", "", raw).strip()
        
        # Wrap description
        lines = _wrap(sdesc, DESC_MAX_CHARS)[:3]  # Max 3 lines to look neat
        scene_wrapped_descs.append(lines)
        
        # Calculate dynamic height for this scene row:
        # Min height 96px, otherwise title + lines + spacing
        h = max(96, 38 + len(lines) * 26 + 10)
        scene_heights.append(h)

    S2_GAP = 18
    # If no scenes, default to a minimum box height
    if not scenes:
        S2_H = S2_HEADER + 240 + 32
    else:
        S2_H = S2_HEADER + sum(scene_heights) + S2_GAP * (len(scenes) - 1) + 32

    # --- S3 (Dış Ses) yüksekliği ---
    S3_HEADER = 80
    MIC_AREA  = 160   # Mikrofon alanı (sabit)
    
    vo_wrapped_lines = _wrap(vo_text, VO_WRAP_LIMIT) if vo_text else ["(Voiceover metni yok)"]
    vo_wrapped_lines = vo_wrapped_lines[:12]  # Max 12 lines
    
    VO_H = len(vo_wrapped_lines) * 32 + 60   # tırnak + metin + kapanış
    S3_H = S3_HEADER + max(MIC_AREA, VO_H) + 40

    # --- Footer ---
    FOOT_H = 140
    NOTE_H  = 70

    # --- Toplam yükseklik ---
    M          = 36
    HEADER_H   = 480
    SLOGAN_H   = 0
    SECTION_GAP = 28
    CARD_H = (HEADER_H + SLOGAN_H
              + S1_H + SECTION_GAP
              + S2_H + SECTION_GAP
              + S3_H + SECTION_GAP
              + FOOT_H + NOTE_H + 20)

    # ═══════════════════════════════════════════════════════════════════════
    # GEÇİŞ 2 — Canvas oluştur ve çiz
    # ═══════════════════════════════════════════════════════════════════════
    img  = Image.new("RGB", (CARD_W, CARD_H), "#F5F7FA")
    draw = ImageDraw.Draw(img)

    # ── Fontlar ─────────────────────────────────────────────────────────────
    B, R = "arialbd.ttf", "arial.ttf"
    f_hlk     = _lf(B, R, 110, bold=True)   # HLK büyük logo
    f_aireklam= _lf(B, R, 44, bold=True)    # AI REKLAM
    f_banner  = _lf(B, R, 56, bold=True)    # Banner başlığı
    f_capsule = _lf(B, R, 32, bold=True)    # Kapsül
    f_slogan  = _lf(R, R, 30, bold=False)   # Slogan (normal)
    f_slogan_b= _lf(B, R, 30, bold=True)    # Slogan (kırmızı)
    f_sec     = _lf(B, R, 46, bold=True)    # Bölüm başlığı
    f_badge   = _lf(B, R, 38, bold=True)    # Badge numarası
    f_field_l = _lf(B, R, 30, bold=True)    # Alan başlığı
    f_field_v = _lf(B, R, 28, bold=True)    # Alan değeri
    f_small   = _lf(R, R, 24, bold=False)   # Küçük açıklama
    f_scene_t = _lf(B, R, 26, bold=True)    # Sahne başlığı
    f_price_l = _lf(B, R, 32, bold=True)    # "TOPLAM FATURA"
    f_price   = _lf(B, R, 80, bold=True)    # Fiyat
    f_note    = _lf(R, R, 26, bold=False)   # Alt not
    f_note_b  = _lf(B, R, 26, bold=True)    # Alt not ONAY vurgusu

    # ═══════════════════════════════════════════════════════════════════════
    # HEADER (0 – 480px)
    # ═══════════════════════════════════════════════════════════════════════
    # Paste header from reference template
    header_img_path = os.path.join(_HERE, "..", "assets", "parts", "header.png")
    if os.path.exists(header_img_path):
        header_img = Image.open(header_img_path)
        img.paste(header_img, (0, 0))
    else:
        draw.rectangle([0, 0, CARD_W, HEADER_H], fill=WHITE)

    # ═══════════════════════════════════════════════════════════════════════
    # BÖLÜM 01 — ÜRÜN BİLGİSİ
    # ═══════════════════════════════════════════════════════════════════════
    M = 36
    S1_Y = HEADER_H + 20
    S1_H = 370
    _card(draw, [M, S1_Y, CARD_W-M, S1_Y+S1_H])

    _section_badge(img, M+14, S1_Y+14, 1)
    draw.text((M+100, S1_Y+18), "ÜRÜN BİLGİSİ", fill=DARK_TEXT, font=f_sec)
    # Kırmızı alt çizgi ve yuvarlak uç
    sec_tw = _tw(draw, "ÜRÜN BİLGİSİ", f_sec)
    line_y = S1_Y + 72
    draw.line([M+100, line_y, M+100+sec_tw, line_y], fill=RED, width=4)
    draw.ellipse([M+100+sec_tw - 2, line_y - 5, M+100+sec_tw + 8, line_y + 5], fill=RED)

    # Alan satırları
    icon_fns  = [_draw_tag_icon, _draw_box_icon, _draw_film_icon]
    field_lbl = ["Marka", "Ürün", "Süre (sn)"]
    field_val = [
        brand[:38] + "..." if len(brand) > 38 else brand,
        product[:38] + "..." if len(product) > 38 else product,
        f"{duration} sn",
    ]
    ROW_H = (S1_H - 96) // 3
    for fi in range(3):
        ry = S1_Y + 90 + fi * ROW_H
        # Load cropped Section 1 icon from parts
        icon_path = os.path.join(_HERE, "..", "assets", "parts", f"sec1_icon_{fi+1}.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            img.paste(icon_img, (130, ry + 3), icon_img.convert("RGBA") if icon_img.mode != "RGBA" else icon_img)
        else:
            icon_fns[fi](draw, 130 + 34, ry + 34)
        # Etiket
        draw.text((219, ry + 20), field_lbl[fi], fill=DARK_TEXT, font=f_field_l)
        # Hizalanmış İki Nokta (Colon)
        colon_x = 400
        draw.text((colon_x, ry + 20), ":", fill=DARK_TEXT, font=f_field_l)
        # Değer veya noktalı çizgi
        value_x = 430
        if field_val[fi] and field_val[fi] != "—":
            draw.text((value_x, ry + 22), field_val[fi], fill=DARK_TEXT, font=f_field_v)
        # Noktalı çizgi
        dot_start = value_x
        if field_val[fi] and field_val[fi] != "—":
            dot_start += _tw(draw, field_val[fi], f_field_v) + 8
        for dx in range(dot_start, CARD_W - M - 30, 10):
            draw.ellipse([dx, ry + 42, dx+4, ry+46], fill=DIVIDER)

    # ═══════════════════════════════════════════════════════════════════════
    # BÖLÜM 02 — SENARYO KURGUSU
    # ═══════════════════════════════════════════════════════════════════════
    S2_Y = S1_Y + S1_H + 28
    _card(draw, [M, S2_Y, CARD_W-M, S2_Y+S2_H])

    _section_badge(img, M+14, S2_Y+14, 2)
    draw.text((M+100, S2_Y+18), "SENARYO KURGUSU", fill=DARK_TEXT, font=f_sec)

    # Film makarası — sağ
    film_reel_path = os.path.join(_HERE, "..", "assets", "parts", "film_reel.png")
    if os.path.exists(film_reel_path):
        film_img = Image.open(film_reel_path)
        film_y = S2_Y + (S2_H - 380)//2
        img.paste(film_img, (650, film_y), film_img.convert("RGBA") if film_img.mode != "RGBA" else film_img)
    else:
        _draw_film_reel(draw, CARD_W - M - 120, S2_Y + S2_H//2 + 10, r=108)

    # Sahne listesi (sol taraf)
    scene_x0 = M + 28
    
    # Calculate scene y-positions first
    scene_y_positions = []
    current_y = S2_Y + 88
    for h in scene_heights:
        scene_y_positions.append(current_y)
        current_y += h + S2_GAP

    # Draw dark vertical line for timeline connecting the centers of first and last dots
    if len(scenes) > 1:
        line_x = scene_x0 + 20
        line_y_start = scene_y_positions[0] + 43
        line_y_end = scene_y_positions[-1] + 43
        draw.line([line_x, line_y_start, line_x, line_y_end], fill=DIVIDER, width=4)

    for si, scene in enumerate(scenes):
        sc_y = scene_y_positions[si]
        sname = scene.get("scene_name", default_names[si] if si < len(default_names) else f"Sahne {si+1}")
        sdur  = scene.get("duration_seconds", 6)
        
        # Red timeline dot with white border
        line_x = scene_x0 + 20
        draw.ellipse([line_x - 12, sc_y + 43 - 12, line_x + 12, sc_y + 43 + 12], fill=RED, outline=WHITE, width=2)

        # Paste the high-quality cropped sec2_icon_X.png circle
        icon_num = (si % 3) + 1
        icon_path = os.path.join(_HERE, "..", "assets", "parts", f"sec2_icon_{icon_num}.png")
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            img.paste(icon_img, (scene_x0 + 50, sc_y), icon_img.convert("RGBA") if icon_img.mode != "RGBA" else icon_img)
        else:
            # Fallback
            _draw_person_icon(draw, scene_x0 + 50 + 43, sc_y + 43)

        # Sahne başlığı
        s_title = f"Sahne {si+1}: {sname}"
        draw.text((scene_x0 + 155, sc_y + 6), s_title, fill=DARK_TEXT, font=f_scene_t)
        # Süre (kırmızı)
        dur_str = f" ({sdur}s)"
        dur_x = scene_x0 + 155 + _tw(draw, s_title, f_scene_t)
        draw.text((dur_x, sc_y + 6), dur_str, fill=RED, font=f_scene_t)

        # Açıklama (dynamic wrapped lines)
        desc_lines = scene_wrapped_descs[si]
        for li, line in enumerate(desc_lines):
            draw.text((scene_x0 + 155, sc_y + 38 + li * 26), line,
                      fill=MID_GREY, font=f_small)

    # ═══════════════════════════════════════════════════════════════════════
    # BÖLÜM 03 — DIŞ SES (VOICEOVER)
    # ═══════════════════════════════════════════════════════════════════════
    S3_Y = S2_Y + S2_H + 28
    _card(draw, [M, S3_Y, CARD_W-M, S3_Y+S3_H])

    _section_badge(img, M+14, S3_Y+14, 3)

    # Mikrofon (sol)
    mic_cx = M + 14 + 72 + 72
    mic_cy = S3_Y + S3_H//2
    mic_path = os.path.join(_HERE, "..", "assets", "parts", "mic.png")
    if os.path.exists(mic_path):
        mic_img = Image.open(mic_path)
        mic_y = S3_Y + (S3_H - 172)//2
        img.paste(mic_img, (58, mic_y), mic_img.convert("RGBA") if mic_img.mode != "RGBA" else mic_img)
    else:
        _draw_mic_icon(draw, mic_cx, mic_cy, size=1.05)

    # Başlık ve Kırmızı Alt Çizgi
    draw.text((mic_cx + 82, S3_Y + 18), "DIŞ SES (VOICEOVER)", fill=DARK_TEXT, font=f_sec)
    sec3_tw = _tw(draw, "DIŞ SES (VOICEOVER)", f_sec)
    line_y = S3_Y + 72
    draw.line([mic_cx + 82, line_y, mic_cx + 82 + sec3_tw, line_y], fill=RED, width=4)
    draw.ellipse([mic_cx + 82 + sec3_tw - 2, line_y - 5, mic_cx + 82 + sec3_tw + 8, line_y + 5], fill=RED)

    # Büyük açılış tırnağı
    f_quote = _lf(B, R, 96, bold=True)
    draw.text((mic_cx + 82, S3_Y + 65), "“", fill=RED, font=f_quote)

    # Voiceover metni
    vo_x = mic_cx + 118
    vo_y = S3_Y + 82
    for line in vo_wrapped_lines:
        draw.text((vo_x, vo_y), line, fill=DARK_TEXT, font=f_small)
        vo_y += 32

    # Kapanış tırnağı
    draw.text((CARD_W - M - 70, vo_y + 10), "”", fill=RED, font=f_quote)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER — TOPLAM FATURA
    # ═══════════════════════════════════════════════════════════════════════
    FOOT_Y = S3_Y + S3_H + 32

    # Paste high-quality cropped gradient footer card background
    footer_card_path = os.path.join(_HERE, "..", "assets", "parts", "footer_card_clean.png")
    if os.path.exists(footer_card_path):
        footer_card_img = Image.open(footer_card_path)
        img.paste(footer_card_img, (M, FOOT_Y), footer_card_img.convert("RGBA") if footer_card_img.mode != "RGBA" else footer_card_img)

    # Fiyat — dinamik, kırmızı, büyük
    price_whole = int(price)
    price_dec   = int(round((price - price_whole) * 100))
    price_main  = f"{price_whole:,}"
    price_sub   = f".{price_dec:02d}"

    # Draw dynamic price text over the card ($ sign on the right side)
    price_x = 350
    draw.text((price_x, FOOT_Y + 44), price_main, fill=PRICE_RED, font=f_price)
    pw = _tw(draw, price_main, f_price)
    draw.text((price_x + pw, FOOT_Y + 70), price_sub, fill=PRICE_RED, font=f_field_l)
    psw = _tw(draw, price_sub, f_field_l)

    # Draw $ sign next to the decimal part
    currency_symbol = " $"
    draw.text((price_x + pw + psw, FOOT_Y + 44), currency_symbol, fill=PRICE_RED, font=f_price)
    pcw = _tw(draw, currency_symbol, f_price)

    # Draw "USD + KDV" next to price
    draw.text((price_x + pw + psw + pcw + 15, FOOT_Y + 70), "USD + KDV", fill=WHITE, font=f_field_l)

    # ── Alt not (Pasted directly from cropped footer note) ──────────────────
    footer_note_path = os.path.join(_HERE, "..", "assets", "parts", "footer_note.png")
    if os.path.exists(footer_note_path):
        note_img = Image.open(footer_note_path)
        img.paste(note_img, (0, CARD_H - 60), note_img.convert("RGBA") if note_img.mode != "RGBA" else note_img)
    else:
        # Fallback to manual draw
        NOTE_Y = CARD_H - 68
        draw.line([M, NOTE_Y - 14, CARD_W - M, NOTE_Y - 14], fill=DIVIDER, width=1)
        note1 = "Lutfen Onaylamak icin Asagidaki "
        note2 = "ONAY"
        note3 = " Butonunu kullaniniz."
        n1w = _tw(draw, note1, f_note)
        n2w = _tw(draw, note2, f_note_b)
        n3w = _tw(draw, note3, f_note)
        total_nw = n1w + n2w + n3w
        nx = (CARD_W - total_nw) // 2
        draw.text((nx, NOTE_Y), note1, fill=DARK_TEXT, font=f_note)
        draw.text((nx + n1w, NOTE_Y), note2, fill=RED, font=f_note_b)
        draw.text((nx + n1w + n2w, NOTE_Y), note3, fill=DARK_TEXT, font=f_note)

    # ── Kaydet ──────────────────────────────────────────────────────────────
    out_dir = os.path.join(_HERE, "..", "assets", "cards")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"proposal_{scenario.get('id', 'temp')}.png")
    img.save(out_path, "PNG")
    return out_path
