#!/usr/bin/env python3
"""
HLK AI Reklam Asistanı — Ana Bot Giriş Noktası

Mimari: ANA_YASA / AR-002_28 / AR-002_36 / AR-002_38 / SE-007 / FD-008
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────
# 1. ORTAM HAZIRLIĞI
# ──────────────────────────────────────────────────────────────────────

# Windows konsolu UTF-8 encoding fix (emoji logger output için)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Python 3.14+: asyncio.get_event_loop() otomatik loop yaratmıyor
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# .env'i EN BAŞTA yükle
from dotenv import load_dotenv
load_dotenv()

# Logging konfigürasyonu — stdout her zaman, dosya opsiyonel
log_dir = Path("logs")
handlers = [logging.StreamHandler()]
try:
    log_dir.mkdir(exist_ok=True)
    handlers.append(logging.FileHandler(log_dir / "bot.log", encoding="utf-8"))
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(name)s — %(levelname)s — %(message)s',
    handlers=handlers,
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# 2. MODÜL BAĞLANTILARI (ANA_YASA / AR-002 / SE-007 / FD-008 uyumlu)
# ──────────────────────────────────────────────────────────────────────

# Telegram API
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
)
from telegram.constants import ChatAction

# Konfigürasyon
from config.settings import Settings
settings = Settings()
logger.info("✅ Settings yüklendi")

# State Engine — SE-007_3/4/5/6
from utils.state_engine import StateEngine, UserState, UserEvent

# Session Timeout — GENEL_KURAL_1
from utils.session_timeout import start_timer, cancel_timer

# Scene Registry — FD-008_1
from services.scene_registry import get_scene_for_state, SCENE_REGISTRY
logger.info(f"✅ Scene Registry: {len(SCENE_REGISTRY)} sahne tanımı yüklendi")

# Scene Engine — AR-002_28
from services.scene_engine import conversation_scene_engine
logger.info("✅ Conversation Scene Engine hazır")

# Scene Delivery — AR-002_36 / AR-002_38
from services.scene_delivery import scene_delivery, DeliveryStatus

# Voice Generator — AR-002_29 / AR-002_30 / AR-002_32
from services.voice_generator import ahu_voice_generator
logger.info("✅ AHU Voice Generator hazır")

# Research Orchestrator — AR-002_13 / AR-002_35
from services.research_orchestrator import run_research_task

# CEE: Constitution Enforcement Engine — AR-002_60 / 21_CEE
from services.constitution_enforcement import constitution_enforcement
logger.info("✅ Constitution Enforcement Engine (CEE) hazır")

# EEC: Execution Event Collector — AR-002_61 / 22_EEC
from services.execution_event_collector import (
    execution_event_collector, EECEventType, ExecutionPhase,
)
logger.info("✅ Execution Event Collector (EEC) hazır")

# Olay Kayıt Merkezi — 14_OLAY_KAYIT_MERKEZI
from services.olay_kayit_merkezi import event_registry
logger.info("✅ Olay Kayıt Merkezi hazır")

# LAC: Live Activity Center — FEAT-015
from services.lac import live_activity_center
logger.info("✅ Live Activity Center (LAC) hazır")

# Constitution Cache Manager — Anayasal İşletim Sistemi
from services.constitution_cache import constitution_cache
logger.info("✅ Constitution Cache Manager hazır")

# Handler'lar
from handlers.start import (
    start_handler,
    button_handler as handle_language_selection,
    message_handler,
    handle_devam_button,
    handle_format_selection as scout_format_handler,
)
from handlers.cancel import handle_cancel
from handlers.start import handle_duration_hlk
from handlers.website import handle_material_choice, handle_platform_selection, handle_format_selection, handle_resolution_selection, handle_audio_toggle, handle_audio_devam
from handlers.website import handle_style_selection, handle_audience_selection
from handlers.website import handle_voice_language, handle_voice_character, handle_emphasis, handle_emphasis_done
from handlers.website import handle_scenario_approve, handle_scenario_reject
from handlers.website import handle_pricing_approve, handle_pricing_reject, handle_payment_declared
from handlers.website import handle_admin_pricing_submit
from handlers.website import handle_brief_approve, handle_brief_edit, handle_brief_edit_field

# Dil destegi dogrulama (AR-002_37 / dil senkron)
from handlers.start import validate_language_support
validate_language_support()

# ──────────────────────────────────────────────────────────────────────
# 3. HANDLER FONKSİYONLARI
# ──────────────────────────────────────────────────────────────────────

async def handle_audit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """CEE denetim geçmişini ve LAC olay akışını kullanıcıya gösterir.

    Olay Kayıt Merkezi ve CEE'den gerçek verileri okur.
    Tahmin üretmez — yalnızca kaydedilmiş Event'leri gösterir.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id

    # LAC panelini Olay Kayıt Merkezi'nden oku
    lac_html = live_activity_center.get_telegram_html(pid=str(user.id), limit=15)

    # CEE enforcement history
    cee_history = constitution_enforcement.get_history()
    if cee_history:
        cee_lines = ["", "<b>📋 CEE Denetim Geçmişi:</b>"]
        for r in cee_history[-5:]:
            emoji = "✅" if r.verdict.value == "PASS" else "❌"
            cee_lines.append(
                f"  {emoji} <code>{r.report_id}</code>: <b>{r.verdict.value}</b> "
                f"(deneme {r.attempt}, eksik: {r.deficiency_count})"
            )
        lac_html += "\n".join(cee_lines)

    await update.message.reply_text(lac_html, parse_mode="HTML")
    logger.info(f"📊 [AUDIT] Kullanıcı {user.id} denetim raporu görüntüledi")


async def handle_constitution_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Constitution Cache durumu ve Anayasal Boot manifest'ini gösterir.

    HLK'nın Anayasal İşletim Sistemi durumunu raporlar:
    - Cache durumu (hangi dosyalar değişmiş)
    - Boot manifest'i (18 katman)
    - CONSTITUTION_READY durumu
    """
    user = update.effective_user

    # Constitution Cache durumu
    cache_html = constitution_cache.get_telegram_html()

    # Boot manifest'i
    manifest = constitution_cache.get_boot_manifest()
    if manifest:
        boot_lines = ["", "<b>📋 BOOT MANIFEST (18 Katman):</b>"]
        for m in manifest:
            status_emoji = {
                "cached": "💾", "changed": "🔄", "new": "🆕",
                "missing": "❌", "error": "⚠️",
            }.get(m["status"], "❓")
            boot_lines.append(
                f"  {status_emoji} <b>{m['layer']}</b> "
                f"({m['size_kb']:.0f}KB) [{m['status']}]"
            )
        cache_html += "\n".join(boot_lines)

    # CEE durumu
    cee_status = constitution_cache.is_valid()
    cee_str = "✅ <b>CONSTITUTION_READY</b>" if cee_status else "❌ <b>CONSTITUTION_DEGISIKLIK_VAR</b>"
    cache_html += f"\n\n{cee_str}\n"
    cache_html += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    cache_html += f"👤 Kullanıcı: <code>{user.id}</code> | "
    cache_html += f"📁 {constitution_cache.get_file_count()} ANA YASA dosyası"

    await update.message.reply_text(cache_html, parse_mode="HTML")
    logger.info(f"📜 [CONSTITUTION] Kullanıcı {user.id} anayasa durumu görüntüledi")


async def handle_rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generic Constitution Index — tüm ANA YASA kurallarının özetini gösterir."""
    try:
        from services.constitution_index import constitution_index
        html = constitution_index.get_telegram_html()
    except Exception as e:
        html = f"⚠️ Constitution Index erişilemedi: {e}"
    await update.message.reply_text(html, parse_mode="HTML")
    logger.info(f"📚 [RULES] Kullanıcı {update.effective_user.id} kural indeksini görüntüledi")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Hataları logla ve kullanıcıya bildir (sadece gerçek hatalar)."""
    error_str = str(context.error).lower()
    # Stale callback_query (buton çok eski) — sessizce yoksay
    if "query is too old" in error_str or "query id is invalid" in error_str:
        logger.warning(f"⏳ Stale callback ignored: {context.error}")
        return

    logger.error(f"Update {update} caused error {context.error}")

    if update is None or not getattr(update, "effective_chat", None):
        return

    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "❌ <b>Bir hata oluştu.</b> "
                "<i>Lütfen</i> <b>tekrar deneyin</b> "
                "<i>veya</i> <b>/start</b> <i>yazarak</i> "
                "<b>baştan başlayın</b>."
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"error_handler içinde gönderme hatası: {e}")


async def handle_unimplemented_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Henüz uygulanmamış buton callback'leri için geçici handler."""
    query = update.callback_query
    await query.answer("⏳ Bu özellik hazırlanıyor...", show_alert=False)
    logger.info(f"⏳ Uygulanmamış callback: {query.data} — user: {query.from_user.id}")


# ──────────────────────────────────────────────────────────────────────
# 4. MAIN — BOT BAŞLATMA
# ──────────────────────────────────────────────────────────────────────

def main():
    """Bot'u başlat — polling modunda, drop_pending_updates ile temiz başlangıç."""
    import os as _os
    logger.info(f"🤖 HLK AI Reklam Asistanı başlatılıyor... PID={_os.getpid()}")

    # Application oluştur — uzun timeout'lar (video upload için)
    app = (
        Application.builder()
        .token(settings.TELEGRAM_TOKEN)
        .connect_timeout(30)
        .read_timeout(60)
        .write_timeout(120)
        .pool_timeout(30)
        .build()
    )

    # ── AR-002_36: Bot instance'ını Scene Delivery'e bağla ──
    scene_delivery.bind_bot(app.bot)
    logger.info("🔗 scene_delivery.bind_bot(app.bot) — Delivery Module bağlandı")

    # ── Command Handlers ──
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("cancel", handle_cancel))
    app.add_handler(CommandHandler("audit", handle_audit_command))
    app.add_handler(CommandHandler("constitution", handle_constitution_command))
    app.add_handler(CommandHandler("rules", handle_rules_command))

    # ── Callback Handlers (Inline Butonlar) ──
    # FD-008_1 Sahne geçişleri için callback handler'ları
    app.add_handler(CallbackQueryHandler(
        handle_language_selection, pattern="^lang_"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_devam_button, pattern="^devam$"
    ))
    app.add_handler(CallbackQueryHandler(
        scout_format_handler, pattern="^fmt_"
    ))

    # SAHNE-01 callback'leri (scene_registry'deki button tanimlari)
    app.add_handler(CallbackQueryHandler(
        handle_material_choice, pattern="^material_"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_material_choice, pattern="^upload_material$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_material_choice, pattern="^skip_material$"
    ))

    # SAHNE-02: Platform Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_platform_selection, pattern="^platform_"
    ))
    # SAHNE-03: Format Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_format_selection, pattern="^format_"
    ))
    # SAHNE-04: Çözünürlük Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_resolution_selection, pattern="^resolution_"
    ))
    # SAHNE-08: Ses Seçimi toggle callback'leri (FD-008_1 uyumlu)
    app.add_handler(CallbackQueryHandler(
        handle_audio_toggle, pattern="^audio_toggle_"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_audio_devam, pattern="^audio_devam$"
    ))

    # SAHNE-05: "HLK'ya Bırak" butonu
    app.add_handler(CallbackQueryHandler(
        handle_duration_hlk, pattern="^duration_hlk$"
    ))
    # SAHNE-06: Tanıtım Tarzı Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_style_selection, pattern="^style_"
    ))
    # SAHNE-07: Hedef Kitle Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_audience_selection, pattern="^audience_"
    ))
    # SAHNE-09: Seslendirme Dili Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_voice_language, pattern="^voicelang_"
    ))
    # SAHNE-10: Ses Karakter Seçimi callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_voice_character, pattern="^voicechar_"
    ))
    # SAHNE-11: Vurgulanacaklar — DEVAM önce gelmeli (spesifik pattern önce)
    app.add_handler(CallbackQueryHandler(
        handle_emphasis_done, pattern="^emphasis_done$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_emphasis, pattern="^emphasis_"
    ))
    # SAHNE-13: Senaryo Onay Formu callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_scenario_approve, pattern="^scenario_approve$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_scenario_reject, pattern="^scenario_reject$"
    ))
    # SAHNE-12: Brief Onay callback'leri (✅ ONAYLIYORUM / ✏️ DÜZELT)
    app.add_handler(CallbackQueryHandler(
        handle_brief_approve, pattern="^brief_approve$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_brief_edit, pattern="^brief_edit$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_brief_edit_field, pattern="^brief_edit_"
    ))
    # STATE_PRICING: Yönetici Fiyatlandırma callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_admin_pricing_submit, pattern="^admin_price_"
    ))
    # STATE_PRICING: Kullanıcı Fiyat Teklif + Ödeme callback'leri
    app.add_handler(CallbackQueryHandler(
        handle_pricing_approve, pattern="^pricing_approve$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_pricing_reject, pattern="^pricing_reject$"
    ))
    app.add_handler(CallbackQueryHandler(
        handle_payment_declared, pattern="^payment_declared$"
    ))

    # ── Message Handler (SE-007_3: State tabanlı yönlendirme) ──
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler,
    ))
    # Medya handler'ları (materyal yükleme için)
    app.add_handler(MessageHandler(
        filters.PHOTO,
        message_handler,
    ))
    app.add_handler(MessageHandler(
        filters.Document.ALL,
        message_handler,
    ))
    app.add_handler(MessageHandler(
        filters.VIDEO,
        message_handler,
    ))

    # ── Error Handler ──
    app.add_error_handler(error_handler)

    logger.info("✅ Bot handler'ları yüklendi")

    # Bot başlatılırken webhook'u sil ve pending updates'leri temizle
    async def post_init(application: Application):
        """Bot başladıktan sonra webhook'u sil + CONSTITUTIONAL BOOT."""
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🔄 Webhook silindi, pending updates temizlendi")

        # ════════════════════════════════════════════════════════════════
        # FAZ 0: CONSTITUTION CACHE MANAGER
        # ════════════════════════════════════════════════════════════════
        logger.info("=" * 50)
        logger.info("CONSTITUTIONAL BOOT SEQUENCE BAŞLADI")
        logger.info("=" * 50)

        # Constitution Cache tara — hash'le, önbellekle
        cache_status = constitution_cache.scan()
        logger.info(f"📚 [BOOT] Constitution Cache: {cache_status.summary}")

        # EEC: Constitution Scan başlangıç event'i
        if cache_status.new_files > 0 or cache_status.changed_files > 0:
            cscan_start = execution_event_collector.emit_event(
                event_type=EECEventType.CONSTITUTION_SCAN_STARTED,
                description=f"ANA YASA taraması: {cache_status.total_files} dosya",
                phase=ExecutionPhase.PRE_CHECK,
                result=f"Yeni:{cache_status.new_files} Değişen:{cache_status.changed_files}",
            )
            event_registry.register_from_eec(cscan_start)

        # ════════════════════════════════════════════════════════════════
        # FAZ 1: 18 KATMANLI CONSTITUTIONAL BOOT
        # ════════════════════════════════════════════════════════════════
        boot_manifest = constitution_cache.get_boot_manifest()
        booted_layers = 0
        for layer in boot_manifest:
            if layer["loaded"]:
                booted_layers += 1
                logger.info(
                    f"  ✅ [{layer['status'].upper()}] {layer['layer']} "
                    f"({layer['size_kb']:.0f}KB)"
                )
            else:
                logger.warning(
                    f"  ⚠️ [{layer['status'].upper()}] {layer['layer']} — YÜKLENEMEDİ"
                )

        logger.info(f"📋 [BOOT] {booted_layers}/{len(boot_manifest)} katman yüklendi")

        # Constitution Scan tamamlandı event'i
        cscan_done = execution_event_collector.emit_event(
            event_type=EECEventType.CONSTITUTION_SCAN_COMPLETED,
            description=f"Constitutional Boot tamamlandı: {booted_layers} katman",
            phase=ExecutionPhase.PRE_CHECK,
            result=f"{booted_layers}/{len(boot_manifest)} katman aktif",
        )
        event_registry.register_from_eec(cscan_done)

        # ════════════════════════════════════════════════════════════════
        # FAZ 2: CONSTITUTION_READY
        # ════════════════════════════════════════════════════════════════
        const_ready = cache_status.is_valid and booted_layers >= len(boot_manifest)
        if const_ready:
            logger.info("✅ [BOOT] CONSTITUTION_READY — tüm katmanlar aktif")
        else:
            logger.warning("⚠️ [BOOT] CONSTITUTION_DEGISIKLIK_VAR — eksik/değişmiş dosya var")

        # CEE FAZ-1: PRE-CHECK — bot oturumu için anayasal görev paketi
        ctp = constitution_enforcement.pre_check(
            task_description="HLK Bot polling session — Telegram reklam asistanı",
            affected_files=[
                "main.py", "handlers/start.py", "handlers/website.py",
                "handlers/cancel.py", "services/scene_engine.py",
                "services/scene_delivery.py", "services/research_orchestrator.py",
            ],
            master_rules=["MASTER-001", "MASTER-002", "MASTER-003"],
            arch_rules=["AR-002_28", "AR-002_36", "AR-002_44", "AR-002_60", "AR-002_61"],
            oper_rules=["OR-004_0", "OR-004_1", "OR-004_2"],
            flow_steps=["FD-008_1: SAHNE-01 → SAHNE-06"],
            state_rules=["SE-007_3", "SE-007_4", "SE-007_5", "SE-007_6"],
            expected_outputs=[
                "Bot polling'e başladı",
                "Tüm handler'lar yüklendi",
                "CEE ve EEC entegrasyonu tamam",
            ],
        )
        logger.info(f"📋 [CEE PRE-CHECK] CTP: {ctp.ctp_id}")

        # EEC: Bot başlangıç event'i
        execution_event_collector.listen(pid=f"BOT-{_os.getpid()}")
        bot_start_event = execution_event_collector.emit_event(
            event_type=EECEventType.TASK_STARTED,
            description="HLK Bot başlatıldı — polling aktif",
            phase=ExecutionPhase.PRE_CHECK,
            result="Bot aktif",
        )

        # Olay Kayıt Merkezi'ne kaydet
        event_registry.register_from_eec(bot_start_event)
        logger.info(f"📝 [EventRegistry] Bot başlangıç event'i kaydedildi: {bot_start_event.event_id}")
        logger.info("=" * 50)
        logger.info("CONSTITUTIONAL BOOT SEQUENCE TAMAMLANDI")
        logger.info("=" * 50)

    app.post_init = post_init

    # ══════════════════════════════════════════════════════════════════════
    # DEBUG: BOT STARTED — süreç başına 1 kez
    # ══════════════════════════════════════════════════════════════════════
    import threading as _threading
    import time as _time
    _now = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime())
    logger.info("=" * 50)
    logger.info("========== BOT STARTED ==========")
    logger.info(f"PID              = {_os.getpid()}")
    logger.info(f"Application ID   = {id(app)}")
    logger.info(f"Thread ID        = {_threading.get_ident()}")
    logger.info(f"Polling Started  = {_now}")
    logger.info("=" * 50)

    # ══════════════════════════════════════════════════════════════════════
    # MASTER-003 SENDMESSAGE TRACE — monkey-patch
    # ExtBot.send_message sınıf seviyesinde wrap edilir.
    # ══════════════════════════════════════════════════════════════════════
    import inspect as _inspect
    import traceback as _traceback
    _BotClass = app.bot.__class__
    _original_sm = _BotClass.send_message

    async def _traced_send_message(self, *args, **kwargs):
        _stack = _traceback.extract_stack(limit=16)[:-1]
        _caller = _stack[-1]
        _msg_text = kwargs.get('text', args[1] if len(args) > 1 else '?')[:120]
        logger.info("=" * 60)
        logger.info(f"SENDMESSAGE TRACE")
        logger.info(f"  Timestamp  = {_time.strftime('%H:%M:%S', _time.localtime())}")
        logger.info(f"  Mesaj      = {_msg_text}")
        logger.info(f"  Chat ID    = {kwargs.get('chat_id', args[0] if len(args) > 0 else '?')}")
        logger.info(f"  Dosya      = {_caller.filename}")
        logger.info(f"  Fonksiyon  = {_caller.name}")
        logger.info(f"  Satır      = {_caller.lineno}")
        for _f in _stack[-10:]:
            logger.info(f"    {_f.filename.split(chr(92))[-1]}:{_f.lineno} in {_f.name}")
        logger.info("=" * 60)
        return await _original_sm(self, *args, **kwargs)

    _BotClass.send_message = _traced_send_message
    logger.info("🔍 SENDMESSAGE TRACE monkey-patch aktif")

    logger.info("🚀 Bot polling başlıyor...")
    app.run_polling(
        poll_interval=2.0,
        timeout=30,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
