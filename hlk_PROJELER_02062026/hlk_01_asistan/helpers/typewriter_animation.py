"""
AR-002_31 Speech-Text-Wave Synchronization — Typewriter Animation Module

HLK konuşma balonunu kelime kelime yazdıran daktilo efekti.
handlers/start.py ve services/scene_delivery.py tarafından ortak kullanılır.

Çağrı standardı:
    message_id = await typewriter_animation(chat_id, text, bot, delay)
"""

import asyncio
import logging
import re

from telegram.constants import ChatAction

logger = logging.getLogger(__name__)


def strip_html(text: str) -> str:
    """HTML etiketlerini temizler, düz metin döndürür."""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = clean.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    clean = clean.replace("&quot;", '"').replace("&#39;", "'")
    return clean


async def typewriter_animation(
    chat_id: int,
    text: str,
    bot,
    delay: float = 0.06,
) -> int | None:
    """
    Daktilo yazı animasyonu — kelime kelime yazı.

    3 aşamalı garantili teslimat:
    1. "▌" ile boş mesaj gönder
    2. 3'er kelime gruplar halinde düzenle (API çağrısı azaltmak için)
    3. Son halini HTML formatında yaz — başarısız olursa
       yeni mesaj gönderip eskiyi sil (kesin çözüm)

    Args:
        chat_id: Telegram chat ID.
        text: Yazılacak metin (HTML formatında olabilir).
        bot: Telegram bot instance'ı.
        delay: Kelime grupları arası gecikme (saniye).

    Returns:
        Oluşturulan mesajın message_id'si, başarısız olursa None.
    """
    plain = strip_html(text)
    words = plain.split()

    if not words:
        logger.warning("⚠️ [Typewriter] Boş metin, atlanıyor")
        return None

    try:
        # ADIM 1: "▌" ile boş mesaj gönder
        msg = await bot.send_message(
            chat_id=chat_id,
            text="▌",
            parse_mode="HTML",
        )
        message_id = msg.message_id
        accumulated = ""

        # ADIM 2: 4'er kelime gruplar halinde ekle
        # NOT: chunk_size ve sleep süresi SAHNE-2 video senkronizasyonu için kritik.
        # Video süresince daktilo devam etmeli — değiştirirken dikkat!
        chunk_size = 4
        for i in range(0, len(words), chunk_size):
            if i == 0:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(delay * chunk_size)

            chunk = words[i:i + chunk_size]
            if accumulated:
                accumulated += " " + " ".join(chunk)
            else:
                accumulated = " ".join(chunk)

            # Sonraki chunk var mı?
            has_more = (i + chunk_size) < len(words)
            display = accumulated + (" ▌" if has_more else "")

            try:
                await msg.edit_text(text=display)
            except Exception as e:
                # Düzenleme başarısız — sonraki chunk'ta tekrar deneriz
                logger.debug(f"⏳ [Typewriter] Ara düzenleme atlandı: {e}")

        # ADIM 3: Son halini HTML formatında yaz (garantili)
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(text=text, parse_mode="HTML")
            logger.info(f"✅ [Typewriter] HTML final: {len(words)} kelime, msg:{message_id}")
        except Exception as e:
            logger.warning(f"⚠️ [Typewriter] HTML edit başarısız, yeni mesaj: {e}")
            # Son çare: yeni bir mesaj gönder, eskiyi sil
            try:
                await msg.delete()
            except Exception as _e:
                pass
            try:
                new_msg = await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="HTML",
                )
                message_id = new_msg.message_id
                logger.info(f"✅ [Typewriter] Yeni mesajla tamamlandı: msg:{message_id}")
            except Exception as e2:
                logger.error(f"❌ [Typewriter] Yeni mesaj da başarısız: {e2}")
                return None

        return message_id

    except Exception as e:
        logger.error(f"❌ [Typewriter] Animasyon hatası: {e}")
        # Son çare: düz metin gönder
        try:
            fallback = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
            )
            logger.info(f"✅ [Typewriter] Fallback mesaj: msg:{fallback.message_id}")
            return fallback.message_id
        except Exception as _e:
            return None
