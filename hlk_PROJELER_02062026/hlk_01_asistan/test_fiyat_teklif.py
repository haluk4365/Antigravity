"""
TEST: HLK Fiyat Teklif Formu — tam görünüm
_build_user_pricing_form() çıktısını Telegram'da gösterir.
"""
import asyncio, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("FIYAT_TEKLIF_TEST")

TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fiyat Teklif Formu'nu göster."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from handlers.website import _build_user_pricing_form

    user_data = {
        "brand": "HLK Cosmetics",
        "website_url": "https://example.com/products/vitamin-c-serum",
        "platform": "Instagram / Facebook",
        "video_format": "Dikey (9:16)",
        "video_resolution": "1080p Full HD",
        "video_duration": 12,
        "ad_style": "UGC Tarzı",
        "target_audience": "Genç Yetişkin (18-24)",
    }

    html = _build_user_pricing_form(user_data, price=24.70, yonetici_fiyat=20.58, katsayi=0.347)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ONAY", callback_data="odeme_yapildi"),
         InlineKeyboardButton("❌ İPTAL", callback_data="odeme_iptal")],
    ])

    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 Fiyat Teklif Formu gönderildi ({len(html)} chars)")


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "odeme_yapildi":
        await query.message.reply_text("✅ <b>Ödemeniz alındı!</b> Üretim süreci başlıyor...", parse_mode="HTML")
    else:
        await query.message.reply_text("❌ İşlem iptal edildi.", parse_mode="HTML")
    await query.edit_message_reply_markup(reply_markup=None)


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback, pattern="^odeme_"))
    logger.info("🧪 HLK Fiyat Teklif Formu — tam test — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
