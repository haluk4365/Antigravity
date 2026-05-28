"""
Akıllı Watchdog — Konfigürasyon Modülü
LLM-destekli pipeline sağlık kontrolü.

İzlenen projeler (17 proje):
  ── Sheets → Notion Pipeline ──────────────────────────
  1.  Lead Pipeline / Tele Satış CRM (Sheets → Notion)
  2.  Lead Notifier Bot (Sheets → Telegram/Email)

  ── Notion Tabanlı ────────────────────────────────────
  3.  Marka İş Birliği (Notion DB)
  4.  Blog Yazıcı (Notion Operations Log)
  5.  Reels Kapak (Notion)
  6.  İşbirliği Tahsilat Takip (Notion)
  7.  LinkedIn Video Paylaşım (Notion)
  8.  LinkedIn Text Paylaşım (Notion)
  9.  Twitter Video Paylaşım (Notion)
  10. YouTube Kapak (Notion + Drive)
  11. Ceren İzlenme Notifier (Apify + Gmail)
  12. Dubai Emlak İçerik Yazarı (Lokal)
  13. Emlak Arazi Drone Çekim (Lokal)

  ── Railway Servisleri ────────────────────────────────
  14. SWC Email Responder (Railway)
  15. Shorts Demo Otomasyonu (Railway)
  16. E-posta Asistanı (Lokal - Windows Görev Zamanlayıcı)
  17. Örnek AI Website (Netlify - Next.js)

Ek Katmanlar:
  - Token Freshness: LinkedIn + API tokenlarının expire takibi
  - Railway Probe: Tüm aktif projelerin son deployment durumu
"""
import os
from datetime import datetime, timezone, timedelta
import json
import logging

# .env dosyasını manuel olarak os.environ'a yükle
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

logger = logging.getLogger(__name__)


def _parse_tabs(csv_str: str) -> list[str]:
    """Virgülle ayrılmış tab isimlerini parse eder."""
    return [t.strip() for t in csv_str.split(",") if t.strip()]


class Config:
    """Environment variable tabanlı konfigürasyon."""

    # ── Groq LLM ──────────────────────────────────────────
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_BASE_URL = os.environ.get(
        "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
    )
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Alarm ─────────────────────────────────────────────
    ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "EMAIL_ADRESI_BURAYA")

    # Gmail API OAuth2 (SMTP yerine — Railway port engellemesi nedeniyle)
    # Railway: GOOGLE_OUTREACH_TOKEN_JSON env variable
    # Lokal: Merkezi google_auth modülü otomatik kullanılır

    # ── Notion ─────────────────────────────────────────────
    NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN", "") or os.environ.get("NOTION_SOCIAL_TOKEN", "")
    NOTION_SOCIAL_TOKEN = os.environ.get("NOTION_SOCIAL_TOKEN", "")
    NOTION_DATABASE_ID = os.environ.get(
        "NOTION_DATABASE_ID", "BURAYA_NOTION_DB_ID"
    )

    # Token registry — proje config'inde notion_token_key ile referans edilir
    NOTION_TOKENS = {
        "NOTION_API_TOKEN": os.environ.get("NOTION_API_TOKEN", "") or os.environ.get("NOTION_SOCIAL_TOKEN", ""),
        "NOTION_SOCIAL_TOKEN": os.environ.get("NOTION_SOCIAL_TOKEN", ""),
    }

    @classmethod
    def get_notion_token(cls, token_key: str) -> str:
        """Proje config'indeki token_key'e göre doğru Notion token'ı döner."""
        return cls.NOTION_TOKENS.get(token_key, cls.NOTION_API_TOKEN)

    # ── Google Auth (Production: Service Account) ─────────
    GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")

    # ── İzlenen Projeler ──────────────────────────────────
    MONITORED_PROJECTS = [

        # ══════════════════════════════════════════════════════
        # GRUP 1: SHEETS → NOTION PİPELINE
        # ══════════════════════════════════════════════════════

        {
            "name": "Lead Pipeline — Tele Satış CRM",
            "spreadsheet_id": os.environ.get(
                "CRM_SPREADSHEET_ID",
                "10uTCr65VlIBng0Sxlmz7h1Q2y5AWBp1qDQHTeqI7mGU"
            ),
            "sheet_tabs": ["Nisan-2026-Saat Bazlı-v2", "Mart-2026-Saat Bazlı-v2"],
            "expected_columns": ["Ad Soyad", "Telefon"],
            "expected_column_keywords": ["ad", "soyad", "telefon", "tarih"],
            "pipeline": "sheets_to_notion",
            "notion_token_key": "NOTION_API_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DATABASE_ID", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Ad Soyad", "Telefon", "Budget"],
            "expected_daily_activity": True,   # Her 10 dakikada cron
            "railway_service_id": os.environ.get("RAILWAY_SVC_LEAD_PIPELINE", ""),
        },
        {
            "name": "Lead Notifier Bot",
            "spreadsheet_id": os.environ.get(
                "NOTIFIER_SPREADSHEET_ID",
                "1DUxt0W6b-Sa5StDdGMnyVm4WFy-PB3FZIlCH30_9sh4"
            ),
            "sheet_tabs": ["Sheet1"],
            "expected_columns": [],
            "expected_column_keywords": ["ad", "soyad", "telefon"],
            "pipeline": "sheets_email",        # Sheets → Email/Telegram bildirimi
            "notion_token_key": "NOTION_API_TOKEN",
            "notion_db_id": "",                # Notion yok
            "notion_properties": [],
            "expected_daily_activity": True,
            "railway_service_id": os.environ.get("RAILWAY_SVC_LEAD_NOTIFIER", ""),
        },

        # ══════════════════════════════════════════════════════
        # GRUP 2: NOTION TABANLI PROJELER
        # ══════════════════════════════════════════════════════

        {
            "name": "Marka İş Birliği",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_BRAND_REACHOUT", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Marka Adı", "Email", "Outreach Status"],
            "expected_daily_activity": False,  # Haftada 3 gün: Pzt, Perş, Cuma
            "railway_service_id": os.environ.get("RAILWAY_SVC_MARKA_IS_BIRLIGI", ""),
        },
        {
            "name": "Blog Yazıcı",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_BLOG_YAZICI", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Title", "Message", "Level", "Component", "Zaman"],
            "expected_daily_activity": False,
            "railway_service_id": os.environ.get("RAILWAY_SVC_BLOG_YAZICI", ""),
        },
        {
            "name": "Reels Kapak",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_REELS_KAPAK", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Name", "Status"],
            "expected_daily_activity": False,
            "railway_service_id": os.environ.get("RAILWAY_SVC_REELS_KAPAK", ""),
        },
        {
            "name": "İşbirliği Tahsilat Takip",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_YOUTUBE_ISBIRLIKLERI", "BURAYA_NOTION_DB_ID"),
            "notion_properties": [],           # DB erişim + kayıt sayısı kontrolü yeterli
            "expected_daily_activity": False,
            "railway_service_id": os.environ.get("RAILWAY_SVC_TAHSILAT", ""),
        },
        {
            "name": "LinkedIn Video Paylaşım",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_LINKEDIN_DB_ID", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Video ID", "Status", "Platform", "TikTok URL", "LinkedIn URL", "Paylaşım Tarihi"],
            "expected_daily_activity": True,   # Günlük cron UTC 10:00
            "shared_notion_db_group": "social_media_db",
            "railway_service_id": os.environ.get("RAILWAY_SVC_LINKEDIN_VIDEO", ""),
        },
        {
            "name": "LinkedIn Text Paylaşım",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_LINKEDIN_DB_ID", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Video ID", "Status", "Platform", "Post Tipi"],
            "expected_daily_activity": False,  # Haftada 2 kez: Pazartesi + Perşembe
            "shared_notion_db_group": "social_media_db",
            "railway_service_id": os.environ.get("RAILWAY_SVC_LINKEDIN_TEXT", ""),
        },
        {
            "name": "Twitter Video Paylaşım",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",  # NOTION_SOCIAL_TOKEN kullan
            "notion_db_id": os.environ.get("NOTION_TWITTER_DB_ID", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Video ID", "Platform", "Status", "TikTok URL", "Twitter URL", "Paylaşım Tarihi"],
            "expected_daily_activity": True,   # Günde 3 kez: UTC 08/11/14
            "shared_notion_db_group": "social_media_db",
            "railway_service_id": os.environ.get("RAILWAY_SVC_TWITTER", ""),
        },
        {
            "name": "YouTube Kapak",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_YOUTUBE_KAPAK", "BURAYA_NOTION_DB_ID"),
            "notion_properties": ["Name", "Status"],
            "expected_daily_activity": False,  # Talep bazlı çalışır
            "railway_service_id": os.environ.get("RAILWAY_SVC_YOUTUBE_KAPAK", ""),
        },
        {
            "name": "eCom Reklam Otomasyonu",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "custom_notion",
            "notion_token_key": "NOTION_SOCIAL_TOKEN",
            "notion_db_id": os.environ.get("NOTION_DB_ECOM_REKLAM", ""),
            "notion_properties": ["Proje", "Marka", "Ürün", "Durum", "Tarih"],
            "expected_daily_activity": False,
            "railway_service_id": os.environ.get("RAILWAY_SVC_ECOM_REKLAM", ""),
        },


        # ══════════════════════════════════════════════════════
        # GRUP 3: RAILWAY SERVİSLERİ
        # ══════════════════════════════════════════════════════

        {
            "name": "SWC Email Responder",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "railway_only",        # Notion yok, sadece Railway health check
            "railway_service_id": os.environ.get("RAILWAY_SVC_SWC", ""),
            "expected_daily_activity": True,
        },
        {
            "name": "Shorts Demo Otomasyonu",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "railway_only",        # Railway deploy — AI short üretim botu
            "railway_service_id": os.environ.get("RAILWAY_SVC_SHORTS", ""),
            "expected_daily_activity": False,  # Talep bazlı çalışır
        },
        {
            "name": "Ceren İzlenme Notifier",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "railway_only",        # Apify scraper + Gmail notifier
            "railway_service_id": os.environ.get("RAILWAY_SVC_CEREN", ""),
            "expected_daily_activity": True,   # Günlük izlenme takibi
        },

        # ══════════════════════════════════════════════════════
        # GRUP 4: LOKAL / ÖZEL PİPELINE
        # ══════════════════════════════════════════════════════

        {
            "name": "E-posta Asistanı",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "local_only",          # Windows Görev Zamanlayıcı — Railway deploy yok
            "railway_service_id": "",          # Railway'de değil
            "expected_daily_activity": True,   # Her gün 12:00 çalışır
            "notes": "Windows Task Scheduler ile günlük 12:00'da çalışır. Gmail + Groq AI.",
        },
        {
            "name": "Dubai Emlak İçerik Yazarı",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "local_only",          # Lokal Python scripti
            "railway_service_id": os.environ.get("RAILWAY_SVC_DUBAI", ""),
            "expected_daily_activity": False,
            "notes": "Gayrimenkul içerik üretim pipeline'ı — blog/sosyal medya yazıları.",
        },
        {
            "name": "Emlak Arazi Drone Çekim",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "local_only",          # Lokal otomasyon
            "railway_service_id": os.environ.get("RAILWAY_SVC_DRONE", ""),
            "expected_daily_activity": False,
            "notes": "Drone çekim organize ve yönetim pipeline'ı.",
        },
        {
            "name": "Örnek AI Website",
            "spreadsheet_id": "",
            "sheet_tabs": [],
            "expected_columns": [],
            "expected_column_keywords": [],
            "pipeline": "static_site",         # Netlify deploy — Next.js
            "railway_service_id": "",          # Railway'de değil, Netlify'da
            "expected_daily_activity": False,
            "notes": "Next.js tabanlı AI website — Netlify'da deploy edildi.",
        },
    ]

    # ── Token Expire Takibi ─────────────────────────────
    # Not: Tarihler master.env'deki yorum satırından alınmıştır
    # LinkedIn token 60 gün geçerli — yenilemek için LinkedIn Developer Portal
    TOKEN_EXPIRY_TRACKING = [
        {
            "name": "LINKEDIN_ACCESS_TOKEN",
            "issued_date": "2026-03-25",
            "expiry_date": "2026-07-24",
            "validity_days": 60,
            "warning_days_before": 14,  # 14 gün kala uyarı
            "description": "LinkedIn OAuth2 bearer token",
            "renewal_url": "https://www.linkedin.com/developers/apps",
        },
    ]

    # ── Railway Deployment Probe ────────────────────────
    RAILWAY_TOKEN = os.environ.get("RAILWAY_TOKEN", "")
    RAILWAY_GRAPHQL_URL = "https://backboard.railway.com/graphql/v2"

    @classmethod
    def get_railway_service_ids(cls) -> list[dict]:
        """Aktif projelerin Railway service ID'lerini toplar."""
        services = []
        for project in cls.MONITORED_PROJECTS:
            sid = project.get("railway_service_id")
            if sid:
                services.append({
                    "name": project["name"],
                    "service_id": sid,
                })
        return services

    # ── Zamanlama ────────────────────────────────────────
    CHECK_INTERVAL_HOURS = int(os.environ.get("CHECK_INTERVAL_HOURS", "24"))

    @classmethod
    def validate(cls) -> bool:
        """Zorunlu konfigürasyon değerlerini kontrol eder."""
        errors = []

        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY tanımlı değil")

        if errors:
            error_msg = f"Eksik konfigürasyon nedeniyle uygulama başlatılamadı: {', '.join(errors)}"
            for err in errors:
                logger.error(f"❌ Config hatası: {err}")
            raise EnvironmentError(error_msg)

        logger.info("✅ Konfigürasyon doğrulandı")
        return True

    @classmethod
    def get_google_credentials_info(cls):
        """Google credentials bilgisini döner."""
        if cls.GOOGLE_SERVICE_ACCOUNT_JSON:
            try:
                return json.loads(cls.GOOGLE_SERVICE_ACCOUNT_JSON)
            except json.JSONDecodeError:
                logger.error("GOOGLE_SERVICE_ACCOUNT_JSON parse edilemedi")
                return None
        return None
