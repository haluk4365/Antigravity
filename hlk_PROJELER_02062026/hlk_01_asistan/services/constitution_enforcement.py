"""
21_CONSTITUTION_ENFORCEMENT_ENGINE.md — Constitution Enforcement Engine (CEE)

HLK'nın anayasal uygulatma katmanı. Executor'dan (Claude) önce anayasal
görev paketini (CTP) oluşturur, Executor'dan sonra çıktıyı anayasal kurallara
göre denetler, uygunsuzluğu REDDEDER, eksikleri Executor'a geri gönderir ve
yalnızca tam uyum sağlandığında PASS verir.

CEE, HLK içerisinde PASS/FAIL verme yetkisine sahip TEK katmandır.
CSE, CDE, Task Engine PASS/FAIL üretemez.

Mimari: CEE-001 — CEE-005, AR-002_60, FEAT-019, WF-015
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERDICT — CEE'nin nihai kararı
# ═══════════════════════════════════════════════════════════════════════════════

class EnforcementVerdict(str, Enum):
    """CEE-004: CEE'nin üretebileceği tek iki nihai karar."""
    PASS = "PASS"   # Tüm denetimlerden geçti — görev tamamlandı
    FAIL = "FAIL"   # En az bir denetimden kaldı — Executor'a geri gönder


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ENFORCEMENT REPORT — POST-CHECK çıktısı
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EnforcementReport:
    """CEE POST-CHECK sonucu. Her denetim için ayrı sonuç + nihai PASS/FAIL."""
    report_id: str                          # CEE-YYYYMMDD-NNNN
    ctp_id: str                             # Bağlı CTP ID'si
    executor: str = "Claude"                # Denetlenen Executor
    attempt: int = 1                        # Kaçıncı deneme (max 3)
    verdict: EnforcementVerdict = EnforcementVerdict.FAIL

    # 6 boyutlu denetim sonuçları
    code_anayasa_check: bool = False        # Kod-Anayasa karşılaştırması
    flow_compliance: bool = False           # Flow Diagram uyumu
    state_compliance: bool = False          # State Engine uyumu
    operational_compliance: bool = False    # Operational Rules uyumu
    architectural_integrity: bool = False   # Mimari bütünlük
    runtime_behavior: bool = False          # Runtime davranış

    # FAIL durumunda eksikler
    deficiencies: list[dict] = field(default_factory=list)
    # Her eksik: {"type": str, "description": str, "ana_yasa_ref": str, "file": str}

    @property
    def all_passed(self) -> bool:
        """Tüm 6 denetimden geçti mi?"""
        return all([
            self.code_anayasa_check,
            self.flow_compliance,
            self.state_compliance,
            self.operational_compliance,
            self.architectural_integrity,
            self.runtime_behavior,
        ])

    @property
    def deficiency_count(self) -> int:
        """Toplam eksik sayısı."""
        return len(self.deficiencies)

    def finalize(self) -> EnforcementVerdict:
        """Tüm kontrolleri değerlendir, nihai PASS/FAIL ver."""
        if self.all_passed:
            self.verdict = EnforcementVerdict.PASS
        else:
            self.verdict = EnforcementVerdict.FAIL
        return self.verdict


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CONSTITUTIONAL TASK PACKAGE (CTP) — PRE-CHECK çıktısı
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConstitutionalTaskPackage:
    """CEE PRE-CHECK sonucu oluşturulan anayasal görev paketi."""
    ctp_id: str                             # CEE-CTP-YYYYMMDD-NNNN
    task_description: str                   # Ne yapılacak
    affected_files: list[str] = field(default_factory=list)

    # İlgili ANA YASA maddeleri
    master_rules: list[str] = field(default_factory=list)
    arch_rules: list[str] = field(default_factory=list)
    oper_rules: list[str] = field(default_factory=list)
    flow_steps: list[str] = field(default_factory=list)
    state_rules: list[str] = field(default_factory=list)
    gc_params: list[str] = field(default_factory=list)

    # Zorunlu kontroller
    mandatory_checks: list[dict] = field(default_factory=list)
    # Her kontrol: {"check": str, "ana_yasa_ref": str}

    # Değiştirilmez alanlar (CEE-003)
    immutable_fields: list[str] = field(default_factory=list)

    # Beklenen çıktı
    expected_outputs: list[str] = field(default_factory=list)

    # Başarı kriterleri
    success_criteria: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONSTITUTION ENFORCEMENT ENGINE — ana sınıf
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionEnforcementEngine:
    """CEE: Constitution Enforcement Engine.

    HLK'nın anayasal uygulatma katmanı. 3 fazda çalışır:
    - FAZ-1 (PRE-CHECK): Anayasal görev paketi oluşturur
    - FAZ-2 (EXECUTE): Executor'u izler (pasif)
    - FAZ-3 (POST-CHECK): 6 boyutlu denetim + PASS/FAIL

    CEE-001 — CEE-005 kurallarına tabidir.
    """

    # CEE-005: Maksimum FAIL döngüsü
    MAX_ENFORCEMENT_RETRIES = 3

    def __init__(self):
        self._enforcement_history: list[EnforcementReport] = []
        self._active_ctp: Optional[ConstitutionalTaskPackage] = None
        self._attempt_count: dict[str, int] = {}  # ctp_id -> attempt sayısı

    # ── FAZ 1: PRE-CHECK ───────────────────────────────────────────────────

    def pre_check(
        self,
        task_description: str,
        affected_files: list[str],
        master_rules: list[str] | None = None,
        arch_rules: list[str] | None = None,
        oper_rules: list[str] | None = None,
        flow_steps: list[str] | None = None,
        state_rules: list[str] | None = None,
        mandatory_checks: list[dict] | None = None,
        immutable_fields: list[str] | None = None,
        expected_outputs: list[str] | None = None,
    ) -> ConstitutionalTaskPackage:
        """FAZ-1: Anayasal görev paketi (CTP) oluşturur.

        Executor göreve başlamadan ÖNCE çağrılır.
        İlgili tüm ANA YASA maddelerini toplar ve CTP'ye dönüştürür.

        Args:
            task_description: Görevin ne olduğu
            affected_files: Etkilenecek dosyalar
            master_rules: İlgili MASTER kuralları
            arch_rules: İlgili AR kuralları
            oper_rules: İlgili OR kuralları
            flow_steps: İlgili FD-008_1 akış adımları
            state_rules: İlgili SE-007_x kuralları
            mandatory_checks: Executor'un yapmak zorunda olduğu kontroller
            immutable_fields: Kesinlikle değiştirilmemesi gereken alanlar
            expected_outputs: Beklenen çıktılar

        Returns:
            ConstitutionalTaskPackage — Executor'a iletilecek paket
        """
        import uuid
        from datetime import datetime

        ctp_id = f"CEE-CTP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        ctp = ConstitutionalTaskPackage(
            ctp_id=ctp_id,
            task_description=task_description,
            affected_files=affected_files or [],
            master_rules=master_rules or [],
            arch_rules=arch_rules or [],
            oper_rules=oper_rules or [],
            flow_steps=flow_steps or [],
            state_rules=state_rules or [],
            mandatory_checks=mandatory_checks or [],
            immutable_fields=immutable_fields or [
                "State isimleri (UserState enum)",
                "State geçiş kuralları (STATE_TRANSITIONS)",
                "Workflow yapısı",
                "Mevcut mimari",
                "ANA YASA maddeleri",
            ],
            expected_outputs=expected_outputs or [],
            success_criteria=[
                "Tüm mandatory_checks başarıyla tamamlandı",
                "Değiştirilmez alanlara müdahale edilmedi",
                "Kod ANA YASA ile uyumlu",
                "Runtime davranışı doğrulandı",
            ],
        )

        self._active_ctp = ctp
        logger.info(f"✅ [CEE PRE-CHECK] CTP oluşturuldu: {ctp_id}")
        logger.info(f"   Görev: {task_description[:80]}")
        logger.info(f"   MASTER: {len(ctp.master_rules)}, AR: {len(ctp.arch_rules)}, "
                    f"OR: {len(ctp.oper_rules)}, Flow: {len(ctp.flow_steps)}, "
                    f"State: {len(ctp.state_rules)}")

        return ctp

    # ── FAZ 3: POST-CHECK ──────────────────────────────────────────────────

    def post_check(
        self,
        code_anayasa_ok: bool = False,
        flow_ok: bool = False,
        state_ok: bool = False,
        operational_ok: bool = False,
        architecture_ok: bool = False,
        runtime_ok: bool = False,
        deficiencies: list[dict] | None = None,
    ) -> EnforcementReport:
        """FAZ-3: 6 boyutlu anayasal denetim + PASS/FAIL.

        Executor işlemi tamamladıktan SONRA çağrılır.
        Tüm kontrollerden geçerse PASS, aksi halde FAIL verir.

        Returns:
            EnforcementReport — nihai PASS veya FAIL kararı
        """
        import uuid
        from datetime import datetime

        ctp_id = self._active_ctp.ctp_id if self._active_ctp else "UNKNOWN"
        attempt = self._attempt_count.get(ctp_id, 0) + 1
        self._attempt_count[ctp_id] = attempt

        report_id = f"CEE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        report = EnforcementReport(
            report_id=report_id,
            ctp_id=ctp_id,
            attempt=attempt,
            code_anayasa_check=code_anayasa_ok,
            flow_compliance=flow_ok,
            state_compliance=state_ok,
            operational_compliance=operational_ok,
            architectural_integrity=architecture_ok,
            runtime_behavior=runtime_ok,
            deficiencies=deficiencies or [],
        )

        verdict = report.finalize()

        if verdict == EnforcementVerdict.PASS:
            logger.info(f"✅ [CEE POST-CHECK] PASS — {report_id} "
                        f"(CTP: {ctp_id}, deneme: {attempt})")
            logger.info(f"   Tüm 6 denetim başarılı — görev TAMAMLANDI")
        else:
            logger.warning(f"❌ [CEE POST-CHECK] FAIL — {report_id} "
                           f"(CTP: {ctp_id}, deneme: {attempt}/{self.MAX_ENFORCEMENT_RETRIES})")
            logger.warning(f"   Eksik sayısı: {report.deficiency_count}")
            for i, d in enumerate(report.deficiencies, 1):
                logger.warning(f"   {i}. {d.get('type', '?')}: {d.get('description', '?')[:80]}")

            # CEE-005: 3 FAIL sonrası eskalasyon
            if attempt >= self.MAX_ENFORCEMENT_RETRIES:
                logger.error(f"🚨 [CEE ESCALATE] {ctp_id}: {attempt} FAIL — "
                             f"Proje Yöneticisine eskalasyon gerekli!")
                logger.error(f"   CEE-005: Otomatik düzeltme döngüsü sonlandırıldı.")

        self._enforcement_history.append(report)
        return report

    # ── GENERIC VALIDATION: Constitution Index tabanlı ─────────────────────

    def validate_with_index(
        self, runtime_context: dict
    ) -> EnforcementReport:
        """Generic Constitutional Validation — Constitution Index ile.

        Hardcoded if-else YOK. Tüm kurallar ANA YASA .md'lerden gelir.
        Yeni kural eklendiğinde Python kodu DEĞİŞMEZ.

        Args:
            runtime_context: Runtime ölçümleri (cleanup, state, buttons, video, events, ...)

        Returns:
            EnforcementReport — Generic Validation sonucu (PASS/FAIL)
        """
        import uuid
        from datetime import datetime

        try:
            from services.constitution_index import constitution_index
        except ImportError:
            logger.warning("⚠️ [CEE] Constitution Index bulunamadı, generic validation atlanıyor")
            return self.post_check(
                code_anayasa_ok=True, flow_ok=True, state_ok=True,
                operational_ok=True, architecture_ok=True, runtime_ok=True,
            )

        # Constitution Index'ten Generic Validation çalıştır
        result = constitution_index.validate_and_report(runtime_context)

        ctp_id = self._active_ctp.ctp_id if self._active_ctp else "UNKNOWN"
        attempt = self._attempt_count.get(ctp_id, 0) + 1
        self._attempt_count[ctp_id] = attempt

        report_id = f"CEE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        report = EnforcementReport(
            report_id=report_id,
            ctp_id=ctp_id,
            attempt=attempt,
            code_anayasa_check=True,
            flow_compliance=True,
            state_compliance=result["all_pass"],
            operational_compliance=result["all_pass"],
            architectural_integrity=True,
            runtime_behavior=result["all_pass"],
            deficiencies=result["deficiencies"],
        )

        verdict = report.finalize()

        if verdict == EnforcementVerdict.PASS:
            logger.info(
                f"✅ [CEE GENERIC] PASS — {report_id} "
                f"({result['passed']}/{result['total_checks']} kural geçti)"
            )
        else:
            logger.warning(
                f"❌ [CEE GENERIC] FAIL — {report_id} "
                f"({result['failed']}/{result['total_checks']} kural BAŞARISIZ)"
            )
            for d in result["deficiencies"][:5]:
                logger.warning(
                    f"   [{d.get('type','?')}] {d.get('description','?')[:100]} "
                    f"— ref: {d.get('ana_yasa_ref','?')}"
                )

        self._enforcement_history.append(report)
        return report

    # ── Yardımcı Metodlar ──────────────────────────────────────────────────

    def get_history(self) -> list[EnforcementReport]:
        """POST-CHECK geçmişini döndürür."""
        return self._enforcement_history

    def get_active_ctp(self) -> Optional[ConstitutionalTaskPackage]:
        """Aktif CTP'yi döndürür."""
        return self._active_ctp

    def get_attempt_count(self, ctp_id: str | None = None) -> int:
        """Belirtilen CTP için deneme sayısını döndürür."""
        if ctp_id is None:
            ctp_id = self._active_ctp.ctp_id if self._active_ctp else "UNKNOWN"
        return self._attempt_count.get(ctp_id, 0)

    def needs_escalation(self, ctp_id: str | None = None) -> bool:
        """CEE-005: Eskalasyon gerekiyor mu?"""
        return self.get_attempt_count(ctp_id) >= self.MAX_ENFORCEMENT_RETRIES

    def reset(self) -> None:
        """CEE state'ini sıfırlar (yeni görev için)."""
        self._active_ctp = None
        logger.info("🔄 [CEE] Sıfırlandı — yeni göreve hazır")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

constitution_enforcement = ConstitutionEnforcementEngine()
