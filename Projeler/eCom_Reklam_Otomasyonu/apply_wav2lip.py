"""
apply_wav2lip.py — Mevcut video uzerine Wav2Lip dudak senkronu uygular.
Video yeniden uretilmez — sadece lip-sync degistirilir. Hizli ve ucuz.
"""
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

log = get_logger("apply_wav2lip")

SUNSET_DIR = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\LARA_Sunset_230526")

# Mevcut video (Kie AI render'dan gelen)
INPUT_VIDEO  = SUNSET_DIR / "SCENE1_BRASIL_WEARING_02.mp4"
# Cikis
OUTPUT_FILE  = SUNSET_DIR / "SCENE1_BRASIL_WEARING_02_WAV2LIP.mp4"

VOICEOVER_TEXT = "Kizlar selam! Lara Ari'nin yeni Sunset bustiyerine bayildim, uzerimdeki durusu saka mi?!"

async def upload_to_tmpfiles(data: bytes, fname: str) -> str:
    def _upload():
        resp = requests.post("https://tmpfiles.org/api/v1/upload",
                             files={"file": (fname, data, "video/mp4")}, timeout=120)
        resp.raise_for_status()
        url = resp.json()["data"]["url"]
        return url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
    return await asyncio.to_thread(_upload)

async def main():
    load_dotenv()

    replicate_key   = os.environ.get("REPLICATE_API_TOKEN")
    elevenlabs_key  = os.environ.get("ELEVENLABS_API_KEY")

    if not all([replicate_key, elevenlabs_key]):
        log.error("Eksik API anahtarlari!")
        return

    replicate = ReplicateService(replicate_key)
    elevenlabs = ElevenLabsService(elevenlabs_key)

    # 1. Ses uret
    log.info("[1/4] ElevenLabs ile ses uretiliyor (Jessica)...")
    audio_bytes = await asyncio.to_thread(
        elevenlabs.generate_speech,
        text=VOICEOVER_TEXT,
        voice_name="Jessica"
    )
    audio_dur = ElevenLabsService.measure_audio_duration(audio_bytes)
    log.info(f"  Ses hazir: {audio_dur:.2f} saniye")

    # 2. Replicate'e ses yukle
    log.info("[2/4] Replicate'e ses yukleniyor...")
    audio_url = await replicate.async_upload_audio(audio_bytes)
    log.info(f"  Ses URL: {audio_url[:80]}...")

    # 3. Videoyu tmpfiles'a yukle (public URL gerekiyor)
    log.info("[3/4] Video tmpfiles'a yukleniyor (public URL icin)...")
    if not INPUT_VIDEO.exists():
        log.error(f"Input video bulunamadi: {INPUT_VIDEO}")
        return
    video_public_url = await upload_to_tmpfiles(INPUT_VIDEO.read_bytes(), INPUT_VIDEO.name)
    log.info(f"  Video URL: {video_public_url}")

    # 4. Wav2Lip uygula
    log.info("[4/4] Wav2Lip dudak senkronizasyonu uygulaniypr...")
    final_url = await replicate.async_wav2lip(
        video_url=video_public_url,
        audio_url=audio_url,
        pads="0 10 0 0",
        resize_factor=1,
        fps=25,
    )
    log.info(f"  Wav2Lip tamamlandi: {final_url[:90]}...")

    # 5. Indir
    log.info(f"Final indiriliyor -> {OUTPUT_FILE.name}")
    resp = requests.get(final_url, timeout=180)
    resp.raise_for_status()
    OUTPUT_FILE.write_bytes(resp.content)
    log.info(f"  Kaydedildi: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024} KB)")
    log.info("WAV2LIP TAMAMLANDI!")

if __name__ == "__main__":
    asyncio.run(main())
