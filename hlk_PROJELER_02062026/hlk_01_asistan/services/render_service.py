"""
HLK Referans Form Render Servisi
MASTER-010: Referans Form PNG render — template.html + render.js → PNG

Bot runtime'ında Referans Form şablonlarını PNG olarak render eder.
Node.js + Puppeteer kullanır (FORMLAR/shared/render-common.js üzerinden).
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# FORMLAR dizini (render.js + node_modules burada)
_FORMLAR_DIR = Path(__file__).resolve().parent.parent / "FORMLAR"


async def render_form_png(form_name: str, data: dict) -> bytes | None:
    """Referans Formu PNG olarak render eder.

    Args:
        form_name: Klasör adı (örn: "REFERANS_SENARYO_ONAY_FORMU")
        data: Template'e enjekte edilecek veri (sample-data.json yapısında)

    Returns:
        PNG bytes veya hata durumunda None
    """
    form_dir = _FORMLAR_DIR / form_name
    render_js = form_dir / "render.js"
    template_html = form_dir / "template.html"

    # MASTER-012 / Rule 6: Tüm dosya yolları Runtime loglarına yazdırılır
    logger.info(f"📁 [RenderService] Referans Form: {form_name}")
    logger.info(f"   Form dizini   = {form_dir}")
    logger.info(f"   template.html = {template_html} (exists={template_html.exists()})")
    logger.info(f"   render.js     = {render_js} (exists={render_js.exists()})")

    if not render_js.exists():
        logger.error(f"❌ [RenderService] render.js bulunamadı: {render_js}")
        return None

    if not template_html.exists():
        logger.error(f"❌ [RenderService] template.html bulunamadı: {template_html}")
        return None

    # Geçici dosyalar
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp_json:
        json.dump(data, tmp_json, ensure_ascii=False)
        tmp_json_path = tmp_json.name

    tmp_png_path = tmp_json_path.replace(".json", ".png")
    logger.info(f"   geçici JSON   = {tmp_json_path}")
    logger.info(f"   hedef PNG     = {tmp_png_path}")

    try:
        # Node.js render.js çağrısı (create_subprocess_exec — shell injection güvenli)
        proc = await asyncio.create_subprocess_exec(
            "node", str(render_js), tmp_json_path, tmp_png_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(form_dir),
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err = stderr.decode("utf-8", errors="replace")[:300]
            logger.error(
                f"❌ [RenderService] Render hatası (exit={proc.returncode}): {err}"
            )
            return None

        png_path = Path(tmp_png_path)
        if not png_path.exists() or png_path.stat().st_size == 0:
            logger.error(f"❌ [RenderService] PNG oluşturulamadı: {tmp_png_path}")
            return None

        png_bytes = png_path.read_bytes()
        logger.info(
            f"✅ [RenderService] {form_name} → {len(png_bytes) / 1024:.0f}KB PNG"
        )
        return png_bytes

    except Exception as e:
        logger.error(f"❌ [RenderService] İstisna: {e}")
        return None

    finally:
        # Temizlik
        for p in (Path(tmp_json_path), Path(tmp_png_path)):
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# Form-specific render helpers
# ═══════════════════════════════════════════════════════════════════════════════

async def render_scenario_approval(user_data: dict) -> bytes | None:
    """REFERANS_SENARYO_ONAY_FORMU → PNG"""
    from handlers.website import _build_scenario_data

    data = _build_scenario_data(user_data)
    return await render_form_png("REFERANS_SENARYO_ONAY_FORMU", data)


async def render_brief_ozeti(user_data: dict, checks: dict) -> bytes | None:
    """REFERANS_BRIEF_OZETI → PNG — sample-data.json şeması tek otorite."""
    from handlers.website import _get_brief_value
    from datetime import datetime

    # Ürün Adı: URL'den veya araştırmadan
    url = user_data.get("website_url", "")
    if url:
        product_name = url.rstrip("/").split("/")[-1].split("?")[0][:40] or "Ürün"
    else:
        product_name = user_data.get("product_name", "—")

    # Marka
    brand = user_data.get("brand", "—")

    # Referans Görsel
    img_count = user_data.get("material_count", 0)
    ref_gorsel = f"{img_count} adet" if img_count > 0 else "Yok"

    data = {
        "adimlar": [
            {"no": 1, "baslik": "Brief", "altbaslik": "Özet İncelemede", "durum": "active"},
            {"no": 2, "baslik": "Senaryo", "altbaslik": "Sıradaki Adım", "durum": "pending"},
        ],
        "urun": [
            {"ikon": "🏷️", "label": "Ürün Adı", "deger": product_name},
            {"ikon": "⭐", "label": "Marka", "deger": brand},
            {"ikon": "🔗", "label": "Ürün Linki", "deger": _get_brief_value(user_data, "brief_link")},
            {"ikon": "🖼️", "label": "Referans Görsel", "deger": ref_gorsel},
            {"ikon": "📦", "label": "Ek Materyal", "deger": _get_brief_value(user_data, "brief_material")},
        ],
        "video": [
            {"ikon": "📱", "label": "Platform", "deger": _get_brief_value(user_data, "brief_platform")},
            {"ikon": "🎬", "label": "Format", "deger": _get_brief_value(user_data, "brief_format")},
            {"ikon": "📺", "label": "Çözünürlük", "deger": _get_brief_value(user_data, "brief_resolution")},
            {"ikon": "⏱️", "label": "Video Süresi", "deger": _get_brief_value(user_data, "brief_duration")},
            {"ikon": "🎨", "label": "Tanıtım Tarzı", "deger": _get_brief_value(user_data, "brief_style")},
            {"ikon": "👥", "label": "Hedef Kitle", "deger": _get_brief_value(user_data, "brief_audience")},
        ],
        "ses": [
            {"ikon": "🎙️", "label": "Ses Yapısı", "deger": _get_brief_value(user_data, "brief_audio")},
            {"ikon": "🌍", "label": "Seslendirme Dili", "deger": _get_brief_value(user_data, "brief_voicelang")},
            {"ikon": "🎭", "label": "Ses Karakteri", "deger": _get_brief_value(user_data, "brief_voicechar")},
        ],
        "tercihler": [
            {"ikon": "✨", "label": "Vurgulanacaklar", "deger": _get_brief_value(user_data, "brief_emphasis")},
        ],
        "footer": {
            "kod": "UI_REF_007_BRIEF_OZETI_V1",
            "versiyon": "V1.0",
            "tarih": datetime.now().strftime("%d.%m.%Y"),
        },
    }
    return await render_form_png("REFERANS_BRIEF_OZETI", data)
