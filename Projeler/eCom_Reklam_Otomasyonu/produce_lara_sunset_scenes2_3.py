"""
produce_lara_sunset_scenes2_3.py — Sahne 2 + 3 (OPTIMIZED — No Timeout)

SAHNE 2: TURKISH DELIGHT (4s) — Simplified prompt
SAHNE 3: Final Moment (4s) — Simplified prompt

Timeout: 20 dakika (1200s)
Kamera: Minimal hareketi (shake-free, smooth only)
"""

import asyncio
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("produce_lara_sunset_scenes2_3")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

CHARACTER_REF = SUNSET_DIR / "lara.jpeg"
PRODUCT_BRASIL = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"
PRODUCT_TURKISH = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"

OUTPUT_DIR = SUNSET_DIR
SCENE2_FILE = OUTPUT_DIR / "SCENE2_TURKISH_DELIGHT.mp4"
SCENE3_FILE = OUTPUT_DIR / "SCENE3_FINAL_MOMENT.mp4"
FINAL_FILE = OUTPUT_DIR / "FINAL_REKLAM_LARA_SUNSET.mp4"

# ============================================================================
# MANKEN
# ============================================================================
CHARACTER_DESC = (
    "A confident, sophisticated young Turkish woman, approximately 25-28 years old, "
    "dark shoulder-length hair, warm tan skin, natural makeup, bright confident eyes. "
    "Warm, playful smile."
)

# ============================================================================
# ÜRÜN AÇIKLAMALARI (SIMPLIFIED)
# ============================================================================
PRODUCT_TURKISH_DESC = (
    "Hand-crocheted white crop-top with red 'Turkish Delight' text and pearl bead details. "
    "Simple, elegant, premium."
)

# ============================================================================
# SAHNE 2 — TURKISH DELIGHT (SIMPLIFIED)
# ============================================================================
SCENE2_PROMPT = (
    f"Character: {CHARACTER_DESC} Warm smile, gentle movement. "
    f"Product: {PRODUCT_TURKISH_DESC} "
    f"Setting: Sunset beach, golden hour, warm light. "
    f"Action: She wears the TURKISH DELIGHT crop-top. She smiles warmly, tilts her head "
    f"gently, and softly moves. Pearl beads catch the light. Simple, elegant, warm. "
    f"Camera: Smooth, stable handheld. No shake. Gentle movement only. "
    f"Format: 9:16 vertical, warm golden-hour editorial fashion, silent, no text."
)

# ============================================================================
# SAHNE 3 — FINAL MOMENT (SIMPLIFIED)
# ============================================================================
SCENE3_PROMPT = (
    f"Character: {CHARACTER_DESC} Confident, radiant, empowered expression. "
    f"Setting: Sunset beach, golden hour, very warm amber light. Sea horizon. "
    f"Action: She stands confidently facing the camera with a warm, radiant smile. "
    f"Her expression is proud and empowered. Natural, gentle movement. "
    f"Camera: Smooth, stable handheld. No shake. Simple framing, no complex moves. "
    f"Format: 9:16 vertical, warm golden-hour editorial fashion, silent, no text."
)

# ============================================================================
# ASYNC RENDER FUNCTION
# ============================================================================
async def render_scene(kie: KieAIService, idx: int, name: str, prompt: str,
                       duration: int, ref_urls: list[str], output_path: Path) -> bool:
    """Render a single scene with extended timeout."""
    log.info(f"\n[Sahne {idx}] {name} — başlıyor...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=prompt,
            duration=duration,
            aspect_ratio="9:16",
            generate_audio=False,
            reference_images=ref_urls,
        )
        log.info(f"  Task ID: {task_id}")
        log.info(f"  Bekleniyor... (10-15 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  HATA: {result.get('error', 'unknown')}")
            return False

        urls = result.get("urls") or []
        if not urls:
            log.error(f"  Video URL alınamadı")
            return False

        video_url = urls[0]
        if isinstance(video_url, dict):
            video_url = video_url.get("url") or ""

        log.info(f"  Video hazir")

        # İndir
        log.info(f"  Indiriliyor...")
        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        size_mb = output_path.stat().st_size / (1024*1024)
        log.info(f"  Kaydedildi: {output_path.name} ({size_mb:.1f} MB)")

        return True

    except Exception as e:
        log.error(f"  HATA: {e}", exc_info=True)
        return False


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI — Sunset Koleksiyonu — Sahne 2 + 3 (OPTIMIZED)")
    log.info("=" * 70)

    # KIE Setup
    kie_key = os.environ.get("KIE_API_KEY")
    if not kie_key:
        log.error("KIE_API_KEY yok!")
        return

    kie = KieAIService(kie_key)
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    imgbb = ImgBBService(imgbb_key) if imgbb_key else None

    # ── Gorselleri Upload ──
    log.info("\nGorselleri yukluyor...")
    ref_urls = []

    for label, path in [("Manken", CHARACTER_REF),
                         ("BRASIL", PRODUCT_BRASIL),
                         ("TURKISH", PRODUCT_TURKISH)]:
        if not path.exists():
            log.warning(f"  {label} bulunamadi")
            continue

        if imgbb:
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                result = imgbb.upload_image_bytes(data, name=path.stem)
                ref_urls.append(result["url"])
                log.info(f"  {label} yuklemd")
            except Exception as e:
                log.warning(f"  {label} hata: {e}")

    if not ref_urls:
        log.error("Gorsel yuklemesi basarisiz!")
        return

    # ── Kredi Kontrol ──
    log.info("\nKredi kontrol ediliyor...")
    try:
        balance_data = await asyncio.to_thread(kie.get_credit_balance)
        balance = 0.0
        if balance_data and isinstance(balance_data, dict):
            data_block = balance_data.get("data", balance_data)
            if isinstance(data_block, dict):
                balance = float(data_block.get("balance", data_block.get("credit", 0)))
            else:
                balance = float(data_block)

        required = (4 + 4) * 25  # 8 sn toplam
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli: {required} kredi")
        if balance < required:
            log.error(f"  Yetersiz!")
            return
        log.info(f"  OK")
    except Exception as e:
        log.warning(f"  Kredi sorgusu basarisiz: {e}")

    # ── Paralel Render (Optimized) ──
    log.info("\nSahne 2 + 3 paralel render (optimized)...\n")

    task2 = asyncio.create_task(
        render_scene(kie, 2, "TURKISH DELIGHT", SCENE2_PROMPT, 4, ref_urls, SCENE2_FILE)
    )
    task3 = asyncio.create_task(
        render_scene(kie, 3, "FINAL MOMENT", SCENE3_PROMPT, 4, ref_urls, SCENE3_FILE)
    )

    results = await asyncio.gather(task2, task3)

    if not all(results):
        log.error("\nRender hata!")
        return

    # ── Birleştir ──
    log.info("\n" + "=" * 70)
    log.info("3 sahne birleştiriliyor...")
    log.info("=" * 70)

    try:
        from moviepy import VideoFileClip, concatenate_videoclips

        scene1 = VideoFileClip(str(SUNSET_DIR / "TEST_SCENE1_BRASIL_HOOK.mp4"))
        scene2 = VideoFileClip(str(SCENE2_FILE))
        scene3 = VideoFileClip(str(SCENE3_FILE))

        clips = [scene1, scene2, scene3]
        final = concatenate_videoclips(clips, method="compose")
        FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(
            str(FINAL_FILE),
            fps=24,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None
        )

        size_mb = FINAL_FILE.stat().st_size / (1024*1024)
        log.info(f"\n✅ Final: {FINAL_FILE.name} ({size_mb:.1f} MB)")
        log.info(f"   Konum: {FINAL_FILE}")
        log.info(f"\n" + "=" * 70)
        log.info("✅ LARA ARI SUNSET REKLAMI TAMAMLANDI!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"Birleştirme hatası: {e}", exc_info=True)
        return


if __name__ == "__main__":
    asyncio.run(main())
