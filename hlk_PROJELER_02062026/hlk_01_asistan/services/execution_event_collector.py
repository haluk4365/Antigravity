"""
22_EXECUTION_EVENT_COLLECTOR.md — Execution Event Collector (EEC)

Executor (Claude) işlemlerini gerçek zamanlı Event'lere dönüştüren,
Olay Kayıt Merkezi'ne kaydeden ve LAC tarafından anlık görüntülenebilmesini
sağlayan Event toplama katmanı.

EEC hiçbir zaman Fake Progress üretmez.
Yalnızca gerçek Executor işlemlerini Event'e dönüştürür.

Mimari: EEC-001 — EEC-005, AR-002_61, FEAT-020, WF-016
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. EVENT CATEGORIES — 6 kategori
# ═══════════════════════════════════════════════════════════════════════════════

class EventCategory(str, Enum):
    """EEC Event kategorileri."""
    TASK_MANAGEMENT = "TASK_MANAGEMENT"       # Görev Yönetimi
    CONSTITUTION_SCAN = "CONSTITUTION_SCAN"   # Anayasa Tarama
    FILE_OPERATION = "FILE_OPERATION"          # Dosya İşlem
    CODE_DEVELOPMENT = "CODE_DEVELOPMENT"      # Kod Geliştirme
    AUDIT = "AUDIT"                            # Denetim
    RESULT = "RESULT"                          # Sonuç


# ═══════════════════════════════════════════════════════════════════════════════
# 2. EXECUTION PHASE — 3 faz
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionPhase(str, Enum):
    """EEC yürütme fazları."""
    PRE_CHECK = "PHASE_PRE_CHECK"
    EXECUTE = "PHASE_EXECUTE"
    POST_CHECK = "PHASE_POST_CHECK"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EEC EVENT TYPES — 28 Event tipi (teknik sabitler)
# ═══════════════════════════════════════════════════════════════════════════════

class EECEventType(str, Enum):
    """EEC tarafından üretilen Event tipleri (OLAY-076 — OLAY-103)."""

    # Görev Yönetimi
    TASK_STARTED = "EVENT_TASK_STARTED"                # OLAY-076
    TASK_CREATED = "EVENT_TASK_CREATED"                # OLAY-077
    EXECUTOR_ASSIGNED = "EVENT_EXECUTOR_ASSIGNED"      # OLAY-078

    # Anayasa Tarama
    MASTER_SCAN_STARTED = "EVENT_MASTER_SCAN_STARTED"              # OLAY-079
    MASTER_SCAN_COMPLETED = "EVENT_MASTER_SCAN_COMPLETED"          # OLAY-080
    FLOW_SCAN_STARTED = "EVENT_FLOW_SCAN_STARTED"                  # OLAY-081
    FLOW_SCAN_COMPLETED = "EVENT_FLOW_SCAN_COMPLETED"              # OLAY-082
    STATE_SCAN_STARTED = "EVENT_STATE_SCAN_STARTED"                # OLAY-083
    STATE_SCAN_COMPLETED = "EVENT_STATE_SCAN_COMPLETED"            # OLAY-084
    ARCHITECTURE_SCAN_STARTED = "EVENT_ARCHITECTURE_SCAN_STARTED"  # OLAY-085
    ARCHITECTURE_SCAN_COMPLETED = "EVENT_ARCHITECTURE_SCAN_COMPLETED"  # OLAY-086
    OPERATIONAL_SCAN_STARTED = "EVENT_OPERATIONAL_SCAN_STARTED"    # OLAY-087
    OPERATIONAL_SCAN_COMPLETED = "EVENT_OPERATIONAL_SCAN_COMPLETED"  # OLAY-088

    # Dosya İşlem
    FILE_OPENED = "EVENT_FILE_OPENED"      # OLAY-089
    FILE_READ = "EVENT_FILE_READ"          # OLAY-090
    FILE_UPDATED = "EVENT_FILE_UPDATED"    # OLAY-091
    FILE_CREATED = "EVENT_FILE_CREATED"    # OLAY-092

    # Kod Geliştirme
    CODE_ANALYSIS_STARTED = "EVENT_CODE_ANALYSIS_STARTED"              # OLAY-093
    CODE_ANALYSIS_COMPLETED = "EVENT_CODE_ANALYSIS_COMPLETED"          # OLAY-094
    CODE_IMPLEMENTATION_STARTED = "EVENT_CODE_IMPLEMENTATION_STARTED"  # OLAY-095
    CODE_IMPLEMENTATION_COMPLETED = "EVENT_CODE_IMPLEMENTATION_COMPLETED"  # OLAY-096
    CODE_COMPLETED = "EVENT_CODE_COMPLETED"                            # OLAY-097

    # Denetim
    CONSTITUTION_SCAN_STARTED = "EVENT_CONSTITUTION_SCAN_STARTED"      # OLAY-098
    CONSTITUTION_SCAN_COMPLETED = "EVENT_CONSTITUTION_SCAN_COMPLETED"  # OLAY-099
    RUNTIME_TEST_STARTED = "EVENT_RUNTIME_TEST_STARTED"                # OLAY-100
    RUNTIME_TEST_COMPLETED = "EVENT_RUNTIME_TEST_COMPLETED"            # OLAY-101
    SYNTAX_CHECK_STARTED = "EVENT_SYNTAX_CHECK_STARTED"                # OLAY-102
    SYNTAX_CHECK_COMPLETED = "EVENT_SYNTAX_CHECK_COMPLETED"            # OLAY-103

    @classmethod
    def category_of(cls, event_type: "EECEventType") -> EventCategory:
        """Event tipinin hangi kategoriye ait olduğunu döndürür."""
        mapping = {
            cls.TASK_STARTED: EventCategory.TASK_MANAGEMENT,
            cls.TASK_CREATED: EventCategory.TASK_MANAGEMENT,
            cls.EXECUTOR_ASSIGNED: EventCategory.TASK_MANAGEMENT,
            cls.MASTER_SCAN_STARTED: EventCategory.CONSTITUTION_SCAN,
            cls.MASTER_SCAN_COMPLETED: EventCategory.CONSTITUTION_SCAN,
            cls.FLOW_SCAN_STARTED: EventCategory.CONSTITUTION_SCAN,
            cls.FLOW_SCAN_COMPLETED: EventCategory.CONSTITUTION_SCAN,
            cls.STATE_SCAN_STARTED: EventCategory.CONSTITUTION_SCAN,
            cls.STATE_SCAN_COMPLETED: EventCategory.CONSTITUTION_SCAN,
            cls.ARCHITECTURE_SCAN_STARTED: EventCategory.CONSTITUTION_SCAN,
            cls.ARCHITECTURE_SCAN_COMPLETED: EventCategory.CONSTITUTION_SCAN,
            cls.OPERATIONAL_SCAN_STARTED: EventCategory.CONSTITUTION_SCAN,
            cls.OPERATIONAL_SCAN_COMPLETED: EventCategory.CONSTITUTION_SCAN,
            cls.FILE_OPENED: EventCategory.FILE_OPERATION,
            cls.FILE_READ: EventCategory.FILE_OPERATION,
            cls.FILE_UPDATED: EventCategory.FILE_OPERATION,
            cls.FILE_CREATED: EventCategory.FILE_OPERATION,
            cls.CODE_ANALYSIS_STARTED: EventCategory.CODE_DEVELOPMENT,
            cls.CODE_ANALYSIS_COMPLETED: EventCategory.CODE_DEVELOPMENT,
            cls.CODE_IMPLEMENTATION_STARTED: EventCategory.CODE_DEVELOPMENT,
            cls.CODE_IMPLEMENTATION_COMPLETED: EventCategory.CODE_DEVELOPMENT,
            cls.CODE_COMPLETED: EventCategory.CODE_DEVELOPMENT,
            cls.CONSTITUTION_SCAN_STARTED: EventCategory.AUDIT,
            cls.CONSTITUTION_SCAN_COMPLETED: EventCategory.AUDIT,
            cls.RUNTIME_TEST_STARTED: EventCategory.AUDIT,
            cls.RUNTIME_TEST_COMPLETED: EventCategory.AUDIT,
            cls.SYNTAX_CHECK_STARTED: EventCategory.AUDIT,
            cls.SYNTAX_CHECK_COMPLETED: EventCategory.AUDIT,
        }
        return mapping.get(event_type, EventCategory.RESULT)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXECUTION EVENT — EEC Event veri yapısı (21 + 8 = 29 alan)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExecutionEvent:
    """EEC tarafından üretilen standart Event.

    Olay Kayıt Merkezi'nin 21 alanlı standardını temel alır,
    8 EEC ek alanı ile genişletir.
    """
    # ── Olay Kayıt Merkezi 21 alanı ──
    event_id: str                               # OLAY-XXX
    event_name: str                             # Olay Adı
    event_constant: EECEventType                # Teknik Sabit
    event_description: str                      # Açıklama
    source_state: str = ""                      # Kaynak Durum
    target_state: str = ""                      # Hedef Durum
    workflow_id: str = ""                       # İlgili Workflow
    feature_id: str = ""                        # İlgili Feature
    module_id: str = ""                         # İlgili Modül
    producer: str = "Execution Event Collector (EEC)"
    consumers: str = "LAC, Operasyon Hafizasi, Log Sistemi"
    trigger: str = ""                           # Tetikleyici
    condition: str = ""                         # Oluşturulma Koşulu
    priority: str = "PRIORITY_LOW"              # Öncelik
    retry_policy: str = "Yok"                   # Tekrar Deneme Politikası
    notifications: str = ""                     # Bildirim Hedefleri
    outputs: str = ""                           # Olay Çıktıları
    next_event: str = ""                        # Sonraki Olay
    record_policy: str = "Loglanir, LAC'ta gorunur"
    result: str = ""                            # Sonuç
    timestamp: str = ""                         # Zaman Damgası

    # ── EEC 8 ek alanı ──
    pid: str = ""                               # Production ID (ZORUNLU)
    event_duration_ms: float = 0.0              # Event süresi (ms)
    related_file: str = ""                      # İlgili Dosya
    related_workflow: str = "WF-016"            # İlgili Workflow
    related_state: str = ""                     # İlgili State
    executor_id: str = "Claude"                 # Executor Kimliği
    execution_phase: ExecutionPhase = ExecutionPhase.EXECUTE
    lac_visible: bool = True                    # LAC'ta Görünür

    # ── İç takip ──
    _start_time: float = field(default_factory=time.time, repr=False)

    def complete(self, result: str = "") -> "ExecutionEvent":
        """Event'i tamamla: süreyi hesapla, sonucu kaydet."""
        self.event_duration_ms = (time.time() - self._start_time) * 1000
        self.result = result
        return self

    def to_lac_entry(self) -> dict:
        """LAC'ta gösterilecek formata dönüştür."""
        return {
            "pid": self.pid,
            "event_id": self.event_id,
            "event_name": self.event_name,
            "phase": self.execution_phase.value,
            "timestamp": self.timestamp or f"{time.time():.0f}",
            "duration_ms": round(self.event_duration_ms, 1),
            "result": self.result,
            "related_file": self.related_file,
            "category": EECEventType.category_of(self.event_constant).value,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. EXECUTION EVENT COLLECTOR — ana sınıf
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionEventCollector:
    """EEC: Execution Event Collector.

    Executor işlemlerini gerçek zamanlı Event'lere dönüştürür,
    Olay Kayıt Merkezi'ne kaydeder ve LAC tarafından okunabilmesini sağlar.

    3 aşamalı çalışır: LISTEN → TRANSFORM → REGISTER
    EEC-001 — EEC-005 kurallarına tabidir.
    """

    def __init__(self):
        self._events: list[ExecutionEvent] = []
        self._events_by_pid: dict[str, list[ExecutionEvent]] = {}
        self._active_pid: str | None = None
        self._session_start: float | None = None

    # ── LISTEN: Executor'u Dinle ───────────────────────────────────────────

    def listen(self, pid: str) -> None:
        """Belirtilen PID için Executor'u dinlemeye başla.

        EEC-002: Her Event PID ile ilişkilendirilir.
        """
        self._active_pid = pid
        self._session_start = time.time()
        if pid not in self._events_by_pid:
            self._events_by_pid[pid] = []
        logger.info(f"👂 [EEC LISTEN] PID={pid} — Executor dinleniyor")

    # ── TRANSFORM + REGISTER: Event Üret ve Kaydet ─────────────────────────

    def emit_event(
        self,
        event_type: EECEventType,
        description: str = "",
        related_file: str = "",
        phase: ExecutionPhase = ExecutionPhase.EXECUTE,
        result: str = "",
    ) -> ExecutionEvent:
        """Bir Executor işlemini Event'e dönüştür ve kaydet.

        Args:
            event_type: Event tipi (EECEventType enum)
            description: İşlem açıklaması
            related_file: İlgili dosya (isteğe bağlı)
            phase: Yürütme fazı
            result: İşlem sonucu

        Returns:
            ExecutionEvent — oluşturulan ve kaydedilen Event
        """
        import uuid as _uuid
        from datetime import datetime as _dt

        pid = self._active_pid or "PID-UNKNOWN"
        now = _dt.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        event = ExecutionEvent(
            event_id=f"OLAY-{_uuid.uuid4().hex[:4].upper()}",
            event_name=event_type.value.replace("EVENT_", "").replace("_", " ").title(),
            event_constant=event_type,
            event_description=description or event_type.value,
            related_file=related_file,
            execution_phase=phase,
            pid=pid,
            timestamp=timestamp,
            workflow_id="WF-016",
            feature_id="FEAT-020",
        )

        if result:
            event.complete(result)
            logger.info(f"📤 [EEC EMIT] {event.event_constant.value} "
                        f"| PID={pid} | file={related_file} | "
                        f"phase={phase.value} | dur={event.event_duration_ms:.0f}ms")
        else:
            logger.info(f"📤 [EEC EMIT] {event.event_constant.value} "
                        f"| PID={pid} | phase={phase.value}")

        # REGISTER: Olay Kayıt Merkezi'ne kaydet
        self._events.append(event)
        if pid not in self._events_by_pid:
            self._events_by_pid[pid] = []
        self._events_by_pid[pid].append(event)

        return event

    # ── START/COMPLETE Pair — EEC-005 uyumlu ───────────────────────────────

    def emit_start_complete(
        self,
        start_type: EECEventType,
        complete_type: EECEventType,
        description: str = "",
        related_file: str = "",
        phase: ExecutionPhase = ExecutionPhase.EXECUTE,
    ) -> tuple[ExecutionEvent, ExecutionEvent]:
        """Bir START + COMPLETE event çifti üretir.

        EEC-005: COMPLETE event'i, işlem gerçekten tamamlandığında üretilir.
        Fake progress üretilmez.
        """
        start_event = self.emit_event(
            start_type, f"{description} başladı", related_file, phase
        )
        time.sleep(0.001)  # Mikro süre farkı — kronolojik sıra için

        complete_event = self.emit_event(
            complete_type, f"{description} tamamlandı", related_file, phase,
            result="Tamamlandı"
        )
        return start_event, complete_event

    # ── LAC Feed ───────────────────────────────────────────────────────────

    def get_events_by_pid(self, pid: str | None = None) -> list[ExecutionEvent]:
        """Belirtilen PID için tüm Event'leri kronolojik sırayla döndürür."""
        if pid is None:
            pid = self._active_pid
        return self._events_by_pid.get(pid or "", [])

    def get_lac_feed(self, pid: str | None = None) -> list[dict]:
        """LAC'ta gösterilecek formatta Event akışı döndürür.

        Yalnızca LACVisible=true olan Event'leri içerir.
        """
        events = self.get_events_by_pid(pid)
        return [e.to_lac_entry() for e in events if e.lac_visible]

    def get_all_events(self) -> list[ExecutionEvent]:
        """Tüm Event'leri döndürür."""
        return self._events

    def get_event_count(self, pid: str | None = None) -> int:
        """Event sayısını döndürür."""
        return len(self.get_events_by_pid(pid))

    def get_session_duration(self) -> float:
        """Oturum süresini saniye olarak döndürür."""
        if self._session_start is None:
            return 0.0
        return time.time() - self._session_start

    def reset(self) -> None:
        """EEC state'ini sıfırlar (yeni görev için)."""
        self._active_pid = None
        self._session_start = None
        logger.info("🔄 [EEC] Sıfırlandı — yeni göreve hazır")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

execution_event_collector = ExecutionEventCollector()
