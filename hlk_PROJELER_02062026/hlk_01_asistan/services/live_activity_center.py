"""
FEAT-015 / AR-002_59: Live Activity Center (LAC) — Canlı İşlem Merkezi.

HLK'nın gerçek zamanlı Event izleme ve görüntüleme katmanı.
Yalnızca EEC tarafından üretilen GERÇEK Event'leri gösterir.
FAKE PROGRESS KESİNLİKLE KULLANILAMAZ (EEC-001).

Bu modül:
- EEC Event'lerini gerçek zamanlı toplar
- Event'leri kronolojik sırayla saklar
- PID bazlı filtreleme yapar
- Event stream'i üretir (EEC → OKM → LAC zinciri)
- LAC durumunu sorgulanabilir hale getirir

Bu modül:
- Event ÜRETMEZ (EEC'in görevi)
- Karar vermez (Decision Engine'in görevi)
- Fake Progress KULLANMAZ (EEC-001 ihlali)

Mimari Dayanak:
- FEAT-015: Live Activity Center
- AR-002_59: LAC Architecture
- EEC-001: Fake Progress yasağı
- 22_EXECUTION_EVENT_COLLECTOR.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. LAC EVENT — LAC'de gösterilebilir Event
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LACEvent:
    """LAC'de gösterilecek Event.

    Yalnızca GERÇEK Event'ler — Fake Progress kesinlikle yasak.
    """
    event_id: str = ""
    event_type: str = ""
    pid: str = ""
    description: str = ""
    phase: str = ""            # PRE_CHECK / EXECUTE / POST_CHECK
    status: str = "PENDING"    # PENDING / RUNNING / COMPLETED / FAILED
    result: str = ""
    timestamp: str = ""
    sequence: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "pid": self.pid,
            "description": self.description,
            "phase": self.phase,
            "status": self.status,
            "result": self.result,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LAC STATUS — Anlık durum özeti
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LACStatus:
    """LAC anlık durum özeti — PID bazlı."""
    pid: str = ""
    is_active: bool = False
    total_events: int = 0
    completed_events: int = 0
    failed_events: int = 0
    current_phase: str = ""
    last_event_type: str = ""
    last_update: str = ""
    has_escalation: bool = False

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "is_active": self.is_active,
            "total_events": self.total_events,
            "completed_events": self.completed_events,
            "failed_events": self.failed_events,
            "current_phase": self.current_phase,
            "last_event_type": self.last_event_type,
            "last_update": self.last_update,
            "has_escalation": self.has_escalation,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LIVE ACTIVITY CENTER
# ═══════════════════════════════════════════════════════════════════════════════

class LiveActivityCenter:
    """FEAT-015: Canlı İşlem Merkezi.

    EEC → OKM → LAC zincirinin son halkası.
    Yalnızca EEC Event'lerini tüketir, Event ÜRETMEZ.

    Özellikler:
    - PID bazlı Event akışı
    - Kronolojik Event sıralaması
    - Anlık durum özeti (LACStatus)
    - Fake Progress engelleme (EEC-001)
    """

    MAX_EVENTS_PER_PID = 100  # PID başına maksimum saklanan Event

    def __init__(self):
        self._events: dict[str, list[LACEvent]] = {}  # pid → events
        self._sequence: int = 0

    # ═══════════════════════════════════════════════════════════════════════
    # Event Kaydı
    # ═══════════════════════════════════════════════════════════════════════

    def register(self, event_data: dict | object) -> LACEvent:
        """EEC'den gelen Event'i LAC'e kaydeder.

        Yalnızca GERÇEK Event'ler kabul edilir.
        Fake Progress Event'leri REDDEDİLİR.

        Args:
            event_data: EEC tarafından üretilen Event (dict veya ExecutionEvent).

        Returns:
            LACEvent — kaydedilen Event.
        """
        # ExecutionEvent objesini dict'e dönüştür
        if hasattr(event_data, 'to_lac_entry'):
            d = event_data.to_lac_entry()
            pid = d.get("pid", "UNKNOWN")
            event_type = d.get("event_name", "")
            event_id = d.get("event_id", "")
            phase = d.get("phase", "")
            result = d.get("result", "")
            description = f"{event_type}"
        elif hasattr(event_data, 'get'):
            pid = event_data.get("pid", "UNKNOWN")
            event_type = event_data.get("event_type", "")
            event_id = event_data.get("event_id", "")
            phase = event_data.get("phase", "")
            result = event_data.get("result", "")
            description = event_data.get("description", "")
        else:
            raise TypeError(f"Beklenmeyen event veri tipi: {type(event_data)}")

        # EEC-001: Fake Progress kontrolü
        if self._is_fake_progress(event_type):
            logger.warning(
                f"🚫 [LAC] FAKE PROGRESS REDDEDİLDİ: {event_type} — "
                f"EEC-001: Fake Progress üretilemez"
            )
            raise ValueError(f"Fake Progress yasak: {event_type}")

        self._sequence += 1
        ts = datetime.now(timezone.utc).isoformat()
        lac_event = LACEvent(
            event_id=event_id or f"LAC-{self._sequence}",
            event_type=event_type,
            pid=pid,
            description=description or event_type,
            phase=phase,
            status="COMPLETED",
            result=result,
            timestamp=ts,
            sequence=self._sequence,
        )

        # PID bazlı Event listesine ekle
        if pid not in self._events:
            self._events[pid] = []
        self._events[pid].append(lac_event)

        # Maksimum Event limitini aşma
        if len(self._events[pid]) > self.MAX_EVENTS_PER_PID:
            self._events[pid] = self._events[pid][-self.MAX_EVENTS_PER_PID:]

        logger.info(
            f"📡 [LAC] Event kaydedildi: #{self._sequence} {event_type} "
            f"PID={pid} — {description[:60]}"
        )

        return lac_event

    # ═══════════════════════════════════════════════════════════════════════
    # Fake Progress Engelleme (EEC-001)
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _is_fake_progress(event_type: str) -> bool:
        """EEC-001: Fake Progress Event'lerini tespit eder.

        Aşağıdaki Event tipleri Fake Progress kabul edilir ve REDDEDİLİR:
        - Tahmini ilerleme yüzdesi içerenler
        - Gerçek bir işlemle ilişkili olmayan durum güncellemeleri
        - "Generating...", "Almost done..." gibi içeriksiz Event'ler
        """
        fake_patterns = [
            "PROGRESS_", "PROGRESS_UPDATE", "FAKE_",
            "ESTIMATED_", "ALMOST_DONE", "GENERATING_",
        ]
        return any(p in event_type.upper() for p in fake_patterns)

    # ═══════════════════════════════════════════════════════════════════════
    # Event Akışı
    # ═══════════════════════════════════════════════════════════════════════

    def get_stream(self, pid: str) -> list[dict]:
        """PID için kronolojik Event akışını döndürür.

        Returns:
            Event dict'lerinin listesi (en eski → en yeni).
        """
        events = self._events.get(pid, [])
        return [e.to_dict() for e in sorted(events, key=lambda e: e.sequence)]

    def get_latest(self, pid: str) -> Optional[LACEvent]:
        """PID için en son Event'i döndürür."""
        events = self._events.get(pid, [])
        if not events:
            return None
        return max(events, key=lambda e: e.sequence)

    # ═══════════════════════════════════════════════════════════════════════
    # Durum Özeti
    # ═══════════════════════════════════════════════════════════════════════

    def get_status(self, pid: str) -> LACStatus:
        """PID için anlık LAC durum özetini döndürür."""
        events = self._events.get(pid, [])
        if not events:
            return LACStatus(pid=pid)

        completed = sum(1 for e in events if e.status == "COMPLETED")
        failed = sum(1 for e in events if e.status == "FAILED")
        latest = max(events, key=lambda e: e.sequence)

        return LACStatus(
            pid=pid,
            is_active=latest.status not in ("COMPLETED", "FAILED"),
            total_events=len(events),
            completed_events=completed,
            failed_events=failed,
            current_phase=latest.phase,
            last_event_type=latest.event_type,
            last_update=latest.timestamp,
            has_escalation=any(
                "ESCALAT" in e.event_type.upper() for e in events
            ),
        )

    def get_all_active_pids(self) -> list[str]:
        """Tüm aktif PID'leri döndürür."""
        active = []
        for pid in self._events:
            status = self.get_status(pid)
            if status.is_active:
                active.append(pid)
        return active

    # ═══════════════════════════════════════════════════════════════════════
    # Temizlik
    # ═══════════════════════════════════════════════════════════════════════

    def clear_pid(self, pid: str) -> None:
        """PID'ye ait tüm Event'leri temizler."""
        self._events.pop(pid, None)
        logger.info(f"🧹 [LAC] PID={pid} Event'leri temizlendi")

    def reset(self) -> None:
        """Tüm LAC verilerini sıfırlar (test amaçlı)."""
        self._events.clear()
        self._sequence = 0
        logger.info("🔄 [LAC] Sıfırlandı")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

live_activity_center = LiveActivityCenter()
"""Global Live Activity Center singleton'ı."""
