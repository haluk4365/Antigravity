"""
14_OLAY_KAYIT_MERKEZI.md — Olay Kayıt Merkezi (Event Registry)

HLK içerisinde gerçekleşen tüm olayların (Event) kaydedildiği,
sorgulandığı ve LAC'a beslendiği merkezi kayıt katmanı.

EEC tarafından üretilen Event'leri alır, indeksler ve LAC tarafından
okunabilir hale getirir.

Mimari: OLAY_KAYIT_MERKEZI, AR-002_61, FEAT-020, WF-016
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EventRecord:
    """Olay Kayıt Merkezi'ne kaydedilen standart Event kaydı.

    EEC ExecutionEvent ile uyumlu alan yapısı — ek alanlarla genişletilmiştir.
    """
    event_id: str
    event_name: str
    event_constant: str             # EECEventType değeri
    event_description: str
    source_state: str = ""
    target_state: str = ""
    producer: str = ""
    pid: str = ""                   # Production ID
    timestamp: str = ""
    duration_ms: float = 0.0
    phase: str = ""
    result: str = ""
    related_file: str = ""
    category: str = ""
    lac_visible: bool = True

    # İç takip
    _registered_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "event_constant": self.event_constant,
            "event_description": self.event_description,
            "pid": self.pid,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "phase": self.phase,
            "result": self.result,
            "related_file": self.related_file,
            "category": self.category,
            "source_state": self.source_state,
            "target_state": self.target_state,
        }


class EventRegistry:
    """HLK Olay Kayıt Merkezi.

    Tüm sistem Event'lerinin kaydedildiği merkezi registry.
    EEC emit_event() ile Event üretir → EventRegistry.register() ile kaydeder.
    LAC get_events() ile okur.
    """

    def __init__(self):
        self._records: list[EventRecord] = []
        self._by_pid: dict[str, list[EventRecord]] = {}
        self._by_category: dict[str, list[EventRecord]] = {}
        self._session_start: float = time.time()

    def register(self, record: EventRecord) -> EventRecord:
        """Bir Event'i kayıt merkezine kaydeder.

        Args:
            record: Kaydedilecek Event kaydı.

        Returns:
            Kaydedilen record (zincirleme çağrı için).
        """
        self._records.append(record)

        # PID indeksi
        if record.pid:
            if record.pid not in self._by_pid:
                self._by_pid[record.pid] = []
            self._by_pid[record.pid].append(record)

        # Kategori indeksi
        cat = record.category or "GENEL"
        if cat not in self._by_category:
            self._by_category[cat] = []
        self._by_category[cat].append(record)

        logger.debug(
            f"📝 [EventRegistry] Kaydedildi: {record.event_id} | "
            f"PID={record.pid} | {record.event_name[:40]}"
        )
        return record

    def register_from_eec(self, execution_event) -> EventRecord:
        """EEC ExecutionEvent'ini EventRecord'a dönüştürüp kaydeder.

        Args:
            execution_event: EEC tarafından üretilen ExecutionEvent.

        Returns:
            Oluşturulan EventRecord.
        """
        from services.execution_event_collector import EECEventType

        record = EventRecord(
            event_id=execution_event.event_id,
            event_name=execution_event.event_name,
            event_constant=execution_event.event_constant.value,
            event_description=execution_event.event_description,
            source_state=execution_event.source_state,
            target_state=execution_event.target_state,
            producer=execution_event.producer,
            pid=execution_event.pid,
            timestamp=execution_event.timestamp or f"{time.time():.0f}",
            duration_ms=execution_event.event_duration_ms,
            phase=execution_event.execution_phase.value,
            result=execution_event.result,
            related_file=execution_event.related_file,
            category=EECEventType.category_of(execution_event.event_constant).value,
            lac_visible=execution_event.lac_visible,
        )
        return self.register(record)

    def get_by_pid(self, pid: str, limit: int = 100) -> list[EventRecord]:
        """Belirtilen PID için Event'leri kronolojik sırayla döndürür."""
        records = self._by_pid.get(pid, [])
        return records[-limit:] if limit > 0 else records

    def get_by_category(self, category: str, limit: int = 50) -> list[EventRecord]:
        """Belirtilen kategori için Event'leri döndürür."""
        records = self._by_category.get(category, [])
        return records[-limit:] if limit > 0 else records

    def get_recent(self, limit: int = 50) -> list[EventRecord]:
        """En son Event'leri döndürür."""
        return self._records[-limit:] if limit > 0 else self._records

    def get_lac_feed(self, pid: str | None = None, limit: int = 20) -> list[dict]:
        """LAC'ta gösterilecek formatta Event akışı döndürür.

        Yalnızca lac_visible=True olan Event'leri içerir.
        """
        if pid:
            records = self.get_by_pid(pid, limit=0)
        else:
            records = self._records

        visible = [r for r in records if r.lac_visible]
        return [r.to_dict() for r in visible[-limit:]]

    def get_stats(self) -> dict:
        """Kayıt merkezi istatistikleri."""
        pids = list(self._by_pid.keys())
        categories = list(self._by_category.keys())
        return {
            "total_events": len(self._records),
            "active_pids": len(pids),
            "pid_list": pids[-10:],
            "categories": categories,
            "events_by_category": {c: len(self._by_category[c]) for c in categories},
            "session_duration_s": time.time() - self._session_start,
        }

    def get_by_result(self, result_filter: str) -> list[EventRecord]:
        """Sonuç metnine göre Event'leri filtrele (örn: 'PASS', 'FAIL')."""
        return [r for r in self._records if result_filter.upper() in r.result.upper()]

    def clear(self):
        """Tüm kayıtları temizler."""
        count = len(self._records)
        self._records.clear()
        self._by_pid.clear()
        self._by_category.clear()
        self._session_start = time.time()
        logger.info(f"🗑️ [EventRegistry] Temizlendi: {count} event silindi")

    def reset(self):
        """Registry'yi sıfırlar (yeni oturum için)."""
        self.clear()


# Global singleton
event_registry = EventRegistry()
