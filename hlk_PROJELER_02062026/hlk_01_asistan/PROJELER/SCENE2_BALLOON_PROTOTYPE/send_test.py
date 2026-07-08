#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sahne-2 Prototip — Telegram'a Video Gönderme Testi

scene2_tr_prototype.mp4'yi @hlk01_test_bot üzerinden Telegram'a gönderir.

Kullanım: python send_test.py
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# SABİTLER
# ============================================================
PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent  # HLK_01_asistan/
VIDEO_PATH = Path("output/scene2_tr_prototype.mp4")
FFPROBE = "ffprobe"

# ============================================================
# FONKSİYONLAR
# ============================================================

def load_env_token():
    """Proje .env dosyasından TELEGRAM_TOKEN_TEST oku."""
    env_path = PROJE_KOK / ".env"

    if not env_path.exists():
        logger.error(f"❌ .env bulunamadı: {env_path}")
        # Doğrudan ortam değişkeninden dene
        token = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
        if token:
            logger.info("  ✓ Token ortam değişkeninden alındı")
            return token
        return None

    load_dotenv(dotenv_path=env_path)
    token = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
    if token:
        logger.info(f"  ✓ Token .env'den yüklendi")
        return token

    logger.error("❌ TELEGRAM_TOKEN_TEST veya TELEGRAM_TOKEN bulunamadı")
    return None


def get_duration(filepath):
    """Video süresini ffprobe ile al."""
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", str(filepath)],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"  ⚠ Süre okunamadı: {e}")
    return 0.0


async def send_video(token, video_path, duration):
    """Video'yu Telegram botu üzerinden gönder."""
    try:
        from telegram import Bot, InputFile

        bot = Bot(token=token)
        bot_info = await bot.get_me()
        logger.info(f"  ✓ Bot: @{bot_info.username}")

        # Bot info alındı — şimdi video gönder
        with open(video_path, "rb") as f:
            msg = await bot.send_video(
                chat_id=bot_info.id,  # kendi chat_id'sine gönder
                video=InputFile(f, filename="scene2_tr_prototype.mp4"),
                supports_streaming=True,
                width=720,
                height=1280,
                duration=int(duration),
                caption="🧪 <b>Prototip: Sahne-2 Video Baloon</b>\n"
                        "HLK + AHU + Konuşma Balonu — Tek Render\n"
                        f"Süre: {duration:.1f}sn",
                parse_mode="HTML",
            )
            logger.info(f"  ✅ Video gönderildi! message_id={msg.message_id}")

            # Dosya ID'sini göster
            if msg.video:
                logger.info(f"  📎 file_id={msg.video.file_id}")
            return True

    except ImportError:
        logger.warning("  ⚠ python-telegram-bot yüklü değil, HTTP API deneniyor...")
        return await send_video_http(token, video_path, duration)
    except Exception as e:
        logger.error(f"  ❌ Gönderme hatası: {e}")
        return False


async def send_video_http(token, video_path, duration):
    """Yedek: Doğrudan Telegram HTTP API ile gönder."""
    import httpx

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    file_size = video_path.stat().st_size

    logger.info(f"  📤 HTTP API ile gönderiliyor... ({file_size // 1024}KB)")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            with open(video_path, "rb") as f:
                files = {"video": ("video.mp4", f, "video/mp4")}
                data = {
                    "chat_id": os.getenv("TEST_CHAT_ID", ""),
                    "supports_streaming": "true",
                    "width": 720,
                    "height": 1280,
                    "duration": int(duration),
                }
                resp = await client.post(url, data=data, files=files)

            if resp.status_code == 200:
                result = resp.json()
                if result.get("ok"):
                    msg_id = result["result"].get("message_id", "?")
                    logger.info(f"  ✅ Video gönderildi! message_id={msg_id}")
                    return True
                else:
                    logger.error(f"  ❌ API hatası: {result.get('description', '?')}")
            else:
                logger.error(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"  ❌ HTTP gönderme hatası: {e}")

    return False


async def main():
    """Ana akış."""
    print("\n📤 Sahne-2 Prototip — Telegram Gönderme Testi")
    print("=" * 50)

    # 1. Video var mı?
    if not VIDEO_PATH.exists():
        logger.error(f"  ❌ Video bulunamadı: {VIDEO_PATH}")
        logger.error(f"  Önce 'python render_scene.py' çalıştırın")
        sys.exit(1)
    logger.info(f"  ✓ Video: {VIDEO_PATH}")

    # 2. Süre
    dur = get_duration(VIDEO_PATH)
    logger.info(f"  ✓ Süre: {dur:.3f}sn")
    logger.info(f"  ✓ Boyut: {VIDEO_PATH.stat().st_size // 1024}KB")

    # 3. Token yükle
    token = load_env_token()
    if not token:
        logger.error("  ❌ Token bulunamadı. Lütfen .env dosyasını kontrol edin.")
        sys.exit(1)
    logger.info(f"  ✓ Token: {token[:10]}...{token[-5:]}")

    # 4. Gönder
    basarili = await send_video(token, VIDEO_PATH, dur)

    if basarili:
        print(f"\n  ✅ Prototip test başarılı!")
        print(f"     Video: {VIDEO_PATH}")
    else:
        print(f"\n  ❌ Prototip test başarısız!")
        print(f"     Yukarıdaki hataları kontrol edin.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
