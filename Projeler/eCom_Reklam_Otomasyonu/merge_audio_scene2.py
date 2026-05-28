import asyncio
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.replicate_service import ReplicateService
from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

log = get_logger("merge_audio_scene2")

SUNSET_DIR = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\LARA_Sunset_230526")
INPUT_VIDEO_URL = "https://tempfile.aiquickdraw.com/seedance/1779706984012-u45fk8kmzv.mp4"
OUTPUT_FILE = SUNSET_DIR / "SCENE2_TURKISH_DELIGHT.mp4"

VOICEOVER_TEXT = "Şu Turkish Delight nakışlı büstiyer çok şık! İncilerdeki zarafeti görüyor musunuz?"

async def main():
    load_dotenv()

    replicate_key  = os.environ.get("REPLICATE_API_TOKEN")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")

    if not all([replicate_key, elevenlabs_key]):
        log.error("Eksik API anahtarlari!")
        return

    replicate  = ReplicateService(replicate_key)
    elevenlabs = ElevenLabsService(elevenlabs_key)

    # 1. Ses uret
    log.info("[1/4] ElevenLabs ile ses uretiliyor (Jessica)...")
    audio_bytes = await asyncio.to_thread(
        elevenlabs.generate_speech,
        text=VOICEOVER_TEXT,
        voice_name="Jessica",
        stability=0.30,
        similarity_boost=0.80,
        style=0.65,
    )
    audio_dur = ElevenLabsService.measure_audio_duration(audio_bytes)
    log.info(f"  Ses hazir: {audio_dur:.2f} saniye")

    # 2. Replicate'e ses yukle
    log.info("[2/4] Replicate'e ses yukleniyor...")
    audio_url = await replicate.async_upload_audio(audio_bytes)
    log.info(f"  Ses URL: {audio_url[:80]}...")

    # 3. Video ve ses birleştirme (off-camera voiceover, NO lip sync)
    log.info("[3/4] Replicate ile video ve ses birleştiriliyor (replace_audio=True)...")
    final_url = await replicate.async_merge_video_audio(
        video_url=INPUT_VIDEO_URL,
        audio_url=audio_url,
        replace_audio=True,
        duration_mode="audio",
        audio_volume=2.5
    )
    log.info(f"  Birleştirme tamamlandi: {final_url[:90]}...")

    # 4. Indir
    log.info(f"[4/4] Final video indiriliyor -> {OUTPUT_FILE.name}...")
    resp = requests.get(final_url, timeout=180)
    resp.raise_for_status()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_bytes(resp.content)
    log.info(f"  Kaydedildi: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024} KB)")
    log.info("BİRLEŞTİRME BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(main())
