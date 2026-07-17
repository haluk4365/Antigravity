"""
AR-002_22 / MASTER-004: Decision Packet — HLK karar veri yapısı.

Decision Engine tarafından üretilen, immutable karar paketi.
Decision Packet; Executor'un ne yapacağını, hangi provider'larla
yapacağını ve kararın gerekçesini taşır.

Bu modül:
- Decision Packet veri modelini tanımlar (AR-002_22 Adım 3)
- Karar gerekçesini 15_KARAR_GEREKCESI_STANDARDI.md formatında tutar
- ReEvaluationContext yapısını tanımlar (Feedback Loop için)
- Immutable — oluşturulduktan sonra değiştirilemez

Bu modül:
- Karar vermez (Decision Engine'in görevi)
- Provider seçmez (Selection Architecture'ın görevi)
- Kod yürütmez (Executor'un görevi)

Mimari Dayanak:
- MASTER-004: Karar Mekanizması
- AR-002_22: Constitutional Feedback Loop
- AR-002_49: Selection Architecture
- 15_KARAR_GEREKCESI_STANDARDI.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PROVIDER REFERENCE — Selection Architecture'ın seçtiği provider
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ProviderRef:
    """Selection Architecture tarafından seçilen provider referansı (immutable)."""
    category: str          # "image", "voice", "video"
    provider: str          # "fal.ai", "kie.ai", "elevenlabs", "hedra", "higgsfield"
    priority: int          # 1 = birincil, 2 = yedek, 3 = üçüncül
    confidence: float      # 0.0 — 1.0 güven skoru
    justification: str     # Seçim gerekçesi (teknik sabit veya açıklama)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "provider": self.provider,
            "priority": self.priority,
            "confidence": self.confidence,
            "justification": self.justification,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RE-EVALUATION CONTEXT — Feedback Loop → Decision Engine bağlamı
# ═══════════════════════════════════════════════════════════════════════════════

class ReEvaluationReason(str, Enum):
    """AR-002_22 Adım 2: Yeniden değerlendirme nedenleri.

    Bunlar KARAR DEĞİLDİR. Bunlar ÖNERİ DEĞİLDİR.
    Bunlar yalnızca "mevcut karar neden geçersiz" sorusunun cevabıdır.
    """
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    CONSTITUTIONAL_BLOCK = "CONSTITUTIONAL_BLOCK"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    STATE_MISMATCH = "STATE_MISMATCH"
    NEW_INFORMATION_RECEIVED = "NEW_INFORMATION_RECEIVED"
    USER_CANCELLED = "USER_CANCELLED"
    GC_LIMIT_EXCEEDED = "GC_LIMIT_EXCEEDED"


@dataclass
class ReEvaluationContext:
    """AR-002_22: Feedback Loop'tan Decision Engine'e iletilen bağlam.

    KARAR İÇERMEZ. ÖNERİ İÇERMEZ.
    Yalnızca mevcut kararın neden yeniden değerlendirilmesi gerektiğini açıklar.
    """
    original_decision_id: str = ""
    trigger_event: str = ""
    re_evaluation_reason: str = ""
    current_state: str = ""
    re_evaluation_count: int = 0
    failure_detail: str = ""
    failed_provider: str = ""

    def to_dict(self) -> dict:
        return {
            "original_decision_id": self.original_decision_id,
            "trigger_event": self.trigger_event,
            "re_evaluation_reason": self.re_evaluation_reason,
            "current_state": self.current_state,
            "re_evaluation_count": self.re_evaluation_count,
            "failure_detail": self.failure_detail,
            "failed_provider": self.failed_provider,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DECISION PACKET — Decision Engine'in nihai kararı
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DecisionPacket:
    """AR-002_22 Adım 3: Decision Engine tarafından üretilen karar paketi.

    Immutable — oluşturulduktan sonra hiçbir alanı değiştirilemez.
    Decision Engine'in TEK çıktısıdır.

    Executor bu paketi uygular, DEĞİŞTİRMEZ.
    Feedback Loop bu paketi denetler, DEĞİŞTİRMEZ.
    """
    # ── Karar Kimliği ────────────────────────────────────────────────────
    decision_id: str = ""
    re_evaluation_of: str = ""           # Bu bir yeniden değerlendirme ise orijinal karar ID'si
    re_evaluation_count: int = 0         # 0 = ilk karar, 1-3 = yeniden değerlendirme

    # ── Üretim Bağlamı ───────────────────────────────────────────────────
    pid: str = ""
    user_id: int = 0
    product_name: str = ""
    brand: str = ""
    duration: int = 15
    voice_lang: str = "tr"

    # ── Provider Seçimleri (Selection Architecture tarafından) ───────────
    image_providers: tuple[ProviderRef, ...] = ()
    voice_providers: tuple[ProviderRef, ...] = ()
    video_providers: tuple[ProviderRef, ...] = ()

    # ── Karar Gerekçesi (15_KARAR_GEREKCESI_STANDARDI.md) ────────────────
    justification: dict = field(default_factory=dict)

    # ── Metadata ─────────────────────────────────────────────────────────
    created_at: str = ""
    decision_maker: str = "HLK_DECISION_ENGINE"
    source_state: str = "STATE_VIDEO_PRODUCTION"

    def __post_init__(self):
        if not self.decision_id:
            ts = datetime.now().strftime("%Y%m%d")
            uid = uuid.uuid4().hex[:4].upper()
            object.__setattr__(self, "decision_id", f"DE-{ts}-{uid}")
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc).isoformat())

    # ── Provider Erişim Yardımcıları ─────────────────────────────────────

    @property
    def primary_image_provider(self) -> Optional[ProviderRef]:
        for p in self.image_providers:
            if p.priority == 1:
                return p
        return self.image_providers[0] if self.image_providers else None

    @property
    def fallback_image_provider(self) -> Optional[ProviderRef]:
        for p in self.image_providers:
            if p.priority == 2:
                return p
        return None

    @property
    def primary_voice_provider(self) -> Optional[ProviderRef]:
        for p in self.voice_providers:
            if p.priority == 1:
                return p
        return self.voice_providers[0] if self.voice_providers else None

    @property
    def primary_video_provider(self) -> Optional[ProviderRef]:
        for p in self.video_providers:
            if p.priority == 1:
                return p
        return self.video_providers[0] if self.video_providers else None

    @property
    def fallback_video_provider(self) -> Optional[ProviderRef]:
        for p in self.video_providers:
            if p.priority == 2:
                return p
        return None

    @property
    def has_image_fallback(self) -> bool:
        return self.fallback_image_provider is not None

    @property
    def has_video_fallback(self) -> bool:
        return self.fallback_video_provider is not None

    def get_provider_list(self, category: str) -> list[ProviderRef]:
        """Kategoriye göre öncelik sıralı provider listesini döndürür."""
        if category == "image":
            providers = list(self.image_providers)
        elif category == "voice":
            providers = list(self.voice_providers)
        elif category == "video":
            providers = list(self.video_providers)
        else:
            return []
        providers.sort(key=lambda p: p.priority)
        return providers

    # ── Serializasyon ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "re_evaluation_of": self.re_evaluation_of,
            "re_evaluation_count": self.re_evaluation_count,
            "pid": self.pid,
            "user_id": self.user_id,
            "product_name": self.product_name,
            "brand": self.brand,
            "duration": self.duration,
            "voice_lang": self.voice_lang,
            "image_providers": [p.to_dict() for p in self.image_providers],
            "voice_providers": [p.to_dict() for p in self.voice_providers],
            "video_providers": [p.to_dict() for p in self.video_providers],
            "justification": self.justification,
            "created_at": self.created_at,
            "decision_maker": self.decision_maker,
            "source_state": self.source_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DecisionPacket:
        return cls(
            decision_id=data.get("decision_id", ""),
            re_evaluation_of=data.get("re_evaluation_of", ""),
            re_evaluation_count=data.get("re_evaluation_count", 0),
            pid=data.get("pid", ""),
            user_id=data.get("user_id", 0),
            product_name=data.get("product_name", ""),
            brand=data.get("brand", ""),
            duration=data.get("duration", 15),
            voice_lang=data.get("voice_lang", "tr"),
            image_providers=tuple(
                ProviderRef(**p) for p in data.get("image_providers", [])
            ),
            voice_providers=tuple(
                ProviderRef(**p) for p in data.get("voice_providers", [])
            ),
            video_providers=tuple(
                ProviderRef(**p) for p in data.get("video_providers", [])
            ),
            justification=data.get("justification", {}),
            created_at=data.get("created_at", ""),
            decision_maker=data.get("decision_maker", "HLK_DECISION_ENGINE"),
            source_state=data.get("source_state", "STATE_VIDEO_PRODUCTION"),
        )
