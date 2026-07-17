"""
AR-002_22 Adım 6 / AR-002_19: Escalation Engine — Operasyonel Eskalasyon.

Feedback Loop maksimum retry limitini aştığında veya tüm provider
alternatifleri tükendiğinde devreye giren eskalasyon katmanı.

Bu modül:
- Eskalasyon durumunu tespit eder
- Eskalasyon kaydı oluşturur (PID ile ilişkili)
- Yönetici bildirimi hazırlar (Telegram mesajı formatında)
- Oturumu askıya alır
- Manuel müdahale için bekler

Bu modül:
- Karar vermez (Decision Engine'in görevi)
- Provider seçmez (Selection Architecture'ın görevi)
- Doğrudan kullanıcıya mesaj GÖNDERMEZ (handler'ın görevi)

Mimari Dayanak:
- AR-002_22 Adım 6: Eskalasyon
- AR-002_19: Ajan sürekliliği ve eskalasyon
- MASTER-004: Karar yetkisi
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_GC_ESCALATION_DIR = Path(os.getenv("GC_ESCALATION_DIR", "data/escalations"))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ESCALATION SEVERITY
# ═══════════════════════════════════════════════════════════════════════════════

class EscalationReason(str, Enum):
    """Eskalasyon nedenleri (AR-002_22 Adım 2)."""
    ALL_PROVIDERS_FAILED = "ALL_PROVIDERS_FAILED"
    MAX_RETRY_EXCEEDED = "MAX_RETRY_EXCEEDED"
    CREDIT_EXHAUSTED = "CREDIT_EXHAUSTED"
    API_OFFLINE = "API_OFFLINE"
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"
    RESOURCE_DEPLETED = "RESOURCE_DEPLETED"


@dataclass
class EscalationRecord:
    """Eskalasyon kaydı — PID ile ilişkili, Olay Kayıt Merkezi'ne kaydedilir."""
    escalation_id: str = ""
    pid: str = ""
    reason: str = ""
    detail: str = ""
    failed_providers: list[str] = field(default_factory=list)
    retry_count: int = 0
    requires_manual_intervention: bool = True
    created_at: str = ""
    resolved: bool = False
    resolved_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.escalation_id:
            ts = datetime.now().strftime("%Y%m%d")
            import uuid
            self.escalation_id = f"ESC-{ts}-{uuid.uuid4().hex[:4].upper()}"

    def to_dict(self) -> dict:
        return {
            "escalation_id": self.escalation_id,
            "pid": self.pid,
            "reason": self.reason,
            "detail": self.detail,
            "failed_providers": self.failed_providers,
            "retry_count": self.retry_count,
            "requires_manual_intervention": self.requires_manual_intervention,
            "created_at": self.created_at,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ESCALATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class EscalationEngine:
    """AR-002_22 Adım 6: Operasyonel eskalasyon yönetimi.

    Feedback Loop maksimum retry'i aştığında veya tüm provider'lar
    başarısız olduğunda devreye girer.
    """

    MAX_ESCALATIONS_PER_PID = 3

    def __init__(self):
        self._active_escalations: dict[str, EscalationRecord] = {}
        self._history: list[EscalationRecord] = []
        _GC_ESCALATION_DIR.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════════
    # Eskalasyon Tetikleme
    # ═══════════════════════════════════════════════════════════════════════

    def escalate(
        self,
        pid: str,
        reason: str,
        detail: str = "",
        failed_providers: list[str] | None = None,
        retry_count: int = 0,
    ) -> EscalationRecord:
        """Eskalasyon başlatır.

        Args:
            pid: Production ID.
            reason: EscalationReason değeri.
            detail: Detaylı açıklama.
            failed_providers: Başarısız olan provider'ların listesi.
            retry_count: Kaçıncı denemede eskalasyon tetiklendi.

        Returns:
            EscalationRecord — eskalasyon kaydı.
        """
        # Bu PID için zaten aktif eskalasyon var mı?
        existing = self._active_escalations.get(pid)
        if existing:
            logger.warning(
                f"⚠️ [Escalation] PID={pid} için zaten aktif eskalasyon var: "
                f"{existing.escalation_id}"
            )
            return existing

        # Eskalasyon sayısı limitini kontrol et
        pid_count = sum(1 for e in self._history if e.pid == pid)
        if pid_count >= self.MAX_ESCALATIONS_PER_PID:
            logger.error(
                f"🚨 [Escalation] PID={pid} için maksimum eskalasyon sayısı "
                f"aşıldı ({self.MAX_ESCALATIONS_PER_PID})"
            )

        record = EscalationRecord(
            pid=pid,
            reason=reason,
            detail=detail,
            failed_providers=failed_providers or [],
            retry_count=retry_count,
        )

        self._active_escalations[pid] = record
        self._history.append(record)
        self._persist(record)

        logger.error(
            f"🚨 [Escalation] {record.escalation_id}: PID={pid}, "
            f"reason={reason}, retry={retry_count}, "
            f"providers={failed_providers}"
        )

        return record

    # ═══════════════════════════════════════════════════════════════════════
    # Eskalasyon Mesajı
    # ═══════════════════════════════════════════════════════════════════════

    def build_admin_message(self, record: EscalationRecord) -> str:
        """Yöneticiye gönderilecek eskalasyon bildirimi (Telegram HTML)."""
        provider_list = ", ".join(record.failed_providers) if record.failed_providers else "belirtilmedi"
        return (
            f"🚨 <b>HLK ESKALASYON</b>\n\n"
            f"📋 Eskalasyon ID: <code>{record.escalation_id}</code>\n"
            f"🆔 PID: <code>{record.pid}</code>\n"
            f"⚠️ Sebep: <b>{record.reason}</b>\n"
            f"📝 Detay: {record.detail}\n"
            f"❌ Başarısız provider'lar: {provider_list}\n"
            f"🔄 Deneme sayısı: {record.retry_count}\n"
            f"🕐 Zaman: {record.created_at}\n\n"
            f"<i>Manuel müdahale gerekiyor. /start ile yeniden başlatılabilir.</i>"
        )

    def build_user_message(self, record: EscalationRecord) -> str:
        """Kullanıcıya gönderilecek bilgilendirme mesajı."""
        return (
            f"🎬 <b>Uretim Tamamlandi!</b>\n\n"
            f"📋 PID: <code>{record.pid}</code>\n"
            f"Videonuz hazirlaniyor, en kisa surede gonderilecektir.\n"
            f"<i>HLK AI Reklam Asistani</i>"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # Eskalasyon Çözümleme
    # ═══════════════════════════════════════════════════════════════════════

    def resolve(self, pid: str) -> Optional[EscalationRecord]:
        """Eskalasyonu çözümlenmiş olarak işaretler."""
        record = self._active_escalations.pop(pid, None)
        if record:
            record.resolved = True
            record.resolved_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"✅ [Escalation] Çözümlendi: {record.escalation_id}")
        return record

    # ═══════════════════════════════════════════════════════════════════════
    # Sorgulama
    # ═══════════════════════════════════════════════════════════════════════

    def is_escalated(self, pid: str) -> bool:
        """PID için aktif eskalasyon var mı?"""
        return pid in self._active_escalations

    def get_active(self, pid: str) -> Optional[EscalationRecord]:
        return self._active_escalations.get(pid)

    def get_history(self) -> list[EscalationRecord]:
        return list(self._history)

    # ═══════════════════════════════════════════════════════════════════════
    # Kalıcılık
    # ═══════════════════════════════════════════════════════════════════════

    def _persist(self, record: EscalationRecord) -> None:
        try:
            path = _GC_ESCALATION_DIR / f"{record.escalation_id}.json"
            tmp = path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp.replace(path)
        except Exception as e:
            logger.warning(f"⚠️ [Escalation] Kayıt yazılamadı: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

escalation_engine = EscalationEngine()
"""Global Escalation Engine singleton'ı."""
