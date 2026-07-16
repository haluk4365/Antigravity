"""TEST: Kullanıcı Fiyat Teklif Formu"""
import asyncio, json, logging, os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("KULLANICI_FIYAT_TEST")
TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime
    tcmb_kur = 46.87
    katsayi = float(context.user_data.get("_katsayi", "0.347"))
    toplam = 59.30
    kdvli = round(toplam * katsayi * 1.20, 2)
    pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
    satis_tl = round(kdvli * tcmb_kur, 2)

    html = (
        "<code>✅Brief › ✅Senaryo › ✅Fiyat › ✅Ödeme</code>\n"
        f"{SEP}\n"
        "<b>HLK BANKA ÖDEME BİLGİLERİ KARTI</b>\n"
        f"<code>{pid}</code>\n"
        f"{SEP}\n\n\n\n\n\n\n"
        f"<b>💰 KDV Dahil Dolar Tutarı:  ${kdvli:.2f}</b>\n"
        f"TCMB Döviz Satış: {tcmb_kur} TL\n\n"
        f"<b>━━━ 💵 SATIŞ FİYATI: {satis_tl:.2f} TL ━━━</b>\n\n\n\n"
        f"{SEP}\n"
        "<b>💳 HESAP SAHİBİ:</b>  <b>HALUK ARI</b>\n\n"
        "▸ <b>Garanti Bankası (TL)</b>\n"
        "  <code>TR69 0006 2000 3910 0006 8957 76</code>\n"
        "▸ <b>Garanti Bankası (USD)</b>\n"
        "  <code>TR69 0006 2000 3910 0009 0255 08</code>\n"
        "▸ <b>Ak Bank (TL)</b>\n"
        "  <code>TR96 0004 6001 6688 8000 0490 88</code>\n"
        f"{SEP}\n"
        "<b>📌 Ödeme Yöntemi:</b>  Banka Havalesi / EFT\n"
        f"{SEP}\n"
        "<b>⚠️ ÖNEMLİ UYARI:</b>\n"
        "• Ödemeniz alındıktan sonra üretim süreci başlar.\n"
        "• Video belirtilen süre içerisinde adresinize dijital Mp4 formatında teslim edilir.\n"
        "• Onayınız sonrası süreç otomatik olarak başlar.\n"
        f"{SEP}"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 ÖDEME YAPTIM", callback_data="payment_done"),
         InlineKeyboardButton("🔴 ÖDEME İPTAL", callback_data="payment_cancel")],
    ])
    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "payment_done":
        await q.message.reply_text(
            "✅ <b>Ödeme bildiriminiz alındı!</b>\n\n"
            "Video üretiminiz başlatılmıştır.\n"
            "Bu süreç yaklaşık 10–15 dakika sürmektedir.\n"
            "Video tamamlandığında otomatik olarak size gönderilecektir.",
            parse_mode="HTML",
        )
    elif q.data == "payment_cancel":
        await q.message.reply_text(
            "❌ <b>Ödeme iptal edildi.</b>\n\n"
            "Yeni bir reklam çalışması başlatmak için "
            "lütfen tekrar <b>/start</b> komutu ile giriş yapınız.",
            parse_mode="HTML",
        )
    await q.edit_message_reply_markup(reply_markup=None)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb, pattern="^payment_"))
    logger.info("🧪 Odeme Karti — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
