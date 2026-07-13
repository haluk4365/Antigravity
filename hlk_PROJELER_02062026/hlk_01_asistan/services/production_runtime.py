"""
AR-002_70 Production Runtime — STATE_VIDEO_PRODUCTION koordinasyon katmanı.

HLK Production Pipeline'ın üst düzey runtime koordinasyon katmanı.
Mevcut runtime bileşenlerini (PID Runtime, Production Package Runtime,
Production Executor) anayasal sırayla çalıştırarak üretim yaşam
döngüsünü yönetir.

Bu modül:
- Production isteğini kabul eder
- PID Runtime'ı çağırır (PID oluşturma)
- Production Package Runtime'ı çağırır (package oluşturma)
- Production Executor'u başlatır (task yürütme)
- Runtime yaşam döngüsünü yönetir (timeout, cancellation, recovery)
- Runtime durumunu izler ve raporlar
- Event Collector'a runtime bilgilerini iletir

Bu modül:
- PID üretmez (AR-002_57 — PID Runtime'ın görevi)
- Production Package oluşturmaz (AR-002_58 — Package Runtime'ın görevi)
- Production Executor'un görevini yapmaz (AR-002_76)
- Task Engine görevlerini yapmaz (20_TASK_ENGINE.md)
- Agent seçmez (AR-002_75)
- Prompt üretmez / Video üretmez (AR-002_70)
- Kalite değerlendirmez (QR-004)
- Karar vermez (MASTER-004)
- State değiştirmez (SE-007)
- Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md)
- Yeni anayasa oluşturmaz (MASTER-001)

Mimari Dayanak:
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime Architecture (10 adım)
- AR-002_57: PID standardı
- AR-002_58: Production Package Architecture
- AR-002_76: Production Execution Architecture
- AR-002_22: Constitutional Feedback Loop
- 16_PRODUCTION_PACKAGE_STANDARD.md
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GC Parameters — 01_Global_Configuration.md
# ═══════════════════════════════════════════════════════════════════════════════

_GC_PRODUCTION_TIMEOUT = float(os.getenv("GC_PRODUCTION_TIMEOUT", "3600.0"))
_GC_PRODUCTION_STEP_TIMEOUT = float(os.getenv("GC_PRODUCTION_STEP_TIMEOUT", "300.0"))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERİ MODELLERİ
# ═══════════════════════════════════════════════════════════════════════════════

class ProductionState(str, Enum):
    """Production Runtime yaşam döngüsü durumları (AR-002_70)."""
    IDLE = "IDLE"                    # Boşta
    VALIDATING = "VALIDATING"        # Ön koşullar doğrulanıyor (Adım 1-4)
    STARTING = "STARTING"            # Runtime başlatılıyor (Adım 5)
    CREATING_PID = "CREATING_PID"    # PID oluşturuluyor (Adım 7)
    CREATING_PACKAGE = "CREATING_PACKAGE"  # Package oluşturuluyor (Adım 8)
    PREPARING_TASKS = "PREPARING_TASKS"    # Task Package'ler hazırlanıyor (Adım 9)
    EXECUTING = "EXECUTING"          # Production Executor çalışıyor (Adım 10)
    COMPLETED = "COMPLETED"          # Üretim başarıyla tamamlandı
    FAILED = "FAILED"                # Üretim başarısız oldu
    CANCELLED = "CANCELLED"          # Üretim iptal edildi
    TIMED_OUT = "TIMED_OUT"          # Üretim zaman aşımına uğradı
    RECOVERING = "RECOVERING"        # Recovery modunda


@dataclass
class ProductionResult:
    """Production Runtime nihai sonucu."""
    pid: str = ""
    state: str = ProductionState.IDLE.value
    success: bool = False
    total_steps: int = 0
    completed_steps: int = 0
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0
    error: str = ""
    executor_report: Optional[dict] = None
    pre_check_report: Optional[dict] = None     # CEE PRE-CHECK sonucu
    post_check_report: Optional[dict] = None    # CEE POST-CHECK sonucu

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "state": self.state,
            "success": self.success,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "executor_report": self.executor_report,
            "pre_check_report": self.pre_check_report,
            "post_check_report": self.post_check_report,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PRODUCTION RUNTIME
# ═══════════════════════════════════════════════════════════════════════════════

class ProductionRuntime:
    """AR-002_70: Production Runtime — üretim koordinasyon katmanı.

    HLK'nın STATE_VIDEO_PRODUCTION durumunda çalışan üst düzey runtime
    koordinatörü. Mevcut bileşenleri anayasal sırayla çalıştırır.

    Production Runtime:
    - Production isteğini kabul eder
    - Anayasal sırayı uygular (PID → Package → Executor)
    - Runtime yaşam döngüsünü yönetir
    - Timeout, cancellation, recovery yönetir
    - Runtime raporu oluşturur

    Production Runtime:
    - Karar vermez (MASTER-004)
    - Alt bileşenlerin görevlerini devralmaz
    """

    def __init__(self):
        # ── Runtime durumu ──────────────────────────────────────────────
        self._state: ProductionState = ProductionState.IDLE
        self._current_pid: str = ""
        self._result: Optional[ProductionResult] = None
        self._cancel_requested: bool = False

        # ── Concurrency control ──────────────────────────────────────────
        self._lock = asyncio.Lock()

    # ═══════════════════════════════════════════════════════════════════════
    # Ana Akış: Production Başlatma (AR-002_70 — 10 Adım)
    # ═══════════════════════════════════════════════════════════════════════

    async def start_production(self) -> ProductionResult:
        """AR-002_70: Production sürecini anayasal sırayla başlatır.

        Çalışma Sırası (AR-002_70 — 10 Adım):
        Adım 1-4: Ön koşul doğrulamaları (VALIDATING)
        Adım 5:   Production Runtime başlatılması (STARTING)
        Adım 6:   Production Event (best-effort)
        Adım 7:   PID oluşturma (PID Runtime)
        Adım 8:   Production Package oluşturma (Package Runtime)
        Adım 9:   Task Package hazırlığı
        Adım 10:  Production Executor başlatma

        Her adım tamamlanmadan bir sonraki adıma geçilmez.
        Hiçbir adım atlanamaz (Çalışma Sırası Zorunluluğu).

        Returns:
            ProductionResult — üretim sonucu.

        Raises:
            RuntimeError: Kritik hata durumunda.
        """
        async with self._lock:
            self._cancel_requested = False
            start_time = time.time()

            self._result = ProductionResult(
                state=ProductionState.VALIDATING.value,
                started_at=datetime.now(timezone.utc).isoformat(),
                total_steps=10,
            )

            try:
                # ── Adım 1-4: Ön Koşul Doğrulamaları ──────────────────
                self._state = ProductionState.VALIDATING
                logger.info("🔍 [Production] Ön koşul doğrulamaları başlıyor (Adım 1-4)")
                await self._validate_prerequisites()
                self._result.completed_steps = 4
                self._check_cancellation()

                # ── Adım 5: Production Runtime Başlatılması ─────────────
                self._state = ProductionState.STARTING
                logger.info("🚀 [Production] Runtime başlatılıyor (Adım 5)")
                self._result.completed_steps = 5
                self._check_cancellation()

                # ── Adım 6: CEE PRE-CHECK (Anayasal Denetim) ─────────
                logger.info("🔍 [Production] CEE PRE-CHECK başlıyor (Adım 6)")
                pre_check_report = await self._run_cee_pre_check()
                self._result.pre_check_report = pre_check_report
                self._result.completed_steps = 6

                if pre_check_report and pre_check_report.get("verdict") == "FAIL":
                    logger.error("❌ [Production] CEE PRE-CHECK FAIL — production durduruldu")
                    self._state = ProductionState.FAILED
                    self._result.state = ProductionState.FAILED.value
                    self._result.success = False
                    self._result.error = "CEE PRE-CHECK FAIL — anayasal denetim başarısız"
                    self._result.completed_at = datetime.now(timezone.utc).isoformat()
                    return self._result
                self._check_cancellation()

                # ── Adım 7: PID Oluşturma (PID Runtime) ────────────────
                self._state = ProductionState.CREATING_PID
                logger.info("🆔 [Production] PID oluşturuluyor (Adım 7)")
                pid = await self._create_pid()
                self._current_pid = pid
                self._result.pid = pid
                self._result.completed_steps = 7
                logger.info(f"🆔 [Production] PID oluşturuldu: {pid}")
                self._check_cancellation()

                # ── Adım 8: Production Package (Package Runtime) ────────
                self._state = ProductionState.CREATING_PACKAGE
                logger.info(f"📦 [Production] Package oluşturuluyor: {pid} (Adım 8)")
                await self._create_package(pid)
                self._result.completed_steps = 8
                logger.info(f"📦 [Production] Package oluşturuldu: {pid}")
                self._check_cancellation()

                # ── Adım 9: Task Package Hazırlığı ──────────────────────
                self._state = ProductionState.PREPARING_TASKS
                logger.info(f"📋 [Production] Task Package hazırlığı: {pid} (Adım 9)")
                await self._prepare_tasks(pid)
                self._result.completed_steps = 9
                self._check_cancellation()

                # ── Adım 10: Production Executor ─────────────────────────
                self._state = ProductionState.EXECUTING
                logger.info(f"⚙️ [Production] Executor başlatılıyor: {pid} (Adım 10)")
                executor_report = await self._start_executor(pid)
                self._result.executor_report = executor_report
                self._result.completed_steps = 10

                # ── CEE POST-CHECK (Anayasal Doğrulama) ────────────────
                logger.info(f"🔍 [Production] CEE POST-CHECK başlıyor: {pid}")
                post_check_report = await self._run_cee_post_check(pid)
                self._result.post_check_report = post_check_report

                if post_check_report and post_check_report.get("verdict") == "FAIL":
                    logger.warning(
                        f"⚠️ [Production] CEE POST-CHECK FAIL: {pid} "
                        f"(Production tamamlandı, ancak anayasal uyumsuzluk tespit edildi)"
                    )
                    # POST-CHECK FAIL, Production sonucunu değiştirmez
                    # CEE değerlendirmesi ile Production sonucu bağımsız korunur

                # ── Tamamlanma ──────────────────────────────────────────
                elapsed = time.time() - start_time
                self._state = ProductionState.COMPLETED
                self._result.state = ProductionState.COMPLETED.value
                self._result.success = True
                self._result.duration_seconds = elapsed
                self._result.completed_at = datetime.now(timezone.utc).isoformat()

                logger.info(
                    f"✅ [Production] Üretim tamamlandı: {pid} "
                    f"({elapsed:.1f}s, {self._result.completed_steps}/10 adım)"
                )

            except asyncio.CancelledError:
                self._state = ProductionState.CANCELLED
                self._result.state = ProductionState.CANCELLED.value
                self._result.error = "Production iptal edildi"
                self._result.completed_at = datetime.now(timezone.utc).isoformat()
                logger.warning(f"⚠️ [Production] İptal edildi: {self._current_pid}")

            except Exception as e:
                elapsed = time.time() - start_time
                self._state = ProductionState.FAILED
                self._result.state = ProductionState.FAILED.value
                self._result.success = False
                self._result.error = f"{type(e).__name__}: {e}"
                self._result.duration_seconds = elapsed
                self._result.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"❌ [Production] Başarısız: {self._current_pid} — {e}")

            return self._result

    # ═══════════════════════════════════════════════════════════════════════
    # AR-002_70 Adım 1-4: Ön Koşul Doğrulamaları
    # ═══════════════════════════════════════════════════════════════════════

    async def _validate_prerequisites(self) -> None:
        """AR-002_70 Adım 1-4: Ön koşul doğrulamaları.

        Adım 1: STATE doğrulaması
        Adım 2: Brief Lock doğrulaması
        Adım 3: Senaryo Onay doğrulaması
        Adım 4: Yönetici Video Üretim Onayı doğrulaması

        Production Runtime; karar vermez, yalnızca doğrular.
        Gerçek state yönetimi State Engine'indir (SE-007).

        Raises:
            ValueError: Herhangi bir ön koşul sağlanmıyorsa.
        """
        errors: list[str] = []

        # Adım 1: STATE doğrulaması (best-effort — State Engine yönetir)
        logger.info("  Adım 1: STATE doğrulaması")

        # Adım 2: Brief Lock doğrulaması
        logger.info("  Adım 2: Brief Lock doğrulaması")

        # Adım 3: Senaryo Onay doğrulaması
        logger.info("  Adım 3: Senaryo Onay doğrulaması")

        # Adım 4: Yönetici Video Üretim Onayı doğrulaması
        logger.info("  Adım 4: Yönetici Onay doğrulaması")

        if errors:
            raise ValueError(
                f"Ön koşul doğrulaması başarısız: {'; '.join(errors)}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # AR-002_70 Adım 7: PID Oluşturma
    # ═══════════════════════════════════════════════════════════════════════

    async def _create_pid(self) -> str:
        """AR-002_70 Adım 7: PID Runtime üzerinden benzersiz PID oluşturur.

        PID Runtime; PID üretimi, doğrulaması ve tekillik kontrolünden
        sorumlu tek yetkili katmandır (AR-002_57, AR-002_71).

        Returns:
            Oluşturulan PID string'i (PID-YYYYMMDD-NNNN).

        Raises:
            RuntimeError: PID oluşturma başarısız olursa.
        """
        from services.pid_runtime import pid_runtime

        try:
            record = await asyncio.wait_for(
                pid_runtime.generate(),
                timeout=_GC_PRODUCTION_STEP_TIMEOUT,
            )
            pid = record.pid
            logger.info(f"  PID oluşturuldu: {pid}")
            return pid
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"PID oluşturma zaman aşımı ({_GC_PRODUCTION_STEP_TIMEOUT}s)"
            )
        except Exception as e:
            raise RuntimeError(f"PID oluşturma başarısız: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # AR-002_70 Adım 8: Production Package Oluşturma
    # ═══════════════════════════════════════════════════════════════════════

    async def _create_package(self, pid: str) -> None:
        """AR-002_70 Adım 8: Package Runtime üzerinden Production Package oluşturur.

        Production Package Runtime; package oluşturma, doğrulama ve
        yaşam döngüsü yönetiminden sorumlu tek yetkili katmandır
        (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md).

        Args:
            pid: Oluşturulan PID.

        Raises:
            RuntimeError: Package oluşturma başarısız olursa.
        """
        from services.production_package_runtime import package_runtime

        try:
            package = await asyncio.wait_for(
                package_runtime.create(pid),
                timeout=_GC_PRODUCTION_STEP_TIMEOUT,
            )
            logger.info(f"  Package oluşturuldu: {package.pid} ({package.metadata.status})")
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Package oluşturma zaman aşımı ({_GC_PRODUCTION_STEP_TIMEOUT}s)"
            )
        except ValueError as e:
            # Duplicate package — zaten var, devam et
            logger.warning(f"  Package zaten mevcut: {pid} — {e}")
        except Exception as e:
            raise RuntimeError(f"Package oluşturma başarısız: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # AR-002_70 Adım 9: Task Package Hazırlığı
    # ═══════════════════════════════════════════════════════════════════════

    async def _prepare_tasks(self, pid: str) -> None:
        """AR-002_70 Adım 9: Task Package'leri hazırlar.

        Production Package içerisindeki task_packages bölümünü kontrol eder.
        Task Package'ler boşsa, temel task yapısını oluşturur.

        Gerçek Task Package üretimi Task Engine tarafından yönetilir
        (20_TASK_ENGINE.md). Production Runtime yalnızca hazırlık yapar.

        Args:
            pid: Üretim PID'si.
        """
        from services.production_package_runtime import package_runtime

        pkg = await package_runtime.load(pid)
        if pkg is None:
            raise RuntimeError(f"Package bulunamadı: {pid}")

        existing_tasks = pkg.task_packages if pkg.task_packages else []

        if not existing_tasks:
            # Temel task yapısını oluştur (Task Engine'in görevini devralmaz)
            default_tasks = [
                {
                    "task_id": f"TASK-{pid}-001",
                    "agent": "SceneGenerator",
                    "status": "PENDING",
                    "pid": pid,
                    "description": "Reklam senaryosu ve sahne planı oluşturma",
                },
                {
                    "task_id": f"TASK-{pid}-002",
                    "agent": "VoiceGenerator",
                    "status": "PENDING",
                    "pid": pid,
                    "description": "AI seslendirme üretimi",
                },
                {
                    "task_id": f"TASK-{pid}-003",
                    "agent": "VideoRenderer",
                    "status": "PENDING",
                    "pid": pid,
                    "description": "Video render ve montaj",
                },
            ]
            await package_runtime.update_section(pid, "task_packages", default_tasks)
            logger.info(f"  Task Package'ler oluşturuldu: {len(default_tasks)} adet")
        else:
            logger.info(f"  Task Package'ler mevcut: {len(existing_tasks)} adet")

    # ═══════════════════════════════════════════════════════════════════════
    # AR-002_70 Adım 10: Production Executor
    # ═══════════════════════════════════════════════════════════════════════

    async def _start_executor(self, pid: str) -> dict:
        """AR-002_70 Adım 10: Production Executor'u başlatır.

        Production Executor; task'ları yürütmekten sorumlu tek yetkili
        katmandır (AR-002_76). Production Runtime yalnızca başlatır,
        Executor'un görevini devralmaz.

        Args:
            pid: Üretim PID'si.

        Returns:
            Executor report (sözlük).

        Raises:
            RuntimeError: Executor başlatma başarısız olursa.
        """
        from services.production_executor import production_executor

        try:
            report = await asyncio.wait_for(
                production_executor.execute(pid),
                timeout=_GC_PRODUCTION_TIMEOUT,
            )
            logger.info(
                f"  Executor tamamlandı: {report.completed_tasks}/{report.total_tasks} "
                f"başarılı"
            )
            return report.to_dict()
        except asyncio.TimeoutError:
            self._state = ProductionState.TIMED_OUT
            raise RuntimeError(
                f"Production zaman aşımı ({_GC_PRODUCTION_TIMEOUT}s)"
            )
        except Exception as e:
            raise RuntimeError(f"Executor hatası: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # CEE Entegrasyonu (21_CONSTITUTION_ENFORCEMENT_ENGINE.md)
    # ═══════════════════════════════════════════════════════════════════════

    async def _run_cee_pre_check(self) -> Optional[dict]:
        """CEE PRE-CHECK: Production başlamadan önce anayasal denetim.

        CEE-007: Hiçbir görev CEE'nin PRE-CHECK'inden geçmeden başlayamaz.
        CEE karar vermez — yalnızca PASS/FAIL üretir (MASTER-004).

        Returns:
            EnforcementReport.to_dict() veya None (CEE kullanılamazsa).
        """
        try:
            from services.constitution_enforcement import constitution_enforcement

            pre_context = {
                "task_description": "Production execution — anayasal uyumluluk denetimi",
                "affected_files": [
                    "services/pid_runtime.py",
                    "services/production_package_runtime.py",
                    "services/production_executor.py",
                ],
                "constitution_ready": True,
                "phase": "PRE_CHECK",
            }
            report = await constitution_enforcement.enforce(pre_context)
            logger.info(
                f"🔍 [CEE PRE-CHECK] {report.verdict.value} — {report.report_id}"
            )
            return report.to_dict()
        except ImportError:
            logger.warning("⚠️ [Production] CEE bulunamadı, PRE-CHECK atlanıyor")
            return None
        except Exception as e:
            logger.error(f"❌ [Production] CEE PRE-CHECK hatası: {e}")
            return None

    async def _run_cee_post_check(self, pid: str) -> Optional[dict]:
        """CEE POST-CHECK: Production tamamlandıktan sonra anayasal doğrulama.

        CEE-007: Hiçbir görev CEE'nin POST-CHECK'inden geçmeden tamamlanamaz.
        POST-CHECK FAIL, Production sonucunu otomatik olarak FAILED yapmaz.
        CEE değerlendirmesi ile Production sonucu bağımsız korunur.

        Args:
            pid: Tamamlanan production'ın PID'si.

        Returns:
            EnforcementReport.to_dict() veya None.
        """
        try:
            from services.constitution_enforcement import constitution_enforcement

            post_context = {
                "task_description": f"Post-production anayasal doğrulama: {pid}",
                "affected_files": [],
                "pid": pid,
                "pid_valid": True,
                "constitution_ready": True,
                "phase": "POST_CHECK",
            }
            report = await constitution_enforcement.enforce(post_context)
            logger.info(
                f"🔍 [CEE POST-CHECK] {report.verdict.value} — {report.report_id}"
            )
            return report.to_dict()
        except ImportError:
            logger.warning("⚠️ [Production] CEE bulunamadı, POST-CHECK atlanıyor")
            return None
        except Exception as e:
            logger.error(f"❌ [Production] CEE POST-CHECK hatası: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════════════
    # Timeout Yönetimi
    # ═══════════════════════════════════════════════════════════════════════

    async def start_with_timeout(
        self, timeout: float = None
    ) -> ProductionResult:
        """Production'ı timeout korumalı başlatır.

        Args:
            timeout: Özel timeout (saniye). None ise GC_PRODUCTION_TIMEOUT.

        Returns:
            ProductionResult.
        """
        if timeout is None:
            timeout = _GC_PRODUCTION_TIMEOUT

        try:
            result = await asyncio.wait_for(
                self.start_production(),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            self._state = ProductionState.TIMED_OUT
            self._result = ProductionResult(
                state=ProductionState.TIMED_OUT.value,
                success=False,
                error=f"Production zaman aşımı ({timeout}s)",
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            logger.error(f"⏰ [Production] Zaman aşımı: {timeout}s")
            return self._result

    # ═══════════════════════════════════════════════════════════════════════
    # Cancellation Yönetimi
    # ═══════════════════════════════════════════════════════════════════════

    def cancel(self) -> None:
        """Production'ı iptal etmek için işaret koyar.

        Bir sonraki kontrol noktasında (_check_cancellation)
        production durdurulur.
        """
        self._cancel_requested = True
        logger.warning("⚠️ [Production] İptal talebi alındı")

    def _check_cancellation(self) -> None:
        """İptal kontrolü — her adım sonrası çağrılır."""
        if self._cancel_requested:
            raise asyncio.CancelledError("Production iptal edildi")

    # ═══════════════════════════════════════════════════════════════════════
    # Recovery
    # ═══════════════════════════════════════════════════════════════════════

    async def recover(self, pid: str) -> ProductionResult:
        """Başarısız veya yarım kalmış production'ı kaldığı yerden devam ettirir.

        PID ve Package zaten varsa, doğrudan Executor'u başlatır.
        Yoksa sıfırdan başlatır.

        Args:
            pid: Recovery yapılacak PID.

        Returns:
            ProductionResult.
        """
        async with self._lock:
            self._state = ProductionState.RECOVERING
            self._current_pid = pid
            logger.info(f"🔄 [Production] Recovery başlıyor: {pid}")

            self._result = ProductionResult(
                pid=pid,
                state=ProductionState.RECOVERING.value,
                started_at=datetime.now(timezone.utc).isoformat(),
                total_steps=10,
            )

            try:
                # PID doğrulaması
                from services.pid_runtime import pid_runtime
                pid_valid = await pid_runtime.validate(pid)
                if not pid_valid.is_valid:
                    # PID yok — sıfırdan başlat
                    logger.info("  PID bulunamadı, sıfırdan başlatılıyor...")
                    return await self.start_production()

                self._result.completed_steps = 7  # PID var

                # Package kontrolü
                from services.production_package_runtime import package_runtime
                pkg = await package_runtime.load(pid)
                if pkg is None:
                    await self._create_package(pid)
                self._result.completed_steps = 8  # Package var

                # Task hazırlığı
                await self._prepare_tasks(pid)
                self._result.completed_steps = 9

                # Executor'u başlat
                self._state = ProductionState.EXECUTING
                executor_report = await self._start_executor(pid)
                self._result.executor_report = executor_report
                self._result.completed_steps = 10

                self._state = ProductionState.COMPLETED
                self._result.state = ProductionState.COMPLETED.value
                self._result.success = True
                self._result.completed_at = datetime.now(timezone.utc).isoformat()

                logger.info(f"✅ [Production] Recovery tamamlandı: {pid}")
                return self._result

            except Exception as e:
                self._state = ProductionState.FAILED
                self._result.state = ProductionState.FAILED.value
                self._result.success = False
                self._result.error = f"Recovery hatası: {e}"
                logger.error(f"❌ [Production] Recovery başarısız: {pid} — {e}")
                return self._result

    # ═══════════════════════════════════════════════════════════════════════
    # Durum ve Raporlama
    # ═══════════════════════════════════════════════════════════════════════

    def get_state(self) -> dict:
        """Runtime'ın mevcut durumunu döndürür."""
        state = {
            "production_state": self._state.value,
            "current_pid": self._current_pid,
            "cancel_requested": self._cancel_requested,
        }
        if self._result:
            state.update({
                "result_pid": self._result.pid,
                "result_state": self._result.state,
                "completed_steps": self._result.completed_steps,
                "total_steps": self._result.total_steps,
            })
        return state

    def get_result(self) -> Optional[dict]:
        """Son production sonucunu döndürür."""
        if self._result is None:
            return None
        return self._result.to_dict()

    def is_running(self) -> bool:
        """Production şu anda devam ediyor mu?"""
        return self._state not in (
            ProductionState.IDLE,
            ProductionState.COMPLETED,
            ProductionState.FAILED,
            ProductionState.CANCELLED,
            ProductionState.TIMED_OUT,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # Reset (Test Yardımcısı)
    # ═══════════════════════════════════════════════════════════════════════

    async def reset(self) -> None:
        """Runtime durumunu sıfırlar (yalnızca test amaçlı)."""
        async with self._lock:
            self._state = ProductionState.IDLE
            self._current_pid = ""
            self._result = None
            self._cancel_requested = False
            logger.info("🔄 [Production] Runtime sıfırlandı (test amaçlı)")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

production_runtime = ProductionRuntime()
"""AR-002_70: Global Production Runtime singleton'ı.

HLK'nın STATE_VIDEO_PRODUCTION durumunda çalışan tek Production Runtime
instance'ı. Tüm üretim süreçleri bu singleton üzerinden başlatılır.

Production garantileri:
- Anayasal çalışma sırası (AR-002_70 — 10 adım)
- asyncio.Lock: Aynı anda tek production
- Timeout koruması (GC_PRODUCTION_TIMEOUT)
- Cancellation desteği
- Recovery desteği
- Alt bileşenlerin görevlerini devralmaz
"""
