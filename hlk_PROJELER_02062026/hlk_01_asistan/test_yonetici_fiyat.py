"""
TEST: Yönetici Fiyatlandırma Formu — kısaltılmış + HLK Sohbet
"""
import asyncio, json, logging, os, sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("YONETICI_TEST")

TOKEN = os.getenv("TELEGRAM_TOKEN_TEST") or os.getenv("TELEGRAM_TOKEN")
SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── HLK Sohbet ──────────────────────────────────────────────────────────
HLK_SYSTEM = """Sen HLK, bir Yapay Zeka Reklam Asistanısın. Yönetici Fiyatlandırma
Formu'nu inceleyen bir yöneticiyle sohbet ediyorsun.

Form verileri:
- Ürün: HLK Vitamin C Serum, Marka: HLK Cosmetics
- Platform: Instagram/Facebook, Dikey 9:16, 1080p, 12sn, 5 sahne
- Ses: Dış Seslendirme (TR, Kadın) + Fon Müziği
- Servisler ve maliyetler: Higgsfield AI ($25), ElevenLabs ($8.50), Kie AI ($10.80)
- Toplam maliyet: $59.30, Önerilen satış fiyatı: $249-$349 aralığı
- Katsayı: değişken, Yönetici fiyatı: $299 + KDV

Kısa, net, 1-3 cümlelik cevaplar ver. Türkçe konuş. Fiyat, maliyet, kar marjı,
servis seçimi konularında yardımcı ol."""

async def hlk_chat(user_msg: str) -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "API anahtarı bulunamadı."
    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-haiku-4-5", max_tokens=300,
            system=HLK_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        return next((b.text for b in resp.content if b.type == "text"), "—")
    except Exception as e:
        return f"HLK yanıt veremedi: {e}"

# ── HTML Üretici ────────────────────────────────────────────────────────
def build_yonetici_html(data: dict) -> str:
    lines = [SEP,
             "<b>━━ 🏷️ HLK YÖNETİCİ FİYATLANDIRMA FORMU ━━</b>",
             "<code>✅Brief › ✅Senaryo › 🔵Fiyat › ⏳Ödeme</code>",
             SEP]

    urun = data["urunOzet"]
    lines.append(f"MARKA: <b>{urun[1]['deger']}</b>")
    lines.append(f"ÜRÜN: <b>{urun[0]['deger']}</b>")
    diger = []
    for u in urun:
        if u['label'] not in ["Ürün Adı", "Marka"]:
            diger.append(u['deger'].replace("Dikey (9:16)", "9:16").replace("1080p Full HD", "1080p")
                         .replace("Dış Seslendirme + Fon Müziği", "Dış ses, fon müziği")
                         .replace("5 sahne • HLK oluşturdu", "5 sahne"))
    lines.append(f"<i>{', '.join(diger)}</i>")
    lines.append(""); lines.append(SEP)

    lines.append("<b>🔌 Servis Sağlayıcı ve Kredi Durumu</b>")
    for i, s in enumerate(data["servisler"], 1):
        durum_icon = {"ok": "✅", "warn": "⚠️"}.get(s["apiDurumSinif"], "⬜")
        kullanim = f" | {s['kullanim']}" if s['kullanim'] != "—" else ""
        lines.append(f"<b>{i}.</b> {durum_icon} <b>{s['ad']}</b> — {s['apiDurum']} | ${s['kredi']} | {s['guvenSkoru']}{kullanim}")
    lines.append(""); lines.append(SEP)

    lines.append(f"<b>⚠️ {data['risk']['baslik']}</b>")
    risk_lines = [
        "Fal.ai servisi normalden yavaş yanıt vermektedir (gecikme: ~4.2s).",
        "Bu üretimde kullanılmayacaktır.",
        "Sıradaki görsel üretici: Kie AI (Güven: 91%, Kredi: $2,000)",
        "Sıradaki video üretici: Higgsfield AI (Güven: 94%, Kredi: $1,200)",
        "Yedek ses üreticisi: OpenAI TTS (Güven: 96%, Kredi: $5,000)",
        "Kritik seviye: Yok. Tüm zorunlu servisler aktif.",
        "Kredi durumu: Yeterli. Tahmini tüketim toplam kredinin %12'si.",
    ]
    for r_line in risk_lines:
        lines.append(f"  - {r_line}")
    lines.append(""); lines.append(SEP)

    def usd(val: str) -> str:
        return "$" + val.replace("₺", "").replace("$", "")
    lines.append("<b>BU İŞ İÇİN TAHMİNİ MALİYETLER</b>")
    lines.append(f"  1- Higgsfield AI (Video Üretimi): {usd('$25.00')}")
    lines.append(f"  2- ElevenLabs (Ses Üretimi): {usd('$8.50')}")
    lines.append(f"  3- Kie AI (Görsel Üretimi): {usd('$10.80')}")
    lines.append(f"  4- Enerji/İşlem: {usd('$12.00')}")
    lines.append(f"  5- Diğer Servisler: {usd('$3.00')}")
    lines.append(f"  <b>TOPLAM: {usd('$59.30')}</b>")
    lines.append("")
    katsayi = float(data.get("_katsayi", "2.5"))
    toplam = 59.30
    yonetici_fiyat = round(toplam * katsayi, 2)
    lines.append(f"<b>KATSAYI:</b> <code>  {katsayi}  </code>")
    lines.append(f"<i>TOPLAM ${toplam:.2f} × {katsayi}</i>")
    lines.append("")
    lines.append(f"<b>━━━ YÖNETİCİ FİYATI: ${yonetici_fiyat:.2f} + KDV ━━━</b>")
    lines.append(""); lines.append(SEP)

    return "\n".join(lines)

# ── Handler'lar ─────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["_katsayi"] = "2.5"
    data_path = Path(__file__).resolve().parent / "FORMLAR" / "REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU" / "sample-data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["_katsayi"] = context.user_data["_katsayi"]
    html = build_yonetici_html(data)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Katsayı Gir", callback_data="enter_katsayi"),
         InlineKeyboardButton("💬 HLK'ya Sor", callback_data="hlk_chat_start")],
        [InlineKeyboardButton("💰 FİYATI ONAYLA", callback_data="price_approve"),
         InlineKeyboardButton("❌ İPTAL", callback_data="price_cancel")],
    ])
    await update.message.reply_text(html, parse_mode="HTML", reply_markup=kb)
    logger.info(f"📤 Yönetici Fiyatlandırma gönderildi ({len(html)} chars)")

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.data == "enter_katsayi":
        await q.answer()
        context.user_data["_waiting_katsayi"] = True
        await q.message.reply_text("✏️ <b>Katsayıyı girin:</b>\n\nÖrn: 1.5, 2.0, 0.8", parse_mode="HTML")
        return
    if q.data == "hlk_chat_start":
        await q.answer()
        context.user_data["_chat_mode"] = True
        await q.message.reply_text(
            "💬 <b>HLK Sohbet Modu</b>\n\nBu form hakkında sorular sorabilirsin.\n"
            "Maliyet, fiyatlandırma, servis seçimi, kar marjı...\n\n"
            "<i>Çıkmak için</i> <b>/iptal</b> <i>yaz.</i>",
            parse_mode="HTML",
        )
        return
    if q.data == "hlk_chat_end":
        await q.answer("✅ Sohbet sonlandı.")
        context.user_data["_chat_mode"] = False
        try: await q.message.delete()
        except: pass
        return
    await q.answer()
    txt = "✅ Fiyat onaylandı!" if q.data == "price_approve" else "❌ İptal edildi."
    await q.message.reply_text(txt, parse_mode="HTML")
    await q.edit_message_reply_markup(reply_markup=None)

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Chat mode'da HLK'ya ilet
    if context.user_data.get("_chat_mode"):
        user_msg = update.message.text
        wait_msg = await update.message.reply_text("⏳ HLK düşünüyor...")
        answer = await hlk_chat(user_msg)
        try: await wait_msg.delete()
        except: pass
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sohbeti Bitir", callback_data="hlk_chat_end"),
            InlineKeyboardButton("💬 Devam", callback_data="hlk_chat_start"),
        ]])
        await update.message.reply_text(answer, parse_mode="HTML", reply_markup=kb)
        return

    # Katsayı giriş modu
    if context.user_data.pop("_waiting_katsayi", False):
        val = update.message.text.strip().replace(",", ".")
        try:
            k = float(val)
            if k <= 0: raise ValueError
        except ValueError:
            await update.message.reply_text("⚠️ Geçersiz. 0.1 - 10 arası bir sayı girin.")
            context.user_data["_waiting_katsayi"] = True
            return
        context.user_data["_katsayi"] = f"{k:.1f}"
        await start(update, context)

# ── Main ────────────────────────────────────────────────────────────────
async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb, pattern="^(price_|enter_katsayi|hlk_chat_)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    logger.info("🧪 Yönetici Fiyatlandırma + HLK Sohbet — @hlk01_test_bot /start")
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("🚀 Dinlemede...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
