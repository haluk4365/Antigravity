"""
redo_scene1.py — Sahne 1 yeniden render (tişört elle tutuluş pozisyonu düzeltilmiş)
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

log = get_logger("redo_scene1")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

CHARACTER_REF = SUNSET_DIR / "lara.jpeg"
PRODUCT_REF = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"
OUTPUT_FILE = SUNSET_DIR / "TEST_SCENE1_BRASIL_HOOK.mp4"

CHARACTER_DESC = (
    "A confident, sophisticated young Turkish woman from the reference image, "
    "approximately 25-28 years old, dark shoulder-length hair, warm tan skin, "
    "natural makeup with soft warm tones, bright confident eyes. Same exact face, hair, and body as reference."
)

PRODUCT_DESC = (
    "Product: hand-crocheted white crop-top bikini with multicolor BRASIL beads "
    "spelling 'BRASIL' in large bright letters. The beads are bright vibrant colors — "
    "green, yellow, blue, white. The top is simple white crochet base with BRASIL beaded text. "
    "Each bead sparkles in light. Artisan handmade with visible crochet stitches. "
    "NO logos, NO tags, NO labels — completely clean white crochet except for beaded BRASIL text."
)

SCENE_PROMPT = (
    f"Character: {CHARACTER_DESC} Warm, playful, genuine smile. Natural expressions. "
    f"Product: {PRODUCT_DESC} "
    f"Setting: Sunset beach, golden hour, warm amber light. Sea horizon, natural breeze. "
    f"ACTION: "
    f"She HOLDS the BRASIL crop-top in BOTH HANDS in front of her chest — absolutely NOT WEARING IT. "
    f"Hands grip opposite sides of the neckline/upper edge, pulling it toward herself, "
    f"showing full front of product to camera. Hands CLEARLY visible holding the fabric. "
    f"She smiles warmly with genuine delight, eyes bright. "
    f"She tilts her head playfully, then shakes it gently so BEADS SWAY and SPARKLE. "
    f"THEN: She naturally touches her hair with ONE HAND while keeping OTHER HAND holding crop-top firmly. "
    f"Both hands never release crop-top simultaneously. "
    f"CRITICAL: Throughout entire scene — crop-top ALWAYS held away from body in hands, "
    f"NEVER stretches over torso, NEVER appears on body, NEVER fitted or worn. "
    f"ALWAYS clearly hand-held product showcase. Beads catch golden light and sparkle. "
    f"Camera: SMOOTH & STABLE gimbal, no shake. Start close on her face and the crop-top neckline in hands. "
    f"Smooth ZOOM OUT — as camera pulls back, her hands holding crop-top come into full view. "
    f"Crop-top dangles/is held away from body, product clearly not worn. "
    f"Gentle ZOOM IN on beads to show sparkle. All moves smooth, locked, stable. "
    f"Format: 9:16 vertical, warm intimate editorial fashion, golden-hour color grading. "
    f"Silent, no text."
)

async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("Sahne 1 — BRASIL Hook (REDO — tişört elle tutuluş)")
    log.info("=" * 70)

    kie_key = os.environ.get("KIE_API_KEY")
    if not kie_key:
        log.error("KIE_API_KEY yok!")
        return

    kie = KieAIService(kie_key)
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    imgbb = ImgBBService(imgbb_key) if imgbb_key else None

    # Upload
    log.info("\nGorselleri yukluyor...")
    ref_urls = []

    for label, path in [("Manken", CHARACTER_REF), ("Urun", PRODUCT_REF)]:
        if not path.exists():
            log.error(f"  {label} bulunamadi: {path}")
            return

        if imgbb:
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                result = imgbb.upload_image_bytes(data, name=path.stem)
                ref_urls.append(result["url"])
                log.info(f"  {label} yuklendi")
            except Exception as e:
                log.error(f"  {label} hata: {e}")
                return

    if not ref_urls:
        log.error("Gorsel yuklemesi basarisiz!")
        return

    # Kredi kontrol
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

        required = 5 * 25
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli: {required} kredi")
        if balance < required:
            log.error(f"  Yetersiz!")
            return
        log.info(f"  OK")
    except Exception as e:
        log.warning(f"  Kredi sorgusu basarisiz: {e}")

    # Render
    log.info("\nVideo render ediliyor (5 saniye)...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=SCENE_PROMPT,
            duration=5,
            aspect_ratio="9:16",
            generate_audio=False,
            reference_images=ref_urls,
        )
        log.info(f"  Task ID: {task_id}")
        log.info(f"  Bekleniyor... (5-10 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  Render basarisiz: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error(f"  Video URL alinamadi")
            return

        video_url = urls[0]
        if isinstance(video_url, dict):
            video_url = video_url.get("url") or ""

        log.info(f"  Video hazir")

        # Download
        log.info(f"  Indiriliyor...")
        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(response.content)
        size_mb = OUTPUT_FILE.stat().st_size / (1024*1024)
        log.info(f"  Kaydedildi: {OUTPUT_FILE.name} ({size_mb:.1f} MB)")

        log.info("\n" + "=" * 70)
        log.info("Sahne 1 render tamamlandi!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"  Hata: {e}", exc_info=True)
        return


if __name__ == "__main__":
    asyncio.run(main())
