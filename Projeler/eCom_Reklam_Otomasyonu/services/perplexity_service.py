"""
Perplexity Service — Marka Araştırması
=======================================
Perplexity API ile marka/ürün araştırması yapar.
Sonuçları yapılandırılmış formatta döndürür.
"""

import requests

from logger import get_logger
from utils.retry import retry_api_call

log = get_logger("perplexity_service")

# Perplexity API timeout
REQUEST_TIMEOUT = 30

# Perplexity bilgi bulamadığında ürettiği metinde geçen tipik fraz örnekleri.
# Bunlardan biri varsa response "found=False" sayılır ve scenario_engine
# generic ton'a düşer (uydurma marka bilgisi senaryoyu zehirlemesin).
_NO_INFO_PATTERNS = (
    "bulamadım",
    "could not find",
    "no information",
    "not available",
    "fictional",
    "made up",
    "doğrulanmış bilgi yok",
    "kaynak bulunamadı",
    "kaynağa ulaşılamadı",
    "bilgi mevcut değil",
    "veri bulunamadı",
    "sources not available",
)


def _looks_like_no_info(text: str) -> bool:
    """Perplexity'nin "bulamadım" tarzı yanıtını tespit eder."""
    if not text:
        return True
    lower = text.lower()
    return any(p in lower for p in _NO_INFO_PATTERNS)


class PerplexityService:
    """Perplexity API ile marka/ürün araştırması."""

    def __init__(self, api_key: str, base_url: str = "https://api.perplexity.ai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def research_brand(self, brand_name: str, product_name: str = "",
                       language: str = "tr") -> str:
        """
        Marka ve ürün hakkında güncel web araştırması yapar. (Geçici olarak devre dışı)
        """
        log.warning(f"Perplexity bypass aktif. '{brand_name}' icin arastirma atlandi.")
        self.last_found = False
        return ""

    @retry_api_call(max_retries=2, base_delay=2.0, operation_name="Perplexity research")
    def _call_perplexity(self, payload: dict, brand_name: str) -> str:
        """Perplexity API çağrısı — retry mekanizmalı."""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        # Güvenli erişim — eksik key'lerde KeyError önlenir
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"Perplexity boş yanıt döndü: {brand_name}")
        content = choices[0].get("message", {}).get("content", "")
        if not content.strip():
            raise RuntimeError(f"Perplexity boş content döndü: {brand_name}")

        log.info(f"Marka araştırması tamamlandı: '{brand_name}' — {len(content)} karakter")
        return content
