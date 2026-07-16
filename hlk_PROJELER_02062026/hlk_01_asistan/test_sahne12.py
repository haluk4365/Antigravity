"""
TEST: SAHNE-12 Brief Onay Formu — direkt test
"""
import asyncio, json, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("SAHNE12_TEST")

TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")

# sample-data'dan brief HTML üret
def build_brief_html(data: dict) -> str:
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    maddeler = data["maddeler"]
    lines = [SEP,
             "<b>📋 BRIEF ONAY FORMU</b>",
             "<code>🔵1.Brief  ›  ⏳2.Senaryo  ›  ⏳3.Fiyat Teklifi</code>",
             SEP,
             "<b>📋 BRIEF ÖZETİ</b>",
             "<i>Şimdiye kadar verdiğiniz tüm bilgiler aşağıda özetlenmiştir.</i>", ""]
    for i in range(0, len(maddeler), 2):
        left = maddeler[i]
        is_first = i < 2
        tik_l = "" if is_first else ("✅" if left["onayli"] else "☐") + " "
        sol = f"{tik_l}{left['ikon']} <b>{left['baslik']}:</b> <b>{left['deger']}</b>"
        if i + 1 < len(maddeler):
            right = maddeler[i + 1]
            ri = i + 1
            tik_r = "" if ri < 2 else ("✅" if right["onayli"] else "☐") + " "
            sag = f"{tik_r}{right['ikon']} <b>{right['baslik']}:</b> <b>{right['deger']}</b>"
            if is_first:
                lines.extend([sol, sag])
            else:
                lines.extend([f"<code>{sol}</code>", f"<code>{sag}</code>"])
        else:
            lines.append(sol if is_first else f"<code>{sol}</code>")
        lines.append("")
    lines.append(SEP)
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_path = Path(__file__).resolve().parent / "FORMLAR" / "REFERANS_Brief_Onay_Formu" / "sample-data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    html = build_brief_html(data)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ONAYLA", callback_data="brief_approve")],
        [InlineKeyboardButton("✏️ DÜZELT", callback_data="brief_edit")],
    ])
    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 SAHNE-12 gönderildi ({len(html)} chars)")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        "✅ Onaylandı → SAHNE-13" if q.data == "brief_approve" else "✏️ Düzeltme modu → alan seçin",
        parse_mode="HTML")
    await q.edit_message_reply_markup(reply_markup=None)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb, pattern="^brief_"))
    logger.info("🧪 SAHNE-12 direkt test — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
