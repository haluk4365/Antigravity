"""
eCom Reklam Otomasyonu — Fail-Fast Config
==========================================
Boot anında tüm gerekli ENV değişkenlerini doğrular.
Eksik varsa uygulama anında çöker (Railway loglarında görünür).
"""

import os
import sys

# .env dosyasını manuel olarak os.environ'a yükle (bağımlılıktan kaçınmak için)
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip("'\""))



class Config:
    def __init__(self):
        # ── Ortam Modu ──
        self.ENV = os.environ.get("ENV", "development").lower()
        self.IS_DRY_RUN = self.ENV == "development" or os.environ.get("DRY_RUN", "0") == "1"

        # ── Telegram ──
        self.TELEGRAM_BOT_TOKEN = self._require_env("TELEGRAM_ECOM_BOT_TOKEN")
        self.ADMIN_CHAT_ID = int(self._require_env("TELEGRAM_ADMIN_CHAT_ID"))
        
        allowed_users_raw = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
        if allowed_users_raw:
            try:
                self.ALLOWED_USER_IDS = [int(x.strip()) for x in allowed_users_raw.split(",") if x.strip()]
            except ValueError:
                self.ALLOWED_USER_IDS = [self.ADMIN_CHAT_ID]
        else:
            self.ALLOWED_USER_IDS = [self.ADMIN_CHAT_ID]
            
        if self.ADMIN_CHAT_ID not in self.ALLOWED_USER_IDS:
            self.ALLOWED_USER_IDS.append(self.ADMIN_CHAT_ID)

        # ── OpenAI (GPT-4.1 Mini — Chat + Vision) ──
        self.OPENAI_API_KEY = self._require_env("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

        # ── Perplexity (Marka Araştırması) ──
        self.PERPLEXITY_API_KEY = self._require_env("PERPLEXITY_API_KEY")
        self.PERPLEXITY_BASE_URL = os.environ.get("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")

        # ── ImgBB (Görsel → Public URL) ──
        self.IMGBB_API_KEY = self._require_env("IMGBB_API_KEY")

        # ── Kie AI (Seedance 2.0 + Nano Banana 2) ──
        self.KIE_API_KEY = self._require_env("KIE_API_KEY")
        self.KIE_BASE_URL = os.environ.get("KIE_BASE_URL", "https://api.kie.ai/api/v1/")

        # ── ElevenLabs (Doğrudan API — Türkçe TTS) ──
        self.ELEVENLABS_API_KEY = self._require_env("ELEVENLABS_API_KEY")
        self.ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_v3")

        # ── Replicate (Video + Ses Birleştirme) ──
        self.REPLICATE_API_TOKEN = self._require_env("REPLICATE_API_TOKEN")

        # ── Firecrawl (URL Scraping — birincil) ──
        self.FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

        # ── Notion (Üretim Logları & Chat Hafızası) ──
        self.NOTION_TOKEN = self._require_env("NOTION_SOCIAL_TOKEN")
        self.NOTION_DB_ID = self._require_env("NOTION_DB_ECOM_REKLAM")
        # Chat hafıza DB'si — kendi Notion DB ID'nizi .env'e girin.
        self.NOTION_CHAT_DB_ID = os.environ.get("NOTION_CHAT_DB_ID", "")

        # ── Upload-Post (Sosyal Medya Paylaşımı) ──
        self.UPLOAD_POST_API_KEY = self._require_env("UPLOAD_POST_API_KEY")
        self.UPLOAD_POST_PROFILE = os.environ.get("UPLOAD_POST_PROFILE", "<UPLOAD_POST_PROFILE>")

        # ── OpenRouter (Google Gemini 2.0 Flash) ──
        self.OPENROUTER_API_KEY = self._require_env("OPENROUTER_API_KEY")
        self.OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash")
        self.OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # ── Yardımcılar ──

    def _require_env(self, key):
        """Fetches an environment variable, raises error if missing."""
        val = os.environ.get(key)
        if not val:
            raise EnvironmentError(
                f"CRITICAL STARTUP FAILURE: Gerekli ortam değişkeni '{key}' bulunamadı! "
                f"Railway dashboard → Variables bölümünden ekleyin."
            )
        return val


# ── Global instance — import anında fail-fast ──
try:
    settings = Config()
except EnvironmentError as e:
    print(f"BOOT ERROR: {e}")
    sys.exit(1)
