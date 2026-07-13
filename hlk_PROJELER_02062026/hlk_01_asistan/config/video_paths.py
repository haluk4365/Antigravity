"""
GC-001 — Merkezi Video Path Yapılandırması

ANA YASA / 01_Global_Configuration.md uyumlu:
- Tüm video ve ses dosyası yolları tek merkezden yönetilir.
- Hiçbir Python dosyasında ham path string'i tekrar edilmez.
- Değişiklik gerektiğinde yalnızca bu dosya güncellenir.

MASTER-003: ANA YASA Güncellendi + Kod Güncellendi + Runtime Doğrulandı = TAMAMLANDI
"""

from pathlib import Path

# ─── Proje Kök Dizini ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ─── Video Ana Dizini ─────────────────────────────────────────────────────────
VIDEO_ROOT = PROJECT_ROOT / "VİDEO Dosyaları"

# ─── SAHNE-01: HLK Karşılama Videosu ──────────────────────────────────────────
SAHNE1_DIR = VIDEO_ROOT / "sahne-1 giriş"
SAHNE1_VIDEO = SAHNE1_DIR / "hlk_sahne1.mp4"
SAHNE1_YEDEK = SAHNE1_DIR / "hlk_sahne1_yedek.mp4"
SAHNE1_SURE = 8  # saniye (~5sn video + 3sn donuk son kare)

# ─── SAHNE-02: Dile Özel Lip-Sync Videoları ──────────────────────────────────
SAHNE2_DIR = VIDEO_ROOT / "sahne-2"
# MASTER-003: SAHNE-3 ile aynı isimlendirme standardı — SAHNE-2_{LANG}_alt.mp4
SAHNE2_VIDEO_TEMPLATE = "SAHNE-2_{LANG}_alt.mp4"
SAHNE2_SURE = 13  # varsayılan (TR/EN)
SAHNE2_SURE_LANG = {
    "TR": 18, "EN": 19, "DE": 20, "FR": 24,
    "ES": 23, "RU": 22, "AR": 23, "KR": 16,
}
SAHNE2_FALLBACK_LANG = "TR"

# ─── Zamanlama Parametreleri (GC uyumlu) ─────────────────────────────────
SAHNE2_EXTRA_WAIT = 5        # SAHNE-2 / SAHNE-13 video sonu ekstra bekleme (sn) — GC_SAHNE2_EXTRA_WAIT uyumlu
LINK_PROCESSING_WAIT = 4     # Link işleme sonrası bekleme (sn)
BALLOON_STAGGER_DELAY = 1    # Konuşma balonları arası gecikme (sn)

# ─── SAHNE-03: Format Seçim Videoları ─────────────────────────────────────────
SAHNE3_DIR = VIDEO_ROOT / "sahne-3"

# ─── SAHNE-13: Brief Tamamlandı Videoları (FD-008_1 uyumlu) ─────────────────
SAHNE13_DIR = VIDEO_ROOT / "sahne-13"
SAHNE13_VIDEO_TEMPLATE = "SAHNE-13_{LANG}_alt.mp4"
SAHNE13_SURE = 32  # varsayılan (ffprobe: TR ~28.9sn)
SAHNE13_SURE_LANG = {
    "TR": 32, "EN": 32, "DE": 39, "FR": 37,
    "ES": 35, "RU": 37, "AR": 35, "KR": 41,
}

# ─── Ses Dosyaları ────────────────────────────────────────────────────────────
SES_ROOT = PROJECT_ROOT / "SES Dosyaları"
SES_SAHNE2_DIR = SES_ROOT / "hedra_SAHNE-2"
SES_SAHNE3_DIR = SES_ROOT / "hedra_SAHNE-3"
SES_SAHNE2_TEMPLATE = "hedra_ses_{lang}.mp3"
SES_TEST_DIR = SES_ROOT / "test"

# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def get_sahne1_video() -> Path:
    """SAHNE-01 karşılama videosunun tam yolunu döndürür."""
    return SAHNE1_VIDEO


def get_sahne2_video(language: str) -> Path | None:
    """Dile göre SAHNE-02 video yolunu döndürür. Yoksa None."""
    path = SAHNE2_DIR / SAHNE2_VIDEO_TEMPLATE.format(LANG=language.upper())
    return path if path.exists() else None


def get_sahne13_video(language: str) -> Path | None:
    """Dile göre SAHNE-13 video yolunu döndürür. Yoksa None.

    KR dil kodu için "kır" dosya adı varyantını dener.
    """
    lang = language.upper()
    path = SAHNE13_DIR / SAHNE13_VIDEO_TEMPLATE.format(LANG=lang)
    if path.exists():
        return path
    # "KR" için "kır" varyantı
    if lang == "KR":
        alt = SAHNE13_DIR / "SAHNE-13_kır_alt.mp4"
        if alt.exists():
            return alt
    return None


def get_sahne2_audio(language: str) -> Path:
    """Dile göre SAHNE-2 ses dosyası yolunu döndürür."""
    return SES_SAHNE2_DIR / SES_SAHNE2_TEMPLATE.format(lang=language.lower())


def validate_all_paths() -> dict[str, bool]:
    """Tüm kritik path'lerin varlığını doğrular (MASTER-003 uyumluluk kontrolü).

    Returns:
        {"sahne1_video": bool, "sahne2_videos": {lang: bool}, ...}
    """
    result = {
        "sahne1_video": SAHNE1_VIDEO.exists(),
        "sahne2_videos": {},
    }
    for lang in ["tr", "en", "de", "fr", "es", "ar", "ru", "kr"]:
        result["sahne2_videos"][lang] = (
            SAHNE2_DIR / SAHNE2_VIDEO_TEMPLATE.format(lang=lang)
        ).exists()
    return result
