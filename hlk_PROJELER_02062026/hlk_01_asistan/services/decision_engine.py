"""
MASTER-004 / FEAT-002: Decision Engine — HLK'nın tek karar vericisi.

HLK içerisinde karar veren, yöneten ve nihai kararı oluşturan TEK yapı.
Decision Engine; Selection Architecture üzerinden provider seçimi yapar,
Decision Packet üretir ve bu paketi Executor'a iletir.

Bu modül:
- Üretim bağlamını analiz eder
- Selection Architecture ile provider seçimi yapar
- Decision Packet üretir (immutable)
- Karar gerekçesini 15_KARAR_GEREKCESI_STANDARDI.md formatında üretir
- ReEvaluationContext ile yeniden değerlendirme yapar

Bu modül:
- Provider seçimi algoritması ÇALIŞTIRMAZ (Selection Architecture'ın görevi)
- Provider durumunu DEĞİŞTİRMEZ (Provider Priority List'in görevi)
- Kod yürütmez / video üretmez (Executor'un görevi)
- PASS/FAIL vermez (CEE'nin görevi)
- State değiştirmez (State Engine'in görevi)

Mimari Dayanak:
- MASTER-004: Karar Mekanizması
- FEAT-002: Decision Engine
- AR-002_22: Constitutional Feedback Loop
- AR-002_49: Selection Architecture
- 15_KARAR_GEREKCESI_STANDARDI.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from services.decision_packet import (
    DecisionPacket,
    ReEvaluationContext,
    ReEvaluationReason,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PRODUCTION CONTEXT — Decision Engine'e giriş
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProductionContext:
    """Video üretimi için gerekli bağlam bilgisi.

    Decision Engine bu bağlamı analiz ederek karar üretir.
    """
    pid: str = ""
    user_id: int = 0
    product_name: str = ""
    brand: str = ""
    duration: int = 15
    voice_lang: str = "tr"
    url: str = ""
    extra_metadata: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class DecisionEngine:
    """MASTER-004: HLK'nın tek karar vericisi.

    Çalışma sırası:
    1. ProductionContext'i analiz et
    2. Selection Architecture ile provider seçimi yap
    3. Decision Packet üret
    4. Karar gerekçesini oluştur (15_KARAR_GEREKCESI_STANDARDI.md)

    Decision Engine:
    - Provider seçer
    - Karar üretir
    - Gerekçe üretir

    Decision Engine:
    - Kod çalıştırmaz
    - Video üretmez
    - State değiştirmez
    """

    def __init__(self):
        self._decision_history: list[DecisionPacket] = []

    # ═══════════════════════════════════════════════════════════════════════
    # Ana Karar Üretme
    # ═══════════════════════════════════════════════════════════════════════

    def decide(self, context: ProductionContext) -> DecisionPacket:
        """MASTER-004: ProductionContext'ten Decision Packet üretir.

        HLK'nın TEK karar üretme noktası.
        Executor bu kararı uygular, DEĞİŞTİRMEZ.

        Args:
            context: Üretim bağlamı (ürün, kullanıcı, brief verileri).

        Returns:
            DecisionPacket — immutable karar paketi.
        """
        from services.selection_architecture import selection_architecture

        logger.info(
            f"🧠 [DecisionEngine] Karar üretiliyor: "
            f"PID={context.pid}, ürün={context.product_name}, "
            f"marka={context.brand}, süre={context.duration}sn, dil={context.voice_lang}"
        )

        # Adım 1: Selection Architecture ile tüm kategoriler için provider seç
        selections = selection_architecture.select_all()

        # Adım 2: Her kategorinin seçim sonucunu ProviderRef'e dönüştür
        image_refs = selections.get("image").to_provider_refs() if selections.get("image") else ()
        voice_refs = selections.get("voice").to_provider_refs() if selections.get("voice") else ()
        video_refs = selections.get("video").to_provider_refs() if selections.get("video") else ()

        # Adım 3: Karar gerekçesini oluştur
        justification = self._build_justification(context, selections)

        # Adım 4: Decision Packet üret
        packet = DecisionPacket(
            pid=context.pid,
            user_id=context.user_id,
            product_name=context.product_name,
            brand=context.brand,
            duration=context.duration,
            voice_lang=context.voice_lang,
            image_providers=image_refs,
            voice_providers=voice_refs,
            video_providers=video_refs,
            justification=justification,
        )

        # Adım 5: Karar geçmişine ekle
        self._decision_history.append(packet)

        # Log: seçilen provider'ları raporla
        primary_img = packet.primary_image_provider
        primary_voice = packet.primary_voice_provider
        primary_video = packet.primary_video_provider

        # Build log message safely
        img_str = f"{primary_img.provider} (güven: {primary_img.confidence:.0%})" if primary_img else "YOK"
        voice_str = f"{primary_voice.provider} (güven: {primary_voice.confidence:.0%})" if primary_voice else "YOK"
        video_str = f"{primary_video.provider} (güven: {primary_video.confidence:.0%})" if primary_video else "YOK"
        logger.info(
            f"✅ [DecisionEngine] Karar üretildi: {packet.decision_id} | "
            f"Görsel: {img_str} | Ses: {voice_str} | Video: {video_str}"
        )

        return packet

    # ═══════════════════════════════════════════════════════════════════════
    # Yeniden Değerlendirme (Feedback Loop sonrası)
    # ═══════════════════════════════════════════════════════════════════════

    def re_evaluate(
        self, context: ReEvaluationContext, original_context: ProductionContext
    ) -> DecisionPacket:
        """AR-002_22 Adım 3: Feedback Loop sonrası yeniden karar üretir.

        Feedback Loop'tan ReEvaluationContext alır.
        Selection Architecture ile GÜNCEL koşullarda yeniden seçim yapar.
        YENİ bir Decision Packet üretir (eski packet'i değiştirmez).

        Args:
            context: Feedback Loop'tan gelen yeniden değerlendirme bağlamı.
            original_context: Orijinal üretim bağlamı.

        Returns:
            Yeni DecisionPacket — eski karardan bağımsız, güncel koşullara göre.
        """
        from services.selection_architecture import selection_architecture

        logger.info(
            f"🔄 [DecisionEngine] Yeniden değerlendirme: "
            f"orijinal={context.original_decision_id}, "
            f"neden={context.re_evaluation_reason}, "
            f"deneme={context.re_evaluation_count}/3, "
            f"başarısız={context.failed_provider}"
        )

        # Selection Architecture cache'ini temizle — güncel koşulları yansıt
        excluded: dict[str, set[str]] = {}
        if context.failed_provider:
            # Hangi kategoride başarısız olduysa o kategorinin cache'ini temizle
            # ve başarısız provider'ı bu re-eval'de hariç tut
            from services.provider_priority import provider_priority
            failed_record = provider_priority.get_provider(context.failed_provider)
            if failed_record:
                selection_architecture.invalidate_cache(failed_record.category)
                excluded[failed_record.category] = {context.failed_provider}
                logger.info(
                    f"🔄 [DecisionEngine] Cache temizlendi + provider hariç: "
                    f"{failed_record.category} (başarısız: {context.failed_provider})"
                )

        # Tüm kategoriler için yeniden seçim yap (başarısız provider hariç)
        selections = selection_architecture.select_all(excluded)

        image_refs = selections.get("image").to_provider_refs() if selections.get("image") else ()
        voice_refs = selections.get("voice").to_provider_refs() if selections.get("voice") else ()
        video_refs = selections.get("video").to_provider_refs() if selections.get("video") else ()

        justification = self._build_justification(original_context, selections)
        justification["re_evaluation"] = {
            "original_decision_id": context.original_decision_id,
            "reason": context.re_evaluation_reason,
            "count": context.re_evaluation_count,
            "failed_provider": context.failed_provider,
            "failure_detail": context.failure_detail,
        }

        packet = DecisionPacket(
            re_evaluation_of=context.original_decision_id,
            re_evaluation_count=context.re_evaluation_count,
            pid=original_context.pid,
            user_id=original_context.user_id,
            product_name=original_context.product_name,
            brand=original_context.brand,
            duration=original_context.duration,
            voice_lang=original_context.voice_lang,
            image_providers=image_refs,
            voice_providers=voice_refs,
            video_providers=video_refs,
            justification=justification,
        )

        self._decision_history.append(packet)

        logger.info(
            f"✅ [DecisionEngine] Yeniden karar üretildi: {packet.decision_id} "
            f"(re-eval of {context.original_decision_id}, "
            f"deneme {context.re_evaluation_count})"
        )

        return packet

    # ═══════════════════════════════════════════════════════════════════════
    # Karar Gerekçesi (15_KARAR_GEREKCESI_STANDARDI.md)
    # ═══════════════════════════════════════════════════════════════════════

    def _build_justification(
        self,
        context: ProductionContext,
        selections: dict,
    ) -> dict:
        """15_KARAR_GEREKCESI_STANDARDI.md formatında karar gerekçesi üretir.

        Decision Packet içerisinde justification alanına yazılır.
        """
        from services.selection_architecture import SelectionResult

        justifications = []
        alternatives = []

        for category, result in selections.items():
            if not isinstance(result, SelectionResult):
                continue
            if result.primary:
                justifications.append(
                    f"{category}: {result.primary.provider} seçildi "
                    f"(güven: {result.primary.confidence:.0%})"
                )
            if result.fallback:
                alternatives.append(
                    f"{category}: {result.fallback.provider} yedek "
                    f"(güven: {result.fallback.confidence:.0%})"
                )
            if not result.has_primary:
                justifications.append(
                    f"{category}: kullanılabilir provider YOK"
                )

        # Genel güven seviyesi: tüm kategorilerde birincil var mı?
        all_have_primary = all(
            s.primary is not None
            for s in selections.values()
            if isinstance(s, SelectionResult)
        )
        confidence = "HIGH" if all_have_primary else "MEDIUM"

        return {
            "DecisionName": f"Video Production — {context.pid}",
            "DecisionDescription": (
                f"{context.brand} {context.product_name} için "
                f"{context.duration}sn video üretimi kararı. "
                f"Dil: {context.voice_lang}"
            ),
            "DecisionMaker": "HLK_DECISION_ENGINE",
            "DecisionTimestamp": datetime.now(timezone.utc).isoformat(),
            "SourceState": "STATE_VIDEO_PRODUCTION",
            "WorkflowID": "WF-008",
            "FeatureID": "FEAT-002",
            "Justifications": justifications,
            "Alternatives": alternatives,
            "ConfidenceLevel": confidence,
            "DecisionOutcomes": [
                "Provider seçimleri Decision Packet'e yazıldı",
                "Executor provider listesini uygulayacak",
            ],
            "PID": context.pid,
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Yardımcı Metodlar
    # ═══════════════════════════════════════════════════════════════════════

    def get_history(self) -> list[DecisionPacket]:
        """Bu oturumda üretilen tüm kararların listesini döndürür."""
        return list(self._decision_history)

    def get_last_decision(self) -> Optional[DecisionPacket]:
        """Son üretilen kararı döndürür."""
        return self._decision_history[-1] if self._decision_history else None

    def reset(self) -> None:
        """Decision Engine geçmişini temizler (test amaçlı)."""
        self._decision_history.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

decision_engine = DecisionEngine()
"""MASTER-004: Global Decision Engine singleton'ı.

HLK'nın TEK karar vericisi. Tüm kararlar bu singleton üzerinden üretilir.
"""
