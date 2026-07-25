"""Telegram /cancel komutunun handler'ı.

FAZ-6: Handler konuşma üretmez. Konuşma Scene Engine tarafından üretilir.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.scene_lock import SceneLock

logger = logging.getLogger(__name__)


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """İşlemi iptal et ve sıfırla.

    AR-002_44: SceneLock'u IDLE'a sıfırlar.
    FAZ-6: Konuşmayı Scene Engine üretir.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(f"🛑 Kullanıcı {user.id} işlemi iptal etti")

    # SceneLock sıfırla — bir sonraki /start SAHNE-1'i tekrar başlatabilir
    SceneLock.reset(context.user_data)

    # User context'i sıfırla
    context.user_data.clear()

    # ── FAZ-6: Konuşmayı Scene Engine üretir ──
    try:
        from services.scene_engine import conversation_scene_engine
        await conversation_scene_engine.produce_scene_response(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
            trigger_event="SESSION_CANCELLED",
        )
    except Exception as _e:
        # Fallback — Scene Engine çalışmazsa
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ **İşlem iptal** _edildi._\n\n"
                 "_Başlamak için_ **/start** _yazın._",
            parse_mode="Markdown"
        )
