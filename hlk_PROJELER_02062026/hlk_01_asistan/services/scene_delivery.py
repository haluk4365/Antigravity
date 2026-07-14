"""
AR-002_36 Scene Delivery Architecture
Conversation Scene Engine tarafından oluşturulan sahnelerin kullanıcıya teslimini yönetir.

Yaşam Döngüsü:
Scene Engine üretir → Payload oluştur → Teslim Modülü çağrılır → API gönderimi → Onay → Teslim
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable
from enum import Enum

from helpers.typewriter_animation import typewriter_animation

logger = logging.getLogger(__name__)


class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


@dataclass
class ScenePayload:
    """Teslim edilecek sahne verisi.

    AR-002_36: Sesli teslimat için audio_path/audio_file_id alanları eklendi.
    Öncelik sırası: audio (varsa ses) → video → text
    """
    scene_id: str
    chat_id: int
    text: str = ""
    parse_mode: str = "HTML"
    video_path: Optional[str] = None
    video_file_id: Optional[str] = None
    audio_path: Optional[str] = None
    audio_file_id: Optional[str] = None
    buttons: Optional[list] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DeliveryReceipt:
    """Teslimat sonucu."""
    scene_id: str
    status: DeliveryStatus
    chat_id: int
    message_id: Optional[int] = None
    error: Optional[str] = None
    retry_count: int = 0


class SceneDeliveryModule:
    """AR-002_36: Sahne teslim modülü.

    Conversation Scene Engine tarafından üretilen sahneleri alır,
    Telegram API üzerinden kullanıcıya teslim eder.
    """

    def __init__(self, bot=None):
        self._bot = bot
        self._delivery_history: dict[str, DeliveryReceipt] = {}
        self._max_retries = 3
        self._chat_last_scene: dict[int, dict] = {}
        # MASTER-003 / FD-008_1: Bekleyen mesaj ID'leri — cleanup'lar arası
        # biriken TÜM mesajların silinmesini garanti eder.
        # register_chat_messages() her çağrıldığında buraya ekleme yapar,
        # cleanup_chat() tüm birikenleri siler ve temizler.
        self._pending_cleanup_ids: dict[int, set[int]] = {}
        # Kullanıcı mesaj ID'leri — kalıcıdır, her cleanup'ta silinmeye çalışılır
        self._user_msg_ids: dict[int, set[int]] = {}

    async def send_and_track(
        self, chat_id: int, text: str,
        parse_mode: str = "HTML",
        reply_markup=None,
    ) -> int | None:
        """Mesaj gönder ve otomatik olarak cleanup havuzuna kaydet.

        Tüm handler'lar bu metodu kullanmalıdır — cleanup_chat() ile
        eksiksiz temizlik garanti edilir.
        """
        if not self._bot:
            return None
        msg = await self._bot.send_message(
            chat_id=chat_id, text=text,
            parse_mode=parse_mode, reply_markup=reply_markup,
        )
        self.register_chat_messages(chat_id, {"auto_tracked": msg.message_id})
        return msg.message_id

    async def replace_ui_component(
        self, chat_id: int, old_msg_id: int,
        text: str, reply_markup,
    ) -> int:
        """Active UI Component Rule: Eski bileşeni sil, yenisini gönder.

        ANA YASA FD-008_1: Aynı STATE içinde yalnızca BİR aktif seçim
        bileşeni bulunur. Yeni bileşen oluşturulmadan önce eski kaldırılır.

        Args:
            chat_id: Telegram chat ID
            old_msg_id: Eski bileşenin message_id'si
            text: Yeni buton mesajı metni
            reply_markup: Yeni inline keyboard

        Returns:
            Yeni mesajın message_id'si
        """
        # 1. Yerinde güncellemeyi dene (kullanıcıya görünmez)
        if old_msg_id and self._bot:
            try:
                await self._bot.edit_message_reply_markup(
                    chat_id=chat_id, message_id=old_msg_id, reply_markup=reply_markup,
                )
                logger.debug(f"🔄 [UI] Yerinde güncellendi: msg_id={old_msg_id}")
                return old_msg_id
            except Exception:
                # Yerinde güncelleme başarısız → sil + yeniden gönder
                try:
                    await self._bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
                except Exception:
                    pass
        # 2. Yeni bileşen gönder (fallback)
        new_msg = await self._bot.send_message(
            chat_id=chat_id, text=text, reply_markup=reply_markup,
        )
        self.register_chat_messages(chat_id, {"btn_msg_id": new_msg.message_id})
        return new_msg.message_id

    def register_user_message(self, chat_id: int, message_id: int) -> None:
        """Kullanıcı mesajını kalıcı temizlik havuzuna ekle (FD-008_1: EKRAN SİLİNİR).

        Telegram bot'ları özel sohbette kullanıcı mesajlarını silemez.
        Bu metod her cleanup'ta dener, başarısız olursa debug log atar.
        """
        if chat_id not in self._user_msg_ids:
            self._user_msg_ids[chat_id] = set()
        self._user_msg_ids[chat_id].add(message_id)
        # İlk cleanup'ta da denensin diye pending'e de ekle
        if chat_id not in self._pending_cleanup_ids:
            self._pending_cleanup_ids[chat_id] = set()
        self._pending_cleanup_ids[chat_id].add(message_id)

    def bind_bot(self, bot):
        """Bot instance'ını bağla (main.py'de çağrılır)."""
        self._bot = bot

    async def cleanup_chat(self, chat_id: int) -> None:
        """Önceki sahneye ait tüm mesajları siler.

        Kanıt: Silinen message_id'ler log'a yazılır.
        Silinemeyenlerin nedeni de log'a yazılır.

        MASTER-003 / FD-008_1: _pending_cleanup_ids havuzundaki TÜM biriken
        mesaj ID'leri silinir. Bu sayede art arda birden fazla
        register_chat_messages() çağrısı arasında hiçbir mesaj kaybolmaz.
        """
        last = self._chat_last_scene.get(chat_id)
        # .pop() YERİNE .get() — başarısız silinen ID'ler kaybolmasın
        pending = set(self._pending_cleanup_ids.get(chat_id, set()))
        # Kalıcı kullanıcı mesaj ID'lerini de ekle
        user_ids = self._user_msg_ids.get(chat_id, set())
        if user_ids:
            pending.update(user_ids)
        logger.info("=" * 50)
        logger.info(f"CLEANUP TRACE — cleanup_chat({chat_id})")
        logger.info(f"  Kayıtlı veri var mı? {'EVET' if last else 'HAYIR — boş!'}")
        logger.info(f"  Bekleyen havuz: {len(pending)} ID")
        if last:
            logger.info(f"  Kayıtlı key'ler: {list(last.keys())}")
            for k in ("success_msg_id", "link_msg_id", "voice_msg_id", "typewriter_msg_id", "btn_msg_id"):
                logger.info(f"    {k:25s} = {last.get(k)}")
            # Son kaydı da bekleyen havuza ekle (tutarlılık için)
            for v in last.values():
                if v is not None:
                    pending.add(v)
        if not pending and not last:
            logger.info(f"  ⛔ cleanup DURDU: {'veri yok' if not last else 'bot yok'}")
            logger.info("=" * 50)
            return
        if not self._bot:
            logger.info(f"  ⛔ cleanup DURDU: bot yok")
            logger.info("=" * 50)
            return

        msg_ids = list(pending)
        if not msg_ids:
            logger.info(f"  ⛔ SİLİNECEK MESAJ YOK")
            logger.info("=" * 50)
            self._chat_last_scene[chat_id] = {}
            return

        logger.info(f"  Silinecek message_id'ler: {msg_ids}")
        silinen = 0
        for mid in list(msg_ids):
            for attempt, delay in ((1, 0), (2, 0.3)):
                try:
                    await self._bot.delete_message(chat_id=chat_id, message_id=mid)
                    silinen += 1
                    # Başarılı → set'ten çıkar, bir daha denenmesin
                    self._pending_cleanup_ids.get(chat_id, set()).discard(mid)
                    if attempt > 1:
                        logger.info(f"  ✅ deleteMessage({mid}) → deneme {attempt}")
                    break
                except Exception as e:
                    err = str(e)
                    if "message can't be deleted" in err.lower():
                        self._pending_cleanup_ids.get(chat_id, set()).discard(mid)
                        break
                    if attempt < 2:
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"  ❌ deleteMessage({mid}) → 2 deneme başarısız, sonraki cleanup'ta tekrar denenecek")
        remaining = len(self._pending_cleanup_ids.get(chat_id, set()))
        logger.info(f"  Sonuç: {silinen}/{len(msg_ids)} mesaj silindi, {remaining} ID sonraki denemeye kaldı")
        # Hicbir mesaj silinemediyse birikmeyi onle — havuzu temizle
        if silinen == 0 and remaining > 0:
            logger.warning(f"  ⚠️ 0/{len(msg_ids)} silindi — havuz temizleniyor ({remaining} ID)")
            self._pending_cleanup_ids[chat_id] = set()
        logger.info("=" * 50)
        self._chat_last_scene[chat_id] = {}

    def register_chat_messages(self, chat_id: int, msg_ids: dict) -> None:
        """Sahneye ait mesaj ID'lerini kaydeder.

        Çağıran taraf (handlers/website.py, scene_engine.py) teslim ettiği
        mesajların ID'lerini buraya bildirir. Bir sonraki sahnede cleanup_chat()
        çağrıldığında bu mesajlar silinir.

        MASTER-003 / FD-008_1: Art arda birden fazla mesaj kaydedildiğinde
        önceki kayıtlar EZİLMEZ. Tüm mesaj ID'leri _pending_cleanup_ids'te
        biriktirilir ve cleanup_chat() hepsini birden siler.

        Args:
            chat_id: Telegram chat ID.
            msg_ids: {
                "success_msg_id": int | None,
                "voice_msg_id": int | None,
                "typewriter_msg_id": int | None,
                "btn_msg_id": int | None,
            }
        """
        if chat_id not in self._chat_last_scene:
            self._chat_last_scene[chat_id] = {}
        self._chat_last_scene[chat_id].update(msg_ids)

        # MASTER-003: Bekleyen temizlik havuzuna EKLE (ezme YOK)
        if chat_id not in self._pending_cleanup_ids:
            self._pending_cleanup_ids[chat_id] = set()
        for v in msg_ids.values():
            if v is not None:
                self._pending_cleanup_ids[chat_id].add(v)

        logger.info(f"REGISTER TRACE — register_chat_messages({chat_id})")
        logger.info(f"  Kaydedilen key'ler: {list(msg_ids.keys())}")
        logger.info(f"  Bekleyen toplam ID: {len(self._pending_cleanup_ids.get(chat_id, set()))}")
        for k, v in msg_ids.items():
            logger.info(f"    {k:25s} = {v}")

    async def deliver(self, payload: ScenePayload) -> DeliveryReceipt:
        """Bir sahneyi teslim eder (AR-002_36 yaşam döngüsü)."""
        receipt = DeliveryReceipt(
            scene_id=payload.scene_id,
            status=DeliveryStatus.PENDING,
            chat_id=payload.chat_id,
        )

        if not self._bot:
            receipt.status = DeliveryStatus.FAILED
            receipt.error = "Bot bağlı değil"
            self._delivery_history[payload.scene_id] = receipt
            logger.error(f"❌ [SceneDelivery] Bot bağlı değil, teslim iptal: {payload.scene_id}")
            return receipt

        for attempt in range(1, self._max_retries + 1):
            try:
                reply_markup = None
                if payload.buttons:
                    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                    keyboard = []
                    for row in payload.buttons:
                        btn_row = []
                        for btn in row:
                            if "callback_data" in btn:
                                btn_row.append(InlineKeyboardButton(
                                    text=btn["text"],
                                    callback_data=btn["callback_data"]
                                ))
                            elif "url" in btn:
                                btn_row.append(InlineKeyboardButton(
                                    text=btn["text"],
                                    url=btn["url"]
                                ))
                        if btn_row:
                            keyboard.append(btn_row)
                    if keyboard:
                        reply_markup = InlineKeyboardMarkup(keyboard)

                if payload.audio_path or payload.audio_file_id:
                    if payload.audio_file_id:
                        voice_msg = await self._bot.send_voice(
                            chat_id=payload.chat_id,
                            voice=payload.audio_file_id,
                        )
                    else:
                        with open(payload.audio_path, "rb") as af:
                            voice_msg = await self._bot.send_voice(
                                chat_id=payload.chat_id,
                                voice=af,
                            )

                    await asyncio.sleep(1.5)
                    tw_msg_id = await typewriter_animation(
                        chat_id=payload.chat_id,
                        text=payload.text,
                        bot=self._bot,
                        delay=0.06,
                    )

                    payload.metadata["voice_msg_id"] = voice_msg.message_id
                    try:
                        await self._bot.delete_message(
                            chat_id=payload.chat_id,
                            message_id=voice_msg.message_id
                        )
                        logger.info(f"🔊 [SceneDelivery] Voice mesaji silindi: msg_id={voice_msg.message_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ [SceneDelivery] Voice mesaji silinemedi: {e}")

                    if payload.buttons and reply_markup:
                        btn_msg = await self._bot.send_message(
                            chat_id=payload.chat_id,
                            text="👇",
                            reply_markup=reply_markup,
                        )
                        payload.metadata["btn_msg_id"] = btn_msg.message_id

                    msg = voice_msg
                    if tw_msg_id:
                        payload.metadata["typewriter_msg_id"] = tw_msg_id

                elif payload.video_path or payload.video_file_id:
                    if payload.video_file_id:
                        msg = await self._bot.send_video(
                            chat_id=payload.chat_id,
                            video=payload.video_file_id,
                            caption=payload.text,
                            parse_mode=payload.parse_mode,
                            supports_streaming=True,
                            reply_markup=reply_markup,
                        )
                    else:
                        with open(payload.video_path, "rb") as vf:
                            msg = await self._bot.send_video(
                                chat_id=payload.chat_id,
                                video=vf,
                                caption=payload.text,
                                parse_mode=payload.parse_mode,
                                supports_streaming=True,
                                reply_markup=reply_markup,
                            )
                else:
                    # FD-008_1: TEXT_ONLY_MODE — daktilo efekti + butonlar
                    tw_msg_id = await typewriter_animation(
                        chat_id=payload.chat_id,
                        text=payload.text,
                        bot=self._bot,
                        delay=0.06,
                    )
                    payload.metadata["typewriter_msg_id"] = tw_msg_id

                    # Butonlar: ayrı mesaj (send_message + reply_markup = tek API çağrısı)
                    if payload.buttons and reply_markup:
                        btn_msg = await self._bot.send_message(
                            chat_id=payload.chat_id,
                            text="▾",
                            reply_markup=reply_markup,
                        )
                        payload.metadata["btn_msg_id"] = btn_msg.message_id
                        self.register_chat_messages(payload.chat_id, {
                            "btn_msg_id": btn_msg.message_id,
                        })

                    # message_id attribute'u olan hafif wrapper (ortak kod ile uyumlu)
                    class _TypewriterMsg:
                        pass
                    msg = _TypewriterMsg()
                    msg.message_id = tw_msg_id

                receipt.status = DeliveryStatus.DELIVERED
                receipt.message_id = msg.message_id
                receipt.error = None
                self._delivery_history[payload.scene_id] = receipt
                logger.info(f"✅ [SceneDelivery] Teslim başarılı: {payload.scene_id} (msg:{msg.message_id})")

                # MASTER-010: Tüm message_id'ler kaydedilir — success_msg_id
                # ana sahne mesajıdır (text + butonlar). Cleanup zincirinin
                # çalışması için ZORUNLUDUR (AR-002_44, FD-008, MR-001).
                self.register_chat_messages(payload.chat_id, {
                    "success_msg_id": msg.message_id,
                    "voice_msg_id": payload.metadata.get("voice_msg_id"),
                    "typewriter_msg_id": payload.metadata.get("typewriter_msg_id"),
                    "btn_msg_id": payload.metadata.get("btn_msg_id"),
                    "link_msg_id": payload.metadata.get("link_msg_id"),
                })
                return receipt

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"⚠️ [SceneDelivery] Teslim başarısız (deneme {attempt}/{self._max_retries}): {error_msg}")
                receipt.status = DeliveryStatus.RETRYING
                receipt.error = error_msg
                receipt.retry_count = attempt

                if attempt < self._max_retries:
                    await asyncio.sleep(1.5 * attempt)

        receipt.status = DeliveryStatus.FAILED
        self._delivery_history[payload.scene_id] = receipt
        logger.error(f"❌ [SceneDelivery] Tüm denemeler başarısız: {payload.scene_id}")
        return receipt

    def get_delivery_status(self, scene_id: str) -> Optional[DeliveryReceipt]:
        """Bir sahnenin teslim durumunu döndürür."""
        return self._delivery_history.get(scene_id)

    def assert_delivered(self, scene_id: str) -> bool:
        """AR-002_36: Bir sahnenin teslim edilip edilmediğini kontrol eder."""
        receipt = self._delivery_history.get(scene_id)
        return receipt is not None and receipt.status == DeliveryStatus.DELIVERED


# Global singleton
scene_delivery = SceneDeliveryModule()
