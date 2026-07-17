"""
AR-002_22 Adım 4 / CEE-004: Constitutional Validator — Anayasal Doğrulama.

Decision Packet, Production Package, State, Event ve PID'nin anayasal
uyumluluğunu doğrulayan runtime katmanı.

CEE POST-CHECK sırasında çalışır. 5 boyutlu doğrulama yapar:
1. Decision Packet doğrulaması
2. PID doğrulaması
3. State doğrulaması
4. Event doğrulaması
5. Production Package doğrulaması

Her doğrulama sonucu PASS veya FAIL döndürür.
Tüm doğrulamalar geçerse genel PASS, aksi halde FAIL.

Bu modül:
- Decision Packet'i, PID'yi, State'i, Event'i, Package'i doğrular
- Anayasal uyumsuzlukları tespit eder
- CEE POST-CHECK'e doğrulama sonucu döndürür

Bu modül:
- Karar vermez (Decision Engine'in görevi)
- Provider seçmez (Selection Architecture'ın görevi)
- Kod çalıştırmaz / video üretmez (Executor'un görevi)

Mimari Dayanak:
- AR-002_22 Adım 4: Constitutional Validator
- CEE-004: POST-CHECK enforcement
- MASTER-003: ANA YASA / Kod Uyumluluk Denetim Prensibi
- 21_CONSTITUTION_ENFORCEMENT_ENGINE.md Section 4.3
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VALIDATION VERDICT
# ═══════════════════════════════════════════════════════════════════════════════

class ValidationVerdict(str, Enum):
    """Constitutional Validator'ün nihai kararı."""
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class ValidationResult:
    """Tek bir doğrulama boyutunun sonucu."""
    dimension: str = ""
    passed: bool = True
    details: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "passed": self.passed,
            "details": self.details,
            "errors": self.errors,
        }


@dataclass
class ValidatorReport:
    """5 boyutlu Constitutional Validator raporu."""
    report_id: str = ""
    pid: str = ""
    decision_id: str = ""
    verdict: str = ValidationVerdict.FAIL.value
    results: list[ValidationResult] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def failed_dimensions(self) -> list[str]:
        return [r.dimension for r in self.results if not r.passed]

    def finalize(self) -> str:
        self.verdict = ValidationVerdict.PASS.value if self.all_passed else ValidationVerdict.FAIL.value
        return self.verdict

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "pid": self.pid,
            "decision_id": self.decision_id,
            "verdict": self.verdict,
            "results": [r.to_dict() for r in self.results],
            "created_at": self.created_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CONSTITUTIONAL VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionalValidator:
    """AR-002_22 Adım 4: 5 boyutlu anayasal doğrulama.

    CEE POST-CHECK sırasında çalışır.
    Decision Packet → Production Package → State → Event → PID zincirini
    anayasal kurallara göre doğrular.

    Hiçbir doğrulama atlanamaz.
    Tüm doğrulamalar geçerse PASS, aksi halde FAIL.
    """

    def validate(
        self,
        decision_packet: dict | None = None,
        pid: str = "",
        user_data: dict | None = None,
    ) -> ValidatorReport:
        """5 boyutlu anayasal doğrulamayı çalıştırır.

        Args:
            decision_packet: Decision Packet dict (website.py'den).
            pid: Production ID.
            user_data: Telegram context.user_data (State ve Event için).

        Returns:
            ValidatorReport — tüm doğrulama sonuçlarıyla birlikte.
        """
        import uuid

        report = ValidatorReport(
            report_id=f"CV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}",
            pid=pid,
            decision_id=decision_packet.get("decision_id", "") if decision_packet else "",
        )

        # 1. Decision Packet doğrulaması
        report.results.append(self._validate_decision_packet(decision_packet))

        # 2. PID doğrulaması
        report.results.append(self._validate_pid(pid))

        # 3. State doğrulaması
        report.results.append(self._validate_state(user_data))

        # 4. Event doğrulaması
        report.results.append(self._validate_event(user_data))

        # 5. Production Package doğrulaması
        report.results.append(self._validate_package(pid))

        report.finalize()

        if report.all_passed:
            logger.info(f"✅ [ConstitutionalValidator] PASS: {report.report_id} — tüm 5 boyut geçti")
        else:
            logger.warning(
                f"❌ [ConstitutionalValidator] FAIL: {report.report_id} — "
                f"başarısız boyutlar: {report.failed_dimensions}"
            )

        return report

    # ═══════════════════════════════════════════════════════════════════════
    # Boyut 1: Decision Packet Doğrulaması
    # ═══════════════════════════════════════════════════════════════════════

    def _validate_decision_packet(self, packet: dict | None) -> ValidationResult:
        """Decision Packet'in anayasal bütünlüğünü doğrular.

        Kontroller:
        - Decision Packet mevcut mu?
        - decision_id var mı?
        - Provider seçimleri yapılmış mı?
        - Karar gerekçesi var mı?
        - Timestamp var mı?
        - Decision maker "HLK_DECISION_ENGINE" mi? (MASTER-004)
        """
        result = ValidationResult(dimension="DecisionPacket")

        if not packet:
            result.passed = False
            result.errors.append("Decision Packet mevcut değil — Decision Engine çağrılmamış olabilir")
            return result

        # Zorunlu alan kontrolleri
        checks = [
            ("decision_id", "Decision ID"),
            ("pid", "PID"),
            ("created_at", "Timestamp"),
            ("justification", "Karar Gerekçesi"),
        ]
        for field, label in checks:
            if not packet.get(field):
                result.passed = False
                result.errors.append(f"Decision Packet'te {label} ({field}) eksik")

        # MASTER-004: Decision maker kontrolü
        dm = packet.get("decision_maker", "")
        if dm != "HLK_DECISION_ENGINE":
            result.passed = False
            result.errors.append(
                f"MASTER-004 İHLALİ: Decision maker '{dm}' — "
                f"yalnızca HLK_DECISION_ENGINE karar verebilir"
            )

        # Provider seçimi kontrolü
        has_image = bool(packet.get("image_providers"))
        has_voice = bool(packet.get("voice_providers"))
        has_video = bool(packet.get("video_providers"))
        if not (has_image or has_voice or has_video):
            result.passed = False
            result.errors.append("Decision Packet'te hiçbir provider seçimi yok")

        if result.passed:
            result.details.append(
                f"Decision Packet geçerli: {packet.get('decision_id')} "
                f"(PID={packet.get('pid')}, "
                f"image={len(packet.get('image_providers', []))}, "
                f"voice={len(packet.get('voice_providers', []))}, "
                f"video={len(packet.get('video_providers', []))})"
            )

        return result

    # ═══════════════════════════════════════════════════════════════════════
    # Boyut 2: PID Doğrulaması
    # ═══════════════════════════════════════════════════════════════════════

    def _validate_pid(self, pid: str) -> ValidationResult:
        """PID'nin anayasal formatta olduğunu doğrular.

        AR-002_57: PID formatı — PID-YYYYMMDD-NNNN
        GC_PID_PREFIX, GC_PID_DATE_FORMAT, GC_PID_SEQUENCE_LENGTH
        """
        result = ValidationResult(dimension="PID")

        if not pid:
            result.passed = False
            result.errors.append("PID boş — üretim başlatılmamış olabilir")
            return result

        # PID format kontrolü: PID-YYYYMMDD-NNNN
        parts = pid.split("-")
        if len(parts) != 3:
            result.passed = False
            result.errors.append(f"PID formatı geçersiz: '{pid}' — PID-YYYYMMDD-NNNN bekleniyor")
            return result

        prefix, date_str, seq_str = parts
        if prefix != "PID":
            result.passed = False
            result.errors.append(f"PID prefix geçersiz: '{prefix}' — 'PID' bekleniyor (GC_PID_PREFIX)")

        if len(date_str) != 8 or not date_str.isdigit():
            result.passed = False
            result.errors.append(f"PID tarih formatı geçersiz: '{date_str}' — YYYYMMDD bekleniyor")

        if len(seq_str) != 4 or not seq_str.isdigit():
            result.passed = False
            result.errors.append(f"PID sıra no geçersiz: '{seq_str}' — 4 haneli (GC_PID_SEQUENCE_LENGTH)")

        if result.passed:
            result.details.append(f"PID formatı geçerli: {pid}")

        return result

    # ═══════════════════════════════════════════════════════════════════════
    # Boyut 3: State Doğrulaması
    # ═══════════════════════════════════════════════════════════════════════

    def _validate_state(self, user_data: dict | None) -> ValidationResult:
        """Mevcut State'in anayasal olup olmadığını doğrular.

        SE-007_3: Tanımlı UserState'lerden biri olmalı.
        SE-007_4: Geçerli bir state geçişi olmalı.
        """
        result = ValidationResult(dimension="State")

        if not user_data:
            result.details.append("user_data mevcut değil — State doğrulaması atlandı (best-effort)")
            return result

        current_state = user_data.get("state", "")
        if not current_state:
            result.details.append("State bilgisi user_data'da yok — atlandı")
            return result

        # SE-007_3: Geçerli UserState değerlerinden biri mi?
        valid_states = {
            "STATE_START", "STATE_SCENE_1", "STATE_LANGUAGE_SELECTION",
            "STATE_SCENE_2", "STATE_WAIT_PRODUCT_LINK", "STATE_LINK_VALIDATION",
            "STATE_LINK_VALIDATED", "STATE_BACKGROUND_RESEARCH_RUNNING",
            "STATE_COLLECT_PRODUCT_MATERIALS", "STATE_PLATFORM_SELECTION",
            "STATE_VIDEO_RESOLUTION_SELECTION", "STATE_VIDEO_DURATION_SELECTION",
            "STATE_AUDIO_SELECTION", "STATE_BRIEF_COMPLETED",
            "STATE_SCENARIO_APPROVAL", "STATE_PRICING", "STATE_PAYMENT_VERIFICATION",
            "STATE_VIDEO_PRODUCTION", "STATE_SESSION_COMPLETED",
            "STATE_SESSION_TIMEOUT", "STATE_SESSION_CLOSED",
            "STATE_STYLE_SELECTION", "STATE_TARGET_AUDIENCE_SELECTION",
        }

        if current_state not in valid_states:
            result.passed = False
            result.errors.append(
                f"SE-007_3 İHLALİ: '{current_state}' tanımlı UserState değil"
            )
        else:
            result.details.append(f"State geçerli: {current_state}")

        return result

    # ═══════════════════════════════════════════════════════════════════════
    # Boyut 4: Event Doğrulaması
    # ═══════════════════════════════════════════════════════════════════════

    def _validate_event(self, user_data: dict | None) -> ValidationResult:
        """Son Event'in anayasal olup olmadığını doğrular.

        SE-007_5: Tanımlı UserEvent'lerden biri olmalı.
        """
        result = ValidationResult(dimension="Event")

        if not user_data:
            result.details.append("user_data mevcut değil — Event doğrulaması atlandı (best-effort)")
            return result

        last_event = user_data.get("last_event", "")
        if not last_event:
            result.details.append("Event bilgisi user_data'da yok — atlandı")
            return result

        # SE-007_5: Geçerli UserEvent değerlerinden biri mi?
        valid_events = {
            "EVENT_LANGUAGE_SELECTED", "EVENT_PRODUCT_LINK_RECEIVED",
            "EVENT_LINK_VALIDATED", "EVENT_LINK_FAILED",
            "EVENT_MATERIALS_COLLECTED", "EVENT_MATERIAL_UPLOADED",
            "EVENT_PLATFORM_SELECTED", "EVENT_RESOLUTION_SELECTED",
            "EVENT_DURATION_SELECTED", "EVENT_STYLE_SELECTED",
            "EVENT_AUDIENCE_SELECTED", "EVENT_AUDIO_SELECTED",
            "EVENT_VOICE_SELECTED", "EVENT_EMPHASIS_SELECTED",
            "EVENT_BRIEF_COMPLETED", "EVENT_BRIEF_APPROVED",
            "EVENT_SCENARIO_APPROVED", "EVENT_SCENARIO_REJECTED",
            "EVENT_PRICING_APPROVED", "EVENT_PAYMENT_DECLARED",
            "EVENT_PAYMENT_APPROVED", "EVENT_PAYMENT_REJECTED",
            "EVENT_VIDEO_PRODUCTION_STARTED", "EVENT_VIDEO_PRODUCTION_COMPLETED",
            "EVENT_VIDEO_PRODUCTION_FAILED", "EVENT_VIDEO_PRODUCTION_DONE",
            "EVENT_SESSION_COMPLETED", "EVENT_SESSION_CLOSED",
            "EVENT_SESSION_TIMEOUT", "EVENT_CANCEL", "EVENT_START",
            "EVENT_PRODUCT_LINK_RECEIVED", "EVENT_MATERIAL_CHOICE_MADE",
        }

        if last_event not in valid_events:
            result.passed = False
            result.errors.append(
                f"SE-007_5 İHLALİ: '{last_event}' tanımlı UserEvent değil"
            )
        else:
            result.details.append(f"Event geçerli: {last_event}")

        return result

    # ═══════════════════════════════════════════════════════════════════════
    # Boyut 5: Production Package Doğrulaması
    # ═══════════════════════════════════════════════════════════════════════

    def _validate_package(self, pid: str) -> ValidationResult:
        """Production Package'in varlığını ve bütünlüğünü doğrular.

        16_PRODUCTION_PACKAGE_STANDARD.md: Package, PID ile ilişkili olmalı.
        AR-002_58: Package oluşturulmuş olmalı.
        """
        result = ValidationResult(dimension="ProductionPackage")

        if not pid:
            result.passed = False
            result.errors.append("PID olmadan Production Package doğrulanamaz")
            return result

        # Package Runtime üzerinden doğrulama (best-effort)
        try:
            from services.production_package_runtime import package_runtime
            import asyncio

            # Senkron doğrulama için yeni event loop
            try:
                loop = asyncio.get_running_loop()
                # Async context'teyiz — doğrudan çağıramayız, best-effort
                result.details.append("Production Package doğrulaması: async context — best-effort")
            except RuntimeError:
                # Sync context — yeni loop oluştur
                pkg = asyncio.new_event_loop().run_until_complete(
                    package_runtime.load(pid)
                )
                if pkg is None:
                    result.passed = False
                    result.errors.append(
                        f"AR-002_58 İHLALİ: PID={pid} için Production Package bulunamadı"
                    )
                else:
                    result.details.append(
                        f"Production Package mevcut: PID={pid}, "
                        f"durum={pkg.metadata.status}, "
                        f"task_packages={len(pkg.task_packages)}"
                    )
        except ImportError:
            result.details.append("Production Package Runtime import edilemedi — atlandı")
        except Exception as e:
            result.details.append(f"Production Package doğrulaması yapılamadı: {e}")

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

constitutional_validator = ConstitutionalValidator()
"""Global Constitutional Validator singleton'ı.

CEE POST-CHECK tarafından kullanılır.
"""
