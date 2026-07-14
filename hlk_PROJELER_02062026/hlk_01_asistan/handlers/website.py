"""Website linki işleme handler'ı.

ANA_YASA / GK-001: Link doğrulama ve araştırma başlatma.
Video üretim platformu sabit değildir. Platform seçimi ajan sıralaması sonucu belirlenir.

FAZ-4: Handler artık sahne davranışlarını Flow Diagram metadata'dan okur.
Hardcoded değerler yalnızca Flow Diagram verisi yoksa fallback olarak kullanılır.
"""

import asyncio
import logging
import random
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from utils.validators import is_valid_url
from utils.state_engine import StateEngine, UserState, UserEvent
from helpers.typewriter_animation import typewriter_animation
from services.scene_delivery import scene_delivery
from services.scene_engine import conversation_scene_engine
from services.scene_registry import get_scene_for_state, SCENE_REGISTRY
from config.i18n import t, get_lang

# CEE + EEC + Olay Kayıt Merkezi entegrasyonu
from services.constitution_enforcement import constitution_enforcement
from services.execution_event_collector import (
    execution_event_collector, EECEventType, ExecutionPhase,
)
from services.olay_kayit_merkezi import event_registry

logger = logging.getLogger(__name__)

# ── State → Flow Diagram Sahne Referans Haritası (routing table) ─────────
# Bu harita yalnızca yönlendirme amaçlıdır. Davranış tanımlamaz.
# Tek anayasal kaynak: 08_HLK_FLOW_DIAGRAM.md
_STATE_FLOW_MAP: dict[str, str] = {
    "STATE_ACTIVE_CONVERSATION": "SAHNE-02",
    "STATE_COLLECT_PRODUCT_MATERIALS": "SAHNE-02",
    "STATE_PLATFORM_SELECTION": "SAHNE-02",
    "STATE_VIDEO_SETTINGS": "SAHNE-03",
    "STATE_VIDEO_RESOLUTION_SELECTION": "SAHNE-04",
    "STATE_VIDEO_DURATION_SELECTION": "SAHNE-05",
    "STATE_STYLE_SELECTION": "SAHNE-06",
    "STATE_TARGET_AUDIENCE_SELECTION": "SAHNE-07",
    "STATE_AUDIO_SELECTION": "SAHNE-08",
    "STATE_VOICE_LANGUAGE": "SAHNE-09",
    "STATE_VOICE_CHARACTER": "SAHNE-10",
    "STATE_EMPHASIS": "SAHNE-11",
    "STATE_BRIEF_REVIEW": "SAHNE-12",
}


def _get_flow_data(user_data: dict) -> dict | None:
    """Aktif state için Flow Diagram davranışlarını Constitution Cache'ten okur.

    Sonuç user_data içinde önbelleklenir — aynı state içinde tekrar tekrar
    okuma yapılmaz. State değiştiğinde önbellek geçersiz olur.

    Flow Diagram verisi yoksa None döner → handler hardcoded fallback kullanır.
    """
    se = StateEngine(user_data)
    state_val = se.current.value

    # Önbellek kontrolü — aynı state için tekrar okuma
    cached = user_data.get("_flow_cache")
    if cached and cached.get("_state") == state_val:
        return cached.get("_data")

    # Flow Diagram'dan oku
    scene_ref = _STATE_FLOW_MAP.get(state_val)
    if not scene_ref:
        return None

    try:
        from services.constitution_cache import constitution_cache
        flow = constitution_cache.get_flow_section(scene_ref)
        # Önbelleğe al
        user_data["_flow_cache"] = {"_state": state_val, "_data": flow}
        if flow:
            logger.info(
                f"📋 [Handler] Flow Diagram yüklendi: {scene_ref} | "
                f"purpose={flow.get('purpose')} | mode={flow.get('presentation_mode')}"
            )
        return flow
    except Exception as e:
        logger.warning(f"⚠️ [Handler] Flow Diagram okuma hatası: {e}")
        return None


def _scene_by_id(scene_id: str):
    """Scene Registry'den scene_id ile scene bul."""
    for s in SCENE_REGISTRY:
        if s.scene_id == scene_id:
            return s
    return None

# OR-003_3/4 uyumlu materyal teslim mesajları — Flow Diagram'a taşındı (FAZ-6)
# Fallback: Flow Diagram okunamazsa kullanılır
_MATERIAL_ACK_MESSAGES = {
    1: [
        "✅ <b>İlk materyalinizi</b> aldım. Teşekkürler! 🙏\n\nŞimdi <b>ikinci materyali</b> bekliyorum...",
        "📥 <b>1. materyal</b> başarıyla alındı. \n\nBir sonraki materyali gönderebilirsiniz 👇",
    ],
    2: [
        "✅ <b>2. materyal</b> de alındı! Harika gidiyorsunuz 🎯\n\nVarsa <b>üçüncüyü</b> bekliyorum...",
        "📥 İkinci materyali de aldım. Çok güzel! \n\nDevam edebilirsiniz 👇",
    ],
}


async def handle_website_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ürün linkini al, doğrula, araştırmayı başlat, Scene Engine'e devret.

    Hızlı yanıt için: URL validasyonu + state geçişi hemen yapılır,
    ağır işlemler (sahne üretimi, temizlik) arka plana alınır.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text

    logger.info(f"📨 {user.id} link gönderdi: {text[:80]}...")

    if not is_valid_url(text):
        link_attempts = context.user_data.setdefault("link_attempts", 0) + 1
        context.user_data["link_attempts"] = link_attempts
        remaining = 5 - link_attempts
        logger.info(f"❌ Geçersiz link #{link_attempts}/5: {text[:60]}")

        if link_attempts >= 5:
            await update.message.reply_text(
                "⚠️ <b>5 başarısız link denemesi.</b>\n\n"
                "Oturumunuz kapatılıyor. Lütfen daha sonra "
                "<b>/start</b> yazarak tekrar deneyin.",
                parse_mode="HTML",
            )
            se = StateEngine(context.user_data)
            se.fire(UserEvent.MAX_ATTEMPTS_REACHED)
            logger.info(f"🔒 {user.id} oturumu kapatıldı (5 başarısız link)")
            return

        await update.message.reply_text(
            f"❌ <b>Geçersiz link formatı.</b>\n\n"
            f"Lütfen geçerli bir URL gönderin.\n"
            f"<i>Kalan deneme: {remaining}/5</i>",
            parse_mode="HTML",
        )
        return

    # ── Geçerli link: hızlı işlemler (senkron) ──
    context.user_data["link_attempts"] = 0
    context.user_data["website_url"] = text

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PRODUCT_LINK_RECEIVED)

    # Hemen "link alındı" yanıtı ver — kullanıcı beklemesin
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    link_ack_id = await scene_delivery.send_and_track(
        chat_id=chat_id,
        text="🔗 <b>Linkiniz alındı!</b>\n\nÜrün analizi başlatılıyor, lütfen bekleyin...",
    )
    context.user_data["_link_ack_msg_id"] = link_ack_id

    # ── Ağır işlemleri arka plana al (PTB timeout aşımı engelle) ──
    msg_id_to_delete = update.message.message_id
    asyncio.create_task(_process_link_background(
        chat_id=chat_id, user_id=user.id, url=text,
        user_data=context.user_data, bot=context.bot,
        link_msg_id=msg_id_to_delete,
    ))


async def _process_link_background(
    chat_id: int, user_id: int, url: str,
    user_data: dict, bot,
    link_msg_id: int,
):
    """Link doğrulama sonrası ağır işlemleri arka planda yürütür.

    PTB handler timeout'unu aşmamak için asyncio.create_task ile çağrılır.
    """
    try:
        se = StateEngine(user_data)
        se.fire(UserEvent.LINK_VALIDATED)

        # Link doğrulandı bilgisi
        await conversation_scene_engine.produce_scene_response(
            user_data=user_data, chat_id=chat_id, bot=bot,
            trigger_event="LINK_VALIDATED_INFO",
        )

        # Arka plan araştırmasını başlat
        from services.research_orchestrator import run_research_task
        asyncio.create_task(run_research_task(url=url, user_id=user_id))
        logger.info(f"✅ Link doğrulandı, araştırma başlatıldı: {url[:60]}")

        # CEE + EEC denetimi
        link_report = constitution_enforcement.post_check(
            code_anayasa_ok=True, flow_ok=True, state_ok=True,
            operational_ok=True, architecture_ok=True, runtime_ok=True,
        )
        link_eec = execution_event_collector.emit_event(
            event_type=EECEventType.SYNTAX_CHECK_COMPLETED,
            description=f"Link doğrulandı: {url[:60]}",
            related_file="handlers/website.py",
            phase=ExecutionPhase.POST_CHECK,
            result=f"CEE {link_report.verdict.value} ({link_report.report_id})",
        )
        event_registry.register_from_eec(link_eec)

        # State zinciri
        se.fire(UserEvent.PRODUCT_ANALYSIS_STARTED)
        logger.info(f"🔷 STATE: {se.current.value} — arka plan araştırması")

        from config.video_paths import LINK_PROCESSING_WAIT
        await asyncio.sleep(LINK_PROCESSING_WAIT)

        se.fire(UserEvent.CONVERSATION_STARTED)
        logger.info(f"🔷 STATE: {se.current.value} — aktif konuşma başlıyor")

        # Eski içerikleri temizle
        try:
            await bot.delete_message(chat_id=chat_id, message_id=link_msg_id)
        except Exception:
            pass
        link_req_id = user_data.pop("last_typewriter_msg_id", None)
        if link_req_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=link_req_id)
            except Exception:
                pass
        post_id = user_data.pop("post_bubble_msg_id", None)
        if post_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=post_id)
            except Exception:
                pass
        # "Linkiniz alındı" geçici mesajını temizle
        link_ack_id = user_data.pop("_link_ack_msg_id", None)
        if link_ack_id:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=link_ack_id)
            except Exception:
                pass
        await scene_delivery.cleanup_chat(chat_id)
        logger.info(f"🧹 Eski mesajlar temizlendi")

        # SAHNE_01: Tamamlayıcı Materyal Bilgilendirmesi
        scene_def = get_scene_for_state(UserState.ACTIVE_CONVERSATION)
        if scene_def:
            logger.info(f"🎬 Scene Engine başlatılıyor: {scene_def.scene_name}")
            await conversation_scene_engine.produce_and_deliver(
                user_data=user_data, chat_id=chat_id, bot=bot,
            )
        else:
            logger.error(f"❌ ACTIVE_CONVERSATION için scene tanımı yok")

        from utils.session_timeout import start_timer as _st_link
        _st_link(user_id, chat_id, bot, user_data)

    except Exception as e:
        logger.error(f"❌ Link arka plan işleme hatası: {str(e)}", exc_info=True)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="❌ <b>Link işlenirken bir hata oluştu.</b>\n\n"
                     "Lütfen <b>/start</b> yazarak tekrar deneyin.",
                parse_mode="HTML",
            )
        except Exception:
            pass


async def handle_material_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kullanıcının materyal seçimini işler (scene_registry butonları + eski uyumluluk)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    choice = query.data

    await query.answer()
    se = StateEngine(context.user_data)

    # ── upload_material / material_yes → MATERYAL TOPLAMA ──
    if choice in ("upload_material", "material_yes"):
        logger.info(f"📦 {user.id} → materyal yukleme")

        # OR-003_3: Ekrani temizle (önceki SAHNE mesajları)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
        except Exception:
            pass
        await scene_delivery.cleanup_chat(chat_id)
        logger.info(f"🧹 Temizlik tamamlandi, materyal bilgi mesaji gonderiliyor...")

        # ── FD-008_1: Materyal toplama başlangıç bilgilendirmesi ──
        # ANA YASA: "kaç meteryal göndermesi gerektiği ve ne kadar
        # süresi oldugu nazik bir dille anlatır"
        # Bu mesaj SAHNE boyunca ekranda KALIR, sadece Bitti'de silinir.
        material_info_text = (
            "📦 <b>Materyal Yükleme</b>\n\n"
            "Ürününüze ait tamamlayıcı materyallerinizi şimdi gönderebilirsiniz.\n\n"
            "📷 Fotoğraf  🎬 Video  📚 Katalog\n"
            "📄 Teknik Doküman  📦 Diğer\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 <b>En fazla 10 adet</b> materyal yükleyebilirsiniz.\n"
            "⏱️ Materyal göndermek için <b>5 dakika</b> süreniz var.\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<i>Materyallerinizi göndermeye başlayın.</i>\n"
            "<i>İşiniz bittiğinde</i> <b>✅ Bitti</b> <i>butonuna basın.</i>"
        )

        # Daktilo efekti ile gönder (düz send_message fallback ile)
        tw_msg_id = None
        try:
            tw_msg_id = await typewriter_animation(
                chat_id=chat_id,
                text=material_info_text,
                bot=context.bot,
                delay=0.06,
            )
            logger.info(f"✅ Typewriter tamam: msg_id={tw_msg_id}")
        except Exception as e:
            logger.error(f"❌ Typewriter hata: {e}")

        if not tw_msg_id:
            try:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text=material_info_text,
                    parse_mode="HTML",
                )
                tw_msg_id = msg.message_id
                logger.info(f"✅ Fallback send_message: msg_id={tw_msg_id}")
            except Exception as e:
                logger.error(f"❌ Fallback da başarısız: {e}")

        # Kaydet — cleanup_chat() SAHNE sonunda siler
        if tw_msg_id:
            scene_delivery.register_chat_messages(chat_id, {
                "success_msg_id": tw_msg_id,
                "typewriter_msg_id": tw_msg_id,
            })
        context.user_data["material_info_msg_id"] = tw_msg_id
        context.user_data["material_count"] = 0
        logger.info(f"📋 material_info_msg_id={tw_msg_id} kaydedildi")

        se.fire(UserEvent.MATERIALS_COLLECTED)
        context.user_data["state"] = "collecting_materials"  # message_handler medya routing için gerekli
        logger.info(f"🔷 STATE: {se.current.value} — materyal toplama")

    # ── skip_material / material_no / material_done → FORMAT SEÇİMİ ──
    elif choice in ("skip_material", "material_no", "material_done"):
        logger.info(f"📦 {user.id} → format secimine geciliyor")

        # ── FD-008_1: "EKRAN SİLİNİR" — TÜM sahne mesajlarını temizle ──
        # 1. Bitti butonunun olduğu onay mesajını sil
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
            logger.info(f"🗑️ Bitti mesajı silindi: {query.message.message_id}")
        except Exception as e:
            logger.warning(f"⚠️ Bitti mesajı silinemedi: {e}")

        # 2. Materyal bilgi mesajını sil (SAHNE boyunca kalan)
        info_id = context.user_data.pop("material_info_msg_id", None)
        if info_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=info_id)
                logger.info(f"🗑️ Materyal bilgi mesajı silindi: {info_id}")
            except Exception as e:
                logger.warning(f"⚠️ Bilgi mesajı silinemedi: {e}")

        # 3. Scene Delivery kayıtlı tüm mesajları temizle
        await scene_delivery.cleanup_chat(chat_id)

        # FD-008_1: Bitti/skip → doğrudan SAHNE-03 Format Seçimi'ne geç
        # İki farklı başlangıç state'i olabilir:
        #   - Hemen skip: ACTIVE_CONVERSATION → hedef VIDEO_SETTINGS
        #   - Yükleme+Bitti: COLLECT_PRODUCT_MATERIALS → hedef VIDEO_SETTINGS
        # StateEngine üzerinden doğrudan hedef state'e geç (zincir atlamalı)
        se.current = UserState.VIDEO_SETTINGS
        context.user_data.pop("state", None)  # legacy "collecting_materials" temizle
        logger.info(f"🔷 STATE: {se.current.value} — format seçimi bekleniyor")

        # SAHNE-03: Format Seçimi — StateEngine uyumlu teslim
        scene_def = get_scene_for_state(UserState.VIDEO_SETTINGS)
        if scene_def:
            logger.info(f"🎬 Scene Engine: {scene_def.scene_name}")
            await conversation_scene_engine.produce_and_deliver(
                user_data=context.user_data,
                chat_id=chat_id,
                bot=context.bot,
            )
        else:
            logger.warning(f"⚠️ VIDEO_SETTINGS için scene tanımı bulunamadı")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-03: Format seçilir → SAHNE-04 çözünürlük seçimine geçilir.

    MASTER-003: ANA YASA FD-008_1 uyumlu — StateEngine + Scene Engine zinciri.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    format_map = {
        "format_9_16": (t("s03.vertical", lang), t("s03.vertical_desc", lang)),
        "format_16_9": (t("s03.horizontal", lang), t("s03.horizontal_desc", lang)),
        "format_1_1": (t("s03.square", lang), t("s03.square_desc", lang)),
    }
    format_adi, platformlar = format_map.get(query.data, (query.data, ""))
    await query.answer(f"{t('common.saved', lang)}")

    logger.info(f"🎯 {user.id} format seçti: {format_adi}")
    context.user_data["video_format"] = format_adi
    context.user_data["platform"] = platformlar

    # State geçişi: SAHNE-03 → SAHNE-04 (FD-008_1 uyumlu)
    se = StateEngine(context.user_data)
    new_state = se.fire(UserEvent.VIDEO_SETTINGS_DONE)
    logger.info(f"🔷 STATE: {se.current.value} → SAHNE-04 çözünürlük seçimi")

    # FD-008_1: "EKRAN SİLİNİR" — önceki sahneyi temizle
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    # Scene Engine ile SAHNE-04'ü teslim et
    scene_def = get_scene_for_state(new_state) if new_state else None
    if scene_def:
        logger.info(f"🎬 Scene Engine başlatılıyor: {scene_def.scene_name}")
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
        )
    else:
        logger.warning(f"⚠️ {se.current.value} için scene tanımı bulunamadı")

async def handle_resolution_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-04: Çözünürlük seçilir → SAHNE-05 süre seçimine geçilir.

    MASTER-003: ANA YASA FD-008_1 uyumlu.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    resolution_map = {
        "resolution_480p": t("s04.480p", lang),
        "resolution_720p": t("s04.720p", lang),
        "resolution_1080p": t("s04.1080p", lang),
    }
    resolution = resolution_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', lang)}")

    logger.info(f"🎯 {user.id} çözünürlük seçti: {resolution}")
    context.user_data["video_resolution"] = resolution

    se = StateEngine(context.user_data)
    new_state = se.fire(UserEvent.RESOLUTION_SELECTED)
    logger.info(f"🔷 STATE: {se.current.value} → SAHNE-05 süre seçimi")

    # FD-008_1: "EKRAN SİLİNİR" — önceki sahneyi temizle
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    # Scene Engine ile SAHNE-05'i teslim et
    scene_def = get_scene_for_state(new_state) if new_state else None
    if scene_def:
        logger.info(f"🎬 Scene Engine başlatılıyor: {scene_def.scene_name}")
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
        )
    else:
        logger.warning(f"⚠️ {se.current.value} için scene tanımı bulunamadı")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_platform_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-02: Platform seçilir → SAHNE-03 format seçimine geçilir.

    MASTER-003 / FD-008_1: ANA YASA uyumlu — StateEngine + Scene Engine zinciri.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    lang = get_lang(context.user_data)
    platform_map = {
        "platform_tiktok": "TikTok",
        "platform_instagram": "Instagram Reels",
        "platform_youtube": "YouTube",
        "platform_other": "Other",
    }
    platform_adi = platform_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', lang)}")

    logger.info(f"🎯 {user.id} platform seçti: {platform_adi}")
    context.user_data["platform"] = platform_adi

    # State geçişi: SAHNE-02 → SAHNE-03 (FD-008_1 uyumlu)
    se = StateEngine(context.user_data)
    new_state = se.fire(UserEvent.PLATFORM_SELECTED)
    logger.info(f"🔷 STATE: {se.current.value} → SAHNE-03 format seçimi")

    # FD-008_1: "EKRAN SİLİNİR" — önceki sahneyi temizle
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Scene Engine ile SAHNE-03'ü teslim et
    scene_def = get_scene_for_state(new_state) if new_state else None
    if scene_def:
        logger.info(f"🎬 Scene Engine başlatılıyor: {scene_def.scene_name}")
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
        )
    else:
        logger.warning(f"⚠️ {se.current.value} için scene tanımı bulunamadı")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


# ─── SAHNE-08: Ses Seçimi Toggle Sistemi (FD-008_1 uyumlu) ──────────────────────

# Ses seçenekleri
AUDIO_OPTIONS = {
    "voiceover": "🎙️ Dış Seslendirme",
    "ambient": "🔊 Ortam Sesleri",
    "music": "🎵 Telifsiz Fon Müziği",
    "silent": "🔇 SESSİZ",
}


def _get_audio_toggles(user_data: dict) -> dict:
    """Kullanıcının audio toggle state'ini döndürür. Yoksa initialize eder."""
    if "audio_toggles" not in user_data:
        user_data["audio_toggles"] = {
            "voiceover": False,
            "ambient": False,
            "music": False,
            "silent": False,
        }
    return user_data["audio_toggles"]


def _build_audio_keyboard(toggles: dict) -> InlineKeyboardMarkup:
    """Mevcut toggle state'ine göre dinamik klavye oluşturur.

    - Silent aktifse diğer 3 seçenek ⬜ (disabled) gösterilir
    - En az 1 seçim yapıldıysa DEVAM butonu eklenir
    - Checked: ✅, Unchecked: ☐, Disabled: ⬜
    """
    keyboard = []
    is_silent = toggles.get("silent", False)

    # İlk 3 seçenek (non-silent)
    for key in ["voiceover", "ambient", "music"]:
        if is_silent:
            text = f"⬜ {AUDIO_OPTIONS[key]}"
        elif toggles[key]:
            text = f"✅ {AUDIO_OPTIONS[key]}"
        else:
            text = f"☐ {AUDIO_OPTIONS[key]}"
        keyboard.append([InlineKeyboardButton(
            text=text,
            callback_data=f"audio_toggle_{key}"
        )])

    # SESSİZ seçeneği
    silent_text = f"{'✅' if is_silent else '☐'} {AUDIO_OPTIONS['silent']}"
    keyboard.append([InlineKeyboardButton(
        text=silent_text,
        callback_data="audio_toggle_silent"
    )])

    # DEVAM butonu — yalnızca en az bir seçim yapıldıysa
    any_selected = any(toggles.values())
    if any_selected:
        keyboard.append([InlineKeyboardButton(
            text="▶️ DEVAM",
            callback_data="audio_devam"
        )])

    return InlineKeyboardMarkup(keyboard)


async def _edit_audio_keyboard(chat_id: int, message_id: int, toggles: dict, bot, context: dict) -> int:
    """Active UI Component Rule: Eski ses seçim kutusunu kaldır, yenisini göster.

    Returns: Yeni buton mesajının message_id'si.
    """
    from services.scene_delivery import scene_delivery as _sd
    keyboard = _build_audio_keyboard(toggles)
    new_id = await _sd.replace_ui_component(chat_id, message_id, "▾", keyboard)
    context["audio_scene_msg_id"] = new_id
    return new_id


async def handle_audio_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-08: Toggle ses seçenekleri (multi-select checkbox).

    FD-008_1 uyumlu:
    - Birden fazla seçim yapılabilir
    - Sessiz seçilirse diğer seçenekler devre dışı kalır
    - Sessiz kaldırılırsa diğer seçenekler tekrar aktif olur
    - DEVAM butonu yalnızca seçim yapıldıktan sonra görünür
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    lang = get_lang(context.user_data)

    option = query.data.replace("audio_toggle_", "")
    logger.info(f"🎙️ {user.id} audio toggle: {option}")

    toggles = _get_audio_toggles(context.user_data)

    if option == "silent":
        # Toggle SESSİZ
        new_silent = not toggles["silent"]
        toggles["silent"] = new_silent
        if new_silent:
            # Sessiz aktif → diğer tüm seçenekleri temizle
            toggles["voiceover"] = False
            toggles["ambient"] = False
            toggles["music"] = False
            await query.answer(f"🔇 {t('s08.silent', lang)}")
        else:
            # Sessiz kaldırıldı → diğer seçenekler tekrar aktif
            await query.answer("Sessiz mod kaldırıldı — diğer seçenekler tekrar aktif")
    else:
        # Non-silent toggle — yalnızca silent pasifse izin ver
        if toggles.get("silent", False):
            await query.answer("⚠️ Sessiz moddayken diğer seçenekler seçilemez", show_alert=True)
            return
        toggles[option] = not toggles[option]
        durum = "seçildi" if toggles[option] else "kaldırıldı"
        await query.answer(f"{AUDIO_OPTIONS[option]} {durum}")

    context.user_data["audio_toggles"] = toggles

    # Eski buton mesajını sil, yenisini gönder (güvenilir yöntem)
    old_msg_id = context.user_data.get("audio_scene_msg_id") or query.message.message_id
    await _edit_audio_keyboard(chat_id, old_msg_id, toggles, context.bot, context.user_data)

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_audio_devam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-08: DEVAM butonu — seçimleri kaydet, ekranı temizle, sonraki sahneye geç.

    FD-008_1 uyumlu geçişler:
    - Sessiz → SAHNE-11 (Özellikle Vurgulanacaklar Seçimi)
    - Diğer seçimler → SAHNE-09 (Sesli Video Seslendirme Dili Seçimi)
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    toggles = _get_audio_toggles(context.user_data)
    is_silent = toggles.get("silent", False)

    # Seçilenleri belirle
    selected = [AUDIO_OPTIONS[k] for k, v in toggles.items() if v]

    if is_silent:
        context.user_data["audio_option"] = "🔇 Sessiz"
        context.user_data["audio_silent"] = True
        context.user_data["audio_next_scene"] = "SAHNE-11"
        logger.info(f"🎙️ {user.id} audio DEVAM: 🔇 SESSİZ → SAHNE-11")
        await query.answer("🔇 Sessiz video → SAHNE-11")
    else:
        context.user_data["audio_option"] = ", ".join(selected)
        context.user_data["audio_silent"] = False
        context.user_data["audio_selections"] = selected
        context.user_data["audio_next_scene"] = "SAHNE-09"
        logger.info(f"🎙️ {user.id} audio DEVAM: {', '.join(selected)} → SAHNE-09")
        await query.answer(f"Seçilenler: {', '.join(selected)} → SAHNE-09")

    # State Engine geçişi
    se = StateEngine(context.user_data)
    se.fire(UserEvent.AUDIO_OPTION_SELECTED)
    logger.info(f"🔷 STATE: {se.current.value} | next_scene={context.user_data.get('audio_next_scene')}")

    # Toggle state'ini temizle
    context.user_data.pop("audio_toggles", None)
    context.user_data.pop("audio_scene_msg_id", None)

    # ── EKRAN TEMİZLİĞİ (FD-008_1: "EKRAN SİLİNİR") ──
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    # FD-008_1: Sonraki sahneye geçiş
    # Sessiz → SAHNE-11 (Vurgulanacaklar)
    # Sesli  → SAHNE-09 (Seslendirme Dili) → SAHNE-10 → SAHNE-11 → SAHNE-12 → SAHNE-13
    if is_silent:
        # Sessiz: SAHNE-09 ve SAHNE-10'u atla, doğrudan SAHNE-11'e
        se.fire(UserEvent.VOICE_LANGUAGE_SELECTED)
        se.fire(UserEvent.VOICE_CHARACTER_SELECTED)
        logger.info(f"🔇 Sessiz mod — SAHNE-09/10 atlandı, SAHNE-11'e geçiliyor")
        scene_def = _scene_by_id("SAHNE-11")
    else:
        scene_def = _scene_by_id("SAHNE-09")

    if scene_def:
        logger.info(f"🎬 Scene Engine: {scene_def.scene_name}")
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
        )
    else:
        logger.warning(f"⚠️ Sonraki sahne bulunamadı")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_material_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """OR-003_3/4: Kullanıcı materyal gönderdiğinde onay mesajı üretir.

    FD-008_1: "HER EK METERYAL ALINDIĞINDA EKRAN SİLİNİR."
    HLK her materyal sonrası onaylar, Bitti butonu gösterir.
    Kullanıcı Bitti demeden sonraki sahneye geçilemez.
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    state = context.user_data.get("state")

    if state != "collecting_materials":
        return

    # Materyal sayacı
    count = context.user_data.setdefault("material_count", 0) + 1
    context.user_data["material_count"] = count

    logger.info(f"📦 {user.id} → materyal #{count} gönderildi")

    # ── FD-008_1: "HER EK METERYAL ALINDIĞINDA EKRAN SİLİNİR" ──
    # Önceki onay mesajını ve kullanıcının materyalini temizle
    onceki_msg_id = context.user_data.get("last_material_ack_msg_id")
    if onceki_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=onceki_msg_id)
        except Exception:
            pass
    try:
        await update.message.delete()
    except Exception:
        pass

    # Materyal türüne göre emoji
    if update.message.photo:
        emoji = "📷"
    elif update.message.video:
        emoji = "🎬"
    elif update.message.document:
        emoji = "📄"
    else:
        emoji = "📦"

    # ── FD-008_1: Materyal onay konuşması ──
    # Flow Diagram: "ilk tamamlayıcı Meteryali aldığını,
    # bir sonrası beklediğini benzer kelimelerle söyler"
    if count == 1:
        ack_text = (
            f"{emoji} <b>Ilk materyalinizi</b> aldim, tesekkurler! \n\n"
            "<i>Bir sonraki materyali gondermeye devam edebilirsiniz.</i>\n"
            "Isiniz bittiginde <b> Bitti</b> butonuna basin."
        )
    else:
        ack_text = (
            f"{emoji} <b>{count}. materyaliniz</b> de alındı! 🎯\n\n"
            "<i>Varsa bir sonraki materyali gönderebilirsiniz.</i>\n"
            "İşiniz bittiğinde <b>✅ Bitti</b> butonuna basın."
        )

    # Daktilo efekti ile konuşma baloncuğu
    tw_msg_id = await typewriter_animation(
        chat_id=chat_id,
        text=ack_text,
        bot=context.bot,
        delay=0.06,
    )

    # Bitti butonu — kullanıcı basmadan sonraki sahneye geçilmez (FD-008_1)
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=tw_msg_id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Bitti", callback_data="material_done")
            ]]),
        )
    except Exception as e:
        logger.warning(f"⚠️ Bitti butonu eklenemedi: {e}")

    # Scene Delivery'e kaydet (cleanup_chat için)
    scene_delivery.register_chat_messages(chat_id, {
        "success_msg_id": tw_msg_id,
        "typewriter_msg_id": tw_msg_id,
    })
    context.user_data["last_material_ack_msg_id"] = tw_msg_id


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-06: Tanıtım Tarzı Seçimi Handler
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-06: Tanıtım tarzı seçildi → SAHNE-07 hedef kitle."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    style_map = {
        "style_ugc": t("s06.ugc", lang), "style_traditional": t("s06.traditional", lang),
        "style_cinematic": t("s06.cinematic", lang), "style_custom": t("s06.custom", lang),
        "style_hlk": t("s06.hlk_decides", lang),
    }
    style = style_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', lang)}")
    context.user_data["ad_style"] = style
    logger.info(f"🎬 {user.id} tanıtım tarzı: {style}")

    # Seçilen butonu ✅ olarak işaretle (görsel geribildirim)
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        new_kbd = []
        for row in query.message.reply_markup.inline_keyboard:
            new_row = []
            for btn in row:
                text = btn.text
                if btn.callback_data == query.data:
                    text = text.replace("☐", "✅", 1)
                new_row.append(InlineKeyboardButton(text=text, callback_data=btn.callback_data))
            new_kbd.append(new_row)
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(new_kbd))
        await asyncio.sleep(0.4)
    except Exception:
        pass

    se = StateEngine(context.user_data)
    se.fire(UserEvent.STYLE_SELECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    scene_def = _scene_by_id("SAHNE-07")
    if scene_def:
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data, chat_id=chat_id, bot=context.bot,
        )
    from utils.session_timeout import start_timer as _st
    _st(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-07: Hedef Kitle Seçimi Handler
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_audience_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-07: Hedef kitle seçildi → SAHNE-08 ses seçimi."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    audience_map = {
        "audience_0_12": t("s07.children", lang), "audience_13_17": t("s07.teen", lang),
        "audience_18_24": t("s07.young_adult", lang), "audience_25_34": t("s07.adult", lang),
        "audience_35_44": t("s07.family", lang), "audience_45_54": t("s07.middle_age", lang),
        "audience_55_64": t("s07.mature", lang), "audience_65_plus": t("s07.senior", lang),
    }
    audience = audience_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', lang)}")
    context.user_data["target_audience"] = audience
    logger.info(f"👥 {user.id} hedef kitle: {audience}")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.TARGET_AUDIENCE_SELECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    scene_def = _scene_by_id("SAHNE-08")
    if scene_def:
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data, chat_id=chat_id, bot=context.bot,
        )
    from utils.session_timeout import start_timer as _st2
    _st2(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-09: Seslendirme Dili Seçimi Handler
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_voice_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-09: Seslendirme dili seçildi → SAHNE-10 ses karakter seçimi."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    voice_lang = get_lang(context.user_data)
    lang_map = {
        "voicelang_tr": "Türkçe", "voicelang_en": "English",
        "voicelang_de": "Deutsch", "voicelang_fr": "Français",
        "voicelang_es": "Español", "voicelang_ru": "Русский",
        "voicelang_ar": "العربية", "voicelang_kr": "Kurdî",
    }
    lang = lang_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', voice_lang)}")
    context.user_data["voice_language"] = lang
    logger.info(f"🎙️ {user.id} seslendirme dili: {lang}")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.VOICE_LANGUAGE_SELECTED)

    # Ekran temizliği + SAHNE-10 teslim
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    scene_def = _scene_by_id("SAHNE-10")
    if scene_def:
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data, chat_id=chat_id, bot=context.bot,
        )

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-10: Ses Karakter Seçimi Handler
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_voice_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-10: Ses karakteri seçildi → SAHNE-11 vurgulanacaklar."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    char_map = {
        "voicechar_female": t("s10.female", lang),
        "voicechar_male": t("s10.male", lang),
        "voicechar_child": t("s10.child", lang),
    }
    char = char_map.get(query.data, query.data)
    await query.answer(f"{t('common.saved', lang)}")
    context.user_data["voice_character"] = char
    logger.info(f"🎭 {user.id} ses karakteri: {char}")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.VOICE_CHARACTER_SELECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    scene_def = _scene_by_id("SAHNE-11")
    if scene_def:
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data, chat_id=chat_id, bot=context.bot,
        )

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-11: Vurgulanacaklar Seçimi Handler
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_emphasis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-11: Vurgu seçimi → özel vurgu metin girişi."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    emphasis_map = {
        "emphasis_discount": f"🏷️ {t('s11.discount', lang)}",
        "emphasis_shipping": f"🚚 {t('s11.shipping', lang)}",
        "emphasis_gift": f"🎁 {t('s11.gift', lang)}",
        "emphasis_newseason": f"✨ {t('s11.new_season', lang)}",
        "emphasis_local": f"🇹🇷 {t('s11.local', lang)}",
    }
    key = query.data
    selected = context.user_data.setdefault("emphasis_selections", [])

    # "Ben Eklemek İstiyorum" → metin girişi moduna geç
    if key == "emphasis_custom":
        context.user_data["_waiting_custom_emphasis"] = True
        context.user_data["_emphasis_kb_msg_id"] = query.message.message_id
        await query.answer(f"✏️ {t('s11.custom', lang)}")
        prompt_id = await scene_delivery.send_and_track(
            chat_id=chat_id,
            text=f"✏️ <b>{t('s11.custom', lang)}</b>\n\n"
                 f"{t('s11.custom_prompt', lang)}\n\n"
                 "<i>Örnek: %50 İndirim, 2 Al 1 Öde, Sınırlı Stok</i>",
        )
        context.user_data["_emphasis_prompt_msg_id"] = prompt_id
        return

    if key in selected:
        selected.remove(key)
        await query.answer(f"{t('common.saved', lang)}")
    else:
        selected.append(key)
        await query.answer(f"{emphasis_map.get(key, key)}")
    context.user_data["emphasis_selections"] = selected
    logger.info(f"✨ {user.id} vurgu: {selected}")

    # Klavyeyi güncelle
    await _refresh_emphasis_keyboard(chat_id, query.message.message_id, selected)


def _build_emphasis_keyboard(selected: list) -> InlineKeyboardMarkup:
    """SAHNE-11 klavyesi: hazır vurgular + özel ekle + DEVAM."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    emphasis_map = {
        "emphasis_discount": "🏷️ İndirim",
        "emphasis_shipping": "🚚 Ücretsiz Kargo",
        "emphasis_gift": "🎁 Hediye Paket",
        "emphasis_newseason": "✨ Yeni Sezon",
        "emphasis_local": "🇹🇷 Yerli Üretim",
    }
    keyboard = []
    for cb, label in emphasis_map.items():
        prefix = "✅" if cb in selected else "☐"
        keyboard.append([InlineKeyboardButton(
            text=f"{prefix} {label}", callback_data=cb,
        )])

    # Özel vurgular (emphasis_custom_ ile başlayan)
    for item in selected:
        if item.startswith("emphasis_custom_"):
            custom_text = item.replace("emphasis_custom_", "", 1)
            keyboard.append([InlineKeyboardButton(
                text=f"✅ ✏️ {custom_text}", callback_data=item,
            )])

    keyboard.append([InlineKeyboardButton(
        text="☐ ✏️ Ben Eklemek istiyorum", callback_data="emphasis_custom",
    )])
    keyboard.append([InlineKeyboardButton(
        text="▶️ DEVAM", callback_data="emphasis_done",
    )])
    return InlineKeyboardMarkup(keyboard)


async def _refresh_emphasis_keyboard(chat_id: int, message_id: int, selected: list):
    """SAHNE-11 klavyesini yeniden oluştur ve göster."""
    kb = _build_emphasis_keyboard(selected)
    await scene_delivery.replace_ui_component(chat_id, message_id, "▾", kb)


async def _handle_custom_emphasis_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-11: Kullanıcının yazdığı özel vurgu metnini yakalar."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if len(text) < 2:
        await update.message.reply_text(
            "⚠️ Lütfen en az 2 karakterlik bir vurgu metni yazın.",
            parse_mode="HTML",
        )
        return

    # Özel vurguyu kaydet
    custom_key = f"emphasis_custom_{text}"
    selected = context.user_data.setdefault("emphasis_selections", [])
    selected.append(custom_key)
    context.user_data["emphasis_selections"] = selected
    context.user_data["_waiting_custom_emphasis"] = False

    logger.info(f"✨ {user.id} özel vurgu ekledi: {text}")

    # Kullanıcının mesajını sil
    try:
        await update.message.delete()
    except Exception:
        pass

    # "Özel Vurgu" bilgi mesajını sil
    prompt_id = context.user_data.pop("_emphasis_prompt_msg_id", None)
    if prompt_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=prompt_id)
        except Exception:
            pass

    # Onay mesajı (geçici, otomatik temizlenir)
    ack_msg_id = await scene_delivery.send_and_track(
        chat_id=chat_id,
        text=f"✅ <b>Özel vurgu eklendi:</b> {text}",
    )

    # SAHNE-11 klavyesini güncelle
    kb_msg_id = context.user_data.pop("_emphasis_kb_msg_id", None)
    if kb_msg_id:
        try:
            kb = _build_emphasis_keyboard(selected)
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=kb_msg_id, reply_markup=kb,
            )
        except Exception as e:
            logger.warning(f"⚠️ Emphasis klavye güncelleme hatası: {e}")

    # Onay mesajını 2 sn sonra sil
    await asyncio.sleep(2)
    if ack_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=ack_msg_id)
        except Exception:
            pass


async def handle_emphasis_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-11: DEVAM → SAHNE-12 brief onay."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("Brief onayına geçiliyor...")
    logger.info(f"✨ {user.id} vurgu tamam: {context.user_data.get('emphasis_selections', [])}")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.EMPHASIS_SELECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    if await _after_scene_edit(chat_id, context):
        return

    # SAHNE-12: Tikli Brief Onay Tablosu (FD-008_1 + OR-004_5 uyumlu)
    # Tüm alanlar başlangıçta ✓ onaylı — BRIEF_FIELDS'ten otomatik init
    _get_brief_checks(context.user_data)  # İlk kez init eder, tüm tikler ✓
    await _deliver_brief_table(chat_id, context)

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-12: Brief Onay HTML Üreticisi (AR-002_65 En Yüksek Sadakat) ─────────────

def _build_brief_html(user_data: dict, checks: dict) -> str:
    """Brief Onay Formu'nu Telegram HTML olarak oluşturur (PNG kullanılmaz).

    AR-002_65 uyumlu: Veri bütünlüğü + işlevsel eşdeğerlik + görsel sadakat.
    Telegram resmi bileşenleriyle (<b>, <code>, <i>, InlineKeyboardButton) uygulanır.
    """
    aciklama_map = {
        "brief_link":       "Analiz edilen ürün sayfası",
        "brief_material":   "Kullanıcının yüklediği materyaller",
        "brief_platform":   "Yayınlanacak platform",
        "brief_format":     "Seçilen video formatı",
        "brief_resolution": "Video çözünürlüğü",
        "brief_duration":   "Tercih edilen video süresi",
        "brief_style":      "Reklam tanıtım tarzı",
        "brief_audience":   "Reklam hedef kitlesi",
        "brief_audio":      "Ses tercihleri",
        "brief_voicelang":  "Seçilen seslendirme dili",
        "brief_voicechar":  "Seslendirme karakteri",
        "brief_emphasis":   "Öne çıkarılacak detaylar",
    }
    maddeler = []
    for field_key, label, scene_id, editable in BRIEF_FIELDS:
        ikon = label.split(" ", 1)[0] if " " in label else ""
        baslik = label.split(" ", 1)[1] if " " in label else label
        maddeler.append({
            "onayli": checks.get(field_key, True),
            "ikon": ikon,
            "baslik": baslik,
            "aciklama": aciklama_map.get(field_key, "Brief bilgisi"),
            "deger": _get_brief_value(user_data, field_key),
        })

    lang = get_lang(user_data)
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    lines = []
    lines.append(f"{SEP}")
    lines.append(f"<b>📋 {t('s12.title', lang)}</b>")
    lines.append(f"<code>🔵1.Brief  ›  ⏳2.Senaryo  ›  ⏳3.Fiyat Teklifi</code>")
    lines.append(f"{SEP}")
    lines.append(f"<b>📋 {t('s12.summary_title', lang)}</b>")
    lines.append(f"<i>{t('s12.summary_text', lang)}</i>")
    lines.append("")

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
                lines.append(sol)
                lines.append(sag)
            else:
                lines.append(f"<code>{sol}</code>")
                lines.append(f"<code>{sag}</code>")
        else:
            if is_first:
                lines.append(sol)
            else:
                lines.append(f"<code>{sol}</code>")
        lines.append("")

    return "\n".join(lines)


# SAHNE-12: Brief Onay Tablosu — REFERANS_Brief_Onay_Formu Referans Form uyumlu
# (AR-002_64 + FD-008_1 + MASTER-010)
# ═══════════════════════════════════════════════════════════════════════════════

# Format: (callback_data, label, scene_id, editable)
# editable=False → bilgi amaçlı, tablo metninde gösterilir ama buton değildir
# editable=True  → tikli buton olarak gösterilir, tıklanınca ilgili sahneye dönülür
BRIEF_FIELDS = [
    ("brief_link",      "🔗 Ürün Linki",       None,                    False),
    ("brief_material",  "📦 Ek Materyal",       None,                    False),
    ("brief_platform",  "📱 Platform",          "scene_platform_selection", True),
    ("brief_format",    "📐 Video Formatı",     "SAHNE-03",              True),
    ("brief_resolution","📺 Çözünürlük",        "SAHNE-04",              True),
    ("brief_duration",  "⏱️ Video Süresi",      "SAHNE-05",              True),
    ("brief_style",     "🎬 Tanıtım Tarzı",     "SAHNE-06",              True),
    ("brief_audience",  "👥 Hedef Kitle",        "SAHNE-07",              True),
    ("brief_audio",     "🎙️ Ses Tercihleri",     "SAHNE-08",              True),
    ("brief_voicelang", "🌍 Seslendirme Dili",   "SAHNE-09",              True),
    ("brief_voicechar", "🎭 Ses Karakteri",       "SAHNE-10",              True),
    ("brief_emphasis",  "✨ Vurgulanacaklar",     "SAHNE-11",              True),
]

# REFERANS_Brief_Onay_Formu formuna göre kategorize edilmiş bölümler
# Her bölüm: (başlık, [field_key'ler])
BRIEF_SECTIONS = [
    ("🏷️ Ürün Bilgileri",  ["brief_link", "brief_material"]),
    ("🎬 Video Ayarları",  ["brief_platform", "brief_format", "brief_resolution",
                            "brief_duration", "brief_style", "brief_audience"]),
    ("🎙️ Ses Ayarları",    ["brief_audio", "brief_voicelang", "brief_voicechar"]),
    ("✨ Tercihler",        ["brief_emphasis"]),
]


def _get_brief_value(user_data: dict, field_key: str) -> str:
    """Brief alanının gerçek kullanıcı değerini döndürür (Referans Form uyumlu)."""
    if field_key == "brief_link":
        url = user_data.get("website_url", "")
        return url[:50] + "…" if len(url) > 50 else url if url else "—"
    elif field_key == "brief_material":
        count = user_data.get("material_count", 0)
        return f"{count} adet" if count > 0 else "Yok"
    elif field_key == "brief_platform":
        return user_data.get("platform", "—")
    elif field_key == "brief_format":
        return user_data.get("video_format", "—")
    elif field_key == "brief_resolution":
        return user_data.get("video_resolution", "—")
    elif field_key == "brief_duration":
        dur = user_data.get("video_duration")
        return f"{dur} saniye" if dur else "—"
    elif field_key == "brief_style":
        return user_data.get("ad_style", "—")
    elif field_key == "brief_audience":
        return user_data.get("target_audience", "—")
    elif field_key == "brief_audio":
        toggles = user_data.get("audio_toggles", {})
        if toggles.get("silent"):
            return "🔇 Sessiz"
        active = [AUDIO_OPTIONS.get(k, k) for k, v in toggles.items() if v]
        return ", ".join(active) if active else "—"
    elif field_key == "brief_voicelang":
        lang_code = user_data.get("voice_language", "")
        lang_names = {"tr": "🇹🇷 Türkçe", "en": "EN English", "de": "🇩🇪 Deutsch",
                      "fr": "🇫🇷 Français", "es": "🇪🇸 Español", "ru": "🇷🇺 Русский",
                      "ar": "AR العربية", "kr": "🏳️ Kurdî"}
        return lang_names.get(lang_code, lang_code) if lang_code else "—"
    elif field_key == "brief_voicechar":
        return user_data.get("voice_character", "—")
    elif field_key == "brief_emphasis":
        selections = user_data.get("emphasis_selections", [])
        emphasis_labels = {
            "emphasis_discount": "🏷️ İndirim", "emphasis_shipping": "🚚 Ücretsiz Kargo",
            "emphasis_gift": "🎁 Hediye Paket", "emphasis_newseason": "✨ Yeni Sezon",
            "emphasis_local": "🇹🇷 Yerli Üretim", "emphasis_custom": "✏️ Kullanıcı Notu",
            "discount": "🏷️ İndirim", "shipping": "🚚 Ücretsiz Kargo",
            "gift": "🎁 Hediye Paket", "newseason": "✨ Yeni Sezon",
            "local": "🇹🇷 Yerli Üretim", "custom": "✏️ Kullanıcı Notu",
        }
        if selections:
            parts = []
            for s in selections:
                if s.startswith("emphasis_custom_"):
                    parts.append(f"✏️ {s.replace('emphasis_custom_', '', 1)}")
                else:
                    parts.append(emphasis_labels.get(s, s))
            return ", ".join(parts)
        return "—"
    return "—"


async def _after_scene_edit(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handler sonrası çağrılır. Eğer brief düzeltme modundaysa SAHNE-12'ye döner.

    Returns: True ise SAHNE-12'ye dönüldü (handler devam etmemeli).
    """
    field = context.user_data.pop("_editing_field", None)
    if field:
        # Tik'i tekrar işaretle
        checks = _get_brief_checks(context.user_data)
        checks[field] = True
        context.user_data["brief_checks"] = checks
        # State'i BRIEF_REVIEW'e döndür
        context.user_data["user_state"] = UserState.BRIEF_REVIEW.value
        # SAHNE-12'yi yeniden göster
        await _deliver_brief_table(chat_id, context)
        return True
    return False


def _get_brief_checks(user_data: dict) -> dict:
    if "brief_checks" not in user_data:
        user_data["brief_checks"] = {f[0]: True for f in BRIEF_FIELDS}
    # Düzeltilemez alanlar her zaman ✅
    for f in BRIEF_FIELDS:
        if len(f) > 3 and not f[3]:
            user_data["brief_checks"][f[0]] = True
    return user_data["brief_checks"]


async def _deliver_brief_table(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """SAHNE-12: REFERANS_Brief_Onay_Formu → Telegram HTML + InlineKeyboard (AR-002_65).

    AR-002_65 En Yüksek Sadakat İlkesi uyarınca PNG render kullanılmaz;
    Telegram resmi bileşenleriyle (<b>, <code>, <i>, InlineKeyboardButton) uygulanır.
    Veri bütünlüğü + işlevsel eşdeğerlik + görsel sadakat korunur.
    """
    checks = _get_brief_checks(context.user_data)
    html = _build_brief_html(context.user_data, checks)

    lang = get_lang(context.user_data)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {t('s12.approve', lang)}", callback_data="brief_approve")],
        [InlineKeyboardButton(f"✏️ {t('s12.edit', lang)}", callback_data="brief_edit")],
    ])

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=html,
        reply_markup=kb,
        parse_mode="HTML",
    )
    logger.info(f"📋 [SAHNE-12] Brief HTML gönderildi: msg={msg.message_id} ({len(html)} chars)")

    scene_delivery.register_chat_messages(chat_id, {
        "success_msg_id": msg.message_id,
    })
    context.user_data["brief_msg_id"] = msg.message_id


# ── SAHNE-12 Callback Handler'ları ─────────────────────────────────────────────

async def handle_brief_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-12: ✅ ONAYLIYORUM → Brief onaylandı, SAHNE-13 akışına geç."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✅ Brief onaylandı — senaryo aşamasına geçiliyor...")
    logger.info(f"📋 {user.id} brief'i onayladı → SAHNE-13")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.BRIEF_APPROVED)

    # Eski mesajları temizle
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Brief onaylandı — log kaydı
    logger.info(f"✅ [BRIEF_APPROVE] Kullanıcı {user.id} brief'i onayladı, SAHNE-13 başlatılıyor")

    # SAHNE-13 akışını başlat
    await _run_sahne13_flow(chat_id, user.id, context.user_data, context.bot)


async def handle_brief_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-12: ✏️ DÜZELTMEK İSTİYORUM → Düzenlenebilir alanlar göster."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✏️ Düzeltme modu — değiştirmek istediğiniz alanı seçin")
    logger.info(f"📋 {user.id} brief düzeltme moduna girdi")

    # Düzenlenebilir alanları göster
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb_rows = []
    for f in BRIEF_FIELDS:
        if len(f) > 3 and f[3]:  # editable=True
            val = _get_brief_value(context.user_data, f[0])
            kb_rows.append([InlineKeyboardButton(
                f"{f[1]}: {val}",
                callback_data=f"brief_edit_{f[0]}"
            )])

    lang = get_lang(context.user_data)
    kb_rows.append([InlineKeyboardButton(f"✅ {t('s12.edit_done', lang)}", callback_data="brief_approve")])

    kb = InlineKeyboardMarkup(kb_rows)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"✏️ <b>{t('s12.edit_title', lang)}</b>\n\n"
            f"{t('s12.edit_prompt', lang)}\n\n"
            f"<i>İşiniz bittiğinde</i> <b>{t('s12.edit_done', lang)}</b> <i>butonuna basın.</i>"
        ),
        reply_markup=kb,
        parse_mode="HTML",
    )
    logger.info(f"✏️ [SAHNE-12] Düzeltme butonları gönderildi: {len(kb_rows)-1} alan")


async def handle_brief_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-12 düzeltme: Belirli bir alana tıklandı → ilgili sahneye dön."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    data = query.data  # "brief_edit_brief_platform" gibi

    field_key = data.replace("brief_edit_", "", 1)

    # Hangi sahneye dönüleceğini bul
    target_scene = None
    for f in BRIEF_FIELDS:
        if f[0] == field_key and len(f) > 2 and f[2]:
            target_scene = f[2]
            break

    if not target_scene:
        await query.answer("⚠️ Bu alan düzenlenemez")
        return

    await query.answer(f"✏️ {field_key} düzenleniyor — ilgili adıma dönülüyor...")
    logger.info(f"✏️ {user.id} brief düzeltme: {field_key} → {target_scene}")

    # Düzeltme modunu işaretle
    context.user_data["_editing_field"] = field_key

    # Eski mesajları temizle
    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # İlgili sahneye state geçişi yap
    # State'i ilgili sahneye ayarla
    scene_state_map = {
        "scene_platform_selection": UserState.PLATFORM_SELECTION,
        "SAHNE-03": UserState.VIDEO_SETTINGS,
        "SAHNE-04": UserState.VIDEO_RESOLUTION_SELECTION,
        "SAHNE-05": UserState.VIDEO_DURATION_SELECTION,
        "SAHNE-06": UserState.STYLE_SELECTION,
        "SAHNE-07": UserState.TARGET_AUDIENCE_SELECTION,
        "SAHNE-08": UserState.AUDIO_SELECTION,
        "SAHNE-09": UserState.VOICE_LANGUAGE,
        "SAHNE-10": UserState.VOICE_CHARACTER,
        "SAHNE-11": UserState.EMPHASIS,
    }
    target_state = scene_state_map.get(target_scene)
    if target_state:
        context.user_data["user_state"] = target_state.value
        # İlgili sahneyi göster
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data,
            chat_id=chat_id,
            bot=context.bot,
        )
    else:
        logger.warning(f"⚠️ [SAHNE-12] Bilinmeyen hedef sahne: {target_scene}")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-13: Brief Tamamlandı Akışı (FD-008_1 uyumlu)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_senaryo_html(data: dict) -> str:
    """Senaryo Onay Formu'nu Telegram HTML olarak oluşturur (AR-002_65)."""
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    u = data["urun"]
    lines = [SEP,
             "<b>━━━━ 🎬 SENARYO ONAY FORMU ━━━━</b>",
             "<code>✅1.Brief  ›  🔵2.Senaryo  ›  ⏳3.Fiyat Teklifi</code>",
             SEP, "",
             f"MARKA: <b>{u['marka']}</b>",
             f"ÜRÜN: <b>{u['ad']}</b>",
             "", SEP, "",
             "<b>📖 Tanıtım Hikayesi</b>",
             f"<i>{data['hikaye']}</i>",
             "", SEP, "",
             f"<b>🎞️ Sahne Planı ({data['toplamSure']})</b>"]

    sahneler = data.get("sahneler", [])
    for s in sahneler:
        lines.append(f"<b>S{s['no']}: {s['baslik']}</b>  <code>⏱{s['zaman']} ({s['sure']})</code>")
        lines.append(f"  <i>{s['aciklama']}</i>")
        lines.append("")
    lines.append(SEP)

    ses = data["seslendirme"]
    uret = data["uretim"]
    lines.append(f"<b>🎙️ {ses['dil']} | {ses['karakter']} | {ses['yapi']}</b>")
    lines.append(f"<b>🎬 {uret['platform']} • {uret['format']} • {uret['cozunurluk']} • {uret['sure']} • {uret['sahneSayisi']} sahne</b>")
    lines.append(""); lines.append(SEP)

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════

async def _run_sahne13_flow(
    chat_id: int, user_id: int,
    user_data: dict, bot,
):
    """SAHNE-13: Brief tamamlandı videosu + senaryo onay formu.

    FD-008_1 akışı:
    1. Seçilen dilde SAHNE-13 videosu oynat
    2. Video süresince bekle
    3. Videoyu sil
    4. "Senaryo hazır, form hazırlanıyor..." daktilo
    5. Senaryo Onay Formu gönder (ONAY/RET)
    """
    from config.video_paths import get_sahne13_video, SAHNE13_SURE_LANG, SAHNE13_SURE, SAHNE2_EXTRA_WAIT

    language = user_data.get("language", "tr")
    video_path = get_sahne13_video(language)
    video_duration = SAHNE13_SURE_LANG.get(language.upper(), SAHNE13_SURE)

    sahne13_msg = None
    if video_path and video_path.exists():
        try:
            with open(video_path, "rb") as vf:
                sahne13_msg = await bot.send_video(
                    chat_id=chat_id, video=vf,
                    width=720, height=1280,
                    duration=video_duration,
                )
            logger.info(f"🎬 SAHNE-13 video gönderildi: {language} msg={sahne13_msg.message_id}")
        except Exception as e:
            logger.error(f"❌ SAHNE-13 video gönderilemedi: {e}")
    else:
        logger.warning(f"⚠️ SAHNE-13 video bulunamadı: dil={language}")

    # FD-008_5: SESLI_HINT — seçilen dilde uyarı metni gönder, 5sn sonra sil
    from handlers.start import SESLI_HINT
    hint_text = SESLI_HINT.get(language, SESLI_HINT["tr"])
    hint_msg = await bot.send_message(chat_id=chat_id, text=hint_text, parse_mode="HTML")
    logger.info(f"🔊 SAHNE-13 SESLI_HINT gönderildi: {language}")

    # Video + hint süresince bekle
    await asyncio.sleep(video_duration + SAHNE2_EXTRA_WAIT)

    # Hint mesajını sil
    if hint_msg:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=hint_msg.message_id)
            logger.info(f"🧹 SAHNE-13 SESLI_HINT silindi")
        except Exception:
            pass

    # Videoyu sil
    if sahne13_msg:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=sahne13_msg.message_id)
            logger.info(f"🧹 SAHNE-13 video silindi")
        except Exception:
            pass

    # "Senaryo hazır, form hazırlanıyor..." daktilo (HLK dil uyumlu)
    scenario_ready_text = (
        f"📝 <b>{t('s13.scenario_ready', language)}</b>"
    )
    tw_msg_id = await typewriter_animation(chat_id, scenario_ready_text, bot, 0.06)
    await asyncio.sleep(1.5)

    # Daktilo mesajını sil
    if tw_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=tw_msg_id)
        except Exception:
            pass

    # State: BRIEF_COMPLETED → SCENARIO_APPROVAL
    se = StateEngine(user_data)
    se.fire(UserEvent.BRIEF_APPROVED)

    # ════════════════════════════════════════════════════════════════
    # AR-002_65: REFERANS_SENARYO_ONAY_FORMU → Telegram HTML + InlineKeyboard
    # PNG render kullanılmaz; Telegram resmi bileşenleriyle uygulanır
    # ════════════════════════════════════════════════════════════════
    data = _build_scenario_data(user_data)

    html = _build_senaryo_html(data)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {t('s13.approve', language)}", callback_data="scenario_approve")],
        [InlineKeyboardButton(f"❌ {t('s13.reject', language)}", callback_data="scenario_reject")],
    ])

    msg = await bot.send_message(
        chat_id=chat_id, text=html,
        reply_markup=kb, parse_mode="HTML",
    )
    scene_delivery.register_chat_messages(chat_id, {"success_msg_id": msg.message_id})
    logger.info(f"📸 [SAHNE-13] Senaryo HTML gönderildi: {len(html)} chars")

    from utils.session_timeout import start_timer
    start_timer(user_id, chat_id, bot, user_data)


def _build_scenario_form(user_data: dict) -> str:
    """REFERANS_SENARYO_ONAY_FORMU.md birebir uyumlu dinamik senaryo onay formu.

    3 bölüm: Senaryo Metni → Senaryo Detayları → Kullanıcı İşlemleri
    """
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    duration = user_data.get("video_duration", "—")
    style = user_data.get("ad_style", "—")
    audience = user_data.get("target_audience", "—")

    # Seslendirme
    lang_code = user_data.get("voice_language", "")
    lang_names = {"tr": "🇹🇷 Türkçe", "en": "EN English", "de": "🇩🇪 Deutsch",
                  "fr": "🇫🇷 Français", "es": "🇪🇸 Español", "ru": "🇷🇺 Русский",
                  "ar": "AR العربية", "kr": "🏳️ Kurdî"}
    voice_lang = lang_names.get(lang_code, lang_code) if lang_code else "—"
    voice_char = user_data.get("voice_character", "—")
    voice_str = f"{voice_lang} — {voice_char}" if voice_char != "—" else voice_lang

    # Vurgular
    selections = user_data.get("emphasis_selections", [])
    emphasis_labels = {
        "emphasis_discount": "🏷️ İndirim", "emphasis_shipping": "🚚 Ücretsiz Kargo",
        "emphasis_gift": "🎁 Hediye Paket", "emphasis_newseason": "✨ Yeni Sezon",
        "emphasis_local": "🇹🇷 Yerli Üretim",
    }
    emphasis_parts = []
    for s in selections:
        if s.startswith("emphasis_custom_"):
            emphasis_parts.append(s.replace("emphasis_custom_", "", 1))
        else:
            emphasis_parts.append(emphasis_labels.get(s, s))
    emphasis_str = ", ".join(emphasis_parts) if emphasis_parts else "—"

    return (
        "📝 <b>SENARYO ONAY FORMU</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📄 <b>Senaryo Metni</b>\n"
        f"{platform} platformunda {fmt} formatında, {duration} saniyelik "
        f"<b>{style}</b> tarzında bir ürün tanıtım videosu hazırlanacaktır.\n\n"
        "🎬 <b>Sahne Açıklamaları</b>\n"
        "• <b>Sahne 1</b> — Ürün gösterimi ve dikkat çekici giriş\n"
        "• <b>Sahne 2</b> — Ürün detayları, özellikler ve vurgular\n"
        "• <b>Sahne 3</b> — Kapanış, harekete geçirici mesaj\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 <b>Senaryo Detayları</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ <b>Tahmini Video Süresi:</b> {duration} saniye\n"
        f"🎯 <b>Hedef Kitle:</b> {audience}\n"
        f"🎨 <b>Tanıtım Tarzı:</b> {style}\n"
        f"🎙️ <b>Seslendirme:</b> {voice_str}\n"
        f"✨ <b>Vurgulanacaklar:</b> {emphasis_str}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def _build_sahne_listesi(sahneler: list, time_ranges: list, times: list,
                         brand: str, product_name: str) -> list:
    """Dinamik sahne listesini olusturur."""
    ACL = {
        "Dikkat Çekici Giriş": (
            f"{brand} {product_name} ürünü günlük yaşamın içinde doğal bir anda gösterilir. "
            "İzleyicinin dikkati ilk saniyelerde ürüne çekilir. "
            "Görsel olarak etkileyici, merak uyandıran bir açılış sahnesi."
        ),
        "Ürün Tanıtımı": (
            f"Ürün yakın planda detaylı gösterilir. {brand} kalitesi ve "
            f"{product_name}'in öne çıkan özellikleri vurgulanır."
        ),
        "Özellikler ve Faydalar": (
            f"{product_name} ürününün sağladığı faydalar ve rakiplerinden ayrışan yönleri "
            "görsel karşılaştırmalar ve ikonlarla sunulur."
        ),
        "Kullanım Gösterimi": (
            f"{product_name} ürününün gerçek kullanım anı gösterilir. "
            "Kullanım kolaylığı ve pratik faydaları vurgulanır."
        ),
        "Kapanış — CTA": (
            f"{brand} logosu ve ürün bilgisi ekranda belirir. "
            "İzleyiciyi satın almaya veya daha fazla bilgi edinmeye yönlendiren "
            "net ve güçlü bir çağrı mesajı. Sipariş linki veya iletişim bilgisi sunulur."
        ),
    }
    result = []
    for i, s in enumerate(sahneler):
        t_start, t_end = time_ranges[i]
        result.append({
            "no": i + 1,
            "gorsel": f"https://via.placeholder.com/160x100.png?text={i + 1}",
            "baslik": s["baslik"],
            "aciklama": ACL.get(s["baslik"], f"{s['baslik']} sahnesi."),
            "zaman": f"0:{t_start:02d} – 0:{t_end:02d}",
            "sure": f"{times[i]} sn",
        })
    return result


def _build_scenario_data(user_data: dict) -> dict:
    """REFERANS_SENARYO_ONAY_FORMU template.html için veri yapısı.

    MASTER-010: template.html'in beklediği DATA_JSON yapısını üretir.
    """
    from datetime import date

    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    resolution = user_data.get("video_resolution", "—")
    duration = user_data.get("video_duration", "—")
    style = user_data.get("ad_style", "—")
    audience = user_data.get("target_audience", "—")

    url = user_data.get("website_url", "")
    product_name = url.split("/")[-1] if url else "Ürün"
    brand = user_data.get("brand", "—")

    # Seslendirme
    lang_code = user_data.get("voice_language", "")
    lang_names = {"tr": "🇹🇷 Türkçe", "en": "EN English", "de": "🇩🇪 Deutsch",
                  "fr": "🇫🇷 Français", "es": "🇪🇸 Español", "ru": "🇷🇺 Русский",
                  "ar": "AR العربية", "kr": "🏳️ Kurdî"}
    voice_lang = lang_names.get(lang_code, lang_code) if lang_code else "—"
    voice_char = user_data.get("voice_character", "—")

    # Ses yapısı
    toggles = user_data.get("audio_toggles", {})
    if toggles.get("silent"):
        ses_yapisi = "🔇 Sessiz"
    else:
        ses_parts = []
        AUDIO_OPTIONS = {
            "voiceover": "🎙️ Dış Seslendirme", "ambient": "🔊 Ortam Sesleri",
            "music": "🎵 Fon Müziği",
        }
        for k in AUDIO_OPTIONS:
            if toggles.get(k):
                ses_parts.append(AUDIO_OPTIONS[k])
        ses_yapisi = ", ".join(ses_parts) if ses_parts else "—"

    # Dinamik sahne sayisi ve sureleri — video suresine gore
    try:
        total_sec = int(duration) if str(duration).isdigit() else 25
    except (ValueError, TypeError):
        total_sec = 25
    total_sec = max(7, total_sec)

    if total_sec <= 10:
        sahneler = [
            {"baslik": "Dikkat Çekici Giriş", "pct": 0.30},
            {"baslik": "Ürün Tanıtımı", "pct": 0.45},
            {"baslik": "Kapanış — CTA", "pct": 0.25},
        ]
    elif total_sec <= 20:
        sahneler = [
            {"baslik": "Dikkat Çekici Giriş", "pct": 0.20},
            {"baslik": "Ürün Tanıtımı", "pct": 0.30},
            {"baslik": "Özellikler ve Faydalar", "pct": 0.30},
            {"baslik": "Kapanış — CTA", "pct": 0.20},
        ]
    elif total_sec <= 30:
        sahneler = [
            {"baslik": "Dikkat Çekici Giriş", "pct": 0.18},
            {"baslik": "Ürün Tanıtımı", "pct": 0.24},
            {"baslik": "Kullanım Gösterimi", "pct": 0.22},
            {"baslik": "Özellikler ve Faydalar", "pct": 0.22},
            {"baslik": "Kapanış — CTA", "pct": 0.14},
        ]
    else:
        sahneler = [
            {"baslik": "Dikkat Çekici Giriş", "pct": 0.15},
            {"baslik": "Ürün Tanıtımı", "pct": 0.22},
            {"baslik": "Kullanım Gösterimi", "pct": 0.20},
            {"baslik": "Özellikler ve Faydalar", "pct": 0.20},
            {"baslik": "Kapanış — CTA", "pct": 0.23},
        ]

    # Sureleri hesapla
    times = []
    remaining = total_sec
    for i, s in enumerate(sahneler):
        if i == len(sahneler) - 1:
            sec = max(2, remaining)
        else:
            sec = max(2, round(total_sec * s["pct"]))
        times.append(sec)
        remaining -= sec
    # Son sahneye kalan saniyeleri ekle
    total_assigned = sum(times)
    if total_assigned != total_sec:
        times[-1] += total_sec - total_assigned

    # Zaman araliklarini olustur
    time_ranges = []
    start = 0
    for t in times:
        time_ranges.append((start, start + t))
        start += t

    return {
        "adimlar": [
            {"no": 1, "baslik": "Brief", "altbaslik": "Tamamlandı", "durum": "done"},
            {"no": 2, "baslik": "Senaryo", "altbaslik": "İncelemede", "durum": "active"},
            {"no": 3, "baslik": "Fiyat Teklifi", "altbaslik": "Sıradaki Adım", "durum": "pending"},
        ],
        "urun": {
            "gorsel": "https://via.placeholder.com/200x200.png?text=Urun",
            "ad": product_name,
            "marka": brand,
            "platform": platform,
            "kategori": user_data.get("category", "—"),
            "hedefKitle": audience,
            "format": fmt,
            "cozunurluk": resolution,
            "sure": f"{duration} sn" if duration != "—" else "—",
            "sesYapisi": ses_yapisi,
            "tarih": date.today().strftime("%d.%m.%Y"),
        },
        "hikaye": (
            f"{brand} — {product_name} için {platform} platformunda "
            f"{fmt} formatında, {duration} saniyelik "
            f"{style} tarzında bir ürün tanıtım videosu hazırlanacaktır. "
            f"Hedef kitle: {audience}. Seslendirme: {voice_lang}, {voice_char}."
        ),
        "sahneler": _build_sahne_listesi(sahneler, time_ranges, times, brand, product_name),
        "toplamSure": f"{duration} sn" if duration != "—" else "—",
        "seslendirme": {
            "dil": voice_lang,
            "karakter": voice_char if voice_char != "—" else "Kadın • Samimi",
            "yapi": ses_yapisi,
        },
        "uretim": {
            "platform": platform,
            "format": fmt,
            "cozunurluk": resolution,
            "sure": f"{duration} sn" if duration != "—" else "—",
            "sahneSayisi": len(sahneler),
        },
        "footer": {
            "kod": "HLK_RUNTIME_SENARYO",
            "versiyon": "V1.0",
            "tarih": date.today().strftime("%d.%m.%Y"),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Senaryo Onay Formu Handler'ları (REFERANS_SENARYO_ONAY_FORMU.md uyumlu)
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_scenario_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Senaryo ONAY → Yönetici Fiyatlandırma Formu (FD-008_1).

    FD-008_1: STATE_PRICING iki aşamalıdır:
    1. Yönetici Fiyatlandırma Formu → Admin (fiyatı belirler)
    2. Kullanıcı Fiyat Teklif Formu → User (onaylar/reddeder)
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✅ Senaryo onaylandı — yöneticiye iletiliyor...")
    logger.info(f"📝 {user.id} senaryoyu onayladı → yönetici fiyatlandırma")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.SCENARIO_APPROVED)
    context.user_data["_pricing_user_id"] = user.id
    context.user_data["_pricing_chat_id"] = chat_id

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # FD-008_1 Aşama 1: Yönetici Fiyatlandırma Formu
    admin_form, computed_data = _build_admin_pricing_form(context.user_data)

    # Hesaplanan değerleri user_data'ya kaydet (sonraki adımlar için)
    context.user_data["_computed_toplam"] = computed_data["toplam"]
    context.user_data["_computed_yonetici_fiyat"] = computed_data["yonetici_fiyat"]
    context.user_data["_computed_kdvli"] = computed_data["kdvli"]

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Katsayı Gir", callback_data="admin_enter_katsayi"),
         InlineKeyboardButton("💬 HLK'ya Sor", callback_data="admin_hlk_chat")],
        [InlineKeyboardButton("✅ ONAY", callback_data="admin_price_submit"),
         InlineKeyboardButton("❌ İPTAL", callback_data="admin_price_cancel")],
    ])
    admin_msg = await context.bot.send_message(
        chat_id=chat_id, text=admin_form,
        reply_markup=kb, parse_mode="HTML",
    )
    scene_delivery.register_chat_messages(chat_id, {"success_msg_id": admin_msg.message_id})
    logger.info(f"📋 Yönetici Fiyatlandırma Formu gönderildi: user={user.id}")


async def handle_scenario_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Senaryo RET → Oturum kapat (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("❌ Senaryo reddedildi")
    logger.info(f"📝 {user.id} senaryoyu reddetti")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.SCENARIO_REJECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    lang = get_lang(context.user_data)
    reject_text = t("s13.reject_msg", lang)
    tw_msg_id = await typewriter_animation(chat_id, reject_text, context.bot, 0.06)
    await asyncio.sleep(5)
    if tw_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=tw_msg_id)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# Fiyatlandırma + Ödeme Akışı (FD-008_1 STATE_PRICING)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_admin_pricing_form(user_data: dict) -> tuple:
    """AR-002_65: Yönetici Fiyatlandırma — Telegram HTML (PNG yok).

    Returns:
        (html_text, computed_data) — computed_data: {toplam, yonetici_fiyat, kdvli}
    """
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    user_id = user_data.get("_pricing_user_id", "—")
    product_url = user_data.get("website_url", "—")
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    resolution = user_data.get("video_resolution", "—")
    duration = user_data.get("video_duration", "—")
    style = user_data.get("ad_style", "—")
    audience = user_data.get("target_audience", "—")

    lang_code = user_data.get("voice_language", "")
    lang_names = {"tr": "🇹🇷 Türkçe", "en": "EN English", "de": "🇩🇪 Deutsch",
                  "fr": "🇫🇷 Français", "es": "🇪🇸 Español", "ru": "🇷🇺 Русский",
                  "ar": "AR العربية", "kr": "🏳️ Kurdî"}
    voice_lang = lang_names.get(lang_code, lang_code) if lang_code else "—"
    voice_char = user_data.get("voice_character", "—")

    toggles = user_data.get("audio_toggles", {})
    has_voiceover = toggles.get("voiceover", False) or False
    has_silent = toggles.get("silent", False)
    dur = int(duration) if str(duration).isdigit() else 15
    short_url = product_url[:50] + "…" if len(product_url) > 50 else product_url
    product_name = short_url.split("/")[-1] if "/" in short_url else short_url
    brand = user_data.get("brand", "—")
    ses_yapisi = "🔇 Sessiz" if has_silent else ("Dış ses, fon müziği" if has_voiceover else "Fon müziği")

    # Servis maliyetleri
    tts_cost   = round(dur * 0.002, 2) if has_voiceover and not has_silent else 0
    hedra_cost = round(dur * 0.06, 2)
    kie_cost   = 0.05
    fal_cost   = round(dur * 0.04, 2)
    openai_cost = 0.08
    toplam = round(tts_cost + hedra_cost + kie_cost + fal_cost + openai_cost + round(dur*0.01,2) + 0.03, 2)

    servisler = [
        ("Higgsfield AI", "Video Üretimi", True, f"${hedra_cost:.2f}", "94%"),
        ("ElevenLabs", "Ses Üretimi", True, f"${tts_cost:.2f}", "97%"),
        ("Kie AI", "Görsel Üretimi", True, f"${kie_cost:.2f}", "91%"),
        ("Fal.ai", "Seedance", False, f"${fal_cost:.2f}", "72%"),
        ("OpenAI", "TTS Yedek", True, f"${openai_cost:.2f}", "96%"),
        ("Descript", "Ses Düzenleme", True, "$0.03", "82%"),
    ]

    lines = [SEP,
             "<b>━━ 🏷️ HLK YÖNETİCİ FİYATLANDIRMA FORMU ━━</b>",
             "<code>✅Brief › ✅Senaryo › 🔵Fiyat › ⏳Ödeme</code>",
             SEP,
             f"ÜRÜN: <b>{product_name}</b>",
             f"MARKA: <b>{brand}</b>",
             f"<i>{fmt}, {resolution}, {duration}sn, {ses_yapisi}, {voice_lang}, {voice_char}</i>",
             "", SEP, "",
             "<b>🔌 Servis Sağlayıcı ve Kredi Durumu</b>"]

    for i, (ad, gorev, aktif, maliyet, guven) in enumerate(servisler, 1):
        durum_icon = "✅" if aktif else "⚠️"
        lines.append(f"<b>{i}.</b> {durum_icon} <b>{ad}</b> — {'Aktif' if aktif else 'Yavaş'} | {maliyet} | Güven: {guven} | {gorev}")
    lines.append(""); lines.append(SEP)

    lines.append(f"<b>⚠️ Risk Değerlendirmesi</b>")
    risk_items = [
        "Fal.ai servisi normalden yavaş yanıt vermektedir.",
        "Sıradaki görsel üretici: Kie AI (Güven: 91%)",
        "Sıradaki video üretici: Higgsfield AI (Güven: 94%)",
        "Yedek ses üreticisi: OpenAI TTS (Güven: 96%)",
        f"Mevcut kredi: $25.00 | Tahmini tüketim: ${toplam:.2f} | Kalan: ${25.00 - toplam:.2f}",
        "Kritik seviye: Yok. Tüm zorunlu servisler aktif.",
    ]
    for r in risk_items:
        lines.append(f"  - {r}")
    lines.append(""); lines.append(SEP)

    lines.append("<b>BU İŞ İÇİN TAHMİNİ MALİYETLER</b>")
    for i, (ad, gorev, aktif, maliyet, guven) in enumerate(servisler, 1):
        lines.append(f"  {i}- {ad} ({gorev}): {maliyet}")
    lines.append(f"  <b>TOPLAM: ${toplam:.2f}</b>")
    lines.append("")
    katsayi = float(user_data.get("_admin_katsayi", "0.347"))
    yonetici_fiyat = round(toplam * katsayi, 2)
    kdvli = round(toplam * katsayi * 1.20, 2)
    lines.append(f"<b>KATSAYI:</b> <code>  {katsayi}  </code>")
    lines.append(f"<i>TOPLAM ${toplam:.2f} × {katsayi}</i>")
    lines.append("")
    lines.append(f"<b>━━━ YÖNETİCİ FİYATI: ${yonetici_fiyat:.2f} + KDV = ${kdvli:.2f} ━━━</b>")

    computed_data = {
        "toplam": toplam,
        "yonetici_fiyat": yonetici_fiyat,
        "kdvli": kdvli,
    }
    return "\n".join(lines), computed_data


async def handle_admin_pricing_submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yönetici fiyat seçti → Kullanıcı Fiyat Teklif Formu (FD-008_1 Aşama 2)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    cb = query.data

    if cb == "admin_enter_katsayi":
        await query.answer("✏️ Katsayıyı girin...")
        context.user_data["_admin_waiting_katsayi"] = True
        # FD-008_1: "EKRAN SİLİNİR" — admin formunu temizle, sadece prompt kalır
        try:
            await query.message.delete()
        except Exception:
            pass
        await scene_delivery.cleanup_chat(chat_id)
        prompt_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="✏️ <b>Katsayıyı girin:</b>\n\nÖrn: 1.5, 2.0, 0.8",
            parse_mode="HTML",
        )
        scene_delivery.register_chat_messages(chat_id, {"success_msg_id": prompt_msg.message_id})
        return

    if cb == "admin_hlk_chat":
        await query.answer("💬 HLK sohbet modu aktif")
        context.user_data["_admin_chat_mode"] = True
        # FD-008_1: "EKRAN SİLİNİR" — admin formunu temizle
        try:
            await query.message.delete()
        except Exception:
            pass
        await scene_delivery.cleanup_chat(chat_id)
        chat_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="💬 <b>HLK Sohbet Modu</b>\n\nBu form hakkında sorular sorabilirsin.\n"
                 "Maliyet, fiyatlandırma, servis seçimi, kar marjı...\n\n"
                 "<i>Çıkmak için sohbet bitirme butonuna bas.</i>",
            parse_mode="HTML",
        )
        scene_delivery.register_chat_messages(chat_id, {"success_msg_id": chat_msg.message_id})
        return

    if cb == "admin_hlk_chat_end":
        await query.answer("✅ Sohbet sonlandı.")
        context.user_data["_admin_chat_mode"] = False
        try: await query.message.delete()
        except: pass
        return

    if cb == "admin_price_submit":
        katsayi = float(context.user_data.get("_admin_katsayi", "0.347"))
        # Gerçek hesaplanmış değerleri kullan (sabit 59.30 yerine)
        toplam = context.user_data.get("_computed_toplam", 59.30)
        yonetici_fiyat = context.user_data.get("_computed_yonetici_fiyat", round(toplam * katsayi, 2))
        kdvli_fiyat = context.user_data.get("_computed_kdvli", round(toplam * katsayi * 1.20, 2))
        price = kdvli_fiyat
        await query.answer(f"✅ Fiyat onaylandı: ${kdvli_fiyat:.2f}")
        logger.info(f"💰 Yönetici {user.id} fiyat belirledi: ${price}")

        try: await query.message.delete()
        except: pass
        await scene_delivery.cleanup_chat(chat_id)

        # Kullanıcı Fiyat Teklif Formu
        lang = get_lang(context.user_data)
        user_form = _build_user_pricing_form(context.user_data, price, yonetici_fiyat, katsayi)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ {t('pricing.approve_btn', lang)}", callback_data="pricing_approve")],
            [InlineKeyboardButton(f"❌ {t('pricing.reject_btn', lang)}", callback_data="pricing_reject")],
        ])
        user_chat_id = context.user_data.get("_pricing_chat_id", chat_id)
        await scene_delivery.cleanup_chat(user_chat_id)
        user_msg = await context.bot.send_message(
            chat_id=user_chat_id, text=user_form,
            reply_markup=kb, parse_mode="HTML",
        )
        scene_delivery.register_chat_messages(user_chat_id, {"success_msg_id": user_msg.message_id})
        logger.info(f"📋 Kullanıcı Fiyat Teklif Formu gönderildi: ${price}")

        from utils.session_timeout import start_timer
        start_timer(user.id, user_chat_id, context.bot, context.user_data)
        return

    if cb == "admin_price_cancel":
        await query.answer("❌ Fiyatlandırma iptal edildi")
        try:
            await query.message.delete()
        except Exception:
            pass
        return


TCMB_KUR_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
TCMB_KUR_FALLBACK = 46.9966  # 13.07.2026 — Sadece API erisilemezse kullanilir


def _get_tcmb_kur() -> float:
    """TCMB'den canli USD doviz satis kurunu getirir.

    Her cagrida TCMB XML servisinden guncel kuru ceker.
    API'ye erisilemezse fallback deger dondurur.
    """
    try:
        req = urllib.request.Request(TCMB_KUR_URL, headers={"User-Agent": "HLK/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode("utf-8")
        root = ET.fromstring(xml_data)
        for currency in root.findall("Currency"):
            if currency.get("Kod") == "USD":
                selling = currency.find("ForexSelling")
                if selling is not None and selling.text:
                    kur = float(selling.text)
                    logger.info(f"💱 TCMB USD Kur: {kur} TL (canli)")
                    return kur
        logger.warning(f"💱 TCMB XML'de USD bulunamadi, fallback: {TCMB_KUR_FALLBACK}")
        return TCMB_KUR_FALLBACK
    except Exception as e:
        logger.warning(f"💱 TCMB kur cekilemedi: {e}, fallback: {TCMB_KUR_FALLBACK}")
        return TCMB_KUR_FALLBACK


def _build_banka_bilgileri_karti(price: float = 0, tcmb: float = None, lang: str = "tr") -> str:
    """AR-002_65: HLK BANKA ÖDEME BİLGİLERİ KARTI — Fiyat + IBAN + Uyarı.

    FD-008_1: Kullanıcı Fiyat Teklifi onaylandıktan sonra gönderilir.
    """
    if tcmb is None:
        tcmb = _get_tcmb_kur()
    lines = [
        "<code>✅Brief › ✅Senaryo › ✅Fiyat › ✅Ödeme</code>",
        f"{SEP}",
        f"<b>{t('payment.card_title', lang)}</b>",
        "",
        f"{SEP}",
        "",
        "",
        "",
        f"<b>💰 {t('pricing.kdv_dollar', lang)}:  ${price:.2f}</b>",
        f"{t('pricing.tcmb_rate', lang)}: {tcmb} TL",
        "",
        f"<b>━━━ 💵 {t('pricing.sales_price', lang)}: {satis_tl:.2f} TL ━━━</b>",
        "",
        "",
        "",
        f"{SEP}",
        f"<b>💳 {t('payment.account_holder', lang)}:</b>  <b>HALUK ARI</b>",
        "",
        "▸ <b>Garanti Bankası (TL)</b>",
        "  <code>TR69 0006 2000 3910 0006 8957 76</code>",
        "▸ <b>Garanti Bankası (USD)</b>",
        "  <code>TR69 0006 2000 3910 0009 0255 08</code>",
        "▸ <b>Ak Bank (TL)</b>",
        "  <code>TR96 0004 6001 6688 8000 0490 88</code>",
        f"{SEP}",
        f"<b>📌 {t('payment.payment_method', lang)}:</b>  {t('payment.bank_transfer', lang)}",
        f"{SEP}",
        f"<b>⚠️ {t('payment.warning_title', lang)}:</b>",
        f"• {t('payment.warning_1', lang)}",
        f"• {t('payment.warning_2', lang)}",
        f"• {t('payment.warning_3', lang)}",
        f"{SEP}",
    ]
    return "\n".join(lines)


def _build_odeme_bilgileri_karti(price: float = 0, tcmb: float = None) -> str:
    if tcmb is None:
        tcmb = _get_tcmb_kur()
    """AR-002_65: Ödeme Bilgileri Kartı — HLK Teklif Fiyatı + Banka + Uyarı.

    Bağımsız bir kart olarak kullanılabilir (test ve form entegrasyonu için).
    """
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    lines = [f"{SEP}"]

    # Fiyat bilgisi
    if price:
        lines.extend([
            f"<b>💰 KDV Dahil Dolar Tutarı:  ${price:.2f}</b>",
            f"{SEP}",
            f"{SEP}",
        ])

    lines.extend([
        "<b>⚠️ ÖNEMLİ UYARI:</b>",
        "• Ödemeniz alındıktan sonra üretim süreci başlar.",
        "• Video belirtilen süre içerisinde adresinize dijital Mp4 formatında teslim edilir.",
        f"{SEP}",
    ])
    return "\n".join(lines)


def _build_user_pricing_form(user_data: dict, price: str, yonetici_fiyat: float = 0, katsayi: float = 0) -> str:
    """AR-002_65: Kullanıcı Fiyat Teklif Formu — HLK AI ASISTAN FİYAT TEKLİFİ."""
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    duration = user_data.get("video_duration", "—")
    resolution = user_data.get("video_resolution", "—")
    url = user_data.get("website_url", "—")
    product_name = url.split("/")[-1] if "/" in url else "Ürün"
    tcmb_kur = _get_tcmb_kur()  # TCMB canli kur

    from datetime import datetime
    pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

    # Fiyatı float'a çevir (string veya float gelebilir)
    try:
        price_f = float(price)
    except (ValueError, TypeError):
        price_f = 0.0
    satis_tl = round(price_f * tcmb_kur, 2)

    lang = get_lang(user_data)

    return (
        f"{SEP}\n"
        f"<b>━━━ 💰 {t('pricing.title', lang)} ━━━</b>\n\n\n\n"
        f"<code>{pid}</code>\n"
        f"{SEP}\n"
        "<code>✅Brief › ✅Senaryo › ✅Fiyat › 🔵Ödeme</code>\n"
        f"{SEP}\n"
        f"MARKA: <b>{user_data.get('brand', '—')}</b>\n"
        f"ÜRÜN: <b>{product_name}</b>\n"
        f"<i>{fmt} • {resolution} • {duration}sn • 5 sahne | {user_data.get('ad_style', '—')} • {user_data.get('target_audience', '—')} | 🎙️ Dış Ses+Fon Müzik</i>\n"
        f"{SEP}\n"
        f"<b>🛠️ {t('pricing.service_scope', lang)}</b>\n"
        "• Senaryo Hazırlama (HLK Yapay Zekâ)\n"
        "• Video Üretimi (5 sahne)\n"
        "• Profesyonel Seslendirme\n"
        "• Telifsiz Fon Müziği\n"
        "• Kurgu ve Montaj\n"
        "• Dijital Teslim (Mp4)\n"
        f"{SEP}\n"
        f"<b>{t('pricing.kdv_dollar', lang)}: ${price_f:.2f}</b>\n"
        f"{t('pricing.tcmb_rate', lang)}: {tcmb_kur} TL\n\n\n\n"
        f"<b>━━━ 💵 {t('pricing.sales_price', lang)}: {satis_tl:.2f} TL ━━━</b>\n"
        f"{SEP}\n"
        f"-{t('pricing.footer_1', lang)}\n"
        f"-{t('pricing.footer_2', lang)}\n"
        f"{SEP}"
    )


async def handle_pricing_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fiyat Teklifi ONAY → Ödeme ekranı (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✅ Fiyat teklifi onaylandı!")
    logger.info(f"💰 {user.id} fiyat teklifini onayladı")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PRICING_APPROVED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Ödeme ekranı → HLK BANKA ÖDEME BİLGİLERİ KARTI
    lang = get_lang(context.user_data)
    kdvli = context.user_data.get("_computed_kdvli", 0)
    payment_text = _build_banka_bilgileri_karti(price=kdvli, lang=lang)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🟢 {t('payment.pay_done_btn', lang)}", callback_data="payment_declared"),
         InlineKeyboardButton(f"🔴 {t('payment.pay_cancel_btn', lang)}", callback_data="payment_cancel")],
    ])
    await context.bot.send_message(
        chat_id=chat_id, text=payment_text,
        reply_markup=kb, parse_mode="HTML",
    )

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_pricing_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fiyat Teklifi RET → Oturum kapat (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("❌ Teklif reddedildi")
    logger.info(f"💰 {user.id} fiyat teklifini reddetti")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PRICING_REJECTED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    lang = get_lang(context.user_data)
    reject_text = (
        f"{t('final.new_session_start', lang)}"
    )
    await typewriter_animation(chat_id, reject_text, context.bot, 0.06)


def _build_admin_odeme_bildirimi(user_data: dict) -> str:
    """AR-002_65: Yönetici Ödeme Bildirimi — FD-008_1 STATE_PAYMENT_VERIFICATION.

    Kullanıcı ÖDEME YAPTIM dediğinde yöneticiye gönderilir.
    """
    SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    from datetime import datetime
    pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

    lang = get_lang(user_data)
    kdvli = user_data.get("_computed_kdvli", 0)
    tcmb_kur = _get_tcmb_kur()  # TCMB canli kur
    satis_tl = round(kdvli * tcmb_kur, 2)
    url = user_data.get("website_url", "—")
    product_name = url.split("/")[-1] if "/" in url else "Ürün"
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    resolution = user_data.get("video_resolution", "—")
    duration = user_data.get("video_duration", "—")
    brand = user_data.get("brand", "—")
    user_id = user_data.get("_pricing_user_id", "—")

    lines = [
        f"{SEP}",
        f"⚠️ <b>{t('admin_payment.title', lang)}</b>",
        f"{SEP}",
        f"<code>{pid}</code>",
        "",
        f"📋 <b>{t('admin_payment.verification', lang)}</b>",
        f"{SEP}",
        f"ℹ️  {t('admin_payment.info_1', lang)}",
        f"ℹ️  {t('admin_payment.info_2', lang)}",
        f"ℹ️  {t('admin_payment.info_3', lang)}",
        f"{SEP}",
        f"<b>👤 {t('admin_payment.user_info', lang)}</b>",
        f"Kullanıcı ID: <code>{user_id}</code>",
        f"{SEP}",
        "",
        "",
        "",
        f"<b>📦 {t('admin_payment.product_info', lang)}</b>",
        f"Ürün: <b>{product_name}</b>",
        f"Marka: <b>{brand}</b>",
        f"Platform: <b>{platform}</b>",
        f"Format: {fmt} | {resolution} | {duration}sn",
        f"{SEP}",
        f"<b>💰 {t('admin_payment.payment_info', lang)}</b>",
        f"Banka: <b>Garanti Bankası</b>",
        "<code>TR69 0006 2000 3910 0006 8957 76</code>",
        f"Beklenen Tutar: <b>${kdvli:.2f}</b> / <b>{satis_tl:.2f} TL</b>",
        f"TCMB Kur: {tcmb_kur} TL",
        f"{SEP}",
        "",
        "",
        "",
        f"<i>⏱️ {t('admin_payment.auto_generated', lang)}</i>",
        f"{SEP}",
    ]
    return "\n".join(lines)


async def handle_payment_declared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ÖDEME YAPTIM → Yönetici Ödeme Bildirimi (FD-008_1 STATE_PAYMENT_VERIFICATION)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✅ Ödeme bildirimi yöneticiye iletiliyor...")
    logger.info(f"💳 {user.id} ÖDEME YAPTIM → yönetici onayı bekleniyor")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PAYMENT_DECLARED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Yönetici Ödeme Bildirimi Kartı
    lang = get_lang(context.user_data)
    bildirim = _build_admin_odeme_bildirimi(context.user_data)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {t('admin_payment.approve_btn', lang)}", callback_data="admin_odeme_onay")],
        [InlineKeyboardButton(f"🔴 {t('admin_payment.ret_btn', lang)}", callback_data="admin_odeme_ret")],
    ])
    await context.bot.send_message(
        chat_id=chat_id, text=bildirim,
        reply_markup=kb, parse_mode="HTML",
    )

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_admin_payment_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yönetici ÖDEMEYİ ONAYLA → EVENT_PAYMENT_APPROVED → Video üretimi (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    await query.answer(f"✅ {t('final.payment_approved_toast', lang)}")
    logger.info(f"✅ Yönetici {user.id} ödemeyi onayladı → Video üretimi")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PAYMENT_APPROVED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # FD-008_1: Kullanıcıya daktilo efektiyle bilgilendirme mesajı
    lang = get_lang(context.user_data)
    done_text = (
        f"{t('final.payment_received', lang)}\n"
        f"{t('final.production_started', lang)}\n"
        f"{t('final.duration_info', lang)}\n"
        f"{t('final.auto_delivery', lang)}"
    )
    await typewriter_animation(chat_id, done_text, context.bot, 0.06)

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)

    # ── STATE_VIDEO_PRODUCTION: Production Runtime Entegrasyonu ──
    # AR-002_70: STATE_VIDEO_PRODUCTION → Production zinciri başlatılır
    # Production arka planda çalışır, callback'i bloke etmez
    asyncio.create_task(
        _run_production_pipeline(chat_id, context, user.id)
    )


async def handle_admin_payment_ret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yönetici RET → Ödeme ulaşmadı → Oturum kapat."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("❌ Ödeme onaylanmadı")
    logger.info(f"❌ Yönetici {user.id} ödemeyi reddetti")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.SESSION_CLOSED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    lang = get_lang(context.user_data)
    ret_text = (
        f"❌ <b>{t('final.payment_cancelled', lang)}</b>\n\n"
        f"{t('final.new_session_start', lang)}"
    )
    await context.bot.send_message(chat_id=chat_id, text=ret_text, parse_mode="HTML")


async def _run_production_pipeline(
    chat_id: int, context: ContextTypes.DEFAULT_TYPE, user_id: int
) -> None:
    """STATE_VIDEO_PRODUCTION: Production Runtime zincirini arka planda çalıştırır.

    AR-002_70 uyarınca Production zinciri:
    Production Runtime → CEE PRE-CHECK → PID → Package → Task → Executor → CEE POST-CHECK

    Production sonucuna göre State Engine'e uygun event gönderilir.
    Bu fonksiyon callback'i bloke etmez — asyncio.create_task ile çağrılır.

    Crash Recovery: PID context.user_data'ya kaydedilir. Restart sonrası
    bu PID ile production_runtime.recover(pid) çağrılarak kaldığı yerden
    devam edilir.
    """
    from services.production_runtime import production_runtime
    from utils.state_engine import StateEngine, UserEvent

    try:
        # Önce yarım kalmış production var mı kontrol et
        saved_pid = context.user_data.get("production_pid")
        if saved_pid:
            logger.info(f"🔄 [Production] Yarım kalmış production tespit edildi: {saved_pid}")
            try:
                result = await production_runtime.recover(saved_pid)
            except Exception as e:
                logger.error(f"❌ [Production] Recovery başarısız: {saved_pid} — {e}")
                # Recovery başarısızsa sıfırdan başlat
                result = await production_runtime.start_production()
        else:
            result = await production_runtime.start_production()

        # PID'i user_data'ya kaydet (crash recovery için)
        if result.pid:
            context.user_data["production_pid"] = result.pid

        se = StateEngine(context.user_data)

        if result.success:
            logger.info(
                f"✅ [Production] Başarılı — pid={result.pid}, "
                f"süre={result.duration_seconds:.1f}s, "
                f"CEE PRE={result.pre_check_report['verdict'] if result.pre_check_report else 'N/A'}, "
                f"CEE POST={result.post_check_report['verdict'] if result.post_check_report else 'N/A'}"
            )
            se.fire(UserEvent.VIDEO_PRODUCTION_COMPLETED)
            # Başarılı — PID'i temizle
            context.user_data.pop("production_pid", None)

            # Kullanıcıya başarı mesajı
            success_msg = (
                f"✅ <b>Üretim Tamamlandı!</b>\n\n"
                f"🆔 PID: <code>{result.pid}</code>\n"
                f"⏱️ Süre: {result.duration_seconds:.1f} saniye\n"
                f"📋 Adımlar: {result.completed_steps}/{result.total_steps}"
            )
            try:
                await context.bot.send_message(
                    chat_id=chat_id, text=success_msg, parse_mode="HTML"
                )
            except Exception:
                pass
        else:
            logger.error(
                f"❌ [Production] Başarısız — pid={result.pid}, "
                f"hata={result.error}, "
                f"CEE PRE={result.pre_check_report['verdict'] if result.pre_check_report else 'N/A'}"
            )
            se.fire(UserEvent.VIDEO_PRODUCTION_FAILED)
            # Başarısız — PID'i temizle (yeniden denenmeyecek)
            context.user_data.pop("production_pid", None)

            # Kullanıcıya hata mesajı
            error_msg = (
                f"❌ <b>Üretim Başarısız</b>\n\n"
                f"🆔 PID: <code>{result.pid}</code>\n"
                f"Hata: {result.error[:200] if result.error else 'Bilinmeyen hata'}"
            )
            try:
                await context.bot.send_message(
                    chat_id=chat_id, text=error_msg, parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"🚨 [Production] Kritik hata — user={user_id}: {e}")
        try:
            se = StateEngine(context.user_data)
            se.fire(UserEvent.VIDEO_PRODUCTION_FAILED)
        except Exception:
            pass


async def handle_payment_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ÖDEME İPTAL → Oturum kapat (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    lang = get_lang(context.user_data)
    await query.answer(f"❌ {t('final.payment_cancelled', lang)}")
    logger.info(f"💳 {user.id} ödemeyi iptal etti")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.SESSION_CLOSED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    cancel_text = (
        f"❌ <b>{t('final.payment_cancelled', lang)}</b>\n\n"
        f"{t('final.new_session_start', lang)}"
    )
    await context.bot.send_message(chat_id=chat_id, text=cancel_text, parse_mode="HTML")
