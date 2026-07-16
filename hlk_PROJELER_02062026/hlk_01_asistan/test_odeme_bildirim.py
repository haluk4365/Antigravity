"""
TEST: Yönetici Ödeme Onay Formu — "Ödemem Gerçekleşti" Bildirim Kartı
FD-008_1: STATE_PAYMENT_VERIFICATION — Yalnızca yöneticiye gönderilir.
"""
import asyncio, logging, os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("ODEME_DOGRULAMA_TEST")
TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Örnek veriler ─────────────────────────────────────────────────────
ORNEK = {
    "kullanici_adi": "Ahmet Yılmaz",
    "kullanici_id": 123456789,
    "urun": "HLK Vitamin C Serum",
    "marka": "HLK Cosmetics",
    "platform": "Instagram",
    "format": "9:16 Dikey",
    "cozunurluk": "1080p Full HD",
    "sure": "12 sn",
    "sahne": "5 sahne",
    "satis_fiyati_dolar": 24.69,
    "satis_fiyati_tl": 1157.22,
    "tcmb_kur": 46.87,
    "banka_adi": "Garanti Bankası",
    "iban": "TR69 0006 2000 3910 0006 8957 76",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

    html = (
        f"{SEP}\n"
        "⚠️ <b>YÖNETİCİ ÖDEME BİLDİRİMİ</b>\n"
        f"{SEP}\n"
        f"<code>{pid}</code>\n"
        "\n"
        "📋 <b>ÖDEME DOĞRULAMA</b>\n"
        f"{SEP}\n"
        "ℹ️  Kullanıcı <b>ÖDEME YAPTIM</b> bildirimi göndermiştir.\n"
        "ℹ️  Lütfen banka hesabınızı kontrol ediniz.\n"
        "ℹ️  Ödeme hesabınıza ulaştıysa aşağıdaki butona basınız.\n"
        f"{SEP}\n"
        "<b>👤 KULLANICI BİLGİLERİ</b>\n"
        f"Ad Soyad: <b>{ORNEK['kullanici_adi']}</b>\n"
        f"Kullanıcı ID: <code>{ORNEK['kullanici_id']}</code>\n"
        f"{SEP}\n\n\n\n"
        "<b>📦 ÜRÜN BİLGİLERİ</b>\n"
        f"Ürün: <b>{ORNEK['urun']}</b>\n"
        f"Marka: <b>{ORNEK['marka']}</b>\n"
        f"Platform: <b>{ORNEK['platform']}</b>\n"
        f"Format: {ORNEK['format']} | {ORNEK['cozunurluk']} | {ORNEK['sure']} | {ORNEK['sahne']}\n"
        f"{SEP}\n"
        "<b>💰 ÖDEME BİLGİLERİ</b>\n"
        f"Banka: <b>{ORNEK['banka_adi']}</b>\n"
        f"IBAN: <code>{ORNEK['iban']}</code>\n"
        f"Beklenen Tutar: <b>${ORNEK['satis_fiyati_dolar']:.2f}</b> / <b>{ORNEK['satis_fiyati_tl']:.2f} TL</b>\n"
        f"TCMB Kur: {ORNEK['tcmb_kur']} TL\n"
        f"{SEP}\n\n\n\n"
        "<i>⏱️ Bu bildirim HLK tarafından otomatik oluşturulmuştur.</i>\n"
        f"{SEP}"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Ödeme hesabıma geçti", callback_data="admin_odeme_onay")],
        [InlineKeyboardButton("🔴 RET — Ödeme Ulaşmadı", callback_data="admin_odeme_ret")],
    ])

    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 Yönetici Ödeme Bildirimi gönderildi ({len(html)} chars)")


async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()

    if q.data == "admin_odeme_onay":
        await q.message.reply_text(
            "✅ <b>ÖDEME ONAYLANDI</b>\n\n"
            "📦 Production Package oluşturuluyor...\n"
            "🎬 Video üretimi başlatılıyor...\n\n"
            "<i>Kullanıcıya üretim başlangıç bildirimi gönderilecek.</i>",
            parse_mode="HTML",
        )
        logger.info("✅ Yönetici ödemeyi onayladı → Video üretimi başlıyor")
    elif q.data == "admin_odeme_ret":
        await q.message.reply_text(
            "❌ <b>ÖDEME ONAYLANMADI</b>\n\n"
            "Kullanıcıya ödemenin ulaşmadığına dair bildirim gönderilecek.\n"
            "Oturum kapatılacak.",
            parse_mode="HTML",
        )
        logger.info("❌ Yönetici ödemeyi reddetti → Oturum kapatılıyor")

    await q.edit_message_reply_markup(reply_markup=None)


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb, pattern="^admin_odeme_"))
    logger.info("🧪 Yönetici Ödeme Onay Formu — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
