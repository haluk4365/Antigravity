"""
create_anchor_turkish.py — LARA ARI Sunset Koleksiyonu
Sahne 2 için anchor frame: Lara + Turkish Delight ürünü

Pipeline (Sahne 1 ile aynı):
  1. Turkish Delight görseli → ImgBB upload
  2. Nano Banana 2 (image-to-image) → Lara + Turkish Delight kompozit
  3. anchor_lara_turkish.jpg olarak kaydet

Çalışma süresi: ~3-5 dakika
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

log = get_logger("create_anchor_turkish")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

# Referanslar
LARA_REF        = SUNSET_DIR / "lara.jpeg"
LARA_REF_02     = SUNSET_DIR / "lara_02.jpeg"
PRODUCT_TURKISH = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"

# Çıktı
ANCHOR_FILE = SUNSET_DIR / "anchor_lara_turkish.jpg"

# ============================================================================
# ANCHOR PROMPT — Sahne 1'e birebir paralel, Turkish Delight versiyonu
# ============================================================================
ANCHOR_CHARACTER_PROMPT = (
    "Young Turkish woman, early 20s, long wavy dark curly hair, "
    "natural makeup, warm tanned skin, warm confident smile, bright eyes. "
    "She is wearing the EXACT white hand-crocheted crop-top with bright red embroidered "
    "'Turkish Delight' script text and pearl bead detailing as shown in the reference image. "
    "The pearl beads are clearly visible, lustrous white/cream pearls catching warm golden light. "
    "She stands at a golden-hour sunset beach, holding her smartphone in selfie mode, "
    "arm extended toward the camera. "
    "Medium shot, upper body visible, 9:16 vertical portrait, photorealistic, "
    "warm golden-hour light, soft beach ambiance."
)


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("ANCHOR FRAME — Turkish Delight (Nano Banana 2)")
    log.info("=" * 70)

    # API Anahtarları
    kie_key   = os.environ.get("KIE_API_KEY")
    imgbb_key = os.environ.get("IMGBB_API_KEY")

    if not kie_key or not imgbb_key:
        log.error("KIE_API_KEY veya IMGBB_API_KEY eksik!")
        return

    kie   = KieAIService(kie_key)
    imgbb = ImgBBService(imgbb_key)

    # ── 1. Zaten Mevcut mu? ──
    if ANCHOR_FILE.exists():
        log.info(f"  Anchor zaten mevcut: {ANCHOR_FILE.name}")
        log.info(f"  Yeniden üretmek istiyorsan dosyayı sil ve tekrar çalıştır.")
        return

    # ── 2. Referans Dosya Kontrolü ──
    for f in [LARA_REF, PRODUCT_TURKISH]:
        if not f.exists():
            log.error(f"  Referans bulunamadı: {f}")
            return

    # ── 3. Turkish Delight Ürün Görselini ImgBB'ye Yükle ──
    log.info("\n[1/3] Turkish Delight ürün görseli ImgBB'ye yükleniyor...")
    try:
        product_res = imgbb.upload_image_bytes(
            PRODUCT_TURKISH.read_bytes(),
            name=PRODUCT_TURKISH.stem
        )
        product_imgbb_url = product_res["url"]
        log.info(f"  Ürün yüklendi: {product_imgbb_url[:80]}...")
    except Exception as e:
        log.error(f"  ImgBB yükleme hatası: {e}")
        return

    # ── 4. Anchor Görseli Üret (Nano Banana 2) ──
    log.info("\n[2/3] Nano Banana 2 ile Lara + Turkish Delight anchor üretiliyor...")
    log.info("  (Beklenen süre: 3-5 dakika)")
    try:
        anchor_url = await kie.async_create_character_with_product(
            character_prompt=ANCHOR_CHARACTER_PROMPT,
            product_image_url=product_imgbb_url,
            aspect_ratio="9:16"
        )
        log.info(f"  Anchor URL: {anchor_url[:80]}...")
    except Exception as e:
        log.error(f"  Anchor üretim hatası: {e}", exc_info=True)
        return

    # ── 5. Lokal Kaydet ──
    log.info(f"\n[3/3] Anchor indiriliyor → {ANCHOR_FILE.name}...")
    try:
        resp = requests.get(anchor_url, timeout=60)
        resp.raise_for_status()
        ANCHOR_FILE.write_bytes(resp.content)
        size_kb = ANCHOR_FILE.stat().st_size // 1024
        log.info(f"  Kaydedildi: {ANCHOR_FILE}")
        log.info(f"  Boyut: {size_kb} KB")
    except Exception as e:
        log.error(f"  İndirme hatası: {e}")
        return

    log.info("\n" + "=" * 70)
    log.info(f"✅ ANCHOR HAZIR: {ANCHOR_FILE.name}")
    log.info(f"   → Sahne 2 render'ında first_frame_url olarak kullanılacak")
    log.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
