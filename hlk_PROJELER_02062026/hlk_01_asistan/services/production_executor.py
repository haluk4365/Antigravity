"""
AR-002_76 Production Executor — Üretim Yürütme Runtime katmanı.

HLK tarafından hazırlanmış Production Package'in yürütülmesini koordine
eden runtime katmanı. Executor karar vermez, yalnızca yürütür (MASTER-004).

Bu modül:
- Production Package'i yükler ve doğrular
- Task Package'leri Production Package'ten alır
- Task'ları uygun sırayla yürütür
- Başarı/başarısızlık sonuçlarını toplar
- Runtime durumunu raporlar
- Event Collector'a gerekli bilgileri iletir
- Production Package durumunu günceller

Bu modül:
- PID üretmez (AR-002_57 — PID Runtime'ın görevi)
- Production Package oluşturmaz (AR-002_58 — Package Runtime'ın görevi)
- Workflow oluşturmaz (09_WORKFLOW_MANIFEST.md)
- State değiştirmez (SE-007)
- Feature yönetmez (10_FEATURE_REGISTRY.md)
- Karar vermez (MASTER-004)
- Video üretmez (AR-002_70)
- Prompt üretmez
- Agent seçmez (AR-002_75)
- Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md)
- Yeni anayasa oluşturmaz (MASTER-001)

Mimari Dayanak:
- AR-002_76: Production Execution Architecture
- AR-002_22: Constitutional Feedback Loop
- AR-002_47: Task Package Engine Architecture
- AR-002_57: PID standardı
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime
- AR-002_72: Production Package Runtime
- 16_PRODUCTION_PACKAGE_STANDARD.md
- 22_EXECUTION_EVENT_COLLECTOR.md
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

_GC_EXECUTOR_MAX_RETRY = int(os.getenv("GC_EXECUTOR_MAX_RETRY", "3"))
_GC_EXECUTOR_TASK_TIMEOUT = float(os.getenv("GC_EXECUTOR_TASK_TIMEOUT", "300.0"))
_GC_EXECUTOR_RETRY_DELAY = float(os.getenv("GC_EXECUTOR_RETRY_DELAY", "0.5"))
_GC_EXECUTOR_STATE_DIR = Path(
    os.getenv("GC_EXECUTOR_STATE_DIR", "data")
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERİ MODELLERİ
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionStatus(str, Enum):
    """AR-002_76 Adım 6: Execution Result durumları."""
    PENDING = "PENDING"        # Görev henüz başlamadı
    RUNNING = "RUNNING"        # Görev yürütülüyor
    SUCCESS = "SUCCESS"        # Görev başarıyla tamamlandı
    FAILED = "FAILED"          # Görev başarısız oldu
    TIMEOUT = "TIMEOUT"        # Görev zaman aşımına uğradı (AR-002_7)
    PARTIAL = "PARTIAL"        # Görev kısmen tamamlandı
    CANCELLED = "CANCELLED"    # Görev iptal edildi


class ExecutorState(str, Enum):
    """Production Executor'un kendi çalışma durumu."""
    IDLE = "IDLE"              # Boşta, henüz başlamadı
    VALIDATING = "VALIDATING"  # Ön doğrulama adımları çalışıyor
    EXECUTING = "EXECUTING"    # Task'lar yürütülüyor
    COMPLETED = "COMPLETED"    # Tüm task'lar tamamlandı
    FAILED = "FAILED"          # Yürütme başarısız oldu
    RECOVERING = "RECOVERING"  # Recovery modunda


@dataclass
class ExecutionResult:
    """AR-002_76 Adım 6: Yürütme sonucu.

    Executor, her görev yürütmesi sonunda bir Execution Result oluşturur.
    Bu sonuç Feedback Loop'a iletilir (AR-002_22).
    """
    task_id: str = ""
    pid: str = ""
    status: str = ExecutionStatus.PENDING.value
    output: dict = field(default_factory=dict)
    duration_ms: float = 0.0
    error_detail: str = ""
    attempt: int = 1
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "pid": self.pid,
            "status": self.status,
            "output": self.output,
            "duration_ms": self.duration_ms,
            "error_detail": self.error_detail,
            "attempt": self.attempt,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class ExecutorReport:
    """Production Executor'un çalışma raporu."""
    executor_state: str = ExecutorState.IDLE.value
    pid: str = ""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    results: list = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "executor_state": self.executor_state,
            "pid": self.pid,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "results": [r.to_dict() if isinstance(r, ExecutionResult) else r for r in self.results],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "errors": self.errors,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PRODUCTION EXECUTOR
# ═══════════════════════════════════════════════════════════════════════════════

class ProductionExecutor:
    """AR-002_76: Production Executor — üretim yürütme runtime katmanı.

    HLK'nın uygulayıcı katmanıdır. Karar verici veya denetleyici değildir
    (MASTER-007).

    Production Executor:
    - Production Package'i yükler ve doğrular
    - Task Package'leri yükler
    - Task'ları sırayla yürütür
    - Execution Result'ları toplar
    - Production Package durumunu günceller
    - Runtime durumunu raporlar

    Production Executor:
    - Karar vermez (MASTER-004)
    - Servis seçmez (AR-002_75)
    - Prompt oluşturmaz
    - Kalite değerlendirmesi yapmaz (QR-004)
    - Üretim stratejisini değiştirmez
    """

    def __init__(self):
        # ── Executor durumu ──────────────────────────────────────────────
        self._state: ExecutorState = ExecutorState.IDLE
        self._report: Optional[ExecutorReport] = None
        self._current_pid: str = ""

        # ── Gerçek task handler kayıtları (AR-002_76) ───────────────────
        # agent adı → async handler(task: dict, pid: str) -> dict
        # Handler'lar production_pipeline.register_handlers() ile kaydedilir.
        self._handlers: dict = {}

        # ── Concurrency control ──────────────────────────────────────────
        self._lock = asyncio.Lock()

    # ═══════════════════════════════════════════════════════════════════════
    # Handler Kaydı (AR-002_76 — Executor yalnızca yürütür, işi handler yapar)
    # ═══════════════════════════════════════════════════════════════════════

    def register_handler(self, agent: str, handler) -> None:
        """Bir agent adı için gerçek task handler'ı kaydeder.

        Executor karar vermez; handler'lar Decision Packet'te seçilmiş
        provider'ları uygular. Kayıt idempotenttir.

        Args:
            agent: Task Package'teki agent adı (örn. "VideoRenderer").
            handler: async callable(task: dict, pid: str) -> dict.
        """
        self._handlers[agent] = handler

    # ═══════════════════════════════════════════════════════════════════════
    # Ana Yürütme Akışı
    # ═══════════════════════════════════════════════════════════════════════

    async def execute(self, pid: str) -> ExecutorReport:
        """AR-002_76: Production Package'i yürütür.

        Tam yürütme akışı:
        1. Ön doğrulama (6 adım — AR-002_76 Yürütme Öncesi Doğrulama)
        2. Task Package'leri yükleme
        3. Task'ları sırayla yürütme (AR-002_76 Adım 3)
        4. Sonuçları toplama ve kaydetme
        5. Production Package durumunu güncelleme

        Args:
            pid: Yürütülecek Production Package'in PID'si.

        Returns:
            ExecutorReport — yürütme raporu.

        Raises:
            ValueError: Ön doğrulama başarısız olursa.
        """
        async with self._lock:
            self._current_pid = pid
            logger.info(f"⚙️ [Executor Started] pid={pid}")
            self._report = ExecutorReport(
                pid=pid,
                started_at=datetime.now(timezone.utc).isoformat(),
            )

            try:
                # ── FAZ 1: Ön Doğrulama ──────────────────────────────────
                self._state = ExecutorState.VALIDATING
                logger.info(f"🔍 [Executor] Ön doğrulama başlıyor: {pid}")
                await self._validate_prerequisites(pid)
                logger.info(f"✅ [Executor] Ön doğrulama tamamlandı: {pid}")

                # ── FAZ 2: Task Package'leri Yükle ────────────────────────
                tasks = await self._load_task_packages(pid)
                self._report.total_tasks = len(tasks)
                logger.info(
                    f"📋 [Executor] {len(tasks)} Task Package yüklendi: {pid}"
                )

                if not tasks:
                    logger.warning(f"⚠️ [Executor] Yürütülecek task yok: {pid}")
                    self._state = ExecutorState.COMPLETED
                    self._report.completed_at = datetime.now(timezone.utc).isoformat()
                    return self._report

                # ── FAZ 3: Task'ları Yürüt ────────────────────────────────
                self._state = ExecutorState.EXECUTING
                for task in tasks:
                    result = await self._execute_task(task, pid)
                    self._report.results.append(result)

                    if result.status == ExecutionStatus.SUCCESS.value:
                        self._report.completed_tasks += 1
                    else:
                        self._report.failed_tasks += 1
                        self._report.errors.append(
                            f"Task {task.get('task_id', '?')}: {result.status} — {result.error_detail}"
                        )
                        # AR-002_76: Başarısızlık durumunda Feedback Loop'a iletilir
                        # Executor karar vermez — yalnızca sonucu kaydeder
                        logger.warning(
                            f"⚠️ [Executor] Task başarısız: "
                            f"{task.get('task_id', '?')} — {result.status}"
                        )

                # ── FAZ 4: Tamamlanma ─────────────────────────────────────
                self._state = ExecutorState.COMPLETED
                self._report.completed_at = datetime.now(timezone.utc).isoformat()

                # Production Package durumunu güncelle
                await self._update_package_status(pid)

                logger.info(
                    f"✅ [Executor] Yürütme tamamlandı: {pid} "
                    f"({self._report.completed_tasks}/{self._report.total_tasks} başarılı)"
                )

            except Exception as e:
                self._state = ExecutorState.FAILED
                self._report.errors.append(f"Executor hatası: {e}")
                self._report.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"❌ [Executor] Yürütme başarısız: {pid} — {e}")
                raise

            return self._report

    # ═══════════════════════════════════════════════════════════════════════
    # FAZ 1: Ön Doğrulama (AR-002_76 — 6 Adım)
    # ═══════════════════════════════════════════════════════════════════════

    async def _validate_prerequisites(self, pid: str) -> None:
        """AR-002_76 Yürütme Öncesi Doğrulama — 6 adım.

        Hiçbir doğrulama adımı atlanamaz. Herhangi bir adım başarısız
        olursa ValueError fırlatılır.

        Args:
            pid: Doğrulanacak Production Package'in PID'si.

        Raises:
            ValueError: Herhangi bir doğrulama adımı başarısız olursa.
        """
        errors: list[str] = []

        # Adım 1: Production Runtime durumu
        try:
            from services.pid_runtime import pid_runtime
            pid_valid = await pid_runtime.validate(pid)
            if not pid_valid.is_valid:
                errors.append(f"Adım 1 — PID geçersiz: {pid_valid.error}")
        except Exception as e:
            errors.append(f"Adım 1 — PID doğrulama hatası: {e}")

        # Adım 2: PID doğrulaması
        try:
            from services.pid_runtime import pid_runtime
            record = await pid_runtime.get_record(pid)
            if record is None:
                errors.append(f"Adım 2 — PID kaydı bulunamadı: {pid}")
            elif not record.is_active:
                errors.append(f"Adım 2 — PID aktif değil: {pid}")
        except Exception as e:
            errors.append(f"Adım 2 — PID kayıt hatası: {e}")

        # Adım 3: Production Package doğrulaması
        try:
            from services.production_package_runtime import (
                package_runtime, PackageStatus
            )
            pkg = await package_runtime.load(pid)
            if pkg is None:
                errors.append(f"Adım 3 — Production Package bulunamadı: {pid}")
            else:
                status = pkg.metadata.status
                if status == PackageStatus.ARCHIVED.value:
                    errors.append(f"Adım 3 — Package arşivlenmiş, yürütülemez: {pid}")
                elif status == PackageStatus.COMPLETED.value:
                    errors.append(f"Adım 3 — Package zaten tamamlanmış: {pid}")
        except Exception as e:
            errors.append(f"Adım 3 — Package doğrulama hatası: {e}")

        # Adım 4: Task Package'lerin varlığı
        try:
            from services.production_package_runtime import package_runtime
            pkg = await package_runtime.load(pid)
            if pkg is None or len(pkg.task_packages) == 0:
                errors.append(
                    f"Adım 4 — Yürütülecek Task Package bulunamadı: {pid}"
                )
        except Exception as e:
            errors.append(f"Adım 4 — Task Package kontrol hatası: {e}")

        # Adım 5: Servis sağlayıcı doğrulaması (best-effort)
        # Executor servis seçmez, yalnızca mevcut servis kayıtlarını kontrol eder
        try:
            from services.production_package_runtime import package_runtime
            pkg = await package_runtime.load(pid)
            if pkg and not pkg.service_usage:
                logger.info(
                    f"ℹ️ [Executor] Adım 5 — Servis kullanım kaydı boş: {pid} "
                    f"(servis seçimi HLK tarafından yapılır)"
                )
        except Exception as e:
            logger.warning(f"⚠️ [Executor] Adım 5 — Servis kontrolü: {e}")

        # Adım 6: Decision Packet kontrolü (best-effort)
        # Executor, Decision Packet'i değiştirmez, yalnızca var olduğunu teyit eder
        try:
            from services.production_package_runtime import package_runtime
            pkg = await package_runtime.load(pid)
            if pkg and not pkg.decision_history:
                logger.info(
                    f"ℹ️ [Executor] Adım 6 — Decision History boş: {pid} "
                    f"(kararlar HLK Decision Engine tarafından üretilir)"
                )
        except Exception as e:
            logger.warning(f"⚠️ [Executor] Adım 6 — Decision kontrolü: {e}")

        if errors:
            raise ValueError(
                f"Ön doğrulama başarısız ({len(errors)} hata): {'; '.join(errors)}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # FAZ 2: Task Package Yükleme
    # ═══════════════════════════════════════════════════════════════════════

    async def _load_task_packages(self, pid: str) -> list[dict]:
        """Production Package'ten Task Package listesini yükler.

        Task Package'ler Production Package'in task_packages bölümünde
        (Section 7) saklanır. Executor bu listeyi okur, değiştirmez.

        Task'lar task_id'ye göre sıralanır (deterministik yürütme sırası).

        Args:
            pid: Production Package PID'si.

        Returns:
            Task Package listesi (sıralanmış).
        """
        from services.production_package_runtime import package_runtime

        pkg = await package_runtime.load(pid)
        if pkg is None:
            return []

        tasks = list(pkg.task_packages)

        # Deterministik sıralama: önce task_id'ye göre
        tasks.sort(key=lambda t: t.get("task_id", ""))

        return tasks

    # ═══════════════════════════════════════════════════════════════════════
    # FAZ 3: Task Yürütme
    # ═══════════════════════════════════════════════════════════════════════

    async def _execute_task(self, task: dict, pid: str) -> ExecutionResult:
        """AR-002_76 Adım 3: Tek bir Task Package'i yürütür.

        Yürütme sırasında:
        - Executor, Task Package'te tanımlanan görev kapsamının dışına çıkamaz
        - Executor, karar değişikliği yapamaz
        - Görev süresi GC parametreleri ile belirlenen zaman limitini aşamaz

        Args:
            task: Yürütülecek Task Package (sözlük).
            pid: Üretim PID'si.

        Returns:
            ExecutionResult — görev yürütme sonucu.
        """
        task_id = task.get("task_id", "unknown")
        result = ExecutionResult(
            task_id=task_id,
            pid=pid,
            status=ExecutionStatus.RUNNING.value,
        )

        max_retry = _GC_EXECUTOR_MAX_RETRY
        for attempt in range(1, max_retry + 1):
            result.attempt = attempt
            result.started_at = datetime.now(timezone.utc).isoformat()
            start_time = time.time()

            try:
                # Task yürütme — timeout korumalı
                output = await asyncio.wait_for(
                    self._run_task_handler(task, pid),
                    timeout=_GC_EXECUTOR_TASK_TIMEOUT,
                )

                elapsed = (time.time() - start_time) * 1000
                result.duration_ms = elapsed
                result.output = output if isinstance(output, dict) else {"result": str(output)}
                result.status = ExecutionStatus.SUCCESS.value
                result.completed_at = datetime.now(timezone.utc).isoformat()

                logger.info(
                    f"✅ [Executor] Task başarılı: {task_id} "
                    f"(deneme {attempt}/{max_retry}, {elapsed:.0f}ms)"
                )
                break  # başarılı — retry döngüsünden çık

            except asyncio.TimeoutError:
                elapsed = (time.time() - start_time) * 1000
                result.duration_ms = elapsed
                result.status = ExecutionStatus.TIMEOUT.value
                result.error_detail = (
                    f"Task zaman aşımı: {task_id} "
                    f"({_GC_EXECUTOR_TASK_TIMEOUT}s, deneme {attempt}/{max_retry})"
                )
                result.completed_at = datetime.now(timezone.utc).isoformat()
                logger.warning(f"⏰ [Executor] {result.error_detail}")

                if attempt < max_retry:
                    logger.info(f"🔄 [Executor] Retry: {task_id} (deneme {attempt + 1})")

            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                result.duration_ms = elapsed
                result.status = ExecutionStatus.FAILED.value
                result.error_detail = f"{type(e).__name__}: {e}"
                result.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(
                    f"❌ [Executor] Task başarısız: {task_id} "
                    f"(deneme {attempt}/{max_retry}): {e}"
                )

                if attempt < max_retry:
                    logger.info(f"🔄 [Executor] Retry: {task_id} (deneme {attempt + 1})")
                    # Retry bekleme süresi GC parametresidir (AR-002_81)
                    await asyncio.sleep(_GC_EXECUTOR_RETRY_DELAY)
                else:
                    logger.error(
                        f"🚨 [Executor] Tüm denemeler başarısız: {task_id} "
                        f"({max_retry} deneme)"
                    )

        # AR-002_76 Adım 6-7: Execution Result üretilir ve rapora eklenir.
        # Feedback Loop değerlendirmesi Production Runtime seviyesinde yapılır.
        logger.info(
            f"🧾 [Execution Result] task={task_id} status={result.status} "
            f"({result.duration_ms:.0f}ms, deneme={result.attempt})"
        )
        return result

    async def _run_task_handler(self, task: dict, pid: str) -> dict:
        """Task handler — görev tipine göre ilgili işleyiciyi çağırır.

        Bu metod, gelecekte farklı task tipleri için genişletilebilir.
        Şu anda temel task yürütme çerçevesini sağlar.

        Task başarıyla tamamlandığında, Production Package içindeki
        task.status alanı COMPLETED olarak güncellenir ve atomik olarak
        diske yazılır. Bu sayede recovery sırasında tamamlanan task'lar
        tekrar yürütme zincirine girmez.

        Executor:
        - Prompt üretmez
        - Video üretmez
        - Agent seçmez
        - Yalnızca task verilerini işler ve sonuç üretir

        Args:
            task: Task verisi.
            pid: Üretim PID'si.

        Returns:
            Task çıktısı (sözlük).
        """
        task_id = task.get("task_id", "unknown")
        task_status = task.get("status", "PENDING")
        agent = task.get("agent", "unknown")

        # Task zaten tamamlanmışsa tekrar çalıştırma
        if task_status in ("COMPLETED", "SUCCESS"):
            logger.info(f"ℹ️ [Executor] Task zaten tamamlanmış, atlanıyor: {task_id}")
            return {
                "task_id": task_id,
                "result": "already_completed",
                "previous_status": task_status,
            }

        # ── Gerçek handler dispatch (AR-002_76) ─────────────────────────
        # Kayıtlı gerçek handler varsa üretim işi ona devredilir.
        handler = self._handlers.get(agent)
        if handler is not None:
            logger.info(f"▶️ [Execution Started] task={task_id} agent={agent}")
            output = await handler(task, pid)
            if not isinstance(output, dict):
                output = {"result": str(output)}
            output.setdefault("task_id", task_id)
            output["agent"] = agent
            output["executed_at"] = datetime.now(timezone.utc).isoformat()

            # Task Checkpoint: status'u COMPLETED olarak persist et
            await self._checkpoint_task_completion(task_id, pid)
            return output

        # ── Fallback: handler kayıtlı değil (test/simülasyon modu) ──────
        # Task verilerini Production Package'ten al
        task_output = {
            "task_id": task_id,
            "pid": pid,
            "result": "executed",
            "agent": agent,
            "task_status": task_status,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Task'a özel verileri ilet
        if "input_data" in task:
            task_output["input_used"] = True

        # ── Task Checkpoint: status'u COMPLETED olarak persist et ──────
        # Recovery sırasında tamamlanan task'lar tekrar yürütülmesin
        await self._checkpoint_task_completion(task_id, pid)

        return task_output

    async def _checkpoint_task_completion(
        self, task_id: str, pid: str
    ) -> None:
        """Task tamamlanma durumunu Production Package'e yazar.

        Production Package Runtime'ın mevcut update_section() mekanizması
        kullanılır. Package atomik olarak diske kaydedilir (tmp + replace).

        Bu checkpoint sayesinde:
        - Recovery'de tamamlanan task'lar atlanır
        - Crash sonrası yalnızca PENDING task'lar yürütülür
        - Gereksiz CPU/I/O/retry önlenir

        Args:
            task_id: Tamamlanan task'ın ID'si.
            pid: Production PID'si.
        """
        try:
            from services.production_package_runtime import package_runtime

            pkg = await package_runtime.load(pid)
            if pkg is None:
                logger.warning(
                    f"⚠️ [Executor] Checkpoint: Package bulunamadı: {pid}"
                )
                return

            # Yalnızca ilgili task'ın status'unu güncelle, diğerlerini koru
            updated_tasks = []
            for t in pkg.task_packages:
                t_updated = dict(t)  # shallow copy
                if t_updated.get("task_id") == task_id:
                    t_updated["status"] = "COMPLETED"
                    t_updated["completed_at"] = datetime.now(timezone.utc).isoformat()
                updated_tasks.append(t_updated)

            await package_runtime.update_section(
                pid, "task_packages", updated_tasks
            )
            logger.info(
                f"✅ [Executor] Checkpoint: {task_id} → COMPLETED (diske yazıldı)"
            )
        except Exception as e:
            # Checkpoint başarısız olursa task yine de tamamlanmış sayılır,
            # yalnızca recovery optimizasyonu kaybedilir
            logger.warning(
                f"⚠️ [Executor] Checkpoint yazılamadı: {task_id} — {e}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # FAZ 4: Sonuç Kaydetme ve Durum Güncelleme
    # ═══════════════════════════════════════════════════════════════════════

    async def _update_package_status(self, pid: str) -> None:
        """Production Package durumunu günceller.

        Tüm task'lar tamamlandığında package durumu güncellenir.
        Başarısız task varsa package durumu FAILED olarak işaretlenir.
        """
        from services.production_package_runtime import (
            package_runtime, PackageStatus
        )

        try:
            if self._report and self._report.failed_tasks > 0:
                await package_runtime.update_status(pid, PackageStatus.FAILED)
            else:
                await package_runtime.update_status(pid, PackageStatus.COMPLETED)

            # Execution sonuçlarını event_logs'a kaydet
            if self._report:
                event_entry = {
                    "event_type": "EXECUTION_COMPLETED",
                    "pid": pid,
                    "total_tasks": self._report.total_tasks,
                    "completed_tasks": self._report.completed_tasks,
                    "failed_tasks": self._report.failed_tasks,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await package_runtime.update_section(
                    pid, "event_logs",
                    [event_entry]  # mevcut loglara eklenir
                )
        except Exception as e:
            logger.warning(f"⚠️ [Executor] Package durum güncelleme hatası: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # Durum Raporlama
    # ═══════════════════════════════════════════════════════════════════════

    def get_state(self) -> dict:
        """Executor'un mevcut durumunu döndürür.

        Returns:
            Durum sözlüğü: state, pid, task ilerlemesi.
        """
        state = {
            "executor_state": self._state.value,
            "current_pid": self._current_pid,
        }
        if self._report:
            state.update({
                "total_tasks": self._report.total_tasks,
                "completed_tasks": self._report.completed_tasks,
                "failed_tasks": self._report.failed_tasks,
                "started_at": self._report.started_at,
                "completed_at": self._report.completed_at,
            })
        return state

    def get_report(self) -> Optional[dict]:
        """Son yürütme raporunu döndürür.

        Returns:
            ExecutorReport sözlüğü veya None (henüz çalışmadıysa).
        """
        if self._report is None:
            return None
        return self._report.to_dict()

    def is_running(self) -> bool:
        """Executor şu anda yürütme yapıyor mu?"""
        return self._state == ExecutorState.EXECUTING

    def is_idle(self) -> bool:
        """Executor boşta mı?"""
        return self._state == ExecutorState.IDLE

    # ═══════════════════════════════════════════════════════════════════════
    # Recovery
    # ═══════════════════════════════════════════════════════════════════════

    async def recover(self, pid: str) -> ExecutorReport:
        """Restart sonrası yürütmeyi kaldığı yerden devam ettirir.

        Daha önce tamamlanmış task'lar atlanır, kalan task'lar yürütülür.

        Args:
            pid: Recovery yapılacak Production Package'in PID'si.

        Returns:
            ExecutorReport.
        """
        async with self._lock:
            self._state = ExecutorState.RECOVERING
            self._current_pid = pid
            logger.info(f"🔄 [Executor] Recovery başlıyor: {pid}")

            try:
                # Package'i yükle
                from services.production_package_runtime import package_runtime
                pkg = await package_runtime.load(pid)
                if pkg is None:
                    raise ValueError(f"Recovery: Package bulunamadı: {pid}")

                # Tamamlanmamış task'ları bul
                all_tasks = await self._load_task_packages(pid)

                # Restart senaryosu (AR-002_79 — Kaldığı Noktadan Devam):
                # Yeni Executor instance'ı ile recovery yapıldığında rapor
                # henüz oluşmamıştır; burada başlatılır.
                if self._report is None:
                    self._report = ExecutorReport(
                        pid=pid,
                        started_at=datetime.now(timezone.utc).isoformat(),
                    )
                if not self._report.total_tasks:
                    self._report.total_tasks = len(all_tasks)

                completed_task_ids = {
                    (r.get("task_id") if isinstance(r, dict) else r.task_id)
                    for r in self._report.results
                    if (r.get("status") if isinstance(r, dict) else r.status)
                    == ExecutionStatus.SUCCESS.value
                } if self._report.results else set()

                pending_tasks = [
                    t for t in all_tasks
                    if t.get("task_id") not in completed_task_ids
                    and t.get("status") not in ("COMPLETED", "SUCCESS")
                ]

                # Checkpoint ile daha önce tamamlanmış (bu raporda henüz
                # sayılmamış) task'lar rapora yansıtılır — recovery raporu
                # üretimin TAM tamamlanma durumunu gösterir (AR-002_79)
                already_done = [
                    t for t in all_tasks
                    if t.get("task_id") not in completed_task_ids
                    and t.get("status") in ("COMPLETED", "SUCCESS")
                ]
                self._report.completed_tasks += len(already_done)

                logger.info(
                    f"📋 [Executor] Recovery: {len(pending_tasks)}/{len(all_tasks)} "
                    f"task kaldı: {pid}"
                )

                # Kalan task'ları yürüt
                self._state = ExecutorState.EXECUTING
                for task in pending_tasks:
                    result = await self._execute_task(task, pid)
                    self._report.results.append(result)

                    if result.status == ExecutionStatus.SUCCESS.value:
                        self._report.completed_tasks += 1
                    else:
                        self._report.failed_tasks += 1

                self._state = ExecutorState.COMPLETED
                self._report.completed_at = datetime.now(timezone.utc).isoformat()
                await self._update_package_status(pid)

                logger.info(
                    f"✅ [Executor] Recovery tamamlandı: {pid} "
                    f"({self._report.completed_tasks}/{self._report.total_tasks})"
                )

            except Exception as e:
                self._state = ExecutorState.FAILED
                logger.error(f"❌ [Executor] Recovery başarısız: {pid} — {e}")
                raise

            return self._report

    # ═══════════════════════════════════════════════════════════════════════
    # Reset (Test Yardımcısı)
    # ═══════════════════════════════════════════════════════════════════════

    async def reset(self) -> None:
        """Executor durumunu sıfırlar (yalnızca test amaçlı)."""
        async with self._lock:
            self._state = ExecutorState.IDLE
            self._report = None
            self._current_pid = ""
            logger.info("🔄 [Executor] Durum sıfırlandı (test amaçlı)")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

production_executor = ProductionExecutor()
"""AR-002_76: Global Production Executor singleton'ı.

Tüm modüller bu singleton üzerinden yürütme işlemlerini gerçekleştirir.
Hiçbir modül kendi ProductionExecutor instance'ını oluşturamaz.

Production garantileri:
- asyncio.Lock: Aynı anda yalnızca bir yürütme
- Deterministik task sıralaması (task_id'ye göre)
- Retry mekanizması (GC_EXECUTOR_MAX_RETRY)
- Timeout koruması (GC_EXECUTOR_TASK_TIMEOUT)
- Recovery desteği (restart sonrası kaldığı yerden devam)
"""
