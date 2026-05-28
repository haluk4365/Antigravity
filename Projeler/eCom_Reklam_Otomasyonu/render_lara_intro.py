"""
render_lara_intro.py — LARA ARI Manken Tanıtım Videosu (Konsept 2 — Sunny Car)
Süre: 4 saniye, 720p, 9:16
Manken Referansları: lara.jpeg, lara_02.jpeg, lara_03.jpeg
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

log = get_logger("render_lara_intro")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

CHARACTER_REFS = [
    SUNSET_DIR / "lara.jpeg",
    SUNSET_DIR / "lara_02.jpeg",
    SUNSET_DIR / "lara_03.jpeg"
]

OUTPUT_FILE = SUNSET_DIR / "LARA_INTRO_CONCEPT2.mp4"

SCENE_PROMPT = (
    "@Image1 and @Image2 and @Image3 as character references. Close-up portrait of Lara, "
    "a young Turkish woman with naturally curly dark brown hair. She is sitting inside a car "
    "near the window, holding her smartphone in her hand to record a selfie video/vlog. "
    "She looks directly into the front camera lens with a cheerful, playful expression and a warm smile. "
    "Her hand and shoulder holding the camera are partially visible at the edge of the frame, showing she is filming herself. "
    "Warm natural sunlight streams in, illuminating her sun-kissed tan skin. "
    "9:16 vertical UGC creator footage, handheld iPhone 15 Pro front camera selfie angle, "
    "real skin texture, natural phone sensor grain, candid imperfect framing, subtle camera shake, "
    "authentic influencer vlog vibe. Smooth motion, 4 seconds, maintain face consistency."
)

async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI — Manken Tanıtım Videosu — Konsept 2 (Sunny Car)")
    log.info("=" * 70)

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

    for path in CHARACTER_REFS:
        if not path.exists():
            log.error(f"❌ Referans görsel bulunamadı: {path}")
            return

        if imgbb:
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                result = imgbb.upload_image_bytes(data, name=path.stem)
                ref_urls.append(result["url"])
                log.info(f"  ✅ {path.name} → {result['url'][:80]}...")
            except Exception as e:
                log.error(f"  ❌ {path.name} upload hatası: {e}")
                return
        else:
            log.warning("  ⚠️ ImgBB key yok, görsel upload atlanıyor")
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

        required = 4 * 25  # 4 sn × 25 kr/s
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli: {required} kredi (4s × 720p)")
        if balance < required:
            log.error(f"  ❌ Yetersiz! ({balance:.1f} < {required})")
            return
        log.info(f"  ✅ Yeterli")
    except Exception as e:
        log.warning(f"  ⚠️ Kredi sorgusu başarısız: {e}")

    # ── Video Render ──
    log.info("\n🎬 Seedance 2.0 ile video render ediliyor (4 sn, 720p)...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=SCENE_PROMPT,
            duration=4,
            aspect_ratio="9:16",
            generate_audio=False,
            reference_images=ref_urls,
        )
        log.info(f"  Task ID: {task_id}")
        log.info(f"  Bekleniyor... (3-5 dakika)")
        
        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  ❌ Render başarısız: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error("  ❌ Video URL alınamadı")
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
        log.info("✅ LARA TANITIM VİDEOSU RENDER TAMAMLANDI!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"  ❌ Render hatası: {e}", exc_info=True)
        return

if __name__ == "__main__":
    asyncio.run(main())
