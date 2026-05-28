"""
render_lara_scene3.py -- LARA ARI Sunset Koleksiyonu -- Sahne 3 (BRASIL Tanktop)

Pipeline:
  1. ElevenLabs Jessica sesi --> Türkçe voiceover
  2. anchor_lara_brasil_tanktop.jpg --> ImgBB upload (yoksa Nano Banana 2 ile üret)
  3. Kie AI Seedance 2.0 (first_frame_url modu) --> tutarlı görünüm (720p, 4s)
  4. Replicate merge_video_audio --> dış ses entegrasyonu
  5. SCENE3_FINAL_MOMENT.mp4 olarak kaydet
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
from services.elevenlabs_service import ElevenLabsService
from services.replicate_service import ReplicateService
from logger import get_logger

log = get_logger("render_lara_scene3")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

PRODUCT_REF     = SUNSET_DIR / "BRASIL-TANKTOP-SUNSETMARKET.jpg"
ANCHOR_FILE     = SUNSET_DIR / "anchor_lara_brasil_tanktop.jpg"
OUTPUT_FILE     = SUNSET_DIR / "SCENE3_FINAL_MOMENT.mp4"

# ============================================================================
# VOICEOVER
# ============================================================================
VOICEOVER_TEXT = "Sunset Koleksiyonu şimdi yayında! Lara Arı ile güneşin enerjisini hisset!"

# ============================================================================
# ANCHOR PROMPT
# ============================================================================
ANCHOR_PROMPT = (
    "Young Turkish woman, early 20s, long wavy dark curly hair, "
    "natural makeup, warm tanned skin, warm confident smile, bright eyes. "
    "She is wearing the EXACT white hand-crocheted tank top with colorful beaded 'BRASIL' lettering "
    "as shown in the reference image. "
    "She is holding a smartphone in selfie mode but with the arm raised UP and to the RIGHT side "
    "at shoulder height -- the phone is positioned beside her head, NOT in front of her body. "
    "This means her entire torso and the tank top are COMPLETELY UNOBSTRUCTED and clearly visible. "
    "The tank top fills the center frame. "
    "She stands on a sandy sunset beach, golden-hour warm light, sea behind her. "
    "Medium shot showing head to waist, 9:16 vertical portrait, photorealistic, "
    "warm golden-hour light."
)

# ============================================================================
# SAHNE PROMPT (first_frame_url modu -- referans görsel YOK)
# ============================================================================
SCENE_PROMPT = (
    "Continue naturally from the first frame. "
    "The young woman is on a sandy beach at golden-hour sunset, "
    "holding her smartphone in selfie mode, arm extended. "
    "She walks slowly along the beach shoreline at a steady pace. "
    "The selfie camera moves in sync with her, maintaining a constant distance so her upper body and the tank top remain in steady, clear focus without scaling distortion, while the sunset beach background moves smoothly behind her. "
    "She looks directly into the lens with a highly energetic, warm, and playful expression, smiling naturally with her mouth closed (no speaking or lip movements). "
    "She smiles warmly and gently poses. "
    "Warm golden sunset light, soft sea breeze, natural curly hair movement. "
    "Raw 9:16 vertical UGC vlog style, silent, 4 seconds."
)


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI -- Sahne 3: BRASIL Tanktop (Anchor Frame Pipeline)")
    log.info("=" * 70)

    # API Anahtarları
    kie_key        = os.environ.get("KIE_API_KEY")
    imgbb_key      = os.environ.get("IMGBB_API_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    replicate_key  = os.environ.get("REPLICATE_API_TOKEN")

    if not all([kie_key, imgbb_key, elevenlabs_key, replicate_key]):
        log.error("Eksik API anahtarı! .env dosyasını kontrol edin.")
        return

    kie        = KieAIService(kie_key)
    imgbb      = ImgBBService(imgbb_key)
    elevenlabs = ElevenLabsService(elevenlabs_key)
    replicate  = ReplicateService(replicate_key)

    # -- 1. ElevenLabs Dış Ses --
    log.info("\n[1/5] ElevenLabs ile Türkçe dış ses üretiliyor...")
    log.info(f"  Metin: {VOICEOVER_TEXT}")
    try:
        audio_bytes = await asyncio.to_thread(
            elevenlabs.generate_speech,
            text=VOICEOVER_TEXT,
            voice_name="Jessica",
            stability=0.30,
            similarity_boost=0.80,
            style=0.65,
        )
        audio_duration = ElevenLabsService.measure_audio_duration(audio_bytes)
        log.info(f"  Dış ses hazır. Süre: {audio_duration:.2f} saniye")

        # Replicate'e yükle (LatentSync için)
        log.info("  Replicate storage'a yükleniyor...")
        audio_url = await replicate.async_upload_audio(audio_bytes)
        log.info(f"  Ses URL: {audio_url[:80]}...")
    except Exception as e:
        log.error(f"Dış ses hatası: {e}")
        return

    # -- 2. Anchor Frame Üretimi / Kontrolü --
    log.info("\n[2/5] Anchor frame kontrol ediliyor...")
    anchor_imgbb_url = None

    if ANCHOR_FILE.exists():
        log.info(f"  Anchor görseli hazır: {ANCHOR_FILE.name} ({ANCHOR_FILE.stat().st_size // 1024} KB)")
        log.info("  ImgBB'ye yükleniyor...")
        try:
            anchor_res = imgbb.upload_image_bytes(ANCHOR_FILE.read_bytes(), name=ANCHOR_FILE.stem)
            anchor_imgbb_url = anchor_res["url"]
            log.info(f"  Anchor URL: {anchor_imgbb_url[:80]}...")
        except Exception as e:
            log.error(f"ImgBB yükleme hatası: {e}")
            return
    else:
        log.info("  Anchor görseli bulunamadı -- Nano Banana 2 ile üretiliyor...")
        # Ürün görselini ImgBB'ye yükle
        if not PRODUCT_REF.exists():
            log.error(f"Ürün görseli bulunamadı: {PRODUCT_REF}")
            return
        try:
            product_res = imgbb.upload_image_bytes(PRODUCT_REF.read_bytes(), name=PRODUCT_REF.stem)
            product_imgbb_url = product_res["url"]
            log.info(f"  Ürün görseli ImgBB'ye yüklendi: {product_imgbb_url[:80]}...")

            anchor_kie_url = await kie.async_create_character_with_product(
                character_prompt=ANCHOR_PROMPT,
                product_image_url=product_imgbb_url,
                aspect_ratio="9:16"
            )
            log.info(f"  Kie AI anchor üretildi: {anchor_kie_url[:80]}...")

            # Lokal kaydet
            resp = requests.get(anchor_kie_url, timeout=60)
            resp.raise_for_status()
            ANCHOR_FILE.write_bytes(resp.content)
            log.info(f"  Anchor lokal kaydedildi: {ANCHOR_FILE}")

            # ImgBB'ye yükle
            anchor_res = imgbb.upload_image_bytes(ANCHOR_FILE.read_bytes(), name=ANCHOR_FILE.stem)
            anchor_imgbb_url = anchor_res["url"]
            log.info(f"  Anchor ImgBB URL: {anchor_imgbb_url[:80]}...")
        except Exception as e:
            log.error(f"Anchor frame üretim/yükleme hatası: {e}", exc_info=True)
            return

    # -- 3. Video Render (Seedance 2.0 -- first_frame_url modu) --
    log.info("\n[3/5] Seedance 2.0 ile video render ediliyor (first_frame_url modu)...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=SCENE_PROMPT,
            first_frame_url=anchor_imgbb_url,
            duration=4,
            aspect_ratio="9:16",
            resolution="720p",
            generate_audio=False,
        )
        log.info(f"  Task ID: {task_id}")
        log.info("  Bekleniyor... (5-10 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  Render başarısız: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error("  Video URL alınamadı")
            return

        raw_video_url = urls[0]
        if isinstance(raw_video_url, dict):
            raw_video_url = raw_video_url.get("url") or ""

        log.info(f"  Ham video hazır: {raw_video_url[:80]}...")
    except Exception as e:
        log.error(f"Video render hatası: {e}", exc_info=True)
        return

    # -- 4. Video ve Ses Birleştirme (off-camera voiceover, NO lip sync) --
    log.info("\n[4/5] Video ve ses birleştiriliyor (off-camera narration)...")
    try:
        final_video_url = await replicate.async_merge_video_audio(
            video_url=raw_video_url,
            audio_url=audio_url,
            replace_audio=True,
            duration_mode="audio",
            audio_volume=2.5
        )
        log.info(f"  Birleştirildi: {final_video_url[:80]}...")
    except Exception as e:
        log.error(f"Birleştirme hatası: {e}", exc_info=True)
        return

    # -- 5. İndir ve Kaydet --
    log.info(f"\n[5/5] Final video indiriliyor -> {OUTPUT_FILE.name}...")
    try:
        response = requests.get(final_video_url, timeout=180)
        response.raise_for_status()
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(response.content)
        size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
        log.info(f"  Kaydedildi: {OUTPUT_FILE}")
        log.info(f"  Boyut: {size_mb:.1f} MB")
    except Exception as e:
        log.error(f"İndirme hatası: {e}")
        return

    log.info("\n" + "=" * 70)
    log.info("SAHNE 3 TAMAMLANDI! (ANCHOR FRAME PIPELINE)")
    log.info(f"  Anchor:    {ANCHOR_FILE.name}")
    log.info(f"  Video:     {OUTPUT_FILE.name}")
    log.info(f"  Süre:      4 saniye")
    log.info(f"  Ses:       {audio_duration:.2f} saniye")
    log.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
