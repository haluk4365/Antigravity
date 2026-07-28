"""Proje konfigürasyonu ve ayarları."""

import os

# Environment Mode (test = local test bot, production = Railway bot)
_ENV = os.getenv("ENV", "production")
_TELEGRAM_TOKEN_TEST = os.getenv("TELEGRAM_TOKEN_TEST", "")
_TELEGRAM_TOKEN_PROD = os.getenv("TELEGRAM_TOKEN", "")


class Settings:
    """Bot ayarlarını merkezi olarak yönet."""

    # Telegram — ENV=test ise test token, yoksa production token
    ENV: str = _ENV
    TELEGRAM_TOKEN: str = _TELEGRAM_TOKEN_TEST if _ENV == "test" else _TELEGRAM_TOKEN_PROD
    TELEGRAM_ALLOWED_USERS: str = os.getenv("TELEGRAM_ALLOWED_USERS", "*")
    TELEGRAM_ADMIN_USER_ID: str = os.getenv("TELEGRAM_ADMIN_USER_ID", "")

    # Kie AI
    KIE_AI_API_KEY: str = os.getenv("KIE_AI_API_KEY", "")

    # Fal.ai (Seedance image-to-video)
    FAL_KEY: str = os.getenv("FAL_KEY", "")

    # ElevenLabs (Ses üretimi)
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

    # Descript API (Video/ses düzenleme ve sentetik ses üretimi)
    DESCRIPT_API_KEY: str = os.getenv("DESCRIPT_API_KEY", "")

    # Telegram file_id cache (ilk /start sonrası otomatik doldurulur)
    INTRO_VIDEO_FILE_ID: str = os.getenv("INTRO_VIDEO_FILE_ID", "")

    # Bot ayarları
    BOT_DEBUG: bool = os.getenv("BOT_DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/bot.db")

    def __init__(self):
        """Ayarları valide et."""
        if not self.TELEGRAM_TOKEN:
            raise ValueError("❌ TELEGRAM_TOKEN env değişkeni gereklidir!")

    @property
    def is_user_allowed(self) -> bool:
        """Tüm kullanıcılar izin verili mi?"""
        return self.TELEGRAM_ALLOWED_USERS == "*"

    def is_admin(self, user_id: str | int) -> bool:
        """Kullanıcı yönetici mi? TELEGRAM_ADMIN_USER_ID tanımlı değilse hiç kimse yönetici kabul edilmez.

        Güvenlik prensibi (AR-002_84): fail-closed — env var eksikse herkes reddedilir.
        Sebep loglanır; sessiz başarısızlık üretilmez.
        """
        if not self.TELEGRAM_ADMIN_USER_ID:
            import logging
            _log = logging.getLogger("hlk.auth")
            _log.warning(
                "⚠️ [AUTH] TELEGRAM_ADMIN_USER_ID tanımlı değil — "
                "hiç kimse yönetici kabul edilmez. "
                "Yönetici işlemleri (fiyat onayı, ödeme onayı, /yeniden) "
                "bu değişken tanımlanana kadar çalışmayacaktır. "
                "Railway'de veya .env dosyasında TELEGRAM_ADMIN_USER_ID=<admin_id> "
                "olarak tanımlanmalıdır."
            )
            return False
        return str(user_id) == str(self.TELEGRAM_ADMIN_USER_ID)
