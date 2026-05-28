"""
produce_lara_sunset_full.py — LARA ARI Sunset Koleksiyonu — 3 Sahne (Paralel)

SAHNE 2: TURKISH DELIGHT (5s)
SAHNE 3: Final Moment / Brand Payoff (5s)

Önceki Sahne 1 test render'ı ile birleştirilecek.
Total: 5s + 5s + 5s = 15 saniye
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

log = get_logger("produce_lara_sunset_full")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

CHARACTER_REF = SUNSET_DIR / "lara.jpeg"
PRODUCT_BRASIL = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"
PRODUCT_TURKISH = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"
PRODUCT_TANKTOP = SUNSET_DIR / "BRASIL-TANKTOP-SUNSETMARKET.jpg"

OUTPUT_DIR = SUNSET_DIR
SCENE2_FILE = OUTPUT_DIR / "SCENE2_TURKISH_DELIGHT.mp4"
SCENE3_FILE = OUTPUT_DIR / "SCENE3_FINAL_MOMENT.mp4"
FINAL_FILE = OUTPUT_DIR / "FINAL_REKLAM_LARA_SUNSET.mp4"

# ============================================================================
# MANKEN
# ============================================================================
CHARACTER_DESC = (
    "A confident, sophisticated young Turkish woman from the reference image, "
    "approximately 25-28 years old, dark shoulder-length hair, warm tan skin, "
    "natural makeup with soft warm tones, bright confident eyes. Same exact face as reference. "
    "Warm, playful, genuine smile. She touches and plays with her hair naturally."
)

# ============================================================================
# ÜRÜN AÇIKLAMALARI
# ============================================================================
PRODUCT_TURKISH_DESC = (
    "Product: hand-crocheted white crop-top bikini top with bright red embroidered "
    "'Turkish Delight' script text and pearl bead detailing. The beads are lustrous "
    "white/cream pearls interspersed throughout the text and edges. Simple white "
    "crochet base. Each pearl catches and reflects light. NO logos, NO tags — "
    "completely clean crochet surface except pearl beads."
)

TANKTOP_DESC = (
    "Product: hand-crocheted white tank-top style with similar pearl bead details. "
    "Versatile, elegant, premium."
)

# ============================================================================
# SAHNE 2 — TURKISH DELIGHT DETAIL
# ============================================================================
SCENE2_PROMPT = (
    f"Character: {CHARACTER_DESC} "
    f"Product: {PRODUCT_TURKISH_DESC} "
    f"Setting: Sunset beach, golden-to-amber hour, very warm light. Soft sea breeze. "
    f"Action: She is wearing the TURKISH DELIGHT crop-top. She tilts her head gracefully, "
    f"smiling warmly. She touches her hair (wind effect, tucking behind ear, playing with strands). "
    f"She gently shakes the top so pearls catch and sparkle in the warm light. Zarif, feminen, "
    f"sophisticated movement. Tactile, affectionate interaction. "
    f"Camera movement: SMOOTH & STABLE (gimbal/tripod, NO shake). Subtle zoom in on pearls "
    f"to show sparkle detail. Gentle pan and push as she moves. All moves are locked & smooth. "
    f"Format: 9:16 vertical, warm intimate editorial fashion, golden-hour color grading. "
    f"Silent, no text."
)

# ============================================================================
# SAHNE 3 — FINAL MOMENT / BRAND PAYOFF
# ============================================================================
SCENE3_PROMPT = (
    f"Character: {CHARACTER_DESC} Confident, radiant, empowered. "
    f"Product: Both items represented — Turkish Delight concept + BRASIL energy. "
    f"Setting: Sunset beach at golden hour ending (very warm amber/orange light), "
    f"siluet mood, sea behind her, soft breeze. "
    f"Action: She walks slowly along the beach (wet sand/shoreline), or stands "
    f"confidently facing the horizon, then turns to camera with a warm, radiant smile. "
    f"Her expression is empowered, proud, showcasing both styles she embodies. "
    f"Natural hair movement, confident posture. She may touch her hair or adjust slightly. "
    f"Camera movement: SMOOTH & STABLE. Start wide (full body). Slow push in as she turns "
    f"to camera. Final close-up on her confident expression. All moves smooth, NO shake. "
    f"Format: 9:16 vertical, warm intimate editorial, warm golden-to-orange color grading, "
    f"cinematic sunset mood (still editorial, not cinematic film). Silent, no text."
)

# ============================================================================
# MAIN
# ============================================================================
async def render_scene(kie: ImgBBService, idx: int, name: str, prompt: str,
                       duration: int, ref_urls: list[str], output_path: Path) -> bool:
    """Render a single scene."""
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
        log.info(f"  Bekleniyor... (5-10 dakika)")

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

        log.info(f"  Video hazır")

        # İndir
        log.info(f"  İndiriliyor...")
        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        size_mb = output_path.stat().st_size / (1024*1024)
        log.info(f"  Kaydedildi: {output_path.name} ({size_mb:.1f} MB)")

        return True

    except Exception as e:
        log.error(f"  Render hatası: {e}", exc_info=True)
        return False


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI — Sunset Koleksiyonu — 3 Sahne (Paralel Render)")
    log.info("=" * 70)

    # KIE Setup
    kie_key = os.environ.get("KIE_API_KEY")
    if not kie_key:
        log.error("KIE_API_KEY .env'de yok!")
        return

    kie = KieAIService(kie_key)
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    imgbb = ImgBBService(imgbb_key) if imgbb_key else None

    # ── Görselleri Upload ──
    log.info("\nGörselleri ImgBB'ye yüklüyorum...")
    ref_urls = []

    for label, path in [("Manken (lara.jpeg)", CHARACTER_REF),
                         ("BRASIL", PRODUCT_BRASIL),
                         ("TURKISH DELIGHT", PRODUCT_TURKISH),
                         ("TANKTOP", PRODUCT_TANKTOP)]:
        if not path.exists():
            log.warning(f"  {label} bulunamadı: {path}")
            continue

        if imgbb:
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                result = imgbb.upload_image_bytes(data, name=path.stem)
                ref_urls.append(result["url"])
                log.info(f"  {label} yüklendi")
            except Exception as e:
                log.warning(f"  {label} upload hatası: {e}")

    if not ref_urls:
        log.error("Hiç görsel yüklenemedi!")
        return

    # ── Kredi Kontrol ──
    log.info("\nKredi bakiyesi kontrol ediliyor...")
    try:
        balance_data = await asyncio.to_thread(kie.get_credit_balance)
        balance = 0.0
        if balance_data and isinstance(balance_data, dict):
            data_block = balance_data.get("data", balance_data)
            if isinstance(data_block, dict):
                balance = float(data_block.get("balance", data_block.get("credit", 0)))
            else:
                balance = float(data_block)

        required = (5 + 5) * 25  # 10 sn toplam × 25 kr/s
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli: {required} kredi (2 sahne)")
        if balance < required:
            log.error(f"  Yetersiz! ({balance:.1f} < {required})")
            return
        log.info(f"  Yeterli")
    except Exception as e:
        log.warning(f"  Kredi sorgusu başarısız: {e}")

    # ── 2 Sahneyi Paralel Render ──
    log.info("\nSahne 2 + 3 paralel render ediliyor...\n")

    task2 = asyncio.create_task(
        render_scene(kie, 2, "TURKISH DELIGHT", SCENE2_PROMPT, 5, ref_urls, SCENE2_FILE)
    )
    task3 = asyncio.create_task(
        render_scene(kie, 3, "FINAL MOMENT", SCENE3_PROMPT, 5, ref_urls, SCENE3_FILE)
    )

    results = await asyncio.gather(task2, task3)

    if not all(results):
        log.error("\nBir veya daha fazla sahne render hatası!")
        return

    # ── Sahne 1 + 2 + 3 Birleştir ──
    log.info("\n" + "=" * 70)
    log.info("3 sahne moviepy ile birleştiriliyor...")
    log.info("=" * 70)

    try:
        from moviepy import VideoFileClip, concatenate_videoclips

        scene1 = VideoFileClip(str(Path(SUNSET_DIR) / "TEST_SCENE1_BRASIL_HOOK.mp4"))
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
        log.info(f"\n✅ Final video: {FINAL_FILE.name} ({size_mb:.1f} MB)")
        log.info(f"   Konum: {FINAL_FILE}")
        log.info(f"\n" + "=" * 70)
        log.info("✅ LARA ARI SUNSET REKLAMI TAMAMLANDI!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"Birleştirme hatası: {e}", exc_info=True)
        return


if __name__ == "__main__":
    asyncio.run(main())
