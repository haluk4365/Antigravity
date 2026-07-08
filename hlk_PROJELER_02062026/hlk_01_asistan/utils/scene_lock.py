"""
AR-002_44 — Scene Lock Mechanism (SAHNE-1)

Her sahne için oturum başına tek seferlik çalışma garantisi sağlar.
SAHNE-1 videosu oturum başına yalnızca 1 kez oynatılabilir.

Zorunlu geçiş zinciri:
    IDLE → LOCKED → PLAYING → COMPLETED → CLEANUP → DONE

Terminal state (DONE) sonrası sahne yeniden oluşturulamaz.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SceneLockState(str, Enum):
    """SAHNE-1 kilit durumları — her state yalnızca bir sonraki state'e geçebilir."""
    IDLE = "SCENE1_IDLE"
    LOCKED = "SCENE1_LOCKED"       # scene tek bir kullanım için rezerve edildi
    PLAYING = "SCENE1_PLAYING"     # video oynatılıyor
    COMPLETED = "SCENE1_COMPLETED" # video oynatma tamamlandı
    CLEANUP = "SCENE1_CLEANUP"     # temizlik aşaması
    DONE = "SCENE1_DONE"           # TERMINAL — sahne bir daha açılamaz

    @classmethod
    def _missing_(cls, value):
        """Bilinmeyen değerleri IDLE'a yönlendir."""
        return cls.IDLE


class SceneLock:
    """SAHNE-1 kilit mekanizması.

    - can_enter() → IDSE değilse ikinci oynatmayı engeller
    - set_state() → geçersiz geçişi reddeder ve log'lar
    - is_terminal() → DONE kontrolü
    """

    # İzin verilen geçişler — sadece bu geçişler mümkündür
    VALID_TRANSITIONS: dict[SceneLockState, list[SceneLockState]] = {
        SceneLockState.IDLE: [SceneLockState.LOCKED],
        SceneLockState.LOCKED: [SceneLockState.PLAYING],
        SceneLockState.PLAYING: [SceneLockState.COMPLETED],
        SceneLockState.COMPLETED: [SceneLockState.CLEANUP],
        SceneLockState.CLEANUP: [SceneLockState.DONE],
        SceneLockState.DONE: [],  # TERMINAL — hiçbir geçişe izin vermez
    }

    @staticmethod
    def get_state(user_data: dict) -> SceneLockState:
        """user_data'dan mevcut kilit durumunu okur."""
        raw = user_data.get("scene1_lock")
        if raw is None:
            return SceneLockState.IDLE
        if isinstance(raw, SceneLockState):
            return raw
        try:
            return SceneLockState(raw)
        except ValueError:
            logger.warning(f"🔒 SceneLock: Bilinmeyen state değeri '{raw}', IDLE'a sıfırlanıyor")
            return SceneLockState.IDLE

    @staticmethod
    def can_enter(user_data: dict) -> bool:
        """SAHNE-1'e GİRİŞ İZNİ.

        - IDLE → izin ver (yeni oturum)
        - LOCKED/PLAYING/COMPLETED/CLEANUP → RED (eşzamanlı oynatma engellenir)
        - DONE → IDLE'a sıfırla ve izin ver (önceki oturum bitti, yeni başlayabilir)
        """
        state = SceneLock.get_state(user_data)

        if state == SceneLockState.IDLE:
            return True

        if state == SceneLockState.DONE:
            # DONE: terminal state — önceki oturum tamamlanmış, yeni /start gelebilir
            SceneLock.reset(user_data)
            logger.info("🔒 SceneLock: DONE → IDLE (yeni oturum başlıyor)")
            return True

        logger.warning(
            f"🔒 SceneLock: SAHNE-1 eşzamanlı giriş REDDEDİLDİ "
            f"(state={state.value})"
        )
        return False

    @staticmethod
    def set_state(user_data: dict, new_state: SceneLockState) -> bool:
        """Kilit durumunu değiştirir. Geçersiz geçiş reddedilir.

        Args:
            user_data: context.user_data
            new_state: Gidilecek yeni state

        Returns:
            True: Geçiş başarılı
            False: Geçiş reddedildi (geçersiz)
        """
        current = SceneLock.get_state(user_data)
        allowed_states = SceneLock.VALID_TRANSITIONS.get(current, [])

        if new_state in allowed_states:
            user_data["scene1_lock"] = new_state.value
            logger.info(f"🔒 SceneLock: {current.value} → {new_state.value}")
            return True

        logger.warning(
            f"🔒 SceneLock: GEÇERSİZ GEÇİŞ {current.value} → {new_state.value}"
        )
        return False

    @staticmethod
    def is_terminal(user_data: dict) -> bool:
        """Terminal state'de mi? (DONE)"""
        return SceneLock.get_state(user_data) == SceneLockState.DONE

    @staticmethod
    def reset(user_data: dict) -> None:
        """Kiliti sıfırlar (yalnızca /cancel veya yeni oturum için)."""
        old = SceneLock.get_state(user_data)
        user_data["scene1_lock"] = SceneLockState.IDLE.value
        logger.info(f"🔒 SceneLock: {old.value} → IDLE (sıfırlandı)")
