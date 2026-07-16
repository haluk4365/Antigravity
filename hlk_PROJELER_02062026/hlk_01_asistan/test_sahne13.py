"""
TEST: SAHNE-13 Senaryo Onay Formu — direkt test
"""
import asyncio, json, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("SAHNE13_TEST")

TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")

SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def build_senaryo_html(data: dict) -> str:
    lines = [SEP,
             "<b>━━━━ 🎬 SENARYO ONAY FORMU ━━━━</b>",
             "<code>✅1.Brief  ›  🔵2.Senaryo  ›  ⏳3.Fiyat Teklifi</code>",
             SEP, ""]

    # Ürün Özeti — Marka ve Ürün
    u = data["urun"]
    lines.append(f"MARKA: <b>{u['marka']}</b>")
    lines.append(f"ÜRÜN: <b>{u['ad']}</b>")
    lines.append(""); lines.append(SEP)

    # Hikaye
    lines.append("<b>📖 Tanıtım Hikayesi</b>")
    lines.append(f"<i>{data['hikaye']}</i>")
    lines.append(""); lines.append(SEP)

    # Sahne Planı — detaylı hikaye anlatımı
    lines.append(f"<b>🎞️ Sahne Planı ({data['toplamSure']})</b>")
    sahneler = [
        ("Dikkat Çekici Giriş", "0:00 – 0:02", "2 sn",
         "Güneşli bir sabah, şehir merkezinde modern bir kafede oturan genç kadın, çantasından HLK Vitamin C Serum'u çıkarıyor. Işık ürünün üzerine düşüyor, ambalaj parlıyor."),
        ("Ürün Tanıtımı", "0:02 – 0:05", "3 sn",
         "Serum yakın planda. Altın damlalık şişeden çıkan portakal rengi sıvı, cilde temas ediyor. Yüksek C vitamini içeriği ekranda vurgulanıyor."),
        ("Kullanım Gösterimi", "0:05 – 0:08", "3 sn",
         "Kadın serumu parmak uçlarıyla nazikçe cildine uyguluyor. Yüzünde ferah bir gülümseme beliriyor. Ayna karşısında cildine bakıyor."),
        ("Faydalar", "0:08 – 0:11", "3 sn",
         "Ekran bölünüyor: solda serum öncesi yorgun cilt, sağda serum sonrası aydınlık ve canlı cilt. Aydınlatma, ton eşitleme, nemlendirme ikonları beliriyor."),
        ("Kapanış — CTA", "0:11 – 0:12", "1 sn",
         "HLK Cosmetics logosu ve 'Işıltını Keşfet' sloganı. Ürün fiyatı ve sipariş linki alt köşede."),
    ]
    for i, (baslik, zaman, sure, aciklama) in enumerate(sahneler, 1):
        lines.append(f"<b>S{i}: {baslik}</b>  <code>⏱{zaman} ({sure})</code>")
        lines.append(f"  <i>{aciklama}</i>")
        lines.append("")
    lines.append(SEP)

    # Seslendirme + Üretim tek satırda
    ses = data["seslendirme"]
    u = data["uretim"]
    lines.append(f"<b>🎙️ {ses['dil']} | {ses['karakter']} | {ses['yapi']}</b>")
    lines.append(f"<b>🎬 {u['platform']} • {u['format']} • {u['cozunurluk']} • {u['sure']} • {u['sahneSayisi']} sahne</b>")
    lines.append(""); lines.append(SEP)

    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_path = Path(__file__).resolve().parent / "FORMLAR" / "REFERANS_SENARYO_ONAY_FORMU" / "sample-data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    html = build_senaryo_html(data)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ONAYLA", callback_data="scn_approve"),
         InlineKeyboardButton("❌ REDDET", callback_data="scn_reject")],
    ])
    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 SAHNE-13 gönderildi ({len(html)} chars)")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    txt = "✅ Senaryo onaylandı!" if q.data == "scn_approve" else "❌ Senaryo reddedildi."
    await q.message.reply_text(txt, parse_mode="HTML")
    await q.edit_message_reply_markup(reply_markup=None)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb, pattern="^scn_"))
    logger.info("🧪 SAHNE-13 direkt test — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
