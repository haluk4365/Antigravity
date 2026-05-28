"""
create_anchor_turkish_v2.py -- Yeni anchor: selfie kolu buyustiyeri kapatmayan pozisyon

Sorun: v1'de telefon tutan kol bustiyer onunu kismen kapatiyor.
Cozum: Telefon ust-yana pozisyon --> bustiyer tam gorunur.
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

log = get_logger("create_anchor_turkish_v2")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

PRODUCT_TURKISH = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"
ANCHOR_FILE     = SUNSET_DIR / "anchor_lara_turkish_v2.jpg"

# Telefon yukarida/yanda -- bustiyer tam acik
ANCHOR_PROMPT = (
    "Young Turkish woman, early 20s, long wavy dark curly hair, "
    "natural makeup, warm tanned skin, warm confident smile, bright eyes. "
    "She is wearing the EXACT white hand-crocheted crop-top with bright red embroidered "
    "'Turkish Delight' script text and lustrous pearl bead detailing as shown in the reference image. "
    "The pearl beads are clearly and fully visible hanging from the crop-top hem. "
    "She is holding a smartphone in selfie mode but with the arm raised UP and to the RIGHT side "
    "at shoulder height -- the phone is positioned beside her head, NOT in front of her body. "
    "This means her entire torso and the crop-top are COMPLETELY UNOBSTRUCTED and clearly visible. "
    "The crop-top fills the center frame -- full view of the 'Turkish Delight' text and all pearl details. "
    "She stands on a sandy sunset beach, golden-hour warm light, sea behind her. "
    "Medium shot showing head to waist, 9:16 vertical portrait, photorealistic, "
    "warm golden-hour light."
)


async def main():
    load_dotenv()
    log.info("=" * 60)
    log.info("ANCHOR v2 -- Selfie yana/yukari, bustiyer tam acik")
    log.info("=" * 60)

    kie_key   = os.environ.get("KIE_API_KEY")
    imgbb_key = os.environ.get("IMGBB_API_KEY")

    if not kie_key or not imgbb_key:
        log.error("API anahtari eksik!")
        return

    kie   = KieAIService(kie_key)
    imgbb = ImgBBService(imgbb_key)

    # Urun gorseli ImgBB'ye yukle
    log.info("\n[1/3] Urun gorseli yukleniyor...")
    product_res = imgbb.upload_image_bytes(
        PRODUCT_TURKISH.read_bytes(), name=PRODUCT_TURKISH.stem
    )
    product_imgbb_url = product_res["url"]
    log.info(f"  Urun: {product_imgbb_url[:80]}...")

    # Nano Banana 2 ile uret
    log.info("\n[2/3] Nano Banana 2 ile anchor uretiliyor (~3-5 dk)...")
    try:
        anchor_url = await kie.async_create_character_with_product(
            character_prompt=ANCHOR_PROMPT,
            product_image_url=product_imgbb_url,
            aspect_ratio="9:16"
        )
        log.info(f"  Anchor URL: {anchor_url[:80]}...")
    except Exception as e:
        log.error(f"  Uretim hatasi: {e}", exc_info=True)
        return

    # Kaydet
    log.info(f"\n[3/3] Kaydediliyor -> {ANCHOR_FILE.name}...")
    resp = requests.get(anchor_url, timeout=60)
    resp.raise_for_status()
    ANCHOR_FILE.write_bytes(resp.content)
    size_kb = ANCHOR_FILE.stat().st_size // 1024
    log.info(f"  Kaydedildi: {ANCHOR_FILE.name} ({size_kb} KB)")
    log.info("\n  ANCHOR v2 HAZIR!")


if __name__ == "__main__":
    asyncio.run(main())
