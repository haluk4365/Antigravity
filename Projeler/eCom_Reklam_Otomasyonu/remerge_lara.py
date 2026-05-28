"""
remerge_lara.py — Lara Arı telaffuzunu düzeltip videoyu yeniden birleştirir.
"""

import asyncio
import os
import re
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.elevenlabs_service import ElevenLabsService
from services.replicate_service import ReplicateService
from logger import get_logger

log = get_logger("remerge_lara")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"
OUTPUT_FILE = SUNSET_DIR / "SCENE1_BRASIL_WEARING.mp4"
LOG_FILE = Path(r"C:\Users\msist\.gemini\antigravity-ide\brain\32bf9548-3684-416b-b727-6416c6d083e5\.system_generated\tasks\task-177.log")

VOICEOVER_TEXT = "Kızlar selam! Lara Arı'nın yeni Sunset büstiyerine bayıldım, üzerimdeki duruşu şaka mı?!"

async def main():
    load_dotenv()
    
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    replicate_key = os.environ.get("REPLICATE_API_TOKEN")
    
    if not elevenlabs_key or not replicate_key:
        log.error("❌ Eksik API anahtarları!")
        return
        
    elevenlabs = ElevenLabsService(elevenlabs_key)
    replicate = ReplicateService(replicate_key)
    
    # 1. Log dosyasından raw_video_url'i oku
    if not LOG_FILE.exists():
        log.error(f"❌ Log dosyası bulunamadı: {LOG_FILE}")
        return
        
    content = LOG_FILE.read_text(encoding="utf-8")
    # Video hazır: https://tempfile.aiquickdraw.com/seedance/...
    match = re.search(r"Video hazır:\s*(https://[^\s]+)", content)
    if not match:
        log.error("❌ Raw video URL'i log dosyasında bulunamadı!")
        return
        
    raw_video_url = match.group(1).strip().rstrip(".")
    log.info(f"Bulunan Raw Video URL: {raw_video_url}")
    
    # 2. Yeni Dış Ses Üret
    log.info("🎙️ ElevenLabs ile düzeltilmiş Türkçe dış ses üretiliyor...")
    audio_bytes = await asyncio.to_thread(
        elevenlabs.generate_speech,
        text=VOICEOVER_TEXT,
        voice_name="Ahu"
    )
    
    # Replicate'e yükle
    log.info("Replicate storage'a ses dosyası yükleniyor...")
    audio_url = await replicate.async_upload_audio(audio_bytes)
    log.info(f"Ses URL: {audio_url}")
    
    # 3. Yeniden Birleştir
    log.info("🔀 Video ve düzeltilmiş ses birleştiriliyor (Replicate)...")
    final_video_url = await replicate.async_merge_video_audio(
        video_url=raw_video_url,
        audio_url=audio_url,
        replace_audio=True,
        duration_mode="audio"
    )
    log.info(f"Birleştirilmiş Video URL: {final_video_url}")
    
    # 4. İndir ve Kaydet
    log.info(f"Final video indiriliyor → {OUTPUT_FILE.name}")
    response = requests.get(final_video_url, timeout=180)
    response.raise_for_status()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_bytes(response.content)
    log.info(f"✅ Düzeltilmiş video kaydedildi: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
