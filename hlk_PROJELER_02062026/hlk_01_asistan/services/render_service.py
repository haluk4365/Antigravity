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


async def render_brief_onay(user_data: dict, checks: dict) -> bytes | None:
    """REFERANS_Brief_Onay_Formu → PNG — SAHNE-12'nin tek resmi referans formu."""
    from handlers.website import _get_brief_value, BRIEF_FIELDS
    from datetime import datetime

    # Maddeler: BRIEF_FIELDS sırasına göre, checks dict'ten onayli durumu
    maddeler = []
    aciklama_map = {
        "brief_link":       "Analiz edilen ürün sayfası",
        "brief_material":   "Kullanıcının yüklediği materyaller",
        "brief_platform":   "Yayınlanacak platform",
        "brief_format":     "Seçilen video formatı",
        "brief_resolution": "Video çözünürlüğü",
        "brief_duration":   "Tercih edilen video süresi",
        "brief_style":      "Reklam tanıtım tarzı",
        "brief_audience":   "Reklam hedef kitlesi",
        "brief_audio":      "Ses tercihleri",
        "brief_voicelang":  "Seçilen seslendirme dili",
        "brief_voicechar":  "Seslendirme karakteri",
        "brief_emphasis":   "Öne çıkarılacak detaylar",
    }

    for field_key, label, scene_id, editable in BRIEF_FIELDS:
        ikon = label.split(" ", 1)[0] if " " in label else ""
        baslik = label.split(" ", 1)[1] if " " in label else label
        maddeler.append({
            "onayli": checks.get(field_key, True),
            "ikon": ikon,
            "baslik": baslik,
            "aciklama": aciklama_map.get(field_key, "Brief bilgisi"),
            "deger": _get_brief_value(user_data, field_key),
        })

    data = {
        "adimlar": [
            {"no": 1, "baslik": "Brief", "altbaslik": "İncelemede", "durum": "active"},
            {"no": 2, "baslik": "Senaryo", "altbaslik": "Sıradaki Adım", "durum": "pending"},
            {"no": 3, "baslik": "Fiyat Teklifi", "altbaslik": "Sıradaki Adım", "durum": "pending"},
        ],
        "maddeler": maddeler,
        "footer": {
            "kod": "UI_REF_002_BRIEF_ONAY_FORMU_V1",
            "versiyon": "V1.0",
            "tarih": datetime.now().strftime("%d.%m.%Y"),
        },
    }
    return await render_form_png("REFERANS_Brief_Onay_Formu", data)
