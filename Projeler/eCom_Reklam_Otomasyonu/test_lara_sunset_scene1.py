"""
test_lara_sunset_scene1.py — LARA ARI Sunset Koleksiyonu — Sahne 1 Test

BRASIL Hook (5 sn, 720p, image-to-video)
Manken: lara.jpeg
Ürün: BRASIL-CROPTOP-SUNSETMARKET.jpg
Mekan: Gün batımı, açık hava
Voiceover: YOKSUZ (görsel test)
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("test_lara_sunset_scene1")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

# Manken seçeneği: lara.jpeg veya bikini klasöründen PINK-b1/b2
CHARACTER_REF = SUNSET_DIR / "lara.jpeg"  # Ana manken
# ALTERNATİF: HLK / "LARA_Bikini_230526" / "LARA17052026" / "lara_pembe_bikini_hlk_rklm.02" / "PINK-b1.jpg"
PRODUCT_REF = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"

OUTPUT_FILE = SUNSET_DIR / "TEST_SCENE1_BRASIL_HOOK.mp4"

# ============================================================================
# MANKEN (lara.jpeg'deki kız)
# ============================================================================
CHARACTER_DESC = (
    "A confident, sophisticated young Turkish woman from the reference image, "
    "approximately 25-28 years old, dark shoulder-length hair, warm tan skin, "
    "natural makeup with soft warm tones, bright confident eyes, relaxed "
    "professional presence. Same exact face, hair, and body as the reference image."
)

# ============================================================================
# ÜRÜN AÇIKLAMASI — BRASIL CROP-TOP
# ============================================================================
PRODUCT_DESC = (
    "Product: hand-crocheted white crop-top bikini with multicolor BRASIL beads "
    "spelling 'BRASIL' in large letters. The beads are bright vibrant colors — "
    "green, yellow, blue, white — hand-strung and densely packed. The top is a "
    "simple halter-style white crochet base with the BRASIL beaded text as the "
    "focal point. Each bead sparkles and catches light. The texture is clearly "
    "artisan handmade with visible crochet stitches. NO logos, NO tags, NO labels — "
    "completely clean white crochet surface except for the beaded BRASIL text."
)

# ============================================================================
# SAHNE 1 — BRASIL HOOK (WARM, DYNAMIC, STABLE CAMERA + HAIR INTERACTION)
# ============================================================================
SCENE_PROMPT = (
    f"Character: {CHARACTER_DESC} Warm, playful, genuine smile. Natural expressions. "
    f"She touches and plays with her hair naturally (tossing, tucking, wind effect). "
    f"Product: {PRODUCT_DESC} "
    f"Setting: Sunset beach, golden hour, warm amber light. Sea horizon, natural breeze "
    f"moving her hair softly. "
    f"Action: She holds the BRASIL crop-top with both hands near her face, eyes bright "
    f"with genuine delight, smiling warmly. She tilts her head playfully, shakes it gently "
    f"so beads sway and sparkle. She naturally touches her hair with one hand (wind effect, "
    f"tucking strands behind ear). Tactile, affectionate interaction with both product and hair. "
    f"Camera movement: SMOOTH & STABLE (on tripod or gimbal, NO shake). Start close on her face "
    f"(eyes, smile). Smooth gradual ZOOM OUT to reveal crop-top in hands with beads catching light. "
    f"Gentle ZOOM IN on beads to show sparkle. Subtle lateral PUSH (dolly) as she turns. "
    f"All camera moves are SMOOTH and LOCKED — no handheld wobble. "
    f"Format: 9:16 vertical, warm intimate editorial fashion, golden-hour color grading, "
    f"sharp focus. Silent, no text."
)

# ============================================================================
# MAIN
# ============================================================================
async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI — Sunset Koleksiyonu — Sahne 1 Test (BRASIL Hook)")
    log.info("=" * 70)

    # KIE API Setup
    kie_key = os.environ.get("KIE_API_KEY")
    if not kie_key:
        log.error("❌ KIE_API_KEY .env'de yok!")
        return

    kie = KieAIService(kie_key)
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    imgbb = ImgBBService(imgbb_key) if imgbb_key else None

    # ── Görsel Upload ──
    log.info("\n📤 Görselleri ImgBB'ye yüklüyorum...")
    ref_urls = []

    for label, path in [("Manken (lara.jpeg)", CHARACTER_REF),
                         ("Ürün (BRASIL crop-top)", PRODUCT_REF)]:
        if not path.exists():
            log.error(f"❌ {label} bulunamadı: {path}")
            return

        if imgbb:
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                result = imgbb.upload_image_bytes(data, name=path.stem)
                ref_urls.append(result["url"])
                log.info(f"  ✅ {label} → {result['url'][:80]}...")
            except Exception as e:
                log.error(f"  ❌ {label} upload hatası: {e}")
                return
        else:
            log.warning(f"  ⚠️ ImgBB key yok, görsel upload atlanıyor")
            break

    if not ref_urls:
        log.error("❌ Hiç görsel yüklenemedi")
        return

    # ── Kredi Kontrol ──
    log.info("\n💰 KIE kredi bakiyesi kontrol ediliyor...")
    try:
        balance_data = await asyncio.to_thread(kie.get_credit_balance)
        balance = 0.0
        if balance_data and isinstance(balance_data, dict):
            data_block = balance_data.get("data", balance_data)
            if isinstance(data_block, dict):
                balance = float(data_block.get("balance", data_block.get("credit", 0)))
            else:
                balance = float(data_block)

        required = 5 * 25  # 5 sn × 25 kr/s
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli: {required} kredi (5s × 720p)")
        if balance < required:
            log.error(f"  ❌ Yetersiz! ({balance:.1f} < {required})")
            return
        log.info(f"  ✅ Yeterli")
    except Exception as e:
        log.warning(f"  ⚠️ Kredi sorgusu başarısız: {e}")

    # ── Video Render ──
    log.info("\n🎬 Seedance 2.0 ile video render ediliyor (5 sn, 720p)...")
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
            log.error(f"  ❌ Render başarısız: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error(f"  ❌ Video URL alınamadı: {result}")
            return

        video_url = urls[0]
        if isinstance(video_url, dict):
            video_url = video_url.get("url") or ""

        log.info(f"  ✅ Video hazır: {video_url[:90]}...")

        # ── İndir ──
        log.info(f"\n💾 Video indiriliyor → {OUTPUT_FILE.name}")
        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(response.content)
        log.info(f"  ✅ Kaydedildi: {OUTPUT_FILE}")
        log.info(f"  📊 Boyut: {OUTPUT_FILE.stat().st_size / (1024*1024):.1f} MB")

        log.info("\n" + "=" * 70)
        log.info("✅ Sahne 1 render BAŞARILI!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"  ❌ Render hatası: {e}", exc_info=True)
        return


if __name__ == "__main__":
    asyncio.run(main())
