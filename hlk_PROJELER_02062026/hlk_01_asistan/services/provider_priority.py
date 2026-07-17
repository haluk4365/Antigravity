"""
AR-002_49 / AR-002_75: Provider Priority List — Servis Sağlayıcı Öncelik Listesi.

Selection Architecture tarafından kullanılan, HLK'nın kullanabileceği tüm
servis sağlayıcılarının (provider) yetenek, maliyet, güvenilirlik ve
operasyonel durum bazlı öncelik sıralamasını yönetir.

Bu modül:
- Provider kayıtlarını tutar (image, voice, video kategorilerinde)
- Provider durumunu değerlendirir (API erişimi, kredi, konfigürasyon)
- Her kategori için öncelik sıralı provider listesi üretir
- Selection Architecture'a provider adaylarını sunar

Bu modül:
- Karar vermez (Decision Engine'in görevi)
- Provider seçimi yapmaz (Selection Architecture'ın görevi)
- Provider'ları çalıştırmaz (Executor'un görevi)

Mimari Dayanak:
- AR-002_49: Selection Architecture
- AR-002_75: Provider Selection
- AR-002_3: Dinamik öncelik sıralaması
- 01_Global_Configuration.md: GC parametreleri
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PROVIDER DURUM SABITLERI
# ═══════════════════════════════════════════════════════════════════════════════

class ProviderStatus(str, Enum):
    """Bir provider'ın operasyonel durumu."""
    AVAILABLE = "AVAILABLE"            # API erişilebilir, kredi yeterli
    DEGRADED = "DEGRADED"             # Yavaş ama çalışıyor
    NO_CREDITS = "NO_CREDITS"         # Kredi tükendi
    API_KEY_MISSING = "API_KEY_MISSING"  # API anahtarı yok
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # Servis çevrim dışı
    DISABLED = "DISABLED"             # Devre dışı bırakıldı
    UNKNOWN = "UNKNOWN"               # Durum bilinmiyor


class ProviderCategory(str, Enum):
    """Provider hizmet kategorileri."""
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PROVIDER KAYDI
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProviderRecord:
    """Tek bir servis sağlayıcısının kaydı."""
    name: str                          # "fal.ai", "kie.ai", "elevenlabs", vb.
    category: str                      # "image", "voice", "video"
    display_name: str = ""             # İnsan-okunur ad
    env_key: str = ""                  # .env'deki API key değişken adı
    base_cost: float = 0.0             # Tahmini birim maliyet (USD)
    typical_confidence: float = 0.85   # Tipik güven skoru (0.0 — 1.0)
    typical_latency_ms: float = 5000.0 # Tipik gecikme (ms)
    max_retries: int = 3               # Maksimum deneme sayısı
    enabled: bool = True               # Sistem genelinde aktif mi?

    @property
    def is_configured(self) -> bool:
        """API anahtarı .env'de tanımlanmış mı?"""
        if not self.env_key:
            return False
        return bool(os.getenv(self.env_key, ""))

    @property
    def status(self) -> ProviderStatus:
        """Provider'ın mevcut operasyonel durumunu belirler."""
        if not self.enabled:
            return ProviderStatus.DISABLED
        if not self.is_configured:
            return ProviderStatus.API_KEY_MISSING
        return ProviderStatus.AVAILABLE


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PROVIDER REGISTRY — Tüm provider'ların kayıtlı olduğu merkezi liste
# ═══════════════════════════════════════════════════════════════════════════════

# Her provider kaydı; ANA YASA değişmedikçe bu liste değişmez.
# Provider ekleme/çıkarma bu listeden yapılır — kodun içine gömülmez.

_PROVIDER_REGISTRY: list[ProviderRecord] = [
    # ── Görsel Üretimi ──────────────────────────────────────────────────
    ProviderRecord(
        name="fal.ai",
        category="image",
        display_name="Fal.ai (Seedance)",
        env_key="FAL_KEY",
        base_cost=0.05,
        typical_confidence=0.82,
        typical_latency_ms=25000.0,
    ),
    ProviderRecord(
        name="kie.ai",
        category="image",
        display_name="Kie AI (z-image)",
        env_key="KIE_AI_API_KEY",
        base_cost=0.03,
        typical_confidence=0.91,
        typical_latency_ms=30000.0,
    ),

    # ── Ses Üretimi ─────────────────────────────────────────────────────
    ProviderRecord(
        name="elevenlabs",
        category="voice",
        display_name="ElevenLabs TTS",
        env_key="ELEVENLABS_API_KEY",
        base_cost=0.02,
        typical_confidence=0.97,
        typical_latency_ms=3000.0,
    ),

    # ── Video Üretimi ───────────────────────────────────────────────────
    ProviderRecord(
        name="hedra",
        category="video",
        display_name="Hedra AI (Lip-Sync)",
        env_key="HEDRA_API_KEY",
        base_cost=0.50,
        typical_confidence=0.88,
        typical_latency_ms=60000.0,
    ),
    ProviderRecord(
        name="higgsfield",
        category="video",
        display_name="Higgsfield AI (Seedance)",
        env_key="HIGGSFIELD_KEY_ID",
        base_cost=0.75,
        typical_confidence=0.94,
        typical_latency_ms=45000.0,
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PROVIDER PRIORITY LIST — Öncelik sıralaması motoru
# ═══════════════════════════════════════════════════════════════════════════════

class ProviderPriorityList:
    """AR-002_75: Kategori bazlı dinamik provider öncelik listesi.

    Selection Architecture tarafından kullanılır.
    Her kategori için provider'ları operasyonel duruma ve
    değerlendirme kriterlerine göre öncelik sırasına dizer.

    Öncelik kriterleri (AR-002_3):
    1. API erişilebilirliği (AVAILABLE > diğerleri)
    2. Güven skoru (yüksek > düşük)
    3. Maliyet (düşük > yüksek)
    4. Gecikme (düşük > yüksek)
    """

    def __init__(self):
        self._registry = list(_PROVIDER_REGISTRY)

    # ── Provider Kayıt Yönetimi ─────────────────────────────────────────

    def get_providers(self, category: str) -> list[ProviderRecord]:
        """Belirli bir kategorideki tüm provider'ları döndürür."""
        return [p for p in self._registry if p.category == category]

    def get_provider(self, name: str) -> Optional[ProviderRecord]:
        """İsme göre provider kaydını döndürür."""
        for p in self._registry:
            if p.name == name:
                return p
        return None

    # ── Operasyonel Durum ───────────────────────────────────────────────

    def get_available(self, category: str) -> list[ProviderRecord]:
        """Kategorideki API anahtarı tanımlı provider'ları döndürür."""
        return [
            p for p in self.get_providers(category)
            if p.status == ProviderStatus.AVAILABLE
        ]

    def get_unavailable(self, category: str) -> list[ProviderRecord]:
        """Kategorideki kullanılamaz durumdaki provider'ları döndürür."""
        return [
            p for p in self.get_providers(category)
            if p.status != ProviderStatus.AVAILABLE
        ]

    # ── Öncelik Skoru Hesaplama ─────────────────────────────────────────

    @staticmethod
    def _score(provider: ProviderRecord) -> float:
        """AR-002_3: Provider için çok boyutlu öncelik skoru hesaplar.

        Skor bileşenleri:
        - API durumu: AVAILABLE ise +100, değilse -1000 (elenir)
        - Güven: confidence * 50 (max +50)
        - Maliyet: (1.0 - base_cost) * 20 (düşük maliyet = yüksek skor, max +20)
        - Gecikme: (1.0 - latency/120000) * 10 (düşük gecikme = yüksek skor, max +10)
        """
        if provider.status != ProviderStatus.AVAILABLE:
            return -1000.0

        score = 100.0  # Temel — API erişilebilir
        score += provider.typical_confidence * 50.0
        score += max(0, (1.0 - min(provider.base_cost, 1.0))) * 20.0
        score += max(0, (1.0 - min(provider.typical_latency_ms, 120000.0) / 120000.0)) * 10.0

        return round(score, 2)

    # ── Öncelik Sıralaması ──────────────────────────────────────────────

    def rank(self, category: str) -> list[ProviderRecord]:
        """Kategorideki provider'ları öncelik skoruna göre sıralar.

        Dönüş:
            En yüksek skorlu (birincil) → en düşük skorlu (son yedek)
            Kullanılamaz durumdaki provider'lar listenin sonunda yer alır.
        """
        providers = self.get_providers(category)
        scored = [(p, self._score(p)) for p in providers]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, s in scored]

    def get_priority_map(self, category: str) -> list[dict]:
        """Kategori için priority-map döndürür (Selection Architecture için).

        Her girdi:
        {
            "provider": str,
            "priority": int (1-indexed),
            "confidence": float,
            "score": float,
            "status": str,
            "justification": str
        }
        """
        ranked = self.rank(category)
        result = []
        for i, p in enumerate(ranked, 1):
            score = self._score(p)
            result.append({
                "provider": p.name,
                "display_name": p.display_name,
                "priority": i,
                "confidence": p.typical_confidence,
                "score": score,
                "status": p.status.value,
                "justification": self._build_justification(p, i, score),
            })
        return result

    @staticmethod
    def _build_justification(provider: ProviderRecord, rank: int, score: float) -> str:
        """15_KARAR_GEREKCESI_STANDARDI.md uyumlu seçim gerekçesi."""
        if provider.status == ProviderStatus.API_KEY_MISSING:
            return "API_KEY_MISSING: Provider API anahtarı tanımlanmamış"
        if provider.status == ProviderStatus.DISABLED:
            return "DISABLED: Provider sistem genelinde devre dışı"
        if provider.status == ProviderStatus.NO_CREDITS:
            return "NO_CREDITS: Provider kredisi tükenmiş"
        if provider.status == ProviderStatus.SERVICE_UNAVAILABLE:
            return "SERVICE_UNAVAILABLE: Provider çevrim dışı"
        reasons = []
        reasons.append(f"API_ACCESSIBLE: Provider erişilebilir (skor={score:.1f})")
        reasons.append(f"CONFIDENCE: {provider.typical_confidence:.0%}")
        reasons.append(f"COST_ESTIMATE: ${provider.base_cost:.2f}/birim")
        return " | ".join(reasons)

    # ── Toplu Kategori Değerlendirmesi ───────────────────────────────────

    def evaluate_all(self) -> dict[str, list[dict]]:
        """Tüm kategoriler için öncelik listesini döndürür.

        Selection Architecture'ın ana giriş noktası.
        """
        return {
            "image": self.get_priority_map("image"),
            "voice": self.get_priority_map("voice"),
            "video": self.get_priority_map("video"),
        }

    def has_any_available(self, category: str) -> bool:
        """Kategoride en az bir kullanılabilir provider var mı?"""
        return len(self.get_available(category)) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

provider_priority = ProviderPriorityList()
"""Global Provider Priority List singleton'ı.

Selection Architecture tarafından kullanılır.
"""
