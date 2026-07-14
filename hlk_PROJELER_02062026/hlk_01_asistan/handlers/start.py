"""Telegram /start komutunun handler'ı."""

import asyncio
import hashlib
import logging
import os
import re
import threading
import time
from pathlib import Path

from dotenv import set_key
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from utils.state_engine import StateEngine, UserState, UserEvent
from utils.session_timeout import start_timer, cancel_timer
from utils.scene_lock import SceneLock, SceneLockState
from helpers.typewriter_animation import typewriter_animation, strip_html
from services.voice_generator import ahu_voice_generator

# CEE + EEC + Olay Kayıt Merkezi entegrasyonu
from services.constitution_enforcement import constitution_enforcement
from services.execution_event_collector import (
    execution_event_collector, EECEventType, ExecutionPhase,
)
from services.olay_kayit_merkezi import event_registry

# GC-001: Merkezi video path yapılandırması (hardcoded path yok)
from config.video_paths import (
    SAHNE1_VIDEO, SAHNE1_SURE,
    SAHNE2_DIR, SAHNE2_VIDEO_TEMPLATE,
    SAHNE2_SURE, SAHNE2_SURE_LANG, SAHNE2_FALLBACK_LANG,
    SAHNE2_EXTRA_WAIT, BALLOON_STAGGER_DELAY,
    SES_SAHNE2_DIR, SES_SAHNE2_TEMPLATE,
    get_sahne1_video, get_sahne2_video, get_sahne2_audio,
)

logger = logging.getLogger(__name__)

# ── HLK Admin Sohbet ────────────────────────────────────────────────────
HLK_ADMIN_SYSTEM = """Sen HLK'nın Yönetici Asistanısın. Bu ekran SADECE yöneticiye gönderilir.

KESİN KURALLAR:
1. SADECE yukaridaki VERILERI kullan. Sistem bilgisi disinda TAHMIN YAPMA.
2. HLK URETIM SISTEMI bolumunde yazan bilgiler haricinde cevap UYDURMA.
3. Tum fiyatlar USD. TL karsiligi TCMB kuruyla hesaplanir. Birim BELIRT ($/TL).
4. Bilmedigin seye "Bu bilgi sistemde mevcut degil" de.
5. Kisa, net, en fazla 3 cumle. SOMUT rakam kullan.
6. Yonetici bilgilenmek icin sorar — dogru ve aciklayici cevap ver."""

def _build_admin_context(user_data: dict, user_msg: str) -> str:
    """Yönetici sohbeti için üretim bağlamını oluşturur."""
    url = user_data.get("website_url", "—")
    product_name = url.split("/")[-1] if "/" in url else "—"
    brand = user_data.get("brand", "—")
    platform = user_data.get("platform", "—")
    fmt = user_data.get("video_format", "—")
    resolution = user_data.get("video_resolution", "—")
    duration = user_data.get("video_duration", "—")
    style = user_data.get("ad_style", "—")
    audience = user_data.get("target_audience", "—")
    voice_lang = user_data.get("voice_language", "—")
    voice_char = user_data.get("voice_character", "—")

    # Gercek fiyat verileri
    katsayi = user_data.get("_admin_katsayi", "1.0")
    toplam = user_data.get("_computed_toplam", "—")
    yonetici_fiyat = user_data.get("_computed_yonetici_fiyat", "—")
    kdvli = user_data.get("_computed_kdvli", "—")

    # TCMB kurunu al (website.py'deki fonksiyon)
    try:
        from handlers.website import _get_tcmb_kur
        tcmb = _get_tcmb_kur()
    except Exception:
        tcmb = 47.0

    try:
        tl_karsilik = round(float(kdvli) * tcmb, 2) if kdvli != "—" else "—"
    except (ValueError, TypeError):
        tl_karsilik = "—"

    return (
        f"Bu bir YONETICI FIYATLANDIRMA EKRANIDIR. Kullaniciya GONDERILMEZ.\n\n"
        f"=== GUNCEL URETIM BILGILERI ===\n"
        f"URUN: {brand} — {product_name}\n"
        f"PLATFORM: {platform} | FORMAT: {fmt} | COZUNURLUK: {resolution}\n"
        f"VIDEO SURESI: {duration} sn | TARZ: {style}\n"
        f"HEDEF KITLE: {audience}\n"
        f"SES: {voice_lang} / {voice_char}\n\n"
        f"=== FIYATLANDIRMA VERILERI (GERCEK) ===\n"
        f"Yonetici Katsayisi: {katsayi}\n"
        f"Toplam Servis Bedeli (USD): ${toplam}\n"
        f"Yonetici Belirledigi Fiyat (USD): ${yonetici_fiyat}\n"
        f"KDV Dahil Teklif Fiyati (USD): ${kdvli}\n"
        f"TCMB USD Satis Kuru: {tcmb} TL\n"
        f"KDV Dahil TL Karsiligi: {tl_karsilik} TL\n\n"
        f"=== HLK URETIM SISTEMI (SADECE BU BILGILERI KULLAN) ===\n"
        f"AJAN SECIMI: HLK, urun kategorisine en uygun arastirma ajanlarini dinamik olarak secer. "
        f"Ajan seçim kriterleri: urun kategorisine uygunluk, arastirma kalitesi, teknolojik yeterlilik, "
        f"dogruluk, guvenilirlik, hiz, kaynak cesitliligi, guncellik ve maliyet. "
        f"Amac en ucuz degil, en yuksek kalite/fayda oranini saglamaktir (AR-002_2).\n"
        f"SENARYO: Arastirma ciktilari kullanilarak hedef kitleye ozel tonlamayla senaryo olusturulur. "
        f"Sahne sayisi video suresine gore dinamik belirlenir (4-10sn→3, 11-20sn→4, 21+sn→5 sahne).\n"
        f"SES: ElevenLabs TTS API kullanilir. Ses karakteri (Kadin/Erkek/Cocuk) secilen dile uygun uretilir. "
        f"MASTER_REFERENCE_VOICE standardina gore tonlama ve ritim HLK tarafindan belirlenir.\n"
        f"VIDEO URETIMI: Production Runtime uzerinden CEE PRE-CHECK → PID → Package → Executor → "
        f"CEE POST-CHECK zinciriyle gerceklesir. Her adim anayasal denetime tabidir.\n"
        f"FIYATLANDIRMA: Servis maliyetleri (API, ses, video uretimi) uzerine yonetici katsayisi ({katsayi}) "
        f"uygulanarak hesaplanir. KDV dahil nihai fiyat TCMB kuruyla TL'ye cevrilir.\n"
        f"TEKNIK: Python 3.14 + Telegram Bot API + OpenAI GPT-4o + ElevenLabs TTS + Fal.ai Seedance.\n\n"
        f"=== YONETICI SORUSU ===\n"
        f"{user_msg}"
    )


async def _hlk_admin_chat(user_msg: str, user_data: dict) -> str:
    """HLK'ya admin sorusu sor, OpenAI API'den cevap al.

    Uretim baglami (urun, platform, format, fiyat vb.) ile birlikte gonderilir.
    """
    try:
        import openai
    except ImportError:
        return "HLK API kütüphanesi yüklü değil."
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "API anahtarı bulunamadı."
    try:
        context_msg = _build_admin_context(user_data, user_msg)
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o", max_tokens=300, temperature=0.0,
            messages=[
                {"role": "system", "content": HLK_ADMIN_SYSTEM},
                {"role": "user", "content": context_msg},
            ],
        )
        return resp.choices[0].message.content or "—"
    except Exception as e:
        return f"HLK yanıt veremedi: {e}"

# Daktilo yazısı mesajları (HTML format — <b>HLK</b> bold)
TYPEWRITER_MESSAGES = {
    "tr": "Merhaba! Ben <b>HLK</b>, <b><i>yapay zeka destekli</i></b> reklam asistanınız. Ürününüz için <b>en iyi reklamı</b> üretmek üzereyim. Başlamadan önce size <b><i>birkaç kısa sorum</i></b> olacak.",
    "en": "Hello! I'm <b>HLK</b>, your <b><i>AI-powered</i></b> ad assistant. I'm here to create the <b>best ads</b> for your products. Before we start, I have a <b><i>few quick questions</i></b> for you.",
    "fr": "Bonjour! Je suis <b>HLK</b>, votre assistant publicitaire <b><i>alimenté par l'IA</i></b>. Je suis là pour créer les <b>meilleures publicités</b> pour vos produits. Avant de commencer, j'ai <b><i>quelques questions rapides</i></b> pour vous.",
    "de": "Hallo! Ich bin <b>HLK</b>, Ihr <b><i>KI-gestützter</i></b> Werbeassistent. Ich bin hier, um die <b>besten Anzeigen</b> für Ihre Produkte zu erstellen. Bevor wir beginnen, habe ich <b><i>ein paar schnelle Fragen</i></b> für Sie.",
    "es": "¡Hola! Soy <b>HLK</b>, tu asistente publicitario <b><i>impulsado por IA</i></b>. Estoy aquí para crear los <b>mejores anuncios</b> para tus productos. Antes de comenzar, tengo <b><i>algunas preguntas rápidas</i></b> para ti.",
    "ar": "مرحبا! أنا <b>HLK</b>، مساعدك الإعلاني <b><i>المدعوم بالذكاء الاصطناعي</i></b>. أنا هنا لإنشاء <b>أفضل الإعلانات</b> لمنتجاتك. قبل أن نبدأ، لدي <b><i>بعض الأسئلة السريعة</i></b> لك.",
    "ru": "Привет! Я <b>HLK</b>, ваш рекламный ассистент <b><i>на основе ИИ</i></b>. Я здесь, чтобы создать <b>лучшую рекламу</b> для ваших продуктов. Прежде чем начать, у меня есть <b><i>несколько быстрых вопросов</i></b> для вас.",
    "kr": "Merheba! Ez <b>HLK</b> me, <b><i>AI-ê rênivîsbariya</i></b> reklamê alîkarê we me. Ez li vir im ji bo hilberîna we <b>baştirîn reklamê</b> çêdikim. Berî ku em dest pê bikin, <b><i>çend pirsên kurt</i></b> hene.",
}

# Web sitesi linki isteme mesajı
LINK_REQUEST_MESSAGE = {
    "tr": "Lütfen ürünün <b>web sitesi linkini</b> veya <b><i>ürün linkini</i></b> gönderin.",
    "en": "Please send your <b>product website link</b> or <b><i>product link</i></b>.",
    "fr": "Veuillez envoyer le <b>lien du site Web</b> de votre produit ou le <b><i>lien du produit</i></b>.",
    "de": "Bitte senden Sie den <b>Link der Produktwebsite</b> oder den <b><i>Produktlink</i></b>.",
    "es": "Por favor, envía el <b>enlace del sitio web</b> del producto o el <b><i>enlace del producto</i></b>.",
    "ar": "يرجى إرسال <b>رابط موقع المنتج</b> أو <b><i>رابط المنتج</i></b>.",
    "ru": "Пожалуйста, отправьте <b>ссылку на сайт товара</b> или <b><i>ссылку на продукт</i></b>.",
    "kr": "Ji kerema xwe <b>rêjeya malpera hilberînê</b> an <b><i>rêjeya hilberînê</i></b> bişînin.",
}

# ═══════════════════════════════════════════════════════════════════════════════
# Video path'leri ve süreler — GC-001: config/video_paths.py merkezî kaynak
# Hiçbir yerde ham path string'i tekrar edilmez (MASTER-001, MASTER-003)
# ═══════════════════════════════════════════════════════════════════════════════

# Video altında ses uyarısı
SESLI_HINT = {
    "tr": "🔊 <b><i>Sesli izlemek için lütfen video üzerine dokunuz.</i></b>",
    "en": "🔊 <b><i>Please touch on the video to watch with sound.</i></b>",
    "fr": "🔊 <b><i>Veuillez toucher la vidéo pour regarder avec le son.</i></b>",
    "de": "🔊 <b><i>Bitte berühren Sie das Video, um es mit Ton zu sehen.</i></b>",
    "es": "🔊 <b><i>Por favor toca el video para verlo con sonido.</i></b>",
    "ar": "🔊 <b><i>يرجى لمس الفيديو للمشاهدة مع الصوت.</i></b>",
    "ru": "🔊 <b><i>Пожалуйста, коснитесь видео, чтобы смотреть со звуком.</i></b>",
    "kr": "🔊 <b><i>Ji bo bi deng temaşekirinê, ji kerema xwe li vîdyoyê bikîte.</i></b>",
}


def _get_scene2_path(language: str) -> Path | None:
    """Dile göre orijinal Hedra video yolunu döndürür. Yoksa None.

    GC-001: Merkezi path yapılandırması kullanılır (config/video_paths.py).
    """
    return get_sahne2_video(language)


ENV_PATH = Path(__file__).parent.parent / ".env"

# Runtime cache — process ömrü boyunca tutulur
_intro_video_file_id: str | None = None


def _get_cached_file_id() -> str | None:
    """Önce process cache, sonra env değişkeni."""
    global _intro_video_file_id
    if _intro_video_file_id:
        return _intro_video_file_id
    val = os.getenv("INTRO_VIDEO_FILE_ID", "").strip().strip("'").strip('"')
    if val:
        _intro_video_file_id = val
        logger.info("📦 Cached file_id env'den yüklendi")
        return val
    return None


def _persist_file_id(file_id: str) -> None:
    """file_id'yi runtime cache'e, env'e ve .env dosyasına yaz."""
    global _intro_video_file_id
    _intro_video_file_id = file_id
    os.environ["INTRO_VIDEO_FILE_ID"] = file_id
    try:
        if ENV_PATH.exists():
            set_key(str(ENV_PATH), "INTRO_VIDEO_FILE_ID", file_id)
            logger.info("💾 INTRO_VIDEO_FILE_ID .env'e kaydedildi")
    except Exception as e:
        logger.warning(f"⚠️ .env yazılamadı (Railway/production:normal): {e}")


async def _send_intro_video(update: Update, reply_markup: InlineKeyboardMarkup | None = None, caption: str = "HLK AI Asistan") -> bool:
    """
    Tanıtım videosunu gönder. file_id varsa onunla, yoksa dosyadan yükle.

    Returns:
        Başarılı ise True
    """
    intro_path = get_sahne1_video()
    logger.info(f"📹 _send_intro_video çağrıldı, path: {intro_path}")
    if not intro_path.exists():
        logger.error(f"❌ Tanıtım videosu bulunamadı: {intro_path}")
        return False

    cached_file_id = _get_cached_file_id()
    try:
        if cached_file_id:
            logger.info(f"⚡ file_id cache'den gönderiliyor")
            msg = await update.message.reply_video(
                video=cached_file_id,
                caption=caption,
                parse_mode="HTML",
                supports_streaming=True,
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            logger.info(f"📤 Dosyadan video yükleniyor: {intro_path}")
            with open(intro_path, "rb") as video:
                msg = await update.message.reply_video(
                    video=video,
                    caption=caption,
                    parse_mode="HTML",

                    reply_markup=ReplyKeyboardRemove(),
                    write_timeout=60,
                    read_timeout=60,
                    connect_timeout=30,
                )

        new_file_id = None
        for attr in ("video", "animation", "video_note", "document"):
            attachment = getattr(msg, attr, None)
            if attachment and hasattr(attachment, "file_id"):
                new_file_id = attachment.file_id
                logger.info(f"📎 file_id {attr} üzerinden alındı")
                break

        if not new_file_id:
            logger.error(f"❌ file_id alınamadı — msg dict: {msg.to_dict()}")
        else:
            if not cached_file_id:
                logger.info(f"✅ Video dosyadan yüklendi, file_id cache'e kaydedildi: {new_file_id}")
                _persist_file_id(new_file_id)
        await asyncio.sleep(SAHNE1_SURE)
        try:
            await msg.delete()
        except:
            pass
        return True
    except Exception as e:
        logger.error(f"❌ Video gönderilemedi: {e}", exc_info=True)
        return False


async def _auto_delete_after(message_id: int, chat_id: int, delay: int, bot) -> None:
    """Bir mesaji N saniye sonra siler."""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


def _get_typewriter_text(language: str, key: str = "welcome") -> str:
    """Dile göre typewriter mesajını döndürür."""
    if key == "link_request":
        return LINK_REQUEST_MESSAGE.get(language, LINK_REQUEST_MESSAGE["tr"])
    return TYPEWRITER_MESSAGES.get(language, TYPEWRITER_MESSAGES["tr"])


def _measure_mp3_duration(filepath: Path) -> float:
    """ffprobe ile bir MP3 dosyasının süresini ölçer."""
    import subprocess
    if not filepath.exists():
        return 0.0
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(filepath)],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0.0


async def _deliver_text_only(
    chat_id: int,
    text: str,
    bot,
) -> int | None:
    """Sadece daktilo — sabit akıcı hız, ses yok, takılma yok.
    Returns: typewriter mesajinin message_id'si veya None."""
    logger.info(f"✏️ Daktilo basliyor")
    msg_id = await typewriter_animation(chat_id, text=text, bot=bot, delay=0.06)
    logger.info(f"✅ Daktilo tamam")
    return msg_id


async def _scout_all_formats(
    chat_id: int,
    language: str,
    bot,
    text: str,
) -> None:
    """SCOUT: Telegram'daki tüm ses formatlarını tek akışta göster (sadece TR)."""
    from io import BytesIO

    logger.info(f"🔍 SCOUT: Telegram ses formatlari gosteriliyor...")

    audio_path = None
    try:
        audio_path = ahu_voice_generator.generate(text=text, language=language)
    except:
        pass

    if not audio_path:
        await bot.send_message(chat_id=chat_id, text="❌ Ses uretilemedi")
        return

    audio_bytes = audio_path.read_bytes()
    audio_dur = int(_measure_mp3_duration(audio_path) or 4)

    # ─── 1️⃣ Voice ───
    await bot.send_message(chat_id=chat_id,
        text="📞 <b>1️⃣ Voice</b>  <code>sendVoice()</code>\nMavi balon, tiklayinca calar",
        parse_mode="HTML")
    await asyncio.sleep(0.5)
    await bot.send_voice(chat_id=chat_id, voice=BytesIO(audio_bytes))
    await asyncio.sleep(0.7)

    # ─── 2️⃣ Audio ───
    await bot.send_message(chat_id=chat_id,
        text="🎵 <b>2️⃣ Audio</b>  <code>sendAudio()</code>\nKapak resimli muzik balonu",
        parse_mode="HTML")
    await asyncio.sleep(0.5)
    await bot.send_audio(chat_id=chat_id, audio=BytesIO(audio_bytes),
        title="HLK Reklam Asistani", performer="AHU", duration=audio_dur)
    await asyncio.sleep(0.7)

    # ─── 3️⃣ Video ───
    await bot.send_message(chat_id=chat_id,
        text="🎬 <b>3️⃣ Video</b>  <code>sendVideo()</code>\nGoruntu oynar, ses MUTE (tucluda duyulur)",
        parse_mode="HTML")
    await asyncio.sleep(0.5)
    proto_path = get_proto_video("tr")
    if proto_path.exists():
        with open(proto_path, "rb") as vf:
            await bot.send_video(chat_id=chat_id, video=vf, width=720, height=1280, duration=audio_dur)
    await asyncio.sleep(0.7)

    # ─── 4️⃣ Document ───
    await bot.send_message(chat_id=chat_id,
        text="📄 <b>4️⃣ Document</b>  <code>sendDocument()</code>\nDosya balonu, indir/tikla gerekir",
        parse_mode="HTML")
    await asyncio.sleep(0.5)
    await bot.send_document(chat_id=chat_id, document=BytesIO(audio_bytes), filename=f"ahu_{language}.mp3")
    await asyncio.sleep(0.7)

    # ─── 5️⃣ Text (current) ───
    await bot.send_message(chat_id=chat_id,
        text="📝 <b>5️⃣ Text</b> (su anki sistem)\nSadece daktilo yazisi, ses balonu yok",
        parse_mode="HTML")
    await asyncio.sleep(0.3)
    await typewriter_animation(chat_id, text=text, bot=bot, delay=0.08)

    # ─── Secim ───
    await bot.send_message(chat_id=chat_id,
        text="━━━━━━━━━━━━━━━━\n📊 <b>Hangi formati kullanalim?</b>\n\n"
             "1️⃣ Voice — mavi balon\n"
             "2️⃣ Audio — kapakli\n"
             "3️⃣ Video — sessiz oynar\n"
             "4️⃣ Document — dosya\n"
             "5️⃣ Text — su anki",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1️⃣ Voice", callback_data="fmt_voice"),
             InlineKeyboardButton("2️⃣ Audio", callback_data="fmt_audio")],
            [InlineKeyboardButton("3️⃣ Video", callback_data="fmt_video"),
             InlineKeyboardButton("4️⃣ Document", callback_data="fmt_doc")],
            [InlineKeyboardButton("5️⃣ Text (su anki)", callback_data="fmt_text")],
        ]))


def _get_mp3_duration(language: str) -> float:
    """AHU MP3 dosyasının gerçek süresini ölçer (ffprobe).

    Daktilo animasyonu hızını AHU ses süresine göre dinamik ayarlamak için kullanılır.
    """
    import subprocess

    mp3_path = get_sahne2_audio(language)
    if not mp3_path.exists():
        logger.warning(f"⚠️ MP3 bulunamadi: {mp3_path}, SAHNE2_SURE kullanilacak")
        return float(SAHNE2_SURE_LANG.get(language.upper(), SAHNE2_SURE))

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(mp3_path)],
            capture_output=True, text=True, timeout=10,
        )
        if result.stdout.strip():
            duration = float(result.stdout.strip())
            logger.info(f"🔊 AHU MP3 süresi: {language}={duration:.3f}sn")
            return duration
    except Exception as e:
        logger.warning(f"⚠️ MP3 süre okunamadi: {e}")

    return float(SAHNE2_SURE_LANG.get(language.upper(), SAHNE2_SURE))


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Müşteri /start yazdığında tanıtım videosu + dil seçim butonlarını göster.

    SCENE LOCK (AR-002_44):
        IDLE → LOCKED → PLAYING → COMPLETED → CLEANUP → DONE
        Terminal state sonrası SAHNE-1 yeniden oluşturulamaz.
    """
    user = update.effective_user
    update_id = getattr(update, "update_id", "N/A")

    # ── SCENE LOCK GUARD #1: SAHNE-1 giriş kontrolü ──────────────
    # Sadece IDLE durumunda SAHNE-1 başlatılabilir.
    # LOCKED/PLAYING/COMPLETED/CLEANUP/DONE → ikinci oynatma REDDEDİLİR.
    if not SceneLock.can_enter(context.user_data):
        logger.warning(
            f"🔒 [SCENE_LOCK] SAHNE-1 girişi RED: user={user.id} "
            f"update_id={update_id} state={SceneLock.get_state(context.user_data).value}"
        )
        await update.message.reply_text(
            "⏳ <b>HLK</b> oturumunuz zaten <i>aktif</i>.\n"
            "Devam etmek için lütfen <b>dil seçimi</b> yapın.",
            parse_mode="HTML",
        )
        return  # ← KESİN ENGELLEME: ikinci send_video asla çağrılmaz

    # ── user_data sıfırlama (lock kontrolü SONRASI, state değişimi ÖNCESİ) ──
    # DİKKAT: clear() scene_lock'u siler — bu yüzden lock kontrolü önce yapılır
    # FD-008_1: Kullanıcının /start mesajının ID'sini sakla — temizlik için
    _start_msg_id = update.message.message_id
    context.user_data.clear()
    context.user_data["user_id"] = user.id
    context.user_data["username"] = user.username or user.full_name
    context.user_data["start_msg_id"] = _start_msg_id  # FD-008_1: EKRAN SİLİNİR

    # FD-008_1: /start kullanıcı mesajını temizlik havuzuna kaydet
    # (Telegram botları özel sohbette kullanıcı mesajlarını silemez,
    #  ama ANA YASA gereği deneriz — başarısız olursa debug log atar)
    from services.scene_delivery import scene_delivery as _sd
    _sd.register_user_message(update.effective_chat.id, _start_msg_id)

    # ── SCENE LOCK #2: IDLE → LOCKED (clear sonrası yeniden yazılır) ─────
    SceneLock.set_state(context.user_data, SceneLockState.LOCKED)
    logger.info(f"🚩 [SCENE_CREATED] user={user.id} update_id={update_id}")

    # State Engine — yalnızca 1 kez tetiklenir (lock koruması altında)
    se = StateEngine(context.user_data)
    se.fire(UserEvent.START_INITIATED)
    logger.info(f"🔷 State Engine: {se.current.value} | Aktif modüller: {se.get_active_modules()}")
    context.user_data["state"] = "selecting_language"

    # ── EEC + CEE: Oturum başlangıcı — kullanıcı PID'si ile dinleme ─
    execution_event_collector.listen(pid=str(user.id))
    eec_start = execution_event_collector.emit_event(
        event_type=EECEventType.TASK_STARTED,
        description=f"/start alındı — SAHNE-1 başlatılıyor (user={user.id})",
        related_file="handlers/start.py",
        phase=ExecutionPhase.PRE_CHECK,
    )
    event_registry.register_from_eec(eec_start)

    ctp_s1 = constitution_enforcement.pre_check(
        task_description="SAHNE-1: HLK Karşılama Videosu + Dil Seçimi",
        affected_files=["handlers/start.py"],
        flow_steps=["SAHNE-1 → SCENE_LOCK → Dil_Seçim_Butonları"],
        state_rules=["SE-007_4: START → SCENE_1 → LANGUAGE_SELECTION"],
        expected_outputs=["SAHNE-1 videosu oynatıldı", "Dil seçim butonları gösterildi"],
    )
    logger.info(f"📋 [CEE PRE-CHECK] SAHNE-1 CTP: {ctp_s1.ctp_id}")

    # ── SCENE LOCK #3: LOCKED → PLAYING (video gönderimi öncesi) ─
    SceneLock.set_state(context.user_data, SceneLockState.PLAYING)

    # GC-001: Merkezi path — hardcoded yol yok (MASTER-003 uyumlu)
    video_path = get_sahne1_video()

    # ══════════════════════════════════════════════════════════════════════
    # DEBUG START — video göndermeden HEMEN ÖNCE
    # ══════════════════════════════════════════════════════════════════════
    _dbg_pid = os.getpid()
    _dbg_app_id = id(context.application)
    _dbg_hfunc_id = id(handle_start)
    logger.info("=" * 50)
    logger.info("DEBUG START — Video Gönderme Öncesi")
    logger.info(f"PID              = {_dbg_pid}")
    logger.info(f"Thread ID        = {threading.get_ident()}")
    logger.info(f"Application ID   = {_dbg_app_id}")
    logger.info(f"Handler Function = handle_start")
    logger.info(f"Function ID      = {_dbg_hfunc_id}")
    logger.info(f"Update ID        = {update_id}")
    logger.info(f"Message ID       = {update.message.message_id}")
    logger.info(f"Chat ID          = {update.effective_chat.id}")
    logger.info(f"User ID          = {user.id}")
    logger.info(f"Current State    = {context.user_data.get('state', 'N/A')}")
    logger.info(f"SceneLock State  = {SceneLock.get_state(context.user_data).value}")
    logger.info(f"Timestamp (ms)   = {int(time.time() * 1000)}")
    logger.info("=" * 50)

    # ── DEFANSİF KONTROL (MASTER-003): Dosya yoksa SceneLock temizlenir ──
    if not video_path.exists() or not video_path.is_file():
        logger.error(
            f"❌ [SAHNE-01] Video bulunamadı: {video_path} | "
            f"exists={video_path.exists()}, is_file={video_path.is_file() if video_path.exists() else 'N/A'}"
        )
        # SceneLock temizle: PLAYING → DONE (terminal) — kullanıcı /start ile tekrar dener
        SceneLock.set_state(context.user_data, SceneLockState.COMPLETED)
        SceneLock.set_state(context.user_data, SceneLockState.CLEANUP)
        SceneLock.set_state(context.user_data, SceneLockState.DONE)
        logger.info(f"🔒 [SCENE_LOCK] Defansif temizlik: PLAYING → COMPLETED → CLEANUP → DONE")
        await update.message.reply_text(
            "❌ <b>Sistem başlatılamadı.</b>\n\n"
            "<i>Lütfen daha sonra</i> <b>/start</b> <i>yazarak tekrar deneyin.</i>",
            parse_mode="HTML",
        )
        return  # ← Runtime exception YOK, bot çalışmaya devam eder

    # ══════════════════════════════════════════════════════════════════════
    # DEBUG FILE CHECK — gönderilen dosya ile diskteki aynı mı?
    # ══════════════════════════════════════════════════════════════════════
    _vp_resolved = video_path.resolve()
    _vp_stat = video_path.stat()
    with open(video_path, 'rb') as _hash_f:
        _vp_sha256 = hashlib.sha256(_hash_f.read()).hexdigest()
    # Referans dosya
    _ref_path = Path(r"VİDEO Dosyaları/sahne-1 giriş/hlk_sahne1.mp4").resolve()
    _ref_stat = _ref_path.stat()
    with open(_ref_path, 'rb') as _hash_f2:
        _ref_sha256 = hashlib.sha256(_hash_f2.read()).hexdigest()
    logger.info("=" * 60)
    logger.info("DEBUG FILE COMPARE — sendVideo() öncesi")
    logger.info(f"GÖNDERİLEN: {_vp_resolved}")
    logger.info(f"  exists   = {video_path.exists()}")
    logger.info(f"  size     = {_vp_stat.st_size} bytes")
    logger.info(f"  mtime    = {_vp_stat.st_mtime}")
    logger.info(f"  SHA-256  = {_vp_sha256}")
    logger.info(f"REFERANS : {_ref_path}")
    logger.info(f"  exists   = {_ref_path.exists()}")
    logger.info(f"  size     = {_ref_stat.st_size} bytes")
    logger.info(f"  mtime    = {_ref_stat.st_mtime}")
    logger.info(f"  SHA-256  = {_ref_sha256}")
    logger.info(f"AYNI DOSYA? {'EVET' if _vp_sha256 == _ref_sha256 else 'HAYIR - FARKLI!'}")
    logger.info("=" * 60)

    with open(video_path, 'rb') as vf:
        logger.info(f"🚩 [VIDEO_PLAYBACK_STARTED] user={user.id} — send_video x1 (duration={SAHNE1_SURE}sn)")
        video_msg = await update.message.reply_video(
            video=vf,
            width=720,
            height=1280,
            duration=SAHNE1_SURE,
            supports_streaming=True,
            reply_markup=ReplyKeyboardRemove()
        )
    actual_msg_id = video_msg.message_id if hasattr(video_msg, 'message_id') else 'N/A'
    logger.info(f"🚩 [VIDEO_SENT] message_id={actual_msg_id}")

    # ══════════════════════════════════════════════════════════════════════
    # DEBUG AFTER VIDEO — video gönderildikten hemen sonra
    # ══════════════════════════════════════════════════════════════════════
    logger.info("=" * 50)
    logger.info("DEBUG AFTER VIDEO — Video Gönderildi")
    logger.info(f"PID              = {_dbg_pid}")
    logger.info(f"Thread ID        = {threading.get_ident()}")
    logger.info(f"Application ID   = {_dbg_app_id}")
    logger.info(f"Handler Function = handle_start")
    logger.info(f"Function ID      = {_dbg_hfunc_id}")
    logger.info(f"Update ID        = {update_id}")
    logger.info(f"Video Message ID = {actual_msg_id}")
    logger.info(f"Chat ID          = {update.effective_chat.id}")
    logger.info(f"User ID          = {user.id}")
    logger.info(f"Current State    = {context.user_data.get('state', 'N/A')}")
    logger.info(f"SceneLock State  = {SceneLock.get_state(context.user_data).value}")
    logger.info(f"Timestamp (ms)   = {int(time.time() * 1000)}")
    logger.info("=" * 50)

    # ══════════════════════════════════════════════════════════════════════
    # DEBUG BEFORE LANG — dil seçim mesajı gönderilmeden hemen önce
    # ══════════════════════════════════════════════════════════════════════
    logger.info("=" * 50)
    logger.info("DEBUG BEFORE LANG — Dil Seçim Mesajı Gönderme Öncesi")
    logger.info(f"PID              = {_dbg_pid}")
    logger.info(f"Thread ID        = {threading.get_ident()}")
    logger.info(f"Application ID   = {_dbg_app_id}")
    logger.info(f"Handler Function = handle_start")
    logger.info(f"Function ID      = {_dbg_hfunc_id}")
    logger.info(f"Update ID        = {update_id}")
    logger.info(f"Video Message ID = {actual_msg_id}")
    logger.info(f"Chat ID          = {update.effective_chat.id}")
    logger.info(f"User ID          = {user.id}")
    logger.info(f"Current State    = {context.user_data.get('state', 'N/A')}")
    logger.info(f"SceneLock State  = {SceneLock.get_state(context.user_data).value}")
    logger.info(f"Timestamp (ms)   = {int(time.time() * 1000)}")
    logger.info("=" * 50)

    btn_msg = await update.message.reply_text(
        "Please select your <b>spoken language</b>.\n"
        "Lütfen konuşma <b><i>dilinizi</i></b> seçiniz.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇹🇷 TR", callback_data="lang_tr"),
                InlineKeyboardButton("🇬🇧 EN", callback_data="lang_en"),
                InlineKeyboardButton("🇩🇪 DE", callback_data="lang_de"),
                InlineKeyboardButton("🇫🇷 FR", callback_data="lang_fr"),
            ],
            [
                InlineKeyboardButton("🇪🇸 ES", callback_data="lang_es"),
                InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru"),
                InlineKeyboardButton("🇸🇦 AR", callback_data="lang_ar"),
                InlineKeyboardButton("☀️ KR", callback_data="lang_kr"),
            ]
        ])
    )

    # ── SCENE LOCK #4: PLAYING → COMPLETED (bekleme + cleanup) ──
    await asyncio.sleep(SAHNE1_SURE)
    SceneLock.set_state(context.user_data, SceneLockState.COMPLETED)
    logger.info(f"🚩 [VIDEO_PLAYBACK_COMPLETED] message_id={actual_msg_id}")

    # ── SCENE LOCK #5: COMPLETED → CLEANUP ──────────────────────
    SceneLock.set_state(context.user_data, SceneLockState.CLEANUP)
    try:
        await video_msg.delete()
        logger.info(f"🚩 [SCENE_CLEANUP] message_id={actual_msg_id} silindi")
    except Exception:
        logger.warning(f"⚠️ [SCENE_CLEANUP] message_id={actual_msg_id} silinemedi (zaten silinmis)")
        pass

    # ── SCENE LOCK #6: CLEANUP → DONE (TERMINAL) ────────────────
    SceneLock.set_state(context.user_data, SceneLockState.DONE)
    logger.info(f"🚩 [NEXT_STATE] SAHNE-1 DONE — dil secimi bekleniyor")

    logger.info("✅ Sahne-1 akışı tamamlandı")

    # ── CEE POST-CHECK + EEC: SAHNE-1 denetimi ──────────────────────
    video_delivered = actual_msg_id and actual_msg_id != 'N/A'
    sahne1_report = constitution_enforcement.post_check(
        code_anayasa_ok=True,
        flow_ok=True,
        state_ok=True,
        operational_ok=video_delivered,
        architecture_ok=True,
        runtime_ok=video_delivered,
    )
    sahne1_eec = execution_event_collector.emit_event(
        event_type=EECEventType.CODE_COMPLETED,
        description="SAHNE-1: HLK Karşılama Videosu tamamlandı",
        related_file="handlers/start.py",
        phase=ExecutionPhase.POST_CHECK,
        result=f"CEE {sahne1_report.verdict.value} ({sahne1_report.report_id})",
    )
    event_registry.register_from_eec(sahne1_eec)
    logger.info(
        f"🔍 [CEE] SAHNE-1 denetim: {sahne1_report.verdict.value} "
        f"| video={video_delivered} | report={sahne1_report.report_id}"
    )

    start_timer(user.id, update.effective_chat.id, context.bot, context.user_data)


async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dil seçimi: butonları kaldır → daktilo animasyonu → link iste."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    language = query.data.replace("lang_", "")
    logger.info(f"🌍 Kullanıcı {user.id} dil seçti: {language}")

    se = StateEngine(context.user_data)
    if not se.can_transition(UserEvent.LANGUAGE_SELECTED):
        if se.current in (UserState.WAIT_PRODUCT_LINK, UserState.LINK_VALIDATION):
            await query.answer("🔒 İşlem devam ediyor. Değiştirmek için /start yazınız.", show_alert=True)
            return
    await query.answer()
    cancel_timer(user.id)
    se.fire(UserEvent.LANGUAGE_SELECTED)
    context.user_data["state"] = "waiting_for_website"

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

    sahne2_sure = SAHNE2_SURE_LANG.get(language.upper(), SAHNE2_SURE)

    sahne2_msg = None
    hint_msg = None
    scene2_path = _get_scene2_path(language)

    # ══════════════════════════════════════════════════════════════════════
    # MASTER-003: SAHNE-2 yalnızca VİDEO Dosyaları/sahne-2/ klasöründen okur.
    # Prototip sistemi, file_id cache, fallback — tamamen kaldırıldı.
    # ══════════════════════════════════════════════════════════════════════
    if not scene2_path:
        logger.error(f"❌ SAHNE-2 video bulunamadi: dil={language}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Video bulunamadı. Lütfen /start ile tekrar deneyin.",
            parse_mode="HTML",
        )
        return

    _s2p = scene2_path.resolve()
    _s2s = scene2_path.stat()
    with open(scene2_path, 'rb') as _f: _s2h = hashlib.sha256(_f.read()).hexdigest()
    logger.info("=" * 60)
    logger.info("DEBUG SAHNE-2 RUNTIME AUDIT")
    logger.info(f"  video param type = BufferedReader (open edilmis dosya)")
    logger.info(f"  open() edilen    = {_s2p}")
    logger.info(f"  size             = {_s2s.st_size} bytes")
    logger.info(f"  SHA-256          = {_s2h}")
    logger.info(f"  dosya adi        = {scene2_path.name}")
    logger.info("=" * 60)

    try:
        with open(scene2_path, "rb") as video:
            sahne2_msg = await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                width=720,
                height=1280,
                duration=sahne2_sure,
                reply_markup=ReplyKeyboardRemove(),
            )
        logger.info(f"🎬 SAHNE-2 video gonderildi: msg_id={sahne2_msg.message_id}")

        hint_text = SESLI_HINT.get(language, SESLI_HINT["tr"])
        hint_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=hint_text,
            parse_mode="HTML",
        )

        # 4 saniye sonra sesli uyarıyı kaldır (arka planda)
        async def _remove_hint():
            await asyncio.sleep(4)
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=hint_msg.message_id)
                logger.info(f"🧹 SAHNE-2 SESLI_HINT 4sn sonra silindi")
            except Exception:
                pass
        asyncio.create_task(_remove_hint())
    except Exception as e:
        logger.error(f"❌ SAHNE-2 gonderilemedi: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Video gönderilemedi. Lütfen /start ile tekrar deneyin.",
            parse_mode="HTML",
        )
        return

    async def _run_balloons():
        """SAHNE-2 konuşma balonları + link isteği. message_id'leri döndürür."""
        welcome_text = _get_typewriter_text(language, "welcome")
        link_text = _get_typewriter_text(language, "link_request")
        words1 = len(strip_html(welcome_text).split())
        words2 = len(strip_html(link_text).split())
        total_words = words1 + words2

        mp3_dur = _get_mp3_duration(language)
        available_time = mp3_dur - 2.0

        if total_words > 0 and available_time > 0.5:
            dynamic_delay = available_time / (total_words + 2)
        else:
            dynamic_delay = 0.06

        logger.info(f"🔊 Daktilo dinamik: {language} | {total_words} kelime, "
                    f"MP3={mp3_dur:.3f}sn, delay={dynamic_delay:.4f}sn")

        await asyncio.sleep(BALLOON_STAGGER_DELAY)
        welcome_msg_id = await typewriter_animation(
            chat_id,
            text=welcome_text,
            bot=context.bot,
            delay=dynamic_delay,
        )
        await asyncio.sleep(BALLOON_STAGGER_DELAY)
        link_msg_id = await _deliver_text_only(
            chat_id=chat_id,
            text=link_text,
            bot=context.bot,
        )
        context.user_data["last_typewriter_msg_id"] = link_msg_id
        return welcome_msg_id, link_msg_id

    welcome_msg_id, link_msg_id = await _run_balloons()

    # Video sonunda ekstra bekleme
    await asyncio.sleep(SAHNE2_EXTRA_WAIT)

    # ── MASTER-003 SAHNE-2 Cleanup: yalnızca link isteği kalsın ──
    logger.info(f"⏱️ SAHNE-2 cleanup: video+uyari+balon siliniyor, link kalıyor")
    cleanup_msgs = [
        ("SAHNE-2 video", sahne2_msg),
        ("🔊 uyarı (zaten silinmiş olabilir)", hint_msg),
        ("konuşma balonu", welcome_msg_id),
    ]
    cleanup_success_count = 0
    cleanup_total = len([m for _, m in cleanup_msgs if m])
    for label, msg in cleanup_msgs:
        if msg:
            try:
                mid = msg.message_id if hasattr(msg, 'message_id') else msg
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                cleanup_success_count += 1
                logger.info(f"🧹 Silindi [{label}] msg_id={mid}")
            except Exception as e:
                logger.warning(f"⚠️ Silinemedi [{label}] msg_id={mid if isinstance(msg, int) else getattr(msg, 'message_id', '?')}: {e}")

    # ── CONSTITUTIONAL RUNTIME VALIDATION: Cleanup denetimi ──
    cleanup_ok = (cleanup_success_count == cleanup_total) if cleanup_total > 0 else True
    logger.info(
        f"🔎 [RUNTIME VALIDATION] SAHNE-2 Cleanup: "
        f"{cleanup_success_count}/{cleanup_total} mesaj silindi → "
        f"{'✅ TEMİZ' if cleanup_ok else '❌ EKSİK TEMİZLİK'}"
    )

    # Son mesaj: link isteği (link_msg_id) kullanıcıya bırakıldı
    logger.info(f"📌 Kullanıcıya bırakılan: link isteği msg_id={link_msg_id}")
    logger.info(f"✅ Dil akışı tamamlandı: {language}")

    # ── CEE POST-CHECK + EEC: SAHNE-2 denetimi ──────────────────────
    # GENERIC VALIDATION: Constitution Index'ten tüm ilgili kuralları yükle
    runtime_context = {
        "state": "STATE_SCENE_2",
        "scene": "SAHNE-02",
        "cleanup": {"total": cleanup_total, "success": cleanup_success_count},
        "buttons": [],  # SAHNE-2 sonrası buton yok (link isteği serbest metin)
        "video_sent": sahne2_msg is not None,
        "events_emitted": ["EVENT_LANGUAGE_SELECTED"],
        "transitions": ["LANGUAGE_SELECTION → WAIT_PRODUCT_LINK"],
    }
    sahne2_report = constitution_enforcement.validate_with_index(runtime_context)
    sahne2_eec = execution_event_collector.emit_event(
        event_type=EECEventType.CODE_COMPLETED,
        description=f"SAHNE-2 tamamlandı: dil={language}",
        related_file="handlers/start.py",
        phase=ExecutionPhase.POST_CHECK,
        result=f"CEE {sahne2_report.verdict.value} ({sahne2_report.report_id})",
    )
    event_registry.register_from_eec(sahne2_eec)
    logger.info(
        f"🔍 [CEE] SAHNE-2 denetim: {sahne2_report.verdict.value} "
        f"| dil={language} | report={sahne2_report.report_id}"
    )

    context.user_data["language"] = language
    context.user_data["state"] = "waiting_for_website"
    start_timer(user.id, chat_id, context.bot, context.user_data)


async def handle_selecting_language_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """State = selecting_language: Dil seçimi bekleniyor. Scene Engine üretir."""
    user = update.effective_user
    from services.scene_engine import conversation_scene_engine
    await conversation_scene_engine.produce_scene_response(
        user_data=context.user_data, chat_id=update.effective_chat.id,
        bot=context.bot, trigger_event="LANGUAGE_REQUIRED",
    )
    logger.info(f"👤 Kullanıcı {user.id} dil seçim sırasında mesaj yazdı")


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """State yok: Henüz /start yapmayan kullanıcının mesajı. Scene Engine üretir."""
    user = update.effective_user
    from services.scene_engine import conversation_scene_engine
    await conversation_scene_engine.produce_scene_response(
        user_data=context.user_data, chat_id=update.effective_chat.id,
        bot=context.bot, trigger_event="SESSION_NOT_STARTED",
    )
    logger.info(f"👤 Kullanıcı {user.id} /start olmadan mesaj yazdı")


async def handle_devam_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if context.user_data.get("state") == "waiting_for_website":
        await query.answer("Zaten bekleme modundasınız.", show_alert=False)
        return
    await query.answer()
    try:
        await query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    context.user_data["state"] = "waiting_for_website"
    logger.info(f"▶️ Devam: {query.from_user.id}")


# ─── Format seçim callback'leri ─────────────────────────────────────────────
async def handle_format_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SCOUT: Kullanıcının seçtiği formatı kaydet."""
    query = update.callback_query
    fmt = query.data.replace("fmt_", "")
    await query.answer(f"Seçiminiz: {fmt}")
    context.user_data["selected_format"] = fmt
    logger.info(f"📊 [SCOUT] Kullanici format secti: {fmt}")


# ─── main.py uyumluluğu için alias'lar ───────────────────────────────────────
start_handler = handle_start
button_handler = handle_language_selection
devam_handler = handle_devam_button
handle_format_selection = handle_format_selection


async def handle_scene2_replay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """V3.5 video replay — butona basinca videoyu bastan gonderir (tam sure)."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    await query.answer("🔊 Video baştan başlatılıyor...")

    logger.info(f"🔊 [SCENE2_REPLAY] user={user.id}")

    # Onceki videolari ve buton mesajini sil
    for key in ["proto_sahne2_msg_id", "proto_btn_msg_id"]:
        mid = context.user_data.get(key)
        if mid:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except:
                pass
    try:
        await query.message.delete()
    except:
        pass

    # Yeni video gonder (file_id ile, baslangictan)
    proto_file_id = context.user_data.get("proto_file_id")

    try:
        if not proto_file_id:
            raise ValueError("file_id bulunamadi")
        replay_msg = await context.bot.send_video(
            chat_id=chat_id,
            video=proto_file_id,
            width=720, height=1280,
            duration=SAHNE2_SURE_LANG.get("TR", 14),
        )
        logger.info(f"✅ [SCENE2_REPLAY] video gonderildi: msg_id={replay_msg.message_id}")

        # Video bitene kadar bekle, sil, link iste
        sure = SAHNE2_SURE_LANG.get("TR", 14)
        await asyncio.sleep(sure + 0.5)
        try:
            await replay_msg.delete()
        except:
            pass

        await typewriter_animation(
            chat_id,
            text=LINK_REQUEST_MESSAGE.get(context.user_data.get("language", "tr"), LINK_REQUEST_MESSAGE["tr"]),
            bot=context.bot,
            delay=0.06,
        )

    except Exception as e:
        logger.error(f"❌ [SCENE2_REPLAY] hata: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Video gönderilemedi.",
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """State'e göre mesajı doğru handler'a yönlendir (SE-007_3/4/5 uyumlu)."""
    from handlers.website import handle_website_link, handle_material_upload
    from services.scene_engine import conversation_scene_engine
    cancel_timer(update.effective_user.id)

    # Admin katsayı girişi
    if context.user_data.pop("_admin_waiting_katsayi", False):
        from handlers.website import _build_admin_pricing_form
        from services.scene_delivery import scene_delivery
        val = update.message.text.strip().replace(",", ".")
        try:
            k = float(val)
            if k <= 0: raise ValueError
        except ValueError:
            await update.message.reply_text("⚠️ Geçersiz. 0.1 - 10 arası bir sayı girin.")
            context.user_data["_admin_waiting_katsayi"] = True
            return
        context.user_data["_admin_katsayi"] = f"{k:.1f}"

        # FD-008_1: "EKRAN SİLİNİR" — eski formu + prompt'u temizle
        try:
            await update.message.delete()
        except Exception:
            pass
        await scene_delivery.cleanup_chat(chat_id=update.effective_chat.id)

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        admin_form, computed_data = _build_admin_pricing_form(context.user_data)
        # Hesaplanan değerleri user_data'ya kaydet
        context.user_data["_computed_toplam"] = computed_data["toplam"]
        context.user_data["_computed_yonetici_fiyat"] = computed_data["yonetici_fiyat"]
        context.user_data["_computed_kdvli"] = computed_data["kdvli"]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ Katsayı Gir", callback_data="admin_enter_katsayi"),
             InlineKeyboardButton("💬 HLK'ya Sor", callback_data="admin_hlk_chat")],
            [InlineKeyboardButton("✅ ONAY", callback_data="admin_price_submit"),
             InlineKeyboardButton("❌ İPTAL", callback_data="admin_price_cancel")],
        ])
        await update.message.reply_text(admin_form, parse_mode="HTML", reply_markup=kb)
        return

    # Admin HLK sohbet modu
    if context.user_data.get("_admin_chat_mode"):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        user_msg = update.message.text
        wait_msg = await update.message.reply_text("⏳ HLK düşünüyor...")
        answer = await _hlk_admin_chat(user_msg, context.user_data)
        try: await wait_msg.delete()
        except: pass
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Sohbeti Bitir", callback_data="admin_hlk_chat_end"),
        ]])
        await update.message.reply_text(answer, parse_mode="HTML", reply_markup=kb)
        return

    se = StateEngine(context.user_data)
    user_state = se.current
    legacy_state = context.user_data.get("state")

    # Materyal toplama modunda medya mesajları
    if legacy_state == "collecting_materials":
        await handle_material_upload(update, context)
        return

    # ── SE-007_6: STATE_VIDEO_DURATION_SELECTION — süre girişi validasyonu ──
    if user_state == UserState.VIDEO_DURATION_SELECTION:
        text = update.message.text.strip()
        chat_id = update.effective_chat.id
        try:
            duration = int(text)
            if 4 <= duration <= 30:
                # Geçerli süre → önce tüm validasyon kalıntılarını temizle
                validation_msg_ids = context.user_data.pop("validation_msg_ids", [])
                for vmid in validation_msg_ids:
                    try:
                        await context.bot.delete_message(chat_id=chat_id, message_id=vmid)
                        logger.info(f"🧹 Validation uyarısı silindi: msg_id={vmid}")
                    except Exception:
                        pass
                logger.info(f"🧹 Toplam {len(validation_msg_ids)} validation mesajı temizlendi")

                # Kullanıcının geçerli mesajını sil
                try:
                    await update.message.delete()
                except Exception:
                    pass

                # EVENT_DURATION_SELECTED ateşle
                context.user_data["video_duration"] = duration
                logger.info(f"⏱️ Kullanıcı {update.effective_user.id} süre seçti: {duration}sn")
                new_state = se.fire(UserEvent.DURATION_SELECTED)
                if new_state:
                    logger.info(f"🔷 STATE: {se.current.value} → SAHNE-06 tanıtım tarzı")
                    # SAHNE-05 temizle + SAHNE-06 teslim et
                    from services.scene_registry import get_scene_for_state
                    scene_def = get_scene_for_state(new_state)
                    if scene_def:
                        from services.scene_delivery import scene_delivery
                        await scene_delivery.cleanup_chat(chat_id)
                        # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
                        from handlers.website import _after_scene_edit
                        if await _after_scene_edit(chat_id, context):
                            return
                        await conversation_scene_engine.produce_and_deliver(
                            user_data=context.user_data,
                            chat_id=chat_id,
                            bot=context.bot,
                        )
                        # SAHNE-08 toggle için message_id yakala
                        last = scene_delivery._chat_last_scene.get(chat_id, {})
                        audio_msg_id = last.get("success_msg_id")
                        if audio_msg_id:
                            context.user_data["audio_scene_msg_id"] = audio_msg_id
                    else:
                        await update.message.reply_text(
                            f"✅ <b>{duration} saniye</b> olarak kaydedildi.\n\n"
                            "🎬 <i>Video üretim aşamasına geçiliyor...</i>",
                            parse_mode="HTML",
                        )
                from utils.session_timeout import start_timer
                start_timer(update.effective_user.id, chat_id, context.bot, context.user_data)
            else:
                # FD-008_1: 4-30 dışında HLK uyarı verir
                # Kullanıcının geçersiz mesajını sil
                try:
                    await update.message.delete()
                except Exception:
                    pass
                # Uyarı gönder, message_id'yi takip listesine ekle
                warning_msg = await update.message.reply_text(
                    f"⚠️ <b>{duration}</b> geçersiz bir süre.\n\n"
                    "Lütfen <b>4 ile 30 saniye</b> arasında bir değer girin.\n\n"
                    "<i>Örnek: 15</i>",
                    parse_mode="HTML",
                )
                context.user_data.setdefault("validation_msg_ids", []).append(warning_msg.message_id)
                logger.info(f"⚠️ Kullanıcı {update.effective_user.id} geçersiz süre girdi: {duration} "
                           f"(validation msg_id={warning_msg.message_id})")
        except ValueError:
            # Kullanıcının geçersiz mesajını sil
            try:
                await update.message.delete()
            except Exception:
                pass
            # Uyarı gönder, message_id'yi takip listesine ekle
            warning_msg = await update.message.reply_text(
                "⚠️ Lütfen <b>sadece rakam</b> girin.\n\n"
                "<b>4 ile 30 saniye</b> arasında bir değer yazın.\n\n"
                "<i>Örnek: 15</i>",
                parse_mode="HTML",
            )
            context.user_data.setdefault("validation_msg_ids", []).append(warning_msg.message_id)
            logger.info(f"⚠️ Kullanıcı {update.effective_user.id} sayısal olmayan değer girdi: {text} "
                       f"(validation msg_id={warning_msg.message_id})")
        return

    # ── SE-007_6: STATE_AUDIO_SELECTION — ses seçimi bekleniyor ──
    if user_state == UserState.AUDIO_SELECTION:
        await update.message.reply_text(
            "🎙️ <b>Ses seçimi</b> aşamasındasınız.\n\n"
            "Bu özellik hazırlanıyor. Lütfen yönergeleri takip edin.",
            parse_mode="HTML",
        )
        logger.info(f"🔊 Kullanıcı {update.effective_user.id} STATE_AUDIO_SELECTION'da mesaj gönderdi")
        return

    if not legacy_state and user_state == UserState.START:
        await handle_unknown_message(update, context)
    elif legacy_state == "selecting_language":
        await handle_selecting_language_message(update, context)
    elif legacy_state == "waiting_for_website" or user_state in (
        UserState.WAIT_PRODUCT_LINK, UserState.LINK_VALIDATION, UserState.LINK_VALIDATED):
        await handle_website_link(update, context)
    # SAHNE-11: Özel vurgu metin girişi
    elif user_state == UserState.EMPHASIS and context.user_data.get("_waiting_custom_emphasis"):
        from handlers.website import _handle_custom_emphasis_text
        await _handle_custom_emphasis_text(update, context)
    elif user_state in (UserState.ACTIVE_CONVERSATION, UserState.COLLECT_PRODUCT_MATERIALS,
                        UserState.PLATFORM_SELECTION, UserState.VIDEO_SETTINGS,
                        UserState.VIDEO_RESOLUTION_SELECTION, UserState.STYLE_SELECTION,
                        UserState.TARGET_AUDIENCE_SELECTION, UserState.VOICE_LANGUAGE,
                        UserState.VOICE_CHARACTER, UserState.EMPHASIS,
                        UserState.BRIEF_REVIEW, UserState.BRIEF_COMPLETED,
                        UserState.SCENARIO_APPROVAL, UserState.PRICING):
        from services.scene_delivery import scene_delivery as _sd
        await _sd.send_and_track(
            chat_id=update.effective_chat.id,
            text="💬 Şu anda butonlu bir seçim aşamasındasınız. Lütfen ekrandaki butonları kullanın.",
        )
    else:
        await handle_unknown_message(update, context)


def validate_language_support() -> None:
    """Sistem başlangıcında 8 dil için video, ses ve metin varlığını doğrular."""
    LANGUAGES = ["tr", "en", "de", "fr", "es", "ar", "ru", "kr"]
    all_ok = True

    for lang in LANGUAGES:
        video = _get_scene2_path(lang)
        ses = get_sahne2_audio(lang)
        karsilama = TYPEWRITER_MESSAGES.get(lang)
        link = LINK_REQUEST_MESSAGE.get(lang)

        eksikler = []
        if not video:
            eksikler.append("video")
        if not ses.exists():
            eksikler.append("ses")
        if not karsilama:
            eksikler.append("karsilama_metni")
        if not link:
            eksikler.append("link_isteme_metni")

        if eksikler:
            all_ok = False
            logger.warning(f"⚠️ Dil eksik [{lang}]: {', '.join(eksikler)}")
        else:
            logger.info(f"✅ Dil tam [{lang}]: video+ses+metin hazir")

    if all_ok:
        logger.info("✅ Tüm diller (8/8) eksiksiz — dil senkronu tamam")
    else:
        logger.warning("⚠️ Bazi dillerde eksik var — bot yine de calisir")


# ═══════════════════════════════════════════════════════════════════════════════
# SAHNE-05: "HLK'ya Bırak" butonu handler (FD-008_1 uyumlu)
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_duration_hlk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """SAHNE-05: HLK'ya Bırak — HLK 4-30sn arası en uygun süreyi belirler.

    FD-008_1: "15sn" UI'da sadece örnektir. HLK her seferinde platforma,
    formata ve ürüne göre dinamik süre belirler.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id

    import random
    platform = context.user_data.get("platform", "")
    fmt = context.user_data.get("video_format", "")

    # Platforma göre ideal aralık (sn)
    if "TikTok" in platform or "Shorts" in platform or "Reels" in platform:
        min_dur, max_dur = 8, 15    # Kısa dikey videolar
    elif "YouTube" in platform:
        min_dur, max_dur = 15, 30   # Uzun yatay videolar
    else:
        min_dur, max_dur = 10, 22   # Genel (Instagram, Diğer)

    # Format etkisi: dikey → kısa, yatay → uzun
    if "9:16" in fmt or "dikey" in fmt.lower():
        max_dur = min(max_dur, 15)
    elif "16:9" in fmt or "yatay" in fmt.lower():
        min_dur = max(min_dur, 12)

    duration = random.randint(min_dur, max_dur)
    context.user_data["video_duration"] = duration
    await query.answer(f"HLK belirledi: {duration} saniye ✨")
    logger.info(f"⏱️ {user.id} HLK'ya Bırak: {duration}sn (platform={platform}, format={fmt}, aralık={min_dur}-{max_dur})")

    se = StateEngine(context.user_data)
    new_state = se.fire(UserEvent.DURATION_SELECTED)

    # FD-008_1: EKRAN SİLİNİR
    try:
        await query.message.delete()
    except Exception:
        pass
    from services.scene_delivery import scene_delivery as _sd
    await _sd.cleanup_chat(chat_id)

    # Merkezi düzeltme kontrolü: SAHNE-12'den geliyorsa geri dön
    from handlers.website import _after_scene_edit
    if await _after_scene_edit(chat_id, context):
        return

    from services.scene_registry import get_scene_for_state
    scene_def = get_scene_for_state(new_state) if new_state else None
    if scene_def:
        from services.scene_engine import conversation_scene_engine
        await conversation_scene_engine.produce_and_deliver(
            user_data=context.user_data, chat_id=chat_id, bot=context.bot,
        )

    from utils.session_timeout import start_timer as _st
    _st(user.id, chat_id, context.bot, context.user_data)
