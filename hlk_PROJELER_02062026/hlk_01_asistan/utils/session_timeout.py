"""
GENEL_KURAL_1 — Oturum zaman aşımı yöneticisi.
SE-007_4/5 uyumlu: Timeout durumunda STATE_SESSION_TIMEOUT tetiklenir.
"""

import asyncio
import logging

from utils.state_engine import StateEngine, UserEvent

logger = logging.getLogger(__name__)

WARNING_MSG = "<b>HLK Reklam Asistanı</b> ile açık bir Telegram oturumunuz kaldı, <b>2 dakika</b> içinde bu oturum kapatılacaktır."
CLOSE_MSG = "<b>HLK Reklam Asistanı</b> ile açık olan Telegram oturumunuz <b>kapatılmıştır.</b>"

_tasks: dict[int, asyncio.Task] = {}


def cancel_timer(user_id: int) -> None:
    """Kullanıcının zamanlayıcısını iptal eder."""
    task = _tasks.pop(user_id, None)
    if task and not task.done():
        task.cancel()
        logger.info(f"⏱️ Timeout iptal edildi: {user_id}")


def start_timer(user_id: int, chat_id: int, bot, user_data: dict) -> None:
    """GENEL_KURAL_1: 5 dakika + 2 dakika uyarı zamanlayıcısı başlatır."""
    cancel_timer(user_id)
    logger.info(f"⏱️ Timeout başlatıldı: {user_id} (5 dk)")

    async def _timer():
        try:
            await asyncio.sleep(300)  # 5 dakika
            se = StateEngine(user_data)
            logger.info(f"🔷 State Engine: {se.current.value}")

            await bot.send_message(
                chat_id=chat_id,
                text=WARNING_MSG,
                parse_mode="HTML",
            )
            logger.info(f"⚠️ Timeout uyarısı: {user_id}")

            await asyncio.sleep(120)  # 2 dakika daha
            se.fire(UserEvent.TIMEOUT_REACHED)
            # OR-004_9: STATE_SESSION_TIMEOUT → STATE_SESSION_CLOSED
            se.fire(UserEvent.SESSION_CLOSED)

            await bot.send_message(
                chat_id=chat_id,
                text=CLOSE_MSG,
                parse_mode="HTML",
            )
            logger.info(f"🔒 Oturum kapatıldı: {user_id}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"❌ Timeout hatası {user_id}: {e}")

    task = asyncio.create_task(_timer())
    _tasks[user_id] = task
