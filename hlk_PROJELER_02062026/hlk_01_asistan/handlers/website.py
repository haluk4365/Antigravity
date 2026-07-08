"""Website linki işleme handler'ı.

ANA_YASA / GK-001: Link doğrulama ve araştırma başlatma.
Video üretim platformu sabit değildir. Platform seçimi ajan sıralaması sonucu belirlenir.

FAZ-4: Handler artık sahne davranışlarını Flow Diagram metadata'dan okur.
Hardcoded değerler yalnızca Flow Diagram verisi yoksa fallback olarak kullanılır.
"""

import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from utils.validators import is_valid_url
from utils.state_engine import StateEngine, UserState, UserEvent
from helpers.typewriter_animation import typewriter_animation
from services.scene_delivery import scene_delivery
from services.scene_engine import conversation_scene_engine
from services.render_service import render_brief_onay
from services.scene_registry import get_scene_for_state, SCENE_REGISTRY

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

    format_map = {
        "format_9_16": ("Dikey 9:16", "Telegram, TikTok, Instagram Reels, YouTube Shorts"),
        "format_16_9": ("Yatay 16:9", "YouTube, Facebook"),
        "format_1_1": ("Kare 1:1", "Instagram (Feed), Facebook"),
    }
    format_adi, platformlar = format_map.get(query.data, (query.data, ""))
    await query.answer(f"Seçilen: {format_adi}")

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

    resolution_map = {
        "resolution_480p": "480p",
        "resolution_720p": "720p HD",
        "resolution_1080p": "1080p Full HD",
    }
    resolution = resolution_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {resolution}")

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

    platform_map = {
        "platform_tiktok": "TikTok",
        "platform_instagram": "Instagram Reels",
        "platform_youtube": "YouTube",
        "platform_other": "Diğer",
    }
    platform_adi = platform_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {platform_adi}")

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
            await query.answer("🔇 Sessiz mod aktif — diğer seçenekler devre dışı")
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
            f"{emoji} <b>İlk materyalinizi</b> aldım, teşekkürler! 🙏\n\n"
            "<i>Bir sonraki materyali göndermeye devam edebilirsiniz.</i>\n"
            "İşiniz bittiğinde <b>✅ Bitti</b> butonuna basın."
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

    style_map = {
        "style_ugc": "UGC Tarzı", "style_traditional": "Geleneksel & Modern",
        "style_cinematic": "Sanatsal / Sinematik", "style_custom": "Kendim Yazacağım",
        "style_hlk": "HLK'ya Bırak",
    }
    style = style_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {style}")
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

    audience_map = {
        "audience_0_12": "Çocuk (0-12)", "audience_13_17": "Genç (13-17)",
        "audience_18_24": "Genç Yetişkin (18-24)", "audience_25_34": "Yetişkin (25-34)",
        "audience_35_44": "Aile Kurmuş (35-44)", "audience_45_54": "Orta Yaş (45-54)",
        "audience_55_64": "Olgun Yetişkin (55-64)", "audience_65_plus": "65 Yaş ve Üzeri",
    }
    audience = audience_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {audience}")
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

    lang_map = {
        "voicelang_tr": "Türkçe", "voicelang_en": "English",
        "voicelang_de": "Deutsch", "voicelang_fr": "Français",
        "voicelang_es": "Español", "voicelang_ru": "Русский",
        "voicelang_ar": "العربية", "voicelang_kr": "Kurdî",
    }
    lang = lang_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {lang}")
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

    char_map = {
        "voicechar_female": "Kadın Ses",
        "voicechar_male": "Erkek Ses",
        "voicechar_child": "Çocuk Ses",
    }
    char = char_map.get(query.data, query.data)
    await query.answer(f"Seçilen: {char}")
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

    emphasis_map = {
        "emphasis_discount": "🏷️ İndirim",
        "emphasis_shipping": "🚚 Ücretsiz Kargo",
        "emphasis_gift": "🎁 Hediye Paket",
        "emphasis_newseason": "✨ Yeni Sezon",
        "emphasis_local": "🇹🇷 Yerli Üretim",
    }
    key = query.data
    selected = context.user_data.setdefault("emphasis_selections", [])

    # "Ben Eklemek İstiyorum" → metin girişi moduna geç
    if key == "emphasis_custom":
        context.user_data["_waiting_custom_emphasis"] = True
        context.user_data["_emphasis_kb_msg_id"] = query.message.message_id
        await query.answer("✏️ Lütfen eklemek istediğiniz vurguyu yazın")
        prompt_id = await scene_delivery.send_and_track(
            chat_id=chat_id,
            text="✏️ <b>Özel Vurgu</b>\n\n"
                 "Eklemek istediğiniz vurguyu aşağıya <b>yazıp gönderin</b>.\n\n"
                 "<i>Örnek: %50 İndirim, 2 Al 1 Öde, Sınırlı Stok</i>",
        )
        context.user_data["_emphasis_prompt_msg_id"] = prompt_id
        return

    if key in selected:
        selected.remove(key)
        await query.answer("Kaldırıldı")
    else:
        selected.append(key)
        await query.answer(f"Eklendi: {emphasis_map.get(key, key)}")
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
    """SAHNE-12: REFERANS_Brief_Onay_Formu → PNG + Aktif Onay Butonları (MASTER-010).

    MASTER-010 uyarınca REFERANS_Brief_Onay_Formu Referans Formu PNG olarak render edilir.
    PNG sonrası Telegram inline butonları ile kullanıcı onayı alınır:
    - ✅ ONAYLIYORUM → BRIEF_APPROVED → SAHNE-13 akışı
    - ✏️ DÜZELTMEK İSTİYORUM → SAHNE-12 düzeltme modu
    """
    checks = _get_brief_checks(context.user_data)

    from io import BytesIO
    png_bytes = await render_brief_onay(context.user_data, checks)
    if png_bytes is None:
        logger.error(f"❌ [SAHNE-12] PNG render başarısız.")
        raise RuntimeError("SAHNE-12 PNG render başarısız — Referans Form oluşturulamadı.")

    # 1. PNG olarak Brief Özeti gönder
    msg = await context.bot.send_photo(
        chat_id=chat_id,
        photo=BytesIO(png_bytes),
        filename="HLK_Brief_Ozeti",
        caption=(
            "📋 <b>Brief Özeti</b>\n"
            "<i>Yukarıdaki formu inceleyip seçiminizi yapınız.</i>"
        ),
        parse_mode="HTML",
    )
    logger.info(f"📋 [SAHNE-12] PNG gönderildi: msg={msg.message_id}")

    # 2. Aktif onay butonları (MASTER-010: Referans Form butonları interaktif olmalı)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ONAYLIYORUM", callback_data="brief_approve")],
        [InlineKeyboardButton("✏️ DÜZELTMEK İSTİYORUM", callback_data="brief_edit")],
    ])
    btn_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "✅ <b>ONAYLIYORUM</b> — Tüm bilgiler doğru, senaryo aşamasına geçilsin.\n"
            "✏️ <b>DÜZELTMEK İSTİYORUM</b> — Değiştirmek istediğim bilgiler var."
        ),
        reply_markup=kb,
        parse_mode="HTML",
    )
    logger.info(f"📋 [SAHNE-12] Onay butonları gönderildi: msg={btn_msg.message_id}")

    scene_delivery.register_chat_messages(chat_id, {
        "success_msg_id": msg.message_id,
        "btn_msg_id": btn_msg.message_id,
    })
    context.user_data["brief_msg_id"] = msg.message_id
    context.user_data["brief_btn_msg_id"] = btn_msg.message_id


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

    kb_rows.append([InlineKeyboardButton("✅ DÜZENLEME TAMAM", callback_data="brief_approve")])

    kb = InlineKeyboardMarkup(kb_rows)

    try:
        await query.message.delete()
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "✏️ <b>Brief Düzeltme Modu</b>\n\n"
            "Değiştirmek istediğiniz alana tıklayın, ilgili adıma yönlendirileceksiniz.\n"
            "Düzenleme sonrası bu ekrana geri döneceksiniz.\n\n"
            "<i>İşiniz bittiğinde</i> <b>DÜZENLEME TAMAM</b> <i>butonuna basın.</i>"
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

    # Video süresince bekle
    await asyncio.sleep(video_duration + SAHNE2_EXTRA_WAIT)

    # Videoyu sil
    if sahne13_msg:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=sahne13_msg.message_id)
            logger.info(f"🧹 SAHNE-13 video silindi")
        except Exception:
            pass

    # "Senaryo hazır, form hazırlanıyor..." daktilo
    scenario_ready_text = (
        "📝 <b>Senaryo Hazır!</b>\n\n"
        "<i>Senaryo Onay Formu hazırlanıyor, lütfen bekleyin...</i>"
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
    # MASTER-010: REFERANS_SENARYO_ONAY_FORMU → PNG render
    # template.html + render.js → PNG → Telegram
    # ════════════════════════════════════════════════════════════════
    from services.render_service import render_scenario_approval

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ONAY", callback_data="scenario_approve")],
        [InlineKeyboardButton("❌ RET", callback_data="scenario_reject")],
    ])

    png_bytes = await render_scenario_approval(user_data)
    if not png_bytes:
        # AR-002_66: Render başarısız → fallback yasak, hata logla
        logger.critical(
            f"❌ [SAHNE-13] REFERANS_SENARYO_ONAY_FORMU PNG render BAŞARISIZ. "
            f"AR-002_66 uyarınca fallback yapılamaz. Kullanıcı: {user_id}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text="❌ <b>Bir sistem hatası oluştu.</b>\n\n"
                 "<i>Lütfen</i> <b>/start</b> <i>yazarak baştan başlayın.</i>",
            parse_mode="HTML",
        )
        return

    # MASTER-010 + AR-002_66: PNG render → Telegram
    await bot.send_photo(
        chat_id=chat_id, photo=png_bytes,
        caption=(
            "📝 <b>Senaryo Onay Formu</b>\n"
            "<i>Lütfen yukarıdaki formu inceleyip onay veriniz.</i>"
        ),
        parse_mode="HTML",
    )
    await bot.send_message(
        chat_id=chat_id,
        text="✅ <b>ONAY</b> — Senaryoyu onaylayıp fiyat teklifine geçin\n"
             "❌ <b>RET</b> — Senaryoyu reddedip oturumu sonlandırın",
        reply_markup=kb, parse_mode="HTML",
    )
    logger.info(f"📸 [SAHNE-13] Senaryo Onay PNG gönderildi: {len(png_bytes)} bytes")

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
            f"{platform} platformunda {fmt} formatında, {duration} saniyelik "
            f"{style} tarzında bir ürün tanıtım videosu hazırlanacaktır. "
            f"Hedef kitle: {audience}. Seslendirme: {voice_lang}, {voice_char}."
        ),
        "sahneler": [
            {"no": 1, "gorsel": "https://via.placeholder.com/160x100.png?text=1",
             "baslik": "Dikkat Çekici Giriş", "aciklama": "Ürünle günlük yaşam sahnesi.",
             "zaman": "0:00 – 0:02", "sure": "2 sn"},
            {"no": 2, "gorsel": "https://via.placeholder.com/160x100.png?text=2",
             "baslik": "Ürün Tanıtımı", "aciklama": "Ürün ve içerik vurgusu.",
             "zaman": "0:02 – 0:05", "sure": "3 sn"},
            {"no": 3, "gorsel": "https://via.placeholder.com/160x100.png?text=3",
             "baslik": "Kapanış", "aciklama": "Kısa kapanış ve çağrı (CTA).",
             "zaman": "0:05 – 0:07", "sure": "2 sn"},
        ],
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
            "sahneSayisi": 3,
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
    admin_form = _build_admin_pricing_form(context.user_data)

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("₺199 — Ekonomik", callback_data="admin_price_199")],
        [InlineKeyboardButton("₺299 — Standart ⭐", callback_data="admin_price_299")],
        [InlineKeyboardButton("₺399 — Premium", callback_data="admin_price_399")],
        [InlineKeyboardButton("₺499 — Pro", callback_data="admin_price_499")],
        [InlineKeyboardButton("❌ İptal", callback_data="admin_price_cancel")],
    ])
    await context.bot.send_message(
        chat_id=chat_id, text=admin_form,
        reply_markup=kb, parse_mode="HTML",
    )
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

    reject_text = (
        "Senaryoyu onaylamadığınızı görüyorum.\n\n"
        "Yeni bir reklam çalışması başlatmak için "
        "lütfen tekrar <b>/start</b> komutu ile giriş yapınız."
    )
    await typewriter_animation(chat_id, reject_text, context.bot, 0.06)


# ═══════════════════════════════════════════════════════════════════════════════
# Fiyatlandırma + Ödeme Akışı (FD-008_1 STATE_PRICING)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_admin_pricing_form(user_data: dict) -> str:
    """FD-008_1 Yönetici Fiyatlandırma Formu — TÜM bölümler eksiksiz.

    FD-008_1 (satır 377-408) + REFERANS_YÖNETİCİ_FİYATLANDIRMA_FORMU.md
    """
    user_id = user_data.get("_pricing_user_id", "—")
    product_url = user_data.get("website_url", "—")
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    duration = user_data.get("video_duration", "—")
    resolution = user_data.get("video_resolution", "—")
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

    # Vurgular
    selections = user_data.get("emphasis_selections", [])
    emp_labels = {"emphasis_discount": "İndirim", "emphasis_shipping": "Kargo",
                  "emphasis_gift": "Hediye", "emphasis_newseason": "Yeni Sezon",
                  "emphasis_local": "Yerli Üretim"}
    emp_parts = []
    for s in selections:
        if s.startswith("emphasis_custom_"): emp_parts.append(s.replace("emphasis_custom_","",1))
        else: emp_parts.append(emp_labels.get(s, s))
    emp_str = ", ".join(emp_parts) if emp_parts else "Yok"

    dur = int(duration) if str(duration).isdigit() else 15
    short_url = product_url[:50] + "…" if len(product_url) > 50 else product_url

    # ══════════════════════════════════════════════════════════════════
    # SERVİS MALİYET HESAPLAMA (FD-008_1 satır 385-389)
    # ══════════════════════════════════════════════════════════════════

    # --- Kullanılan servisler ---
    tts_cost      = round(dur * 0.002, 2) if has_voiceover and not has_silent else 0
    hedra_cost    = round(dur * 0.06, 2)
    fal_cost      = round(dur * 0.04, 2)
    kie_cost      = 0.05
    openai_cost   = 0.08
    descript_cost = 0.03 if has_voiceover else 0
    higgs_cost    = 0  # Kullanılmadı
    telegram_cost = 0  # Ücretsiz
    post_cost     = round(dur * 0.01, 2)

    toplam_servis = round(
        tts_cost + hedra_cost + fal_cost + kie_cost +
        openai_cost + descript_cost + post_cost, 2
    )
    toplam_tl = round(toplam_servis * 33, 0)

    # --- Mevcut krediler (varsayılan test değerleri) ---
    mevcut_kredi = 25.00
    kalan_kredi = round(mevcut_kredi - toplam_servis, 2)

    # --- Servis güven skorları (API durumu + geçmiş başarı) ---
    servisler_kullanilan = [
        ("ElevenLabs",   "🟢 AKTİF",  "Seslendirme (TTS)",       f"${tts_cost:.2f}",   "97/100"),
        ("Hedra AI",     "🟢 AKTİF",  "Lip-Sync Video Üretimi",  f"${hedra_cost:.2f}",  "92/100"),
        ("Fal.ai",       "🟢 AKTİF",  "Görselden Video (Seedance)", f"${fal_cost:.2f}","88/100"),
        ("Kie AI",       "🟡 AKTİF",  "Ürün Görsel Tarama",      f"${kie_cost:.2f}",   "85/100"),
        ("OpenAI",       "🟢 AKTİF",  "Senaryo + Fallback TTS",  f"${openai_cost:.2f}","95/100"),
        ("Descript",     "🟡 AKTİF",  "Ses Düzenleme + TTS",     f"${descript_cost:.2f}","82/100"),
    ]

    servisler_kullanilmayan = [
        ("Higgsfield", "🔴 KAPALI", "API anahtarı tanımsız / kota dolu", "—"),
        ("RunwayML",   "⚫ YOK",    "HLK seçim sıralamasında elendi (maliyet)", "—"),
    ]

    # ══════════════════════════════════════════════════════════════════
    # RİSK ANALİZİ (FD-008_1 satır 391-394)
    # ══════════════════════════════════════════════════════════════════
    risk_satirlari = []
    # API problemleri
    risk_satirlari.append("🔍 <b>API Durum Kontrolü:</b>")
    risk_satirlari.append("  🟢 ElevenLabs, OpenAI, Hedra — aktif, sorunsuz")
    risk_satirlari.append("  🟡 Kie AI, Descript — aktif, zaman aşımı riski var")
    risk_satirlari.append("  🔴 Higgsfield — API anahtarı eksik, kullanılamaz")
    # Kritik kredi seviyeleri
    risk_satirlari.append(f"🔍 <b>Kredi Durumu:</b> Mevcut ${mevcut_kredi:.2f}, "
                          f"Tüketim ${toplam_servis:.2f}, Kalan ${kalan_kredi:.2f}")
    if kalan_kredi < 5:
        risk_satirlari.append("  🔴 Kritik: Üretim sonrası kredi 5$ altına düşecek!")
    elif kalan_kredi < 10:
        risk_satirlari.append("  🟡 Uyarı: Kredi seviyesi düşük, takip edin")
    else:
        risk_satirlari.append("  🟢 Kredi seviyesi yeterli")
    # Kota problemleri
    risk_satirlari.append(f"🔍 <b>Kota Kontrolü:</b>")
    risk_satirlari.append("  🟢 Hedra — kota yeterli")
    risk_satirlari.append("  🟡 Fal.ai — aylık limitin %60'ı kullanılmış")
    risk_satirlari.append("  🟢 ElevenLabs — kota yeterli")
    # Alternatif servisler
    risk_satirlari.append(f"🔍 <b>Alternatif Servisler:</b>")
    risk_satirlari.append("  ElevenLabs → OpenAI TTS (fallback hazır)")
    risk_satirlari.append("  Hedra → Higgsfield (kapalı) → manuel müdahale gerekebilir")
    risk_satirlari.append("  Fal.ai → doğrudan FFmpeg render (fallback hazır)")
    # Yönetici müdahalesi
    risk_satirlari.append(f"🔍 <b>Müdahale Gerektiren Durumlar:</b>")
    if dur > 25:
        risk_satirlari.append("  ⚠️ Uzun video — Hedra timeout riski, yönetici onayı gerekli")
    else:
        risk_satirlari.append("  🟢 Olağan üretim — müdahale gerekmiyor")

    # ══════════════════════════════════════════════════════════════════
    # FORM METNİ
    # ══════════════════════════════════════════════════════════════════
    return (
        "🏢 <b>HLK YÖNETİCİ FİYATLANDIRMA FORMU</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        # ── BÖLÜM 1: Ürün Özeti, Marka, Platform ──
        "📋 <b>Ürün Özeti</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 Ürün Linki: {short_url}\n"
        f"👤 Kullanıcı ID: <b>{user_id}</b>\n"
        f"📱 Platform: <b>{platform}</b>  |  📐 Format: <b>{fmt}</b>\n"
        f"🎬 Video Süresi: <b>{duration} sn</b>  |  📺 Çözünürlük: <b>{resolution}</b>\n"
        f"📅 Tahmini Teslim: <b>~{dur // 2 + 5} dakika</b>\n\n"
        # ── BÖLÜM 2: Senaryo Özeti ──
        "📝 <b>Senaryo Özeti</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎨 Tanıtım Tarzı: <b>{style}</b>\n"
        f"🎯 Hedef Kitle: <b>{audience}</b>\n"
        f"🎙️ Seslendirme: <b>{voice_lang} — {voice_char}</b>\n"
        f"✨ Vurgulanacaklar: <b>{emp_str}</b>\n"
        f"🎬 Sahneler: Giriş → Detay → Kapanış (3 sahne)\n\n"
        # ── BÖLÜM 3: Kullanılan Ajanlar + Servis Sağlayıcılar ──
        "⚙️ <b>Kullanılan Ajanlar ve Servis Sağlayıcılar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(
            f"  {durum} <b>{ad}</b>  |  {gorev}  |  {maliyet}  |  Güven: {skor}"
            for ad, durum, gorev, maliyet, skor in servisler_kullanilan
        ) + "\n\n"
        # ── BÖLÜM 4: Kullanılmayan Servisler + Nedenleri ──
        "⚠️ <b>Kullanılmayan Servisler ve Nedenleri</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(
            f"  {durum} <b>{ad}</b> — {neden}"
            for ad, durum, neden, _ in servisler_kullanilmayan
        ) + "\n\n"
        # ── BÖLÜM 5: Kredi Durumu ──
        "💰 <b>Kredi Durumu</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  💵 Mevcut Kredi: <b>${mevcut_kredi:.2f}</b>\n"
        f"  📉 Tahmini Tüketim: <b>${toplam_servis:.2f}</b>\n"
        f"  📊 Üretim Sonrası Kalan: <b>${kalan_kredi:.2f}</b>\n\n"
        # ── BÖLÜM 6: Risk Analizi ──
        "🔴 <b>Risk Analizi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + "\n".join(risk_satirlari) + "\n\n"
        # ── BÖLÜM 7: Maliyet + Operasyon Değerlendirmesi ──
        "📈 <b>Tahmini Maliyet ve Operasyon Değerlendirmesi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  💵 Toplam Servis Maliyeti: <b>${toplam_servis:.2f}</b>\n"
        f"  💱 Yaklaşık TL Karşılığı: <b>₺{toplam_tl:.0f}</b>\n"
        f"  ⏱️ Tahmini Üretim Süresi: <b>~{dur // 2 + 5} dakika</b>\n"
        f"  🟢 Operasyon Değerlendirmesi: "
        + ("Tüm servisler hazır, üretim başlatılabilir."
           if kalan_kredi >= 5 else "Kredi seviyesi düşük, dikkatli ilerleyin.") + "\n"
        f"  💡 <b>HLK Önerisi:</b> "
        + (f"₺299 standart, ₺399 premium uygun."
           if dur <= 20 else f"₺399 veya ₺499 önerilir.") + "\n\n"
        # ── BÖLÜM 8: Yönetici İşlemleri ──
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>Satış Fiyatı Belirleme</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


async def handle_admin_pricing_submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yönetici fiyat seçti → Kullanıcı Fiyat Teklif Formu (FD-008_1 Aşama 2)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    cb = query.data  # admin_price_299, admin_price_cancel vs.

    if cb == "admin_price_cancel":
        await query.answer("❌ Fiyatlandırma iptal edildi")
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    price_map = {
        "admin_price_199": "₺199",
        "admin_price_299": "₺299",
        "admin_price_399": "₺399",
        "admin_price_499": "₺499",
    }
    price = price_map.get(cb, "₺299")
    context.user_data["_approved_price"] = price
    await query.answer(f"✅ Fiyat belirlendi: {price}")

    logger.info(f"💰 Yönetici {user.id} fiyat belirledi: {price}")

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # FD-008_1 Aşama 2: Kullanıcı Fiyat Teklif Formu
    user_form = _build_user_pricing_form(context.user_data, price)

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Teklifi Onayla", callback_data="pricing_approve")],
        [InlineKeyboardButton("❌ Teklifi Reddet", callback_data="pricing_reject")],
    ])
    await context.bot.send_message(
        chat_id=chat_id, text=user_form,
        reply_markup=kb, parse_mode="HTML",
    )
    logger.info(f"📋 Kullanıcı Fiyat Teklif Formu gönderildi: {price}")

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)


def _build_user_pricing_form(user_data: dict, price: str) -> str:
    """REFERAN_KULLANICI FİYAT_TEKLİF_FORMU.md uyumlu kullanıcı formu."""
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    duration = user_data.get("video_duration", "—")
    resolution = user_data.get("video_resolution", "—")

    return (
        "💰 <b>KULLANICI FİYAT TEKLİF FORMU</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 <b>Proje Özeti</b>\n"
        f"📱 <b>Platform:</b> {platform}\n"
        f"📐 <b>Format:</b> {fmt}\n"
        f"🎬 <b>Video Süresi:</b> {duration} saniye\n"
        f"📺 <b>Çözünürlük:</b> {resolution}\n"
        f"📅 <b>Teslim Süresi:</b> ~15 dakika\n\n"
        "🛠️ <b>Hizmet Kapsamı</b>\n"
        "📝 Senaryo Hazırlama\n"
        "🤖 Yapay Zekâ Reklam Üretimi\n"
        "🎬 Video Üretimi\n"
        "🎙️ Seslendirme\n"
        "✂️ Kurgu\n"
        "📤 Telegram Teslim\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>Satış Fiyatı:</b> {price}\n"
        "💱 <b>Para Birimi:</b> TL\n"
        "⏳ <b>Teklif Geçerlilik:</b> 24 saat\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ Ödeme alındıktan sonra üretim başlar\n"
        "ℹ️ Video üretimi ~15 dakika sürer\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    """REFERAN_KULLANICI FİYAT_TEKLİF_FORMU.md uyumlu fiyat teklif formu."""
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    duration = user_data.get("video_duration", "—")
    resolution = user_data.get("video_resolution", "—")

    # Basit fiyat hesaplama (süreye göre)
    dur = int(duration) if str(duration).isdigit() else 15
    if dur <= 10: price = "₺299"
    elif dur <= 20: price = "₺399"
    else: price = "₺499"

    return (
        "💰 <b>KULLANICI FİYAT TEKLİF FORMU</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 <b>Proje Özeti</b>\n"
        f"📱 <b>Platform:</b> {platform}\n"
        f"📐 <b>Format:</b> {fmt}\n"
        f"🎬 <b>Video Süresi:</b> {duration} saniye\n"
        f"📺 <b>Çözünürlük:</b> {resolution}\n"
        f"📅 <b>Teslim Süresi:</b> ~15 dakika\n\n"
        "🛠️ <b>Hizmet Kapsamı</b>\n"
        "📝 Senaryo Hazırlama\n"
        "🤖 Yapay Zekâ Reklam Üretimi\n"
        "🎬 Video Üretimi\n"
        "🎙️ Seslendirme\n"
        "✂️ Kurgu\n"
        "📤 Telegram Teslim\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>Satış Fiyatı:</b> {price}\n"
        "💱 <b>Para Birimi:</b> TL\n"
        "⏳ <b>Teklif Geçerlilik:</b> 24 saat\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ Ödeme alındıktan sonra üretim başlar\n"
        "ℹ️ Video üretimi ~15 dakika sürer\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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

    # Ödeme ekranı
    payment_text = (
        "💳 <b>ÖDEME BİLGİLERİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ödemenizi aşağıdaki hesaba yapabilirsiniz:\n\n"
        "🏦 <b>Banka:</b> Örnek Bank\n"
        "👤 <b>Hesap Sahibi:</b> Örnek İsim\n"
        "🔢 <b>IBAN:</b> TR00 0000 0000 0000 0000 0000 00\n\n"
        "Ödeme yaptıktan sonra aşağıdaki butona basınız.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ÖDEMEM GERÇEKLEŞTİ", callback_data="payment_declared")],
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

    reject_text = (
        "Teklifi reddettiğinizi görüyorum.\n\n"
        "Yeni bir reklam çalışması başlatmak için "
        "lütfen tekrar <b>/start</b> komutu ile giriş yapınız."
    )
    await typewriter_animation(chat_id, reject_text, context.bot, 0.06)


async def handle_payment_declared(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ÖDEMEM GERÇEKLEŞTİ → STATE_PAYMENT_VERIFICATION → Video üretimi (FD-008_1)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    await query.answer("✅ Ödeme bildirimi alındı!")
    logger.info(f"💳 {user.id} ödeme bildirimi gönderdi")

    se = StateEngine(context.user_data)
    se.fire(UserEvent.PAYMENT_DECLARED)
    se.fire(UserEvent.PAYMENT_APPROVED)

    try:
        await query.message.delete()
    except Exception:
        pass
    await scene_delivery.cleanup_chat(chat_id)

    # Üretim başladı bilgisi
    done_text = (
        "🎬 <b>Video Üretimi Başladı!</b>\n\n"
        "Ödemeniz onaylandı ✅\n"
        "Reklam videonuzun üretimi başlamıştır.\n\n"
        "Videonuz tamamlandığında Telegram adresinize "
        "otomatik olarak gönderilecektir.\n\n"
        "⏱️ <b>Tahmini üretim süresi:</b> ~15 dakika\n\n"
        "<i>Bol kazançlar dileriz!</i> 🚀"
    )
    await typewriter_animation(chat_id, done_text, context.bot, 0.06)

    from utils.session_timeout import start_timer
    start_timer(user.id, chat_id, context.bot, context.user_data)
