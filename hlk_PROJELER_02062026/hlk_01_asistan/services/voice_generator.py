"""
AHU Voice Generator — ElevenLabs TTS servis katmanı.

AR-002_29 AHU Character Identity and Reference Library Architecture
AR-002_30 AHU Multi-Language Voice Generation Architecture
AR-002_32 Master Reference Voice Architecture

Bu servis, mevcut çalışan ElevenLabs TTS kodunu (generate_hlk_voice.py'dan)
ortak servis katmanına taşır. Scene Engine tarafından çağrılır.
"""

import logging
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# AHU karakter sabitleri
AHU_VOICE_ID = "xyqF3vGMQlPk3e7yA4DI"
AHU_MODEL_ID = "eleven_multilingual_v2"

# Varsayılan ses ayarları
AHU_VOICE_SETTINGS = {
    "stability": 0.65,
    "similarity_boost": 0.80,
    "style": 0.40,
    "use_speaker_boost": True,
}

OUTPUT_FORMAT = "mp3_44100_128"
OUTPUT_DIR = Path("ses_dosyalari")


class AHUVoiceGenerator:
    """AR-002_30: AHU Multi-Language Voice Generator.

    ElevenLabs TTS ile AHU sesi üretir, MP3 dosyasına kaydeder.
    """

    def __init__(self):
        load_dotenv()
        self._api_key: str | None = None

    def _sanitize_filename(self, text: str, max_len: int = 50) -> str:
        """Dosya adı için metni temizler: HTML, emoji, özel karakterler çıkarılır."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.encode('ascii', 'ignore').decode('ascii')
        clean = clean.replace('\r\n', ' ').replace('\n', ' ')
        clean = re.sub(r'[<>:"/\\|?*!.]', '', clean)
        clean = re.sub(r'[ _]+', '_', clean)
        clean = clean.strip('_')[:max_len]
        return clean

    def _get_api_key(self) -> str:
        """API anahtarını .env'den alır."""
        if not self._api_key:
            key = os.getenv("ELEVENLABS_API_KEY", "")
            if not key:
                raise RuntimeError("ELEVENLABS_API_KEY .env içinde bulunamadı")
            self._api_key = key
        return self._api_key

    def generate(
        self,
        text: str,
        language: str = "tr",
        voice_id: str = AHU_VOICE_ID,
    ) -> Path | None:
        """AHU sesi üretir, MP3 dosyasına kaydeder.

        Args:
            text: Seslendirilecek metin.
            language: Kullanıcının seçtiği dil kodu (tr/en/fr/de/es/ar/ru).
            voice_id: ElevenLabs voice ID (varsayılan: Ahu).

        Returns:
            MP3 dosya yolu (Path), başarısız olursa None.
        """
        api_key = self._get_api_key()
        OUTPUT_DIR.mkdir(exist_ok=True)

        lang_suffix = language.lower()
        safe_name = self._sanitize_filename(text)
        output_path = OUTPUT_DIR / f"ahu_{lang_suffix}_{safe_name}.mp3"

        if output_path.exists():
            logger.info(f"🔊 [VoiceGen] Cache hit: {output_path}")
            return output_path

        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": AHU_MODEL_ID,
            "voice_settings": AHU_VOICE_SETTINGS,
            "output_format": OUTPUT_FORMAT,
        }

        api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        logger.info(
            f"🔊 [VoiceGen] TTS basliyor: lang={language}, "
            f"text_len={len(text)}, voice={voice_id}"
        )
        t0 = time.time()

        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=120)
            elapsed = time.time() - t0

            if resp.status_code != 200:
                logger.error(
                    f"❌ [VoiceGen] ElevenLabs hata ({elapsed:.1f}s): "
                    f"{resp.status_code} — {resp.text[:200]}"
                )
                return None

            output_path.write_bytes(resp.content)
            size_kb = len(resp.content) / 1024
            logger.info(
                f"✅ [VoiceGen] MP3 kaydedildi ({elapsed:.1f}s): "
                f"{output_path} ({size_kb:.1f} KB)"
            )
            return output_path

        except requests.Timeout:
            logger.error("❌ [VoiceGen] ElevenLabs timeout (120s)")
            return None
        except requests.RequestException as e:
            logger.error(f"❌ [VoiceGen] Istek hatasi: {e}")
            return None


# Global singleton
ahu_voice_generator = AHUVoiceGenerator()
