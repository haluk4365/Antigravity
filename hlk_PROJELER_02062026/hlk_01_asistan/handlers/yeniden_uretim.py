"""
AR-002_84 — Yönetici Yeniden Üretim Prosedürü (Admin Reproduction Procedure)

Üretimi başarısız olan bir PID'nin, HLK Anayasası doğrultusunda yalnızca
Yönetici tarafından yeniden üretilebilmesini sağlayan Telegram handler katmanı.

Anayasal konum:
- Bu katman KARAR VERMEZ (MASTER-013). Yalnızca Yönetici girdisini alır,
  Production Package'i mevcut arama mimarisiyle bulur (AR-002_72), onay
  ekranını gösterir ve onay sonrası prosedürü Production Runtime'a devreder
  (AR-002_70: Production Runtime tek giriş noktasıdır).
- Üretimin devamı, yeniden üretim kararı, sağlayıcı/model seçimleri ve tüm
  teknik kararlar HLK Runtime tarafından üretilir (MASTER-013, AR-002_81,
  AR-002_82, AR-002_83).
- Bu prosedür kullanıcı tarafından BAŞLATILAMAZ; yalnızca Yönetici
  başlatabilir (OLAY-025 Tekrar Deneme Politikası: "Yönetici onayı gerekir").

Kullanım:
    /yeniden <PID veya Ürün Adı>
"""

import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config.settings import Settings

logger = logging.getLogger(__name__)

# Callback verisi ön ekleri (main.py pattern kayıtları ile eşleşir)
CB_ONAY_PREFIX = "reprod_onay:"
CB_IPTAL_PREFIX = "reprod_iptal:"

# PackageStatus → Yönetici ekranı Türkçe durum etiketi
_STATUS_LABELS = {
    "CREATED": "Olusturuldu (uretim baslamadi)",
    "BUILDING": "Hazirlaniyor",
    "READY": "Uretime Hazir",
    "PRODUCING": "Uretim Yarim Kaldi",
    "COMPLETED": "Tamamlandi",
    "FAILED": "BASARISIZ",
    "ARCHIVED": "Arsivlendi",
}


def _format_date(iso_date: str) -> str:
    """ISO tarih damgasını Yönetici ekranı formatına çevirir."""
    if not iso_date:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M UTC")
    except (ValueError, TypeError):
        return iso_date


def _is_admin(user_id: int) -> bool:
    """Yönetici kontrolü — TELEGRAM_ADMIN_USER_ID (config/settings.py).

    AR-002_84: Prosedür yalnızca Yönetici tarafından başlatılabilir.
    Settings.is_admin ile aynı kural uygulanır (sınıf özniteliği üzerinden;
    TELEGRAM_ADMIN_USER_ID tanımlı değilse hiç kimse Yönetici kabul edilmez).
    """
    admin_id = Settings.TELEGRAM_ADMIN_USER_ID
    if not admin_id:
        return False
    return str(user_id) == str(admin_id)


def _build_confirmation_screen(package) -> str:
    """Yönetici bilgi kartı + anayasal onay ekranı metnini oluşturur.

    Metin, Proje Yöneticisi tarafından onaylanan referans forma birebir
    uygundur (AR-002_84 Onay Ekranı standardı).
    """
    brief = package.brief or {}
    metadata = package.metadata
    status = metadata.status
    status_label = _STATUS_LABELS.get(status, status)

    sep = "─" * 28
    lines = [
        "🔄 <b>YENIDEN URETIM PROSEDURU</b>",
        sep,
        f"📋 PID: <code>{package.pid}</code>",
        f"📦 Urun Adi: <b>{brief.get('product_name', '-') or '-'}</b>",
        f"🏷 Marka: <b>{brief.get('brand', '-') or '-'}</b>",
        f"📅 Uretim Tarihi: <b>{_format_date(metadata.created_at)}</b>",
        f"🧾 Mevcut Uretim Durumu: <b>{status_label}</b>",
        sep,
        "",
        "HLK Anayasasina gore bu uretim icin yeniden uretim proseduru "
        "uygulanacaktir.",
        "",
        "HLK;",
        "",
        "• Production Package'i inceleyecektir.",
        "",
        "• Uretim durumunu analiz edecektir.",
        "",
        "• Uretimin kaldigi yerden devam edip edemeyecegini "
        "degerlendirecektir.",
        "",
        "• Gerekli olmasi halinde yeniden uretim prosedurunu uygulayacaktir.",
        "",
        "• Tum islemleri HLK Anayasasina uygun sekilde yonetecektir.",
        "",
        "<b>Yeniden uretim prosedurunu baslatmak istiyor musunuz?</b>",
    ]
    return "\n".join(lines)


async def handle_yeniden_uretim_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """/yeniden <PID veya Ürün Adı> — Yönetici Yeniden Üretim Prosedürü girişi.

    AR-002_84 Yönetici İş Akışı:
    1. Yönetici yalnızca PID veya Ürün Adı verir.
    2. HLK ilgili Production Package'i otomatik bulur (find_package).
    3. PID, Ürün Adı, Marka, Üretim Tarihi ve Mevcut Üretim Durumu gösterilir.
    4. Anayasal onay ekranı sunulur ([Evet, Başlat] / [İptal]).

    İstisna: PID doğrulanamaz veya Production Package bulunamazsa prosedür
    başlatılmaz; durum anayasal gerekçesiyle Yöneticiye bildirilir ve işlem
    güvenli şekilde sonlandırılır.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ── Yetki katmanı: yalnızca Yönetici (MASTER-013, OLAY-025) ─────────
    if not _is_admin(user.id):
        logger.warning(
            f"⛔ [Reproduction] Yetkisiz erişim denemesi: user={user.id} "
            f"(/yeniden komutu yalnızca Yönetici içindir)"
        )
        await update.message.reply_text(
            "⛔ Bu komut yalnizca Yonetici tarafindan kullanilabilir "
            "(HLK Anayasasi AR-002_84).",
        )
        return

    query_text = " ".join(context.args or []).strip()
    if not query_text:
        await update.message.reply_text(
            "🔄 <b>Yeniden Uretim Proseduru</b>\n\n"
            "Kullanim: <code>/yeniden &lt;PID veya Urun Adi&gt;</code>\n\n"
            "Ornek:\n"
            "<code>/yeniden PID-20260718-0001</code>\n"
            "<code>/yeniden Akilli Saat X</code>",
            parse_mode="HTML",
        )
        return

    logger.info(
        f"🔄 [Reproduction] Yönetici sorgusu: '{query_text}' (yönetici={user.id})"
    )

    # ── Production Package otomatik bulunur (AR-002_72 mevcut arama) ────
    from services.production_package_runtime import package_runtime
    package = await package_runtime.find_package(query_text)

    if package is None:
        # İstisna akışı — bildirim içeriği HLK Runtime kararıdır (MASTER-013)
        from services.hlk_runtime import (
            hlk_runtime, DecisionRequest, DecisionCategory,
        )
        notify = hlk_runtime.request_decision(DecisionRequest(
            pid="",
            category=DecisionCategory.USER_NOTIFICATION.value,
            requester="yeniden_uretim.handle_yeniden_uretim_command",
            context={
                "kind": "reproduction_not_found",
                "query": query_text,
                "reason": (
                    "PID dogrulanamadi veya Production Package bulunamadi "
                    "(AR-002_57 PID standardi / AR-002_72 paket kaydi)"
                ),
            },
        ))
        if notify.verdict == "NOTIFY":
            await context.bot.send_message(
                chat_id=chat_id,
                text=notify.params.get("text", ""),
                parse_mode=notify.params.get("parse_mode", "HTML"),
            )
        logger.warning(
            f"⛔ [Reproduction] Paket bulunamadı, güvenli sonlandırma: "
            f"'{query_text}'"
        )
        return

    # ── Onay ekranı (AR-002_56 yönetici onay katmanı deseni) ────────────
    text = _build_confirmation_screen(package)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "✅ Evet, Baslat",
            callback_data=f"{CB_ONAY_PREFIX}{package.pid}",
        )],
        [InlineKeyboardButton(
            "🔴 Iptal",
            callback_data=f"{CB_IPTAL_PREFIX}{package.pid}",
        )],
    ])
    await context.bot.send_message(
        chat_id=chat_id, text=text, reply_markup=kb, parse_mode="HTML",
    )
    logger.info(
        f"🖥 [Reproduction] Onay ekranı gösterildi: {package.pid} "
        f"(yönetici={user.id})"
    )


async def handle_yeniden_uretim_onay(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """[Evet, Başlat] — Yönetici onayı sonrası anayasal prosedür başlar.

    Yönetici yalnızca prosedürü başlatır (AR-002_84 Yetki bölümü).
    Adım 1-21'in tamamı HLK Runtime kontrolünde Production Runtime
    tarafından otomatik yürütülür (production_runtime.launch_reproduction).
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    if not _is_admin(user.id):
        await query.answer("⛔ Yalnizca Yonetici", show_alert=True)
        logger.warning(
            f"⛔ [Reproduction] Yetkisiz onay denemesi: user={user.id}"
        )
        return

    pid = query.data[len(CB_ONAY_PREFIX):].strip()
    await query.answer("🔄 Yeniden uretim proseduru baslatiliyor...")
    logger.info(
        f"✅ [Reproduction] Yönetici onayı alındı: {pid} (yönetici={user.id})"
    )

    # Onay ekranı kaldırılır (FD-008_1 ekran temizliği ilkesi)
    try:
        await query.message.delete()
    except Exception as _e:
        pass

    # ── Constitutional Boot Chain (AR-002_62/70) ─────────────────────────
    # Yeniden üretim de bir üretimdir: HLK Runtime + Constitution Runtime
    # aktif olmadan Production Runtime başlatılamaz. Yönetici oturumu yoksa
    # tetikleyici komut (/yeniden onayı) üzerinden boot edilir (MASTER-013).
    from services.hlk_runtime import (
        hlk_runtime, DecisionRequest, DecisionCategory,
    )
    if hlk_runtime.get_session(user.id) is None:
        hlk_runtime.boot(user.id)

    if not hlk_runtime.authorize_production(user.id):
        deny = hlk_runtime.request_decision(DecisionRequest(
            pid=pid,
            category=DecisionCategory.USER_NOTIFICATION.value,
            requester="yeniden_uretim.handle_yeniden_uretim_onay",
            context={"kind": "authorization_denied"},
        ))
        if deny.verdict == "NOTIFY":
            await context.bot.send_message(
                chat_id=chat_id,
                text=deny.params.get("text", ""),
                parse_mode=deny.params.get("parse_mode", "HTML"),
            )
        logger.critical(
            f"🚨 [Reproduction] Anayasal yetkilendirme REDDEDİLDİ: {pid}"
        )
        return

    # ── Prosedür Production Runtime'a devredilir (AR-002_70 tek giriş) ──
    from services.production_runtime import production_runtime
    production_runtime.launch_reproduction(
        pid=pid,
        bot=context.bot,
        admin_chat_id=chat_id,
        admin_user_id=user.id,
    )


async def handle_yeniden_uretim_iptal(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """[İptal] — Yönetici prosedürü başlatmadan vazgeçti.

    Hiçbir üretim işlemi başlatılmaz; işlem güvenli şekilde sonlandırılır.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    if not _is_admin(user.id):
        await query.answer("⛔ Yalnizca Yonetici", show_alert=True)
        return

    pid = query.data[len(CB_IPTAL_PREFIX):].strip()
    await query.answer("Islem iptal edildi")
    logger.info(
        f"🚫 [Reproduction] Yönetici iptali: {pid} (yönetici={user.id}) — "
        f"prosedür başlatılmadı"
    )

    try:
        await query.message.delete()
    except Exception as _e:
        pass

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🚫 <b>Yeniden uretim proseduru iptal edildi.</b>\n\n"
            f"📋 PID: <code>{pid}</code>\n"
            f"<i>Hicbir uretim islemi baslatilmadi.</i>"
        ),
        parse_mode="HTML",
    )
