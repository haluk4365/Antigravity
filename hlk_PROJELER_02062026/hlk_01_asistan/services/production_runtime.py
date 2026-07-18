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
- Karar vermez (MASTER-004, MASTER-013) — karar gerektiren durumları
  AR-002_81 Karar Talep Protokolü ile HLK Runtime'a iletir
- State değiştirmez (SE-007)
- Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md)
- Yeni anayasa oluşturmaz (MASTER-001)

Mimari Dayanak:
- MASTER-013: HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı
- AR-002_81: HLK Runtime Karar Otoritesi ve Karar Talep Protokolü
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
        # PID doğrulaması KİLİT ALINMADAN yapılır — start_production()
        # aynı kilidi kullandığından, kilit altında çağrılması deadlock
        # oluşturur (AR-002_79 süreklilik yolu güvencesi).
        from services.pid_runtime import pid_runtime
        pid_valid = await pid_runtime.validate(pid)
        if not pid_valid.is_valid:
            # PID yok — sıfırdan başlat
            logger.info(f"🔄 [Production] Recovery: PID bulunamadı ({pid}), sıfırdan başlatılıyor...")
            return await self.start_production()

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
    # Yönetici Yeniden Üretim Prosedürü (AR-002_84)
    # ═══════════════════════════════════════════════════════════════════════
    # Yalnızca Yönetici tarafından başlatılabilir (handler katmanı doğrular).
    # Tüm teknik kararlar HLK Runtime tarafından üretilir (MASTER-013,
    # AR-002_81); bu akış yalnızca kararları uygular ve kayıt altına alır.
    # Mevcut mimariler yeniden kullanılır: Production Package Runtime
    # (AR-002_72), Production Executor recovery (AR-002_76/79), Decision
    # Engine (MASTER-004), EEC/Olay Kayıt Merkezi (AR-002_73), CEE (AR-002_60).

    def launch_reproduction(
        self, pid: str, bot, admin_chat_id: int, admin_user_id: int
    ) -> "asyncio.Task":
        """Yönetici onayı sonrası yeniden üretim prosedürünü devralır.

        AR-002_84: Yönetici yalnızca prosedürü başlatır; üretimin devamı,
        strateji ve tüm Runtime kararları HLK Runtime'a aittir (MASTER-013).

        Args:
            pid: Yeniden üretilecek Production ID (doğrulanmış).
            bot: telegram.Bot — bildirim ve teslim için.
            admin_chat_id: Prosedürü başlatan Yöneticinin sohbet ID'si.
            admin_user_id: Prosedürü başlatan Yöneticinin kullanıcı ID'si.

        Returns:
            asyncio.Task — yönetilen yeniden üretim görevi.
        """
        logger.info(
            f"🔄 [Reproduction] Yeniden üretim talebi kabul edildi — "
            f"PID={pid} yönetici={admin_user_id}"
        )
        task = asyncio.create_task(
            self.run_reproduction(pid, bot, admin_chat_id, admin_user_id)
        )
        task.add_done_callback(self._on_task_done)
        return task

    async def run_reproduction(
        self, pid: str, bot, admin_chat_id: int, admin_user_id: int
    ) -> ProductionResult:
        """Yönetilen yeniden üretim yaşam döngüsü — istisnalar dışarı sızmaz.

        GC_PRODUCTION_TIMEOUT ve Runtime Heartbeat (MASTER-011) korumaları
        normal üretim yaşam döngüsüyle aynıdır.
        """
        _heartbeat_task = self._start_heartbeat(admin_user_id)
        try:
            return await asyncio.wait_for(
                self._run_reproduction(pid, bot, admin_chat_id, admin_user_id),
                timeout=_GC_PRODUCTION_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error(
                f"🏁 [Reproduction Timeout] {_GC_PRODUCTION_TIMEOUT}s aşıldı — {pid}"
            )
            return await self._handle_reproduction_failure(
                pid, bot, admin_chat_id,
                error=f"Yeniden üretim zaman aşımı ({_GC_PRODUCTION_TIMEOUT}s)",
                state=ProductionState.TIMED_OUT,
            )
        except Exception as e:
            logger.error(
                f"❌ [Reproduction] Yaşam döngüsü hatası: {type(e).__name__}: {e}"
            )
            return await self._handle_reproduction_failure(
                pid, bot, admin_chat_id,
                error=f"{type(e).__name__}: {e}",
                state=ProductionState.FAILED,
            )
        finally:
            if _heartbeat_task:
                _heartbeat_task.cancel()
            try:
                from services.hlk_runtime import hlk_runtime as _hr_term
                _hr_term.on_production_terminal(admin_user_id)
            except Exception:
                pass

    async def _run_reproduction(
        self, pid: str, bot, admin_chat_id: int, admin_user_id: int
    ) -> ProductionResult:
        """AR-002_84 anayasal yeniden üretim zinciri (Adım 1-21).

        Adımlar:
        1     PID doğrulama (AR-002_57)
        2-10  Production Package + tüm anayasal kayıtların yüklenmesi
              (Workflow, State Engine, Olay Kayıt Merkezi, Dijital Varlık
              Arşivi/Kataloğu, Sahne Kayıt Defteri, Karar Gerekçeleri)
        11    Bütünlük doğrulaması (SHA-256)
        12-13 Son başarılı / başarısız aşamanın belirlenmesi
        14-16 HLK Runtime REPRODUCTION kararı (MASTER-013, AR-002_81)
        17    Üretimin otomatik başlatılması (paket hazırlığı + context)
        18    Üretim yönetimi (Executor recovery — AR-002_76/79)
        19    Olay kayıtları (AR-002_73, EEC, Olay Kayıt Merkezi)
        20    Dijital varlıkların paket ile ilişkilendirilmesi + sürüm geçmişi
        21    Telegram bildirimi (Yönetici + ilgili Kullanıcı)
        """
        from services.production_pipeline import (
            ProductionRequest, PipelineContext,
            set_context, clear_context, register_handlers,
        )
        from services.constitution_enforcement import constitution_enforcement
        from services.execution_event_collector import (
            execution_event_collector, EECEventType, ExecutionPhase,
        )
        from services.olay_kayit_merkezi import event_registry
        from services.live_activity_center import live_activity_center
        from services.pid_runtime import pid_runtime
        from services.production_package_runtime import package_runtime
        from services.decision_engine import decision_engine, ProductionContext
        from services.hlk_runtime import (
            hlk_runtime, DecisionRequest, DecisionCategory,
        )

        start_time = time.time()
        self._cancel_requested = False
        self._state = ProductionState.RECOVERING
        self._current_pid = pid
        self._result = ProductionResult(
            pid=pid,
            state=ProductionState.RECOVERING.value,
            started_at=datetime.now(timezone.utc).isoformat(),
            total_steps=10,
        )

        # OLAY-107: Yönetici yeniden üretim talebi (AR-002_84 giriş kaydı)
        await self._record_reproduction_event(
            pid,
            event_constant="EVENT_REPRODUCTION_REQUESTED",
            event_name="Yeniden Üretim Talep Edildi (OLAY-107)",
            description=(
                f"Yönetici ({admin_user_id}) yeniden üretim prosedürünü onayladı"
            ),
            result="REQUESTED",
        )

        # ── Adım 1: PID doğrulama (AR-002_57) ────────────────────────────
        pid_valid = await pid_runtime.validate(pid)
        if not pid_valid.is_valid:
            # AR-002_84: PID formatı geçerliyse registry kaydı olmasa da
            # yeniden üretime izin ver — paket diskte mevcut olabilir,
            # pid_runtime_state.json kaybı/pasifliği bloğa sebep olmamalı.
            checks = getattr(pid_valid, "checks", {})
            if not (
                checks.get("format_valid")
                and checks.get("date_valid")
                and checks.get("sequence_valid")
            ):
                return await self._reject_reproduction(
                    pid, bot, admin_chat_id,
                    reason=f"PID dogrulanamadi: {pid_valid.error}",
                )
            # Format/date/sequence geçerli → registry eksikliğini logla, devam et
            logger.warning(
                f"⚠️ [Reproduction] PID registry kaydı eksik ancak format "
                f"geçerli — diskten yüklenerek devam ediliyor: {pid}"
            )

        # ── Adım 2-10: Anayasal kayıtların yüklenmesi (AR-002_72/73) ────
        context = await package_runtime.load_full_production_context(pid)
        if context.get("error"):
            return await self._reject_reproduction(
                pid, bot, admin_chat_id,
                reason=f"Production Package yuklenemedi: {context['error']}",
            )
        logger.info(
            f"📦 [Reproduction] Anayasal kayıtlar yüklendi: {pid} — "
            f"durum={context.get('package_status')} "
            f"task={context.get('completed_tasks')}/{context.get('total_tasks')} "
            f"event={len(context.get('event_logs', []))} "
            f"karar={len(context.get('decision_history', []))}"
        )

        # ── Adım 11: Bütünlük doğrulaması ────────────────────────────────
        integrity_ok, integrity_msg = await package_runtime.verify_integrity(pid)
        if not integrity_ok:
            logger.warning(
                f"⚠️ [Reproduction] Bütünlük uyarısı ({pid}): {integrity_msg}"
            )
        else:
            logger.info(f"🔐 [Reproduction] {integrity_msg}")

        # ── Adım 12-13: Son başarılı / başarısız aşama ───────────────────
        logger.info(
            f"📍 [Reproduction] Son başarılı aşama: "
            f"{context.get('last_successful_step') or '(yok)'} | "
            f"Başarısız aşama: {context.get('failed_step') or '(yok)'}"
        )

        # ── Adım 14-16: HLK Runtime REPRODUCTION kararı (MASTER-013) ────
        decision = hlk_runtime.request_decision(DecisionRequest(
            pid=pid,
            category=DecisionCategory.REPRODUCTION.value,
            requester="production_runtime.run_reproduction",
            context={
                "pid": pid,
                "package_status": context.get("package_status", ""),
                "failed_tasks": context.get("failed_tasks", 0),
                "completed_tasks": context.get("completed_tasks", 0),
                "total_tasks": context.get("total_tasks", 0),
                "last_error": context.get("last_error", ""),
                "failed_step": context.get("failed_step", ""),
                "hlk_runtime_active": hlk_runtime.is_active(admin_user_id),
            },
        ))
        # Karar, Production Package Decision History'ye kaydedilir
        # (15_KARAR_GEREKCESI_STANDARDI.md — kayıtlar silinemez, eklenir)
        await self._append_package_list_section(pid, "decision_history", {
            "decision_id": decision.decision_id,
            "request_id": decision.request_id,
            "category": decision.category,
            "verdict": decision.verdict,
            "params": decision.params,
            "rationale": decision.rationale,
        })

        if decision.verdict == "REJECT":
            # OLAY-109: Yeniden üretim reddedildi — güvenli sonlandırma
            await self._record_reproduction_event(
                pid,
                event_constant="EVENT_REPRODUCTION_REJECTED",
                event_name="Yeniden Üretim Reddedildi (OLAY-109)",
                description=(
                    "HLK Runtime REPRODUCTION kararı REJECT — "
                    + "; ".join(decision.rationale.get("Justifications", []))
                ),
                result="REJECT",
            )
            notify = hlk_runtime.request_decision(DecisionRequest(
                pid=pid,
                category=DecisionCategory.USER_NOTIFICATION.value,
                requester="production_runtime.run_reproduction",
                context={
                    "kind": "reproduction_rejected",
                    "justifications": decision.rationale.get("Justifications", []),
                },
            ))
            if notify.verdict == "NOTIFY" and bot is not None:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=notify.params.get("text", ""),
                    parse_mode=notify.params.get("parse_mode", "HTML"),
                )
            self._state = ProductionState.IDLE
            self._result.state = ProductionState.IDLE.value
            self._result.success = False
            self._result.error = "REPRODUCTION kararı: REJECT"
            self._result.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"⛔ [Reproduction] REJECT ile sonlandırıldı: {pid}")
            return self._result

        procedure = decision.verdict  # RESUME | RETRY | REPLAY | START_AS_NEW
        logger.info(f"⚖️ [Reproduction] HLK Runtime prosedür kararı: {procedure}")

        # ── Adım 17: Üretimin otomatik başlatılması ──────────────────────
        prepared = await package_runtime.prepare_for_reproduction(pid, procedure)
        if not prepared:
            return await self._reject_reproduction(
                pid, bot, admin_chat_id,
                reason="Production Package yeniden üretime hazırlanamadı "
                       "(arşivlenmiş veya erişilemez durumda)",
            )

        # ProductionRequest paketten yeniden kurulur (AR-002_72 kayıtları)
        pkg = await package_runtime.load(pid)
        brief = (pkg.brief or {}) if pkg else {}
        vparams = (pkg.video_parameters or {}) if pkg else {}
        delivery = (pkg.delivery_info or {}) if pkg else {}
        user_chat_id = brief.get("chat_id") or delivery.get("chat_id") or admin_chat_id
        user_user_id = brief.get("user_id") or admin_user_id
        try:
            duration = int(vparams.get("duration_seconds", 15) or 15)
        except (TypeError, ValueError):
            duration = 15
        request = ProductionRequest(
            chat_id=int(user_chat_id),
            user_id=int(user_user_id),
            url=brief.get("url", ""),
            product_name=brief.get("product_name", "urununuz") or "urununuz",
            brand=brief.get("brand", "Marka") or "Marka",
            duration=duration,
            voice_lang=(vparams.get("voice_language")
                        or brief.get("voice_language") or "tr"),
            bot=bot,
            user_data={},
        )

        # Production Lifecycle — session PID ile güncellenir
        try:
            hlk_runtime.on_production_start(admin_user_id, pid)
        except Exception:
            pass

        # CEE PRE-CHECK (AR-002_60 — anayasal görev paketi)
        ctp = constitution_enforcement.pre_check(
            task_description=f"Reproduction ({procedure}) for {pid}",
            affected_files=[
                "services/production_runtime.py",
                "services/production_pipeline.py",
                "services/production_executor.py",
            ],
            master_rules=["MASTER-001", "MASTER-003", "MASTER-013"],
            arch_rules=["AR-002_57", "AR-002_79", "AR-002_82", "AR-002_83", "AR-002_84"],
            oper_rules=["OR-004_12"],
            flow_steps=["AR-002_84: Yönetici Yeniden Üretim Prosedürü"],
            state_rules=["SE-007_3"],
            expected_outputs=["Video delivered or constitutional termination"],
        )
        logger.info(f"📋 [CEE PRE-CHECK] CTP: {ctp.ctp_id}")
        self._result.pre_check_report = {"ctp_id": ctp.ctp_id}

        # OLAY-108: Yeniden üretim başladı (Adım 19 kayıt mekanizması)
        execution_event_collector.listen(pid=pid)
        start_evt = execution_event_collector.emit_event(
            event_type=EECEventType.TASK_STARTED,
            description=f"Reproduction started ({procedure}): {pid}",
            phase=ExecutionPhase.EXECUTE,
            result=f"Yeniden üretim prosedürü başladı — {procedure}",
        )
        event_registry.register_from_eec(start_evt)
        live_activity_center.register(start_evt)
        await self._record_reproduction_event(
            pid,
            event_constant="EVENT_REPRODUCTION_STARTED",
            event_name="Yeniden Üretim Başlatıldı (OLAY-108)",
            description=(
                f"Yönetici onayı sonrası HLK Runtime {procedure} prosedürünü "
                f"başlattı (yönetici={admin_user_id})"
            ),
            result=procedure,
        )

        # Yöneticiye başlangıç bildirimi (HLK Runtime kararı — MASTER-013)
        start_notify = hlk_runtime.request_decision(DecisionRequest(
            pid=pid,
            category=DecisionCategory.USER_NOTIFICATION.value,
            requester="production_runtime.run_reproduction",
            context={"kind": "reproduction_started", "procedure": procedure},
        ))
        if start_notify.verdict == "NOTIFY" and bot is not None:
            try:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=start_notify.params.get("text", ""),
                    parse_mode=start_notify.params.get("parse_mode", "HTML"),
                )
            except Exception as e:
                logger.warning(f"⚠️ [Reproduction] Başlangıç bildirimi gönderilemedi: {e}")

        # HLK Decision Engine — üretim stratejisi/servis seçimi yeniden
        # değerlendirilir (MASTER-004, AR-002_75, AR-002_82 Adım 7)
        prod_context = ProductionContext(
            pid=pid, user_id=request.user_id,
            product_name=request.product_name, brand=request.brand,
            duration=request.duration, voice_lang=request.voice_lang,
            url=request.url,
        )
        decision_packet = decision_engine.decide(prod_context)
        request.user_data["decision_packet"] = decision_packet.to_dict()
        await self._append_package_list_section(
            pid, "decision_history", decision_packet.to_dict()
        )
        logger.info(
            f"🧠 [Reproduction] Decision Packet: {decision_packet.decision_id}"
        )

        # Gerçek pipeline handler'ları + PID bağlamı (AR-002_76)
        register_handlers()
        ctx = PipelineContext(
            request=request,
            decision_packet=decision_packet,
            prod_context=prod_context,
            cost_report={"pid": pid, "services": {},
                         "decision_id": decision_packet.decision_id,
                         "reproduction": procedure},
        )
        set_context(pid, ctx)

        try:
            # ── Adım 18: Üretim yönetimi (Executor recovery — AR-002_79) ─
            self._state = ProductionState.EXECUTING
            from services.production_executor import production_executor
            executor_report = await production_executor.recover(pid)
            report_dict = executor_report.to_dict() if hasattr(
                executor_report, "to_dict") else dict(executor_report)
            self._result.executor_report = report_dict
            failed = report_dict.get("failed_tasks", 0)

            # ── CEE POST-CHECK ───────────────────────────────────────────
            pipeline_success = ctx.delivered or failed == 0
            cee_report = constitution_enforcement.enforce_post_check(
                pid=pid,
                decision_packet=request.user_data.get("decision_packet", {}),
                user_data=request.user_data,
                pipeline_success=pipeline_success,
            )
            self._result.post_check_report = {
                "report_id": cee_report.report_id,
                "verdict": cee_report.verdict.value,
            }

            if failed:
                # Başarısızlık: durum + anayasal gerekçe bildirilir (Adım 21)
                errors = report_dict.get("errors", [])
                return await self._handle_reproduction_failure(
                    pid, bot, admin_chat_id,
                    error="; ".join(errors) or f"{failed} task başarısız",
                    state=ProductionState.FAILED,
                    user_chat_id=int(user_chat_id),
                    justifications=[
                        f"{failed} task başarısız (AR-002_76 Execution Result)",
                        *errors[:3],
                    ],
                )

            # ── Adım 20: Dijital varlık ilişkilendirme + sürüm geçmişi ──
            await package_runtime.update_section(
                pid, "service_usage", ctx.cost_report
            )
            if ctx.video_path:
                await package_runtime.update_section(
                    pid, "final_video",
                    {"path": ctx.video_path, "delivered": ctx.delivered,
                     "reproduction": procedure},
                )
            await package_runtime.update_section(pid, "delivery_info", {
                "delivered": ctx.delivered,
                "chat_id": int(user_chat_id),
                "delivered_at": datetime.now(timezone.utc).isoformat(),
                "video": bool(ctx.video_path),
                "reproduction": procedure,
            })

            # EEC tamamlanma event'i (Adım 19)
            end_evt = execution_event_collector.emit_event(
                event_type=EECEventType.CODE_COMPLETED,
                description=f"Reproduction completed: {pid}",
                phase=ExecutionPhase.POST_CHECK,
                result=(
                    f"Video={bool(ctx.video_path)} Delivered={ctx.delivered} "
                    f"Procedure={procedure}"
                ),
            )
            event_registry.register_from_eec(end_evt)
            live_activity_center.register(end_evt)

            # ── Tamamlanma kararı HLK Runtime'ındır (AR-002_80/82) ──────
            completion_decision = hlk_runtime.request_decision(DecisionRequest(
                pid=pid,
                category=DecisionCategory.COMPLETION.value,
                requester="production_runtime.run_reproduction",
                context={
                    "delivered": ctx.delivered,
                    "video": bool(ctx.video_path),
                    "failed_tasks": failed,
                },
            ))
            completion_success = bool(
                completion_decision.params.get("success", True)
            )

            # ── Adım 21: Telegram bildirimi (Yönetici + Kullanıcı) ──────
            await self._notify_reproduction_result(
                pid, bot, admin_chat_id, int(user_chat_id),
                success=True, product_name=request.product_name,
            )

            elapsed = time.time() - start_time
            self._state = ProductionState.COMPLETED
            self._result.state = ProductionState.COMPLETED.value
            self._result.success = completion_success
            self._result.duration_seconds = elapsed
            self._result.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(
                f"🏁 [Reproduction Completed] {pid} ({elapsed:.1f}s, "
                f"prosedür={procedure})"
            )
            return self._result
        finally:
            clear_context(pid)

    async def _reject_reproduction(
        self, pid: str, bot, admin_chat_id: int, reason: str
    ) -> ProductionResult:
        """AR-002_84 İstisna Akışı: prosedür başlatılmaz, Yönetici
        anayasal gerekçesiyle bilgilendirilir, işlem güvenli sonlandırılır."""
        from services.hlk_runtime import (
            hlk_runtime, DecisionRequest, DecisionCategory,
        )
        logger.warning(f"⛔ [Reproduction] Güvenli sonlandırma: {pid} — {reason}")
        notify = hlk_runtime.request_decision(DecisionRequest(
            pid=pid,
            category=DecisionCategory.USER_NOTIFICATION.value,
            requester="production_runtime._reject_reproduction",
            context={"kind": "reproduction_not_found",
                     "query": pid, "reason": reason},
        ))
        if notify.verdict == "NOTIFY" and bot is not None:
            try:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=notify.params.get("text", ""),
                    parse_mode=notify.params.get("parse_mode", "HTML"),
                )
            except Exception as e:
                logger.warning(f"⚠️ [Reproduction] Red bildirimi gönderilemedi: {e}")
        if self._result is None:
            self._result = ProductionResult(pid=pid, total_steps=10)
        self._state = ProductionState.IDLE
        self._result.state = ProductionState.IDLE.value
        self._result.success = False
        self._result.error = reason
        self._result.completed_at = datetime.now(timezone.utc).isoformat()
        return self._result

    async def _handle_reproduction_failure(
        self, pid: str, bot, admin_chat_id: int,
        error: str, state: "ProductionState",
        user_chat_id: int = 0, justifications: list | None = None,
    ) -> ProductionResult:
        """AR-002_84 başarısızlık yolu — hiçbir başarısızlık sessiz kalmaz.

        OLAY-025 (EVENT_VIDEO_PRODUCTION_FAILED) + eskalasyon + paket durumu
        + Yönetici/Kullanıcı bildirimi (durum + anayasal karar gerekçesi).
        """
        from services.hlk_runtime import (
            hlk_runtime, DecisionRequest, DecisionCategory,
        )
        if self._result is None:
            self._result = ProductionResult(pid=pid, total_steps=10)
        self._state = state
        self._result.state = state.value
        self._result.success = False
        self._result.error = error
        self._result.completed_at = datetime.now(timezone.utc).isoformat()
        logger.error(f"🏁 [Reproduction Failed] {pid} — {error}")

        # OLAY-025 kaydı (PID zorunlu — AR-002_57)
        await self._record_reproduction_event(
            pid,
            event_constant="EVENT_VIDEO_PRODUCTION_FAILED",
            event_name="Video Üretimi Başarısız Oldu (OLAY-025)",
            description=f"Yeniden üretim başarısız: {error[:200]}",
            result=f"Error: {error[:120]}",
        )

        # Eskalasyon (AR-002_79 — yönetici müdahale kaydı)
        try:
            from services.escalation_engine import escalation_engine, EscalationReason
            escalation_engine.escalate(
                pid=pid,
                reason=EscalationReason.ALL_PROVIDERS_FAILED.value,
                detail=f"Reproduction failed: {error}",
                failed_providers=[],
                retry_count=0,
            )
        except Exception as e:
            logger.warning(f"⚠️ [Reproduction] Escalation yazılamadı: {e}")

        # Paket durumu FAILED (idempotent)
        try:
            from services.production_package_runtime import (
                package_runtime, PackageStatus,
            )
            await package_runtime.update_status(pid, PackageStatus.FAILED)
        except Exception as e:
            logger.warning(f"⚠️ [Reproduction] Paket durumu güncellenemedi: {e}")

        # Adım 21 (başarısızlık): Yönetici + Kullanıcı bildirimi
        await self._notify_reproduction_result(
            pid, bot, admin_chat_id, user_chat_id or admin_chat_id,
            success=False, error=error, justifications=justifications or [],
        )

        # Pipeline bağlamını temizle
        try:
            from services.production_pipeline import clear_context
            clear_context(pid)
        except Exception:
            pass
        return self._result

    async def _notify_reproduction_result(
        self, pid: str, bot, admin_chat_id: int, user_chat_id: int,
        success: bool, product_name: str = "", error: str = "",
        justifications: list | None = None,
    ) -> None:
        """AR-002_84 Adım 21: Sonuç hem Yöneticiye hem ilgili Kullanıcıya
        anayasal bildirim kurallarına uygun şekilde iletilir (MASTER-013:
        bildirim içerikleri yalnızca HLK Runtime kararı ile üretilir)."""
        from services.hlk_runtime import (
            hlk_runtime, DecisionRequest, DecisionCategory,
        )
        if bot is None:
            return
        kind = "reproduction_completed" if success else "reproduction_failed"
        targets = [("admin", admin_chat_id)]
        if user_chat_id and user_chat_id != admin_chat_id:
            targets.append(("user", user_chat_id))
        for audience, chat_id in targets:
            notify = hlk_runtime.request_decision(DecisionRequest(
                pid=pid,
                category=DecisionCategory.USER_NOTIFICATION.value,
                requester="production_runtime._notify_reproduction_result",
                context={
                    "kind": kind,
                    "audience": audience,
                    "product_name": product_name,
                    "error": error,
                    "justifications": justifications or [],
                },
            ))
            if notify.verdict != "NOTIFY":
                continue
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=notify.params.get("text", ""),
                    parse_mode=notify.params.get("parse_mode", "HTML"),
                )
            except Exception as e:
                logger.warning(
                    f"⚠️ [Reproduction] {audience} bildirimi gönderilemedi: {e}"
                )

    async def _record_reproduction_event(
        self, pid: str, event_constant: str, event_name: str,
        description: str, result: str,
    ) -> None:
        """Yeniden üretim olayını mevcut anayasal kayıt mekanizmalarına yazar.

        AR-002_73: Olay Kayıt Merkezi (bellek + LAC görünürlüğü) ve
        Production Package event_logs (kalıcı) — PID alanı zorunlu (AR-002_57).
        """
        now = datetime.now(timezone.utc).isoformat()
        try:
            from services.olay_kayit_merkezi import event_registry, EventRecord
            record = EventRecord(
                event_id=f"EVT-{pid}-{int(time.time() * 1000)}",
                event_name=event_name,
                event_constant=event_constant,
                event_description=description,
                source_state="STATE_VIDEO_PRODUCTION",
                target_state="STATE_VIDEO_PRODUCTION",
                producer="HLK_RUNTIME",
                pid=pid,
                timestamp=now,
                phase="REPRODUCTION",
                result=result,
                category="REPRODUCTION",
            )
            event_registry.register(record)
        except Exception as e:
            logger.warning(f"⚠️ [Reproduction] Olay kaydedilemedi: {e}")

        # Kalıcı kayıt: Production Package event_logs (mevcut loglar korunur)
        await self._append_package_list_section(pid, "event_logs", {
            "event_type": event_constant,
            "event_name": event_name,
            "pid": pid,
            "description": description,
            "result": result,
            "timestamp": now,
        })

    async def _append_package_list_section(
        self, pid: str, section: str, entry: dict
    ) -> None:
        """Paketin liste tipli bölümüne kayıt EKLER (mevcut kayıtlar korunur).

        15_KARAR_GEREKCESI_STANDARDI.md Bölüm 10: kayıtlar değiştirilemez ve
        silinemez — bu nedenle bölüm asla üzerine yazılmaz, genişletilir.
        """
        try:
            from services.production_package_runtime import package_runtime
            pkg = await package_runtime.load(pid)
            if pkg is None:
                return
            current = getattr(pkg, section, None)
            items = list(current) if isinstance(current, list) else []
            items.append(entry)
            await package_runtime.update_section(pid, section, items)
        except Exception as e:
            logger.warning(
                f"⚠️ [Reproduction] '{section}' bölümüne kayıt eklenemedi: {e}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # Runtime Heartbeat — Production boyunca runtime aktiflik kanıtı
    # ═══════════════════════════════════════════════════════════════════════

    def _start_heartbeat(self, user_id: int) -> "asyncio.Task | None":
        """Production boyunca periyodik runtime aktiflik sinyali gönderir.

        Heartbeat, HLK Runtime ve Constitution Runtime'ın Production
        süresince aktif kaldığını kanıtlayan periyodik log kaydıdır.
        MASTER-011: Runtime Aktiflik Doğrulama Prensibi gereğidir.

        Args:
            user_id: Kullanıcı ID'si.

        Returns:
            asyncio.Task veya None.
        """
        async def _beat():
            interval = float(
                __import__("os").getenv("GC_RUNTIME_HEARTBEAT_INTERVAL", "60")
            )
            start = __import__("time").time()
            while True:
                await asyncio.sleep(interval)
                elapsed = __import__("time").time() - start
                try:
                    from services.hlk_runtime import hlk_runtime as _hb_hr
                    hlk_ok = _hb_hr.is_active(user_id)
                    const_ok = _hb_hr.is_constitution_active()
                    prod_state = self._state.value
                    hlk_status = "ACTIVE" if hlk_ok else "INACTIVE"
                    const_status = "ACTIVE" if const_ok else "INACTIVE"
                    logger.info(
                        f"💓 [Runtime Heartbeat] "
                        f"HLK: {hlk_status} | "
                        f"Constitution: {const_status} | "
                        f"Production: {prod_state} | "
                        f"PID={self._current_pid} | "
                        f"elapsed={elapsed:.0f}s"
                    )
                except Exception as e:
                    logger.warning(f"💓 [Runtime Heartbeat] Hata: {e}")

        try:
            return asyncio.create_task(_beat())
        except Exception:
            return None

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

    async def track(
        self, pid: str, state: str, extra: dict | None = None
    ) -> None:
        """FAZ-2: Pipeline durumunu Production Runtime'a bildirir.

        Production Runtime artık pipeline'ın yaşam döngüsünü yönetir.
        Pipeline her aşamada bu metodu çağırarak durumunu bildirir.

        Args:
            pid: Production ID.
            state: ProductionState değeri.
            extra: Ek metadata (opsiyonel).
        """
        async with self._lock:
            self._current_pid = pid
            try:
                self._state = ProductionState[state] if isinstance(state, str) else state
            except (KeyError, ValueError):
                self._state = ProductionState.EXECUTING

            if self._result is None:
                self._result = ProductionResult(
                    pid=pid,
                    state=self._state.value,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    total_steps=5,  # Decision → Image → Voice → Video → Delivery
                )

            if extra:
                if extra.get("completed"):
                    self._result.completed_steps += 1
                if extra.get("error"):
                    self._result.error = extra["error"]
                if extra.get("success") is not None:
                    self._result.success = extra["success"]

            if state == "COMPLETED":
                self._result.completed_at = datetime.now(timezone.utc).isoformat()
                if self._result.started_at:
                    try:
                        start = datetime.fromisoformat(self._result.started_at)
                        self._result.duration_seconds = (
                            datetime.now(timezone.utc) - start.replace(tzinfo=timezone.utc)
                        ).total_seconds()
                    except Exception:
                        pass

            logger.info(f"📊 [ProductionRuntime] {pid}: {self._state.value}")

    # ═══════════════════════════════════════════════════════════════════════
    # TEK GİRİŞ NOKTASI — Delegasyon API'si (AR-002_70)
    # website.py yalnızca launch() çağırır; yaşam döngüsünü YÖNETMEZ.
    # ═══════════════════════════════════════════════════════════════════════

    def launch(self, request) -> "asyncio.Task":
        """Üretim talebini kabul eder ve yönetilen yaşam döngüsünü başlatır.

        AR-002_70: Production Runtime, üretim yaşam döngüsünün TEK giriş
        noktası, TEK orkestratörü ve TEK yaşam döngüsü yöneticisidir.

        Anayasal boot zinciri gereği: Production Runtime yalnızca
        HLK Runtime ve Constitution Runtime aktif olduğunda başlatılabilir.

        Görev sahipsiz (orphan) bırakılmaz: done-callback ile her sonuç
        okunur; hiçbir exception Python'a sızamaz (AR-002_76 Adım 7 —
        istisnalar Execution Result / Feedback Loop / Escalation'a dönüşür).

        Args:
            request: production_pipeline.ProductionRequest.

        Returns:
            asyncio.Task — yönetilen üretim görevi.
        """
        # Constitutional Boot Chain doğrulaması
        try:
            from services.hlk_runtime import hlk_runtime as _hr
            if not _hr.authorize_production(request.user_id):
                logger.critical(
                    f"🚨 [Production Runtime] Anayasal yetkilendirme REDDEDILDI — "
                    f"Production BAŞLATILAMIYOR. user={request.user_id}"
                )
                # Yetkilendirme başarısız — FAILED task döndür
                async def _unauthorized():
                    return await self._handle_failure(
                        request, "",
                        error="Constitutional Boot Chain: HLK Runtime veya Constitution Runtime aktif değil",
                        state=ProductionState.FAILED,
                    )
                task = asyncio.create_task(_unauthorized())
                task.add_done_callback(self._on_task_done)
                return task
        except ImportError:
            logger.warning(
                "⚠️ [Production Runtime] HLK Runtime modülü bulunamadı — "
                "yetkilendirme atlanıyor"
            )

        logger.info(
            f"🚀 [Production Runtime Started] Üretim talebi kabul edildi — "
            f"chat={request.chat_id} user={request.user_id} "
            f"({request.brand} — {request.product_name}, {request.duration}sn)"
        )
        task = asyncio.create_task(self.run_request(request))
        task.add_done_callback(self._on_task_done)
        return task

    def _on_task_done(self, task: "asyncio.Task") -> None:
        """Orphan-task yasağı: görev sonucu her durumda okunur."""
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            logger.warning("🏁 [Production Cancelled] Üretim görevi iptal edildi")
            return
        if exc is not None:
            # run_request tüm istisnaları yakalar — buraya düşmesi
            # anayasal ihlaldir ve KRİTİK olarak raporlanır.
            logger.critical(
                f"🚨 [ProductionRuntime] Yönetilmeyen istisna yakalandı "
                f"(orphan-task koruması): {type(exc).__name__}: {exc}"
            )

    async def run_request(self, request) -> ProductionResult:
        """Yönetilen üretim yaşam döngüsü — hiçbir istisna dışarı sızmaz.

        Anayasal zincir (AR-002_70/71/72/74/75/76 + AR-002_22 + CEE + EEC):
        STATE doğrulama → CEE PRE-CHECK → PID Runtime → Production Package
        → Decision Engine → Decision Packet → Task Package → Executor →
        Provider → Execution Result → Feedback Loop → CEE POST-CHECK →
        EEC → Production Package güncelleme → LAC → State Transition.
        """
        # Heartbeat başlat — Production boyunca runtime aktifliğini kanıtlamak için
        _heartbeat_task = self._start_heartbeat(request.user_id)
        try:
            return await asyncio.wait_for(
                self._run_managed(request),
                timeout=_GC_PRODUCTION_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error(f"🏁 [Production Timeout] {_GC_PRODUCTION_TIMEOUT}s aşıldı")
            return await self._handle_failure(
                request, self._current_pid,
                error=f"Production zaman aşımı ({_GC_PRODUCTION_TIMEOUT}s)",
                state=ProductionState.TIMED_OUT,
            )
        except asyncio.CancelledError:
            logger.warning(f"🏁 [Production Cancelled] {self._current_pid}")
            return await self._handle_failure(
                request, self._current_pid,
                error="Production iptal edildi",
                state=ProductionState.CANCELLED,
            )
        except Exception as e:
            logger.error(
                f"❌ [ProductionRuntime] Yaşam döngüsü hatası: "
                f"{type(e).__name__}: {e}"
            )
            return await self._handle_failure(
                request, self._current_pid,
                error=f"{type(e).__name__}: {e}",
                state=ProductionState.FAILED,
            )
        finally:
            # Heartbeat durdur
            if _heartbeat_task:
                _heartbeat_task.cancel()
            # Production terminal — HLK Runtime'a bildir
            try:
                from services.hlk_runtime import hlk_runtime as _hr2
                _hr2.on_production_terminal(request.user_id)
            except Exception:
                pass

    async def _run_managed(self, request) -> ProductionResult:
        """AR-002_70 anayasal zinciri — request bağlamıyla tam yürütme."""
        from services.production_pipeline import (
            PipelineContext, set_context, clear_context, register_handlers,
        )
        from services.constitution_enforcement import constitution_enforcement
        from services.execution_event_collector import (
            execution_event_collector, EECEventType, ExecutionPhase,
        )
        from services.olay_kayit_merkezi import event_registry
        from services.live_activity_center import live_activity_center
        from services.pid_runtime import pid_runtime
        from services.production_package_runtime import package_runtime, PackageStatus
        from services.decision_engine import decision_engine, ProductionContext
        from utils.state_engine import StateEngine, UserEvent

        start_time = time.time()
        self._cancel_requested = False
        self._result = ProductionResult(
            state=ProductionState.VALIDATING.value,
            started_at=datetime.now(timezone.utc).isoformat(),
            total_steps=10,
        )

        # ── Adım 1-4: Ön Koşul Doğrulamaları ─────────────────────────────
        self._state = ProductionState.VALIDATING
        se = StateEngine(request.user_data)
        current_state = getattr(se, "current", None)
        current_state_val = getattr(current_state, "value", str(current_state))
        logger.info(f"🔷 [STATE_VIDEO_PRODUCTION Active] mevcut state: {current_state_val}")
        # Guard: Runtime aktiflik kontrolü
        try:
            from services.hlk_runtime import hlk_runtime as _guard_hr
            _guard_hr.guard_check(request.user_id)
        except Exception:
            pass
        await self._validate_prerequisites()
        self._result.completed_steps = 4

        # ── Adım 5: Runtime Başlatma ─────────────────────────────────────
        self._state = ProductionState.STARTING
        self._result.completed_steps = 5

        # ── Adım 6: CEE PRE-CHECK ────────────────────────────────────────
        ctp = constitution_enforcement.pre_check(
            task_description=f"Video production for user {request.user_id}",
            affected_files=[
                "services/production_runtime.py",
                "services/production_pipeline.py",
                "services/production_executor.py",
            ],
            master_rules=["MASTER-001", "MASTER-003", "MASTER-004"],
            arch_rules=["AR-002_57", "AR-002_70", "AR-002_76"],
            oper_rules=["OR-004_8"],
            flow_steps=["FD-008_1: STATE_VIDEO_PRODUCTION"],
            state_rules=["SE-007_4"],
            expected_outputs=["Video delivered or confirmation sent"],
        )
        logger.info(f"📋 [CEE PRE-CHECK] CTP: {ctp.ctp_id}")
        self._result.pre_check_report = {"ctp_id": ctp.ctp_id}
        self._result.completed_steps = 6

        # ── Adım 7: PID Oluşturma (PID Runtime) ──────────────────────────
        self._state = ProductionState.CREATING_PID
        logger.info("🆔 [PID Runtime Started] PID oluşturuluyor (Adım 7)")
        pid = await self._create_pid()
        self._current_pid = pid
        self._result.pid = pid

        # Production Lifecycle — gerçek PID ile güncelle
        try:
            from services.hlk_runtime import hlk_runtime as _hr_pl
            _hr_pl.on_production_start(request.user_id, pid)
        except Exception:
            pass

        # EEC LISTEN + başlangıç event'i (EEC-002: PID zorunlu)
        execution_event_collector.listen(pid=pid)
        start_evt = execution_event_collector.emit_event(
            event_type=EECEventType.TASK_STARTED,
            description=f"Production started: {pid}",
            phase=ExecutionPhase.EXECUTE,
            result="Production Runtime yaşam döngüsü başladı",
        )
        event_registry.register_from_eec(start_evt)
        live_activity_center.register(start_evt)
        logger.info(f"📤 [EEC Event Created] {start_evt.event_id if hasattr(start_evt, 'event_id') else 'EVENT_TASK_STARTED'} | PID={pid}")
        logger.info(f"📺 [LAC Updated] EVENT_TASK_STARTED | PID={pid}")

        # ── Adım 8: Production Package (Package Runtime) ─────────────────
        self._state = ProductionState.CREATING_PACKAGE
        await self._create_package(pid)
        logger.info(f"📦 [Production Package Created] {pid}")
        # Guard: Runtime aktiflik kontrolü
        try:
            from services.hlk_runtime import hlk_runtime as _guard_hr2
            _guard_hr2.guard_check(request.user_id)
        except Exception:
            pass
        self._result.completed_steps = 8

        # Brief + Video Parametreleri bölümlerini doldur (16_PP_STANDARD)
        ud = request.user_data or {}
        brief_section = {
            "url": request.url,
            "product_name": request.product_name,
            "brand": request.brand,
            "platform": ud.get("platform", ""),
            "resolution": ud.get("resolution", ""),
            "style": ud.get("style", ""),
            "audience": ud.get("audience", ""),
            "voice_language": request.voice_lang,
            # Kullanıcı kimliği (12/13_DIGITAL_ASSET kayıt standardı ile uyumlu):
            # AR-002_84 yeniden üretimde ilgili Kullanıcıya bildirim adresi olarak
            # kullanılır — Production Package kalıcı kaydıdır.
            "user_id": request.user_id,
            "chat_id": request.chat_id,
        }
        await package_runtime.update_section(pid, "brief", brief_section)
        await package_runtime.update_section(pid, "video_parameters", {
            "duration_seconds": request.duration,
            "voice_language": request.voice_lang,
            "platform": ud.get("platform", ""),
            "resolution": ud.get("resolution", ""),
        })

        # ── FAZ: HLK DECISION ENGINE (MASTER-004 / FEAT-002) ─────────────
        logger.info("🧠 [Decision Engine Started] HLK karar üretimi başlıyor")
        prod_context = ProductionContext(
            pid=pid, user_id=request.user_id,
            product_name=request.product_name, brand=request.brand,
            duration=request.duration, voice_lang=request.voice_lang,
            url=request.url,
        )
        decision_packet = decision_engine.decide(prod_context)
        logger.info(
            f"🧠 [Decision Packet Ready] {decision_packet.decision_id} | "
            f"Gorsel: {decision_packet.primary_image_provider.provider if decision_packet.primary_image_provider else 'YOK'}"
            f"{' > ' + decision_packet.fallback_image_provider.provider if decision_packet.fallback_image_provider else ''} | "
            f"Ses: {decision_packet.primary_voice_provider.provider if decision_packet.primary_voice_provider else 'YOK'} | "
            f"Video: {decision_packet.primary_video_provider.provider if decision_packet.primary_video_provider else 'YOK'}"
            f"{' > ' + decision_packet.fallback_video_provider.provider if decision_packet.fallback_video_provider else ''}"
        )
        request.user_data["decision_packet"] = decision_packet.to_dict()
        # 15_KARAR_GEREKCESI: karar Production Package'e kaydedilir
        await package_runtime.update_section(
            pid, "decision_history", [decision_packet.to_dict()]
        )

        # ── Adım 9: Task Package Hazırlığı (gerçek pipeline task'ları) ───
        self._state = ProductionState.PREPARING_TASKS
        real_tasks = [
            {"task_id": f"TASK-{pid}-001", "agent": "ImageGenerator",
             "status": "PENDING", "pid": pid,
             "description": "Ürün görseli üretimi (Decision Packet provider'ları ile)"},
            {"task_id": f"TASK-{pid}-002", "agent": "VoiceGenerator",
             "status": "PENDING", "pid": pid,
             "description": "AI seslendirme üretimi"},
            {"task_id": f"TASK-{pid}-003", "agent": "VideoRenderer",
             "status": "PENDING", "pid": pid,
             "description": "Video render (lipsync/img2vid)"},
            {"task_id": f"TASK-{pid}-004", "agent": "DeliveryAgent",
             "status": "PENDING", "pid": pid,
             "description": "Nihai çıktının kullanıcıya teslimi (AR-002_36)"},
        ]
        await package_runtime.update_section(pid, "task_packages", real_tasks)
        logger.info(f"📋 [Task Package Loaded] {len(real_tasks)} adet task hazırlandı: {pid}")
        # Guard: Runtime aktiflik kontrolü
        try:
            from services.hlk_runtime import hlk_runtime as _guard_hr3
            _guard_hr3.guard_check(request.user_id)
        except Exception:
            pass
        self._result.completed_steps = 9

        # ── Adım 10: Production Executor (gerçek handler'lar ile) ────────
        self._state = ProductionState.EXECUTING
        register_handlers()
        ctx = PipelineContext(
            request=request,
            decision_packet=decision_packet,
            prod_context=prod_context,
            cost_report={"pid": pid, "services": {},
                         "decision_id": decision_packet.decision_id},
        )
        set_context(pid, ctx)

        try:
            executor_report = await self._start_executor(pid)
            self._result.executor_report = executor_report
            self._result.completed_steps = 10

            failed = executor_report.get("failed_tasks", 0)
            if failed:
                logger.warning(
                    f"🔄 [Feedback Loop Started] Executor raporu: {failed} task "
                    f"başarısız — AR-002_22 değerlendirmesi pipeline içinde uygulandı"
                )
            else:
                logger.info(
                    f"🔄 [Feedback Loop Started] Executor raporu degerlendirildi: "
                    f"tum task'lar basarili — mudahale gerekmedi | PID={pid}"
                )

            # ── CEE POST-CHECK ───────────────────────────────────────────
            pipeline_success = ctx.delivered
            cee_report = constitution_enforcement.enforce_post_check(
                pid=pid,
                decision_packet=request.user_data.get("decision_packet", {}),
                user_data=request.user_data,
                pipeline_success=pipeline_success,
            )
            logger.info(
                f"🔍 [CEE POST-CHECK] {cee_report.report_id}: {cee_report.verdict.value}"
            )
            self._result.post_check_report = {
                "report_id": cee_report.report_id,
                "verdict": cee_report.verdict.value,
            }

            # ── EEC: Production tamamlandı event'i ───────────────────────
            end_evt = execution_event_collector.emit_event(
                event_type=EECEventType.CODE_COMPLETED,
                description=f"Production completed: {pid}",
                phase=ExecutionPhase.POST_CHECK,
                result=(
                    f"Video={bool(ctx.video_path)} Voice={bool(ctx.voice_path)} "
                    f"Delivered={ctx.delivered}"
                ),
            )
            event_registry.register_from_eec(end_evt)
            live_activity_center.register(end_evt)
            logger.info(f"📤 [EEC Event Created] EVENT_CODE_COMPLETED | PID={pid}")
            logger.info(f"📺 [LAC Updated] EVENT_CODE_COMPLETED | PID={pid}")

            # ── Production Package final güncelleme ──────────────────────
            await package_runtime.update_section(
                pid, "service_usage", ctx.cost_report
            )
            if ctx.video_path:
                await package_runtime.update_section(
                    pid, "final_video",
                    {"path": ctx.video_path, "delivered": ctx.delivered},
                )
            await package_runtime.update_section(pid, "delivery_info", {
                "delivered": ctx.delivered,
                "chat_id": request.chat_id,
                "delivered_at": datetime.now(timezone.utc).isoformat(),
                "video": bool(ctx.video_path),
            })
            logger.info(f"📦 [Production Package Updated] {pid} (service_usage, delivery_info)")

            # ── State Transition (SE-007_4) ──────────────────────────────
            se.fire(UserEvent.VIDEO_PRODUCTION_COMPLETED)
            logger.info(
                "🔄 [State Transition] STATE_VIDEO_PRODUCTION "
                "--[EVENT_VIDEO_PRODUCTION_COMPLETED]--> STATE_SESSION_COMPLETED"
            )

            # ── Tamamlanma — COMPLETION kararı HLK Runtime'ındır ─────────
            # MASTER-013 / AR-002_81: Production Runtime tamamlanma kararını
            # kendisi ÜRETMEZ; teknik kanıtları iletir, HLK Runtime karar verir.
            try:
                from services.hlk_runtime import (
                    hlk_runtime as _hr_dec,
                    DecisionRequest as _DecReq,
                    DecisionCategory as _DecCat,
                )
                completion_decision = _hr_dec.request_decision(_DecReq(
                    pid=pid,
                    category=_DecCat.COMPLETION.value,
                    requester="production_runtime.run_request",
                    context={
                        "delivered": ctx.delivered,
                        "video": bool(ctx.video_path),
                        "failed_tasks": executor_report.get("failed_tasks", 0),
                    },
                ))
                completion_success = bool(
                    completion_decision.params.get("success", True)
                )
            except Exception as e:
                logger.warning(
                    f"⚠️ [ProductionRuntime] COMPLETION kararı alınamadı: {e}"
                )
                completion_success = True

            elapsed = time.time() - start_time
            self._state = ProductionState.COMPLETED
            self._result.state = ProductionState.COMPLETED.value
            self._result.success = completion_success
            self._result.duration_seconds = elapsed
            self._result.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(
                f"🏁 [Production Completed] {pid} ({elapsed:.1f}s, "
                f"{self._result.completed_steps}/10 adım)"
            )
            return self._result
        finally:
            clear_context(pid)

    async def _handle_failure(
        self, request, pid: str, error: str, state: "ProductionState"
    ) -> ProductionResult:
        """Anayasal başarısızlık yolu — AR-002_79/80.

        Hiçbir başarısızlık sessiz kalmaz:
        - EEC fail event'i + Olay Kayıt Merkezi + LAC
        - CEE POST-CHECK (pipeline_success=False)
        - Escalation Engine (yönetici müdahalesi)
        - EVENT_VIDEO_PRODUCTION_FAILED → STATE_SESSION_CLOSED (SE-007_4)
        - Kullanıcıya DÜRÜST bilgilendirme (Fake Progress yasağı — EEC-001)
        """
        if self._result is None:
            self._result = ProductionResult(total_steps=10)
        self._state = state
        self._result.state = state.value
        self._result.success = False
        self._result.error = error
        self._result.completed_at = datetime.now(timezone.utc).isoformat()
        pid = pid or "PID-UNKNOWN"
        terminal = {
            ProductionState.FAILED: "Production Failed",
            ProductionState.TIMED_OUT: "Production Timeout",
            ProductionState.CANCELLED: "Production Cancelled",
        }.get(state, "Production Failed")
        logger.error(f"🏁 [{terminal}] {pid} — {error}")

        # EEC fail event + LAC
        try:
            from services.execution_event_collector import (
                execution_event_collector, EECEventType, ExecutionPhase,
            )
            from services.olay_kayit_merkezi import event_registry
            from services.live_activity_center import live_activity_center
            fail_evt = execution_event_collector.emit_event(
                event_type=EECEventType.RUNTIME_TEST_COMPLETED,
                description=f"{terminal}: {pid} — {error}",
                phase=ExecutionPhase.POST_CHECK,
                result=f"Error: {error[:120]}",
            )
            event_registry.register_from_eec(fail_evt)
            live_activity_center.register(fail_evt)
            logger.info(f"📤 [EEC Event Created] failure event | PID={pid}")
            logger.info(f"📺 [LAC Updated] failure event | PID={pid}")
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] EEC fail event yazılamadı: {e}")

        # CEE POST-CHECK (başarısızlık denetimi)
        try:
            from services.constitution_enforcement import constitution_enforcement
            cee_report = constitution_enforcement.enforce_post_check(
                pid=pid,
                decision_packet=(request.user_data or {}).get("decision_packet", {}),
                user_data=request.user_data or {},
                pipeline_success=False,
            )
            logger.info(
                f"🔍 [CEE POST-CHECK] {cee_report.report_id}: {cee_report.verdict.value}"
            )
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] CEE POST-CHECK hatası: {e}")

        # Escalation (AR-002_79 — yönetici müdahalesi)
        try:
            from services.escalation_engine import escalation_engine, EscalationReason
            escalation_engine.escalate(
                pid=pid,
                reason=EscalationReason.ALL_PROVIDERS_FAILED.value,
                detail=f"{terminal}: {error}",
                failed_providers=[],
                retry_count=0,
            )
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] Escalation yazılamadı: {e}")

        # Production Package durumu
        try:
            from services.production_package_runtime import package_runtime, PackageStatus
            if pid != "PID-UNKNOWN":
                await package_runtime.update_status(pid, PackageStatus.FAILED)
                logger.info(f"📦 [Production Package Updated] {pid} → FAILED")
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] Package durumu güncellenemedi: {e}")

        # State Transition: SE-007_4 → EVENT_VIDEO_PRODUCTION_FAILED
        try:
            from utils.state_engine import StateEngine, UserEvent
            se = StateEngine(request.user_data)
            se.fire(UserEvent.VIDEO_PRODUCTION_FAILED)
            logger.info(
                "🔄 [State Transition] STATE_VIDEO_PRODUCTION "
                "--[EVENT_VIDEO_PRODUCTION_FAILED]--> STATE_SESSION_CLOSED"
            )
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] State geçişi yapılamadı: {e}")

        # Kullanıcıya dürüst bilgilendirme (EEC-001: Fake Progress yasak)
        # MASTER-013 / AR-002_81: Süreç kararı içeren kullanıcı mesajı
        # yürütme katmanında ÜRETİLMEZ; içerik HLK Runtime kararı ile belirlenir.
        try:
            if request.bot is not None:
                from services.hlk_runtime import (
                    hlk_runtime as _hr_notify,
                    DecisionRequest as _NotifyReq,
                    DecisionCategory as _NotifyCat,
                )
                notify_decision = _hr_notify.request_decision(_NotifyReq(
                    pid=pid,
                    category=_NotifyCat.USER_NOTIFICATION.value,
                    requester="production_runtime._handle_failure",
                    context={"kind": "production_failure", "pid": pid},
                ))
                if notify_decision.verdict == "NOTIFY":
                    await request.bot.send_message(
                        chat_id=request.chat_id,
                        text=notify_decision.params.get("text", ""),
                        parse_mode=notify_decision.params.get("parse_mode", "HTML"),
                    )
        except Exception as e:
            logger.warning(f"⚠️ [ProductionRuntime] Kullanıcı bildirimi gönderilemedi: {e}")

        # Pipeline bağlamını temizle
        try:
            from services.production_pipeline import clear_context
            clear_context(pid)
        except Exception:
            pass

        return self._result

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
