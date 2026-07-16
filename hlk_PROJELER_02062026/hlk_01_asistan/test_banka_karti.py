"""
TEST: Banka Bilgileri Kartı — bağımsız test
"""
import asyncio, logging, os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("BANKA_KARTI_TEST")
TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from handlers.website import _build_banka_bilgileri_karti
    html = _build_banka_bilgileri_karti()
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ ÖDEMEM GERÇEKLEŞTİ", callback_data="odeme_yapildi"),
    ]])
    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 Banka Bilgileri Kartı gönderildi ({len(html)} chars)")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.message.reply_text("✅ Bildiriminiz alındı.", parse_mode="HTML")
    await q.edit_message_reply_markup(reply_markup=None)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback, pattern="^odeme_"))
    logger.info("🧪 Banka Bilgileri Kartı — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
