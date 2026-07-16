"""
TEST: Brief Onay Formu → Telegram HTML (PNG YOK) + InlineKeyboard
=================================================================
Saf Telegram HTML mesajı. PNG render YOK, Puppeteer YOK.
Kullanıcının işaretlediği maddeler ✅ tikli, diğerleri ☐ boş gelir.
Alt kısımda tıklanabilir Onayla / Düzelt butonları.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logger = logging.getLogger("TEST_HTML")

TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("❌ TELEGRAM_TOKEN_TEST bulunamadı!")
    sys.exit(1)

logger.info(f"🔑 Test botu: ...{TOKEN[-8:]}")


def build_brief_html(data: dict) -> str:
    """Brief Onay Formu'nu Telegram uyumlu HTML olarak oluştur.
    Kullanıcının seçtiği maddeler ✅, diğerleri ☐ ile gösterilir.
    """
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    lines = []
    lines.append(f"{SEP}")
    lines.append("<b>📋 BRIEF ONAY FORMU</b>")

    # Adım göstergesi — tek satır
    adim_parts = []
    for a in data["adimlar"]:
        if a["durum"] == "done":
            adim_parts.append(f"✅{a['no']}.{a['baslik']}")
        elif a["durum"] == "active":
            adim_parts.append(f"🔵{a['no']}.{a['baslik']}")
        else:
            adim_parts.append(f"⏳{a['no']}.{a['baslik']}")
    lines.append(f"<code>{'  ›  '.join(adim_parts)}</code>")
    lines.append(f"{SEP}")

    # Checklist
    lines.append("<b>📋 BRIEF ÖZETİ</b>")
    lines.append("<i>Şimdiye kadar verdiğiniz tüm bilgiler aşağıda özetlenmiştir.</i>")
    lines.append("")

    # 2 sütunlu düzen
    maddeler = data["maddeler"]
    for i in range(0, len(maddeler), 2):
        left = maddeler[i]
        is_first_pair = i < 2
        tik_l = "" if is_first_pair else ("✅" if left["onayli"] else "☐") + " "
        sol = f"{tik_l}{left['ikon']} <b>{left['baslik']}:</b> <b>{left['deger']}</b>"

        if i + 1 < len(maddeler):
            right = maddeler[i + 1]
            ri = i + 1
            tik_r = "" if ri < 2 else ("✅" if right["onayli"] else "☐") + " "
            sag = f"{tik_r}{right['ikon']} <b>{right['baslik']}:</b> <b>{right['deger']}</b>"
            # İlk 2 madde code bloğu DIŞINDA (siyah bold), diğerleri İÇİNDE
            if is_first_pair:
                lines.append(sol)
                lines.append(sag)
            else:
                lines.append(f"<code>{sol}</code>")
                lines.append(f"<code>{sag}</code>")
        else:
            if is_first_pair:
                lines.append(sol)
            else:
                lines.append(f"<code>{sol}</code>")
        lines.append("")

    lines.append(f"{SEP}")
    lines.append("<b>NOT: DÜZELTMEK İÇİN TİKİ KALDIRIN.</b>")

    return "\n".join(lines)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"👤 /start — {user.full_name} (chat_id={chat_id})")

    # sample-data.json oku
    data_path = Path(__file__).resolve().parent / "FORMLAR" / "REFERANS_Brief_Onay_Formu" / "sample-data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = build_brief_html(data)

    keyboard = [
        [InlineKeyboardButton("✅ ONAYLA", callback_data="brief_approve")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        html,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    logger.info(f"📤 Brief HTML gönderildi ({len(html)} chars) → {user.full_name}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "brief_approve":
        await query.message.reply_text(
            f"✅ <b>Brief Onaylandı!</b>\n\n"
            f"Harika {user.first_name}, seçimlerin onaylandı.\n"
            f"Senaryo aşamasına geçiliyor...",
            parse_mode="HTML",
        )
        logger.info(f"✅ Onaylandı — {user.full_name}")

    elif query.data == "brief_edit":
        await query.message.reply_text(
            "✏️ <b>Düzeltme Modu</b>\n\n"
            "Hangi bilgiyi düzeltmek istersin?\n"
            "Lütfen düzeltmek istediğin maddeyi yaz.",
            parse_mode="HTML",
        )
        logger.info(f"✏️ Düzeltme istendi — {user.full_name}")

    # Butonları pasif yap
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^brief_"))

    logger.info("=" * 50)
    logger.info("🧪 TEST: Telegram HTML + InlineKeyboard (PNG YOK)")
    logger.info("🤖 @hlk01_test_bot — /start yazın")
    logger.info("=" * 50)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")

    try:
        stop_event = asyncio.Event()
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("⏹️ Kapatılıyor...")

    await app.updater.stop()
    await app.stop()
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
