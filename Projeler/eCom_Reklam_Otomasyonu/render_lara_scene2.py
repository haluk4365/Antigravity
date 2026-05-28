"""
render_lara_scene2.py -- LARA ARI Sunset Koleksiyonu -- Sahne 2 (Turkish Delight)

Pipeline (Sahne 1 ile birebir ayni -- kanitlanmis standart):
  1. ElevenLabs Jessica sesi --> Turkce voiceover
  2. anchor_lara_turkish.jpg --> ImgBB upload
  3. Kie AI Seedance 2.0 (first_frame_url modu) --> tutarli gorunum
  4. Replicate LatentSync (guidance_scale=1.0) --> dudak senkronizasyonu
  5. SCENE2_TURKISH_DELIGHT.mp4 olarak kaydet

NOT: reference_images kullanilmaz -- first_frame_url yontemi Lara'nin
yuzunu/gorunumunu sabitler. Bu Sahne 1 icin kanitlanmis standartir.
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

log = get_logger("render_lara_scene2")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

ANCHOR_FILE     = SUNSET_DIR / "anchor_lara_turkish_v2.jpg"      # Sahne 2 anchor
PRODUCT_REF     = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"
OUTPUT_FILE     = SUNSET_DIR / "SCENE2_TURKISH_DELIGHT.mp4"

# ============================================================================
# VOICEOVER
# ============================================================================
VOICEOVER_TEXT = '<break time="0.5s"/> Şu Turkish Delight nakışlı büstiyer çok şık! İncilerdeki zarafeti görüyor musunuz?'

# ============================================================================
# SAHNE PROMPT (first_frame_url modu -- referans gorsel YOK)
# ============================================================================
SCENE_PROMPT = (
    "Continue naturally from the first frame. "
    "The young woman is on a sandy beach at golden-hour sunset, "
    "holding her smartphone in selfie mode, arm extended. "
    "She walks slowly along the beach shoreline at a steady pace. "
    "The selfie camera moves in sync with her, maintaining a constant distance so her upper body and the crop-top remain in steady, clear focus without scaling distortion, while the sunset beach background moves smoothly behind her. "
    "She looks directly into the lens with a highly energetic, warm, and playful expression, smiling naturally with her mouth closed (no speaking or lip movements). "
    "She smiles warmly and gently touches the pearl bead details on her white crocheted crop-top with her free hand, highlighting them. "
    "Warm golden sunset light, soft sea breeze, natural curly hair movement. "
    "Raw 9:16 vertical UGC vlog style, silent, 6 seconds."
)


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI -- Sahne 2: Turkish Delight (Anchor Frame Pipeline)")
    log.info("=" * 70)

    # API Anahtarlari
    kie_key        = os.environ.get("KIE_API_KEY")
    imgbb_key      = os.environ.get("IMGBB_API_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    replicate_key  = os.environ.get("REPLICATE_API_TOKEN")

    if not all([kie_key, imgbb_key, elevenlabs_key, replicate_key]):
        log.error("Eksik API anahtari! .env dosyasini kontrol edin.")
        return

    kie        = KieAIService(kie_key)
    imgbb      = ImgBBService(imgbb_key)
    elevenlabs = ElevenLabsService(elevenlabs_key)
    replicate  = ReplicateService(replicate_key)

    # -- 1. Anchor Kontrol --
    log.info("\n[0/5] Anchor frame kontrol ediliyor...")
    if not ANCHOR_FILE.exists():
        log.error(f"Anchor bulunamadi: {ANCHOR_FILE}")
        log.error("Once create_anchor_turkish.py calistirin!")
        return
    log.info(f"  Anchor hazir: {ANCHOR_FILE.name} ({ANCHOR_FILE.stat().st_size // 1024} KB)")

    # -- 2. ElevenLabs Dis Ses --
    log.info("\n[1/5] ElevenLabs ile Turkce dis ses uretiliyor...")
    log.info(f"  Metin: {VOICEOVER_TEXT}")
    try:
        audio_bytes = await asyncio.to_thread(
            elevenlabs.generate_speech,
            text=VOICEOVER_TEXT,
            voice_name="Jessica",   # Genç, neşeli, samimi -- UGC ideal (Sahne 1 ile aynı)
            stability=0.30,
            similarity_boost=0.80,
            style=0.65,
        )
        audio_duration = ElevenLabsService.measure_audio_duration(audio_bytes)
        log.info(f"  Dis ses hazir. Sure: {audio_duration:.2f} saniye")

        # Replicate'e yukle (LatentSync icin)
        log.info("  Replicate storage'a yukleniyor...")
        audio_url = await replicate.async_upload_audio(audio_bytes)
        log.info(f"  Ses URL: {audio_url[:80]}...")
    except Exception as e:
        log.error(f"Dis ses hatasi: {e}")
        return

    # -- 3. Anchor'u ImgBB'ye Yukle --
    log.info("\n[2/5] Anchor gorsel ImgBB'ye yukleniyor...")
    try:
        anchor_res = imgbb.upload_image_bytes(
            ANCHOR_FILE.read_bytes(),
            name=ANCHOR_FILE.stem
        )
        anchor_imgbb_url = anchor_res["url"]
        log.info(f"  Anchor URL: {anchor_imgbb_url[:80]}...")
    except Exception as e:
        log.error(f"ImgBB yukleme hatasi: {e}")
        return

    # -- 4. Video Render (Seedance 2.0 -- first_frame_url modu) --
    log.info("\n[3/5] Seedance 2.0 ile video render ediliyor (first_frame_url modu)...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=SCENE_PROMPT,
            first_frame_url=anchor_imgbb_url,   # ANCHOR --> tutarli gorunum garantisi
            duration=6,
            aspect_ratio="9:16",
            resolution="720p",
            generate_audio=False,
            # NOT: first_frame_url kullanildiginda reference_images KULLANILMAZ
        )
        log.info(f"  Task ID: {task_id}")
        log.info("  Bekleniyor... (5-10 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  Render basarisiz: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error("  Video URL alinamadi")
            return

        raw_video_url = urls[0]
        if isinstance(raw_video_url, dict):
            raw_video_url = raw_video_url.get("url") or ""

        log.info(f"  Ham video hazir: {raw_video_url[:80]}...")
    except Exception as e:
        log.error(f"Video render hatasi: {e}", exc_info=True)
        return

    # -- 5. Video ve Ses Birleştirme (off-camera voiceover, NO lip sync) --
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
        log.error(f"Birleştirme hatasi: {e}", exc_info=True)
        return

    # -- 6. Indir ve Kaydet --
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
        log.error(f"Indirme hatasi: {e}")
        return

    log.info("\n" + "=" * 70)
    log.info("SAHNE 2 TAMAMLANDI! (ANCHOR FRAME PIPELINE)")
    log.info(f"  Anchor:    {ANCHOR_FILE.name}")
    log.info(f"  Video:     {OUTPUT_FILE.name}")
    log.info(f"  Sure:      6 saniye")
    log.info(f"  Ses:       {audio_duration:.2f} saniye")
    log.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
