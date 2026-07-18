"""
AR-002_58 Production Package Runtime — Production Package yaşam döngüsü yönetimi.

HLK içerisinde her üretim için oluşturulan Production Package'in
yaşam döngüsünü yöneten tek yetkili runtime katmanı.

Bu modül:
- Production Package oluşturur (16_PRODUCTION_PACKAGE_STANDARD.md)
- Production Package yükler / doğrular / günceller
- Production Package kapatır / arşivler
- Package bütünlüğünü doğrular (SHA-256)
- Package metadata yönetir

Bu modül:
- Decision Engine değildir (MASTER-004)
- Workflow yönetmez (09_WORKFLOW_MANIFEST.md)
- PID üretmez (AR-002_57 — PID Runtime'ın görevi)
- Production Executor çalıştırmaz (AR-002_76)
- Video Production başlatmaz (AR-002_70)
- State değiştirmez (SE-007)
- Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md)
- Yeni Feature oluşturmaz (10_FEATURE_REGISTRY.md)
- Yeni anayasa oluşturmaz (MASTER-001)

Mimari Dayanak:
- AR-002_58: Production Package Architecture
- 16_PRODUCTION_PACKAGE_STANDARD.md: Paket yapısı, bölümler, yaşam döngüsü
- AR-002_57: PID standardı (doğrulama için)
- FEAT-014: Production Package Engine
- 01_Global_Configuration.md: GC parametreleri
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GC Parameters — 01_Global_Configuration.md
# ═══════════════════════════════════════════════════════════════════════════════

_GC_PACKAGE_STORAGE_DIR = Path(
    os.getenv("GC_PACKAGE_STORAGE_DIR", "data/production_packages")
)
_GC_PACKAGE_ARCHIVE_DIR_NAME = os.getenv(
    "GC_PACKAGE_ARCHIVE_DIR", "archive"
)
_GC_PACKAGE_HASH_ALGORITHM = os.getenv(
    "GC_PACKAGE_HASH_ALGORITHM", "sha256"
)
_GC_REPRODUCE_SEARCH_LIMIT = int(
    os.getenv("GC_REPRODUCE_SEARCH_LIMIT", "20")
)
_GC_REPRODUCE_MAX_CANDIDATES = int(
    os.getenv("GC_REPRODUCE_MAX_CANDIDATES", "5")
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERİ MODELLERİ
# ═══════════════════════════════════════════════════════════════════════════════

class PackageStatus(str, Enum):
    """Production Package yaşam döngüsü durumları.

    16_PRODUCTION_PACKAGE_STANDARD.md Section 6 — Yaşam Döngüsü.
    """
    CREATED = "CREATED"         # Paket oluşturuldu, henüz boş
    BUILDING = "BUILDING"       # Bölümler dolduruluyor
    READY = "READY"             # Tüm zorunlu bölümler tamam, üretime hazır
    PRODUCING = "PRODUCING"     # Video üretimi devam ediyor
    COMPLETED = "COMPLETED"     # Üretim tamamlandı
    ARCHIVED = "ARCHIVED"       # Arşivlendi (silinemez)
    FAILED = "FAILED"           # Üretim başarısız oldu


@dataclass
class ProductionMetadata:
    """16_Section 2: Production Metadata — üretim tarihi, türü, durumu, sürüm."""
    production_type: str = "initial"       # initial | revision
    status: str = PackageStatus.CREATED.value
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""
    archived_at: str = ""

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "production_type": self.production_type,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "archived_at": self.archived_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ProductionMetadata:
        return cls(
            production_type=data.get("production_type", "initial"),
            status=data.get("status", PackageStatus.CREATED.value),
            version=data.get("version", "1.0"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            completed_at=data.get("completed_at", ""),
            archived_at=data.get("archived_at", ""),
        )


@dataclass
class ProductionPackage:
    """16_PRODUCTION_PACKAGE_STANDARD.md: Production Package ana veri modeli.

    PID ile birebir ilişkilidir. Her PID için yalnızca bir Production Package
    oluşturulabilir (Temel İlke #1).
    """
    # ── Section 1: PID (Zorunlu) ──────────────────────────────────────────
    pid: str = ""

    # ── Section 2: Production Metadata (Zorunlu) ─────────────────────────
    metadata: ProductionMetadata = field(default_factory=ProductionMetadata)

    # ── Section 3: Brief (Zorunlu) ───────────────────────────────────────
    brief: dict = field(default_factory=dict)

    # ── Section 4: Senaryo (Zorunlu) ─────────────────────────────────────
    scenario: dict = field(default_factory=dict)

    # ── Section 5: Storyboard (İsteğe Bağlı) ─────────────────────────────
    storyboard: dict = field(default_factory=dict)

    # ── Section 6: Prompt Setleri (Zorunlu) ──────────────────────────────
    prompt_sets: dict = field(default_factory=dict)

    # ── Section 7: Task Package Listesi (Zorunlu) ────────────────────────
    task_packages: list = field(default_factory=list)

    # ── Section 8: Araştırma Sonuçları (Zorunlu) ─────────────────────────
    research_results: dict = field(default_factory=dict)

    # ── Section 9: Referans Görseller (Zorunlu) ──────────────────────────
    reference_images: list = field(default_factory=list)

    # ── Section 10: Kullanıcı Dosyaları (İsteğe Bağlı) ──────────────────
    user_files: list = field(default_factory=list)

    # ── Section 11: Dijital Varlıklar (Zorunlu) ──────────────────────────
    digital_assets: list = field(default_factory=list)

    # ── Section 12: Ses Dosyaları (İsteğe Bağlı) ─────────────────────────
    audio_files: list = field(default_factory=list)

    # ── Section 13: Video Parametreleri (Zorunlu) ────────────────────────
    video_parameters: dict = field(default_factory=dict)

    # ── Section 14: Servis Kullanımları (Zorunlu) ────────────────────────
    service_usage: dict = field(default_factory=dict)

    # ── Section 15: Agent Logları (Zorunlu) ──────────────────────────────
    agent_logs: list = field(default_factory=list)

    # ── Section 16: Event Logları (Zorunlu) ──────────────────────────────
    event_logs: list = field(default_factory=list)

    # ── Section 17: Kalite Raporları (Zorunlu) ───────────────────────────
    quality_reports: list = field(default_factory=list)

    # ── Section 18: Revizyon Geçmişi (İsteğe Bağlı) ─────────────────────
    revision_history: list = field(default_factory=list)

    # ── Section 19: Teslim Bilgileri (Zorunlu) ───────────────────────────
    delivery_info: dict = field(default_factory=dict)

    # ── Section 20: Karar Gerekçeleri (Zorunlu) ──────────────────────────
    decision_history: list = field(default_factory=list)

    # ── Section 21: Nihai Video (Zorunlu) ────────────────────────────────
    final_video: dict = field(default_factory=dict)

    # ── Internal: Bütünlük hash'i ────────────────────────────────────────
    _integrity_hash: str = ""

    def to_dict(self) -> dict:
        """Production Package'i sözlük olarak döndürür (persistence için)."""
        return {
            "pid": self.pid,
            "metadata": self.metadata.to_dict(),
            "brief": self.brief,
            "scenario": self.scenario,
            "storyboard": self.storyboard,
            "prompt_sets": self.prompt_sets,
            "task_packages": self.task_packages,
            "research_results": self.research_results,
            "reference_images": self.reference_images,
            "user_files": self.user_files,
            "digital_assets": self.digital_assets,
            "audio_files": self.audio_files,
            "video_parameters": self.video_parameters,
            "service_usage": self.service_usage,
            "agent_logs": self.agent_logs,
            "event_logs": self.event_logs,
            "quality_reports": self.quality_reports,
            "revision_history": self.revision_history,
            "delivery_info": self.delivery_info,
            "decision_history": self.decision_history,
            "final_video": self.final_video,
        }

    def compute_hash(self) -> str:
        """Package içeriğinin SHA-256 hash'ini hesaplar.

        Hash hesaplaması tüm bölümleri kapsar. Bütünlük doğrulaması
        için kullanılır.
        """
        content = json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict) -> ProductionPackage:
        """Sözlükten ProductionPackage oluşturur (persistence'tan geri yükleme)."""
        return cls(
            pid=data.get("pid", ""),
            metadata=ProductionMetadata.from_dict(data.get("metadata", {})),
            brief=data.get("brief", {}),
            scenario=data.get("scenario", {}),
            storyboard=data.get("storyboard", {}),
            prompt_sets=data.get("prompt_sets", {}),
            task_packages=data.get("task_packages", []),
            research_results=data.get("research_results", {}),
            reference_images=data.get("reference_images", []),
            user_files=data.get("user_files", []),
            digital_assets=data.get("digital_assets", []),
            audio_files=data.get("audio_files", []),
            video_parameters=data.get("video_parameters", {}),
            service_usage=data.get("service_usage", {}),
            agent_logs=data.get("agent_logs", []),
            event_logs=data.get("event_logs", []),
            quality_reports=data.get("quality_reports", []),
            revision_history=data.get("revision_history", []),
            delivery_info=data.get("delivery_info", {}),
            decision_history=data.get("decision_history", []),
            final_video=data.get("final_video", {}),
            _integrity_hash=data.get("_integrity_hash", ""),
        )


@dataclass
class PackageValidationResult:
    """Production Package doğrulama sonucu."""
    is_valid: bool
    pid: str = ""
    status: str = ""
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    missing_required: list = field(default_factory=list)
    hash_match: bool = False

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "pid": self.pid,
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "missing_required": self.missing_required,
            "hash_match": self.hash_match,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PRODUCTION PACKAGE RUNTIME
# ═══════════════════════════════════════════════════════════════════════════════

class ProductionPackageRuntime:
    """AR-002_58: Production Package yaşam döngüsünü yöneten runtime katmanı.

    Production Package Runtime:
    - Production Package oluşturur (PID doğrulaması yapar)
    - Production Package yükler / doğrular / günceller
    - Production Package kapatır / arşivler
    - Package bütünlüğünü doğrular
    - Package metadata yönetir

    Production Package Runtime:
    - Karar vermez (MASTER-004)
    - PID üretmez — yalnızca PIDRuntime tarafından üretilen PID'yi kullanır
    - Workflow, State, Event, Feature yönetmez
    - Yeni anayasa/mimari oluşturmaz

    İlişkili Bileşenler (entegrasyon, devralma değil):
    - PID Runtime: PID doğrulama
    - Task Engine: Task Package listesi
    - Digital Asset Archive: Varlık referansları
    - Digital Asset Catalog: Katalog kayıtları
    - Event Collector: Event logları
    - Olay Kayıt Merkezi: Event referansları
    """

    def __init__(self):
        # ── In-memory package registry ────────────────────────────────────
        self._packages: dict[str, ProductionPackage] = {}

        # ── Concurrency control ──────────────────────────────────────────
        self._lock = asyncio.Lock()

        # ── Storage yollarını hazırla ────────────────────────────────────
        _GC_PACKAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        (_GC_PACKAGE_STORAGE_DIR / _GC_PACKAGE_ARCHIVE_DIR_NAME).mkdir(
            parents=True, exist_ok=True
        )

    # ── Dosya Yolu Yardımcıları ──────────────────────────────────────────

    @staticmethod
    def _package_path(pid: str) -> Path:
        """PID'ye ait Production Package dosya yolunu döndürür."""
        safe_pid = pid.replace("/", "_").replace("\\", "_")
        return _GC_PACKAGE_STORAGE_DIR / f"{safe_pid}.json"

    @staticmethod
    def _archive_path(pid: str) -> Path:
        """PID'ye ait arşivlenmiş Production Package dosya yolunu döndürür."""
        safe_pid = pid.replace("/", "_").replace("\\", "_")
        return (
            _GC_PACKAGE_STORAGE_DIR
            / _GC_PACKAGE_ARCHIVE_DIR_NAME
            / f"{safe_pid}.json"
        )

    # ── Package Oluşturma ────────────────────────────────────────────────

    async def create(self, pid: str) -> ProductionPackage:
        """Yeni bir Production Package oluşturur.

        16_Section 7: STATE_VIDEO_PRODUCTION girişinde, PID oluşturulduktan
        hemen sonra çağrılır.

        - PID'nin geçerli ve benzersiz olduğunu doğrular
        - Aynı PID için ikinci bir package oluşturulamaz (Temel İlke #1)
        - Oluşturulan package CREATED durumunda başlar
        - Package diske kaydedilir

        Args:
            pid: Production ID (AR-002_57 formatında: PID-YYYYMMDD-NNNN)

        Returns:
            Oluşturulan ProductionPackage.

        Raises:
            ValueError: PID geçersiz veya bu PID için package zaten mevcut.
        """
        async with self._lock:
            # PID doğrulama — PID Runtime üzerinden
            from services.pid_runtime import pid_runtime

            # PID'nin geçerli bir formatta olduğunu kontrol et
            validation = await pid_runtime.validate(pid)
            if not validation.is_valid:
                raise ValueError(
                    f"Geçersiz PID: {pid} — {validation.error}"
                )

            # Aynı PID için package zaten var mı?
            # (kilit tutulurken load() ÇAĞRILMAZ — deadlock; bkz. _load_unlocked)
            existing = self._load_unlocked(pid)
            if existing is not None:
                raise ValueError(
                    f"Bu PID için Production Package zaten mevcut: {pid} "
                    f"(Temel İlke #1: Her PID yalnızca bir adet Production "
                    f"Package oluşturabilir)"
                )

            # Yeni package oluştur
            package = ProductionPackage(pid=pid)
            package.metadata = ProductionMetadata(
                production_type="initial",
                status=PackageStatus.CREATED.value,
            )
            package.compute_hash()
            package._integrity_hash = package.compute_hash()

            # Registry ve diske kaydet
            self._packages[pid] = package
            self._save_to_disk(package)

            logger.info(
                f"📦 [Package Runtime] Production Package oluşturuldu: {pid} "
                f"(durum: {package.metadata.status})"
            )
            return package

    # ── Package Yükleme ──────────────────────────────────────────────────

    async def load(self, pid: str) -> Optional[ProductionPackage]:
        """PID'ye ait Production Package'i yükler.

        Önce in-memory registry'ye, sonra diske bakar.

        Args:
            pid: Yüklenecek package'in PID'si.

        Returns:
            ProductionPackage veya None (bulunamazsa).
        """
        async with self._lock:
            return self._load_unlocked(pid)

    def _load_unlocked(self, pid: str) -> Optional[ProductionPackage]:
        """Kilitsiz iç yükleyici — YALNIZCA self._lock altında çağrılır.

        asyncio.Lock re-entrant değildir; kilit tutan metodların (create vb.)
        load() çağırması deadlock üretir. Bu helper her iki kullanım için
        tek gerçek yükleme mantığıdır.
        """
        # In-memory kontrol
        if pid in self._packages:
            return self._packages[pid]

        # Diskten yükle
        pkg_path = self._package_path(pid)
        archive_path = self._archive_path(pid)

        for path in (pkg_path, archive_path):
            if path.exists():
                try:
                    package = self._load_from_disk(path)
                    if package:
                        self._packages[pid] = package
                        return package
                except Exception as e:
                    logger.warning(
                        f"⚠️ [Package Runtime] Package yüklenemedi "
                        f"{pid}: {e}"
                    )

        return None

    # ── Package Doğrulama ────────────────────────────────────────────────

    async def validate(self, pid: str) -> PackageValidationResult:
        """Production Package'in bütünlüğünü ve standart uyumluluğunu doğrular.

        16_Section 5: Tüm zorunlu bölümlerin varlığını ve içerik
        bütünlüğünü kontrol eder.

        Denetimler:
        1. Package mevcut mu?
        2. PID alanı dolu ve geçerli mi?
        3. Zorunlu bölümler mevcut mu?
        4. Hash bütünlüğü korunuyor mu?
        5. Metadata tutarlı mı?

        Args:
            pid: Doğrulanacak package'in PID'si.

        Returns:
            PackageValidationResult.
        """
        async with self._lock:
            errors: list[str] = []
            warnings: list[str] = []
            missing: list[str] = []

            # Package'i yükle
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
            if package is None:
                # Arşivde ara
                package = self._load_from_disk(self._archive_path(pid))

            if package is None:
                return PackageValidationResult(
                    is_valid=False,
                    pid=pid,
                    errors=["Production Package bulunamadı"],
                )

            # Denetim 1: PID alanı
            if not package.pid:
                errors.append("PID alanı boş (Zorunlu Bölüm #1)")
            elif package.pid != pid:
                errors.append(
                    f"PID uyuşmazlığı: istek={pid}, package={package.pid}"
                )

            # Denetim 2: Zorunlu bölümler
            required_sections = {
                "brief": "Section 3 — Brief",
                "scenario": "Section 4 — Senaryo",
                "prompt_sets": "Section 6 — Prompt Setleri",
                "task_packages": "Section 7 — Task Package Listesi",
                "research_results": "Section 8 — Araştırma Sonuçları",
                "reference_images": "Section 9 — Referans Görseller",
                "digital_assets": "Section 11 — Dijital Varlıklar",
                "video_parameters": "Section 13 — Video Parametreleri",
                "service_usage": "Section 14 — Servis Kullanımları",
                "agent_logs": "Section 15 — Agent Logları",
                "event_logs": "Section 16 — Event Logları",
                "quality_reports": "Section 17 — Kalite Raporları",
                "delivery_info": "Section 19 — Teslim Bilgileri",
                "decision_history": "Section 20 — Karar Gerekçeleri",
                "final_video": "Section 21 — Nihai Video",
            }

            for field_name, section_label in required_sections.items():
                value = getattr(package, field_name, None)
                if value is None:
                    missing.append(section_label)
                elif isinstance(value, (dict, list)) and len(value) == 0:
                    warnings.append(f"{section_label} boş (zorunlu bölüm)")

            if missing:
                errors.append(
                    f"Eksik zorunlu bölümler: {', '.join(missing)}"
                )

            # Denetim 3: Hash bütünlüğü
            current_hash = package.compute_hash()
            stored_hash = package._integrity_hash
            hash_ok = (current_hash == stored_hash) if stored_hash else None
            if hash_ok is False:
                errors.append(
                    "Hash bütünlüğü bozuk — package içeriği değiştirilmiş olabilir"
                )

            # Denetim 4: Metadata
            if not package.metadata or not package.metadata.created_at:
                errors.append("Production Metadata eksik (Zorunlu Bölüm #2)")

            is_valid = len(errors) == 0
            return PackageValidationResult(
                is_valid=is_valid,
                pid=pid,
                status=package.metadata.status if package.metadata else "",
                errors=errors,
                warnings=warnings,
                missing_required=missing,
                hash_match=hash_ok if hash_ok is not None else False,
            )

    # ── Package Güncelleme ───────────────────────────────────────────────

    async def update_section(
        self, pid: str, section: str, data: dict | list
    ) -> bool:
        """Production Package'in belirli bir bölümünü günceller.

        16_Section 16: Mevcut bölümler değiştirilmez, yalnızca güncellenir.

        Bu metod yalnızca bölüm içeriğini günceller. Yeni bölüm oluşturmaz.
        Standart dışı bölüm adı kabul edilmez.

        Geçerli bölüm adları (16_Section 5):
        brief, scenario, storyboard, prompt_sets, task_packages,
        research_results, reference_images, user_files, digital_assets,
        audio_files, video_parameters, service_usage, agent_logs,
        event_logs, quality_reports, revision_history, delivery_info,
        decision_history, final_video

        Args:
            pid: Güncellenecek package'in PID'si.
            section: Bölüm adı.
            data: Yeni bölüm içeriği.

        Returns:
            True: Güncelleme başarılı.
            False: PID bulunamadı veya bölüm geçersiz.

        Raises:
            ValueError: Standart dışı bölüm adı.
        """
        # Geçerli bölüm adları (16_Section 5)
        valid_sections = {
            "brief", "scenario", "storyboard", "prompt_sets",
            "task_packages", "research_results", "reference_images",
            "user_files", "digital_assets", "audio_files",
            "video_parameters", "service_usage", "agent_logs",
            "event_logs", "quality_reports", "revision_history",
            "delivery_info", "decision_history", "final_video",
        }

        if section not in valid_sections:
            raise ValueError(
                f"Geçersiz bölüm adı: '{section}'. "
                f"Geçerli bölümler: {', '.join(sorted(valid_sections))}"
            )

        async with self._lock:
            # Package'i yükle
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
                if package:
                    self._packages[pid] = package

            if package is None:
                logger.warning(
                    f"⚠️ [Package Runtime] Güncelleme başarısız — "
                    f"PID bulunamadı: {pid}"
                )
                return False

            # Arşivlenmiş package güncellenemez
            if package.metadata.status == PackageStatus.ARCHIVED.value:
                logger.warning(
                    f"⚠️ [Package Runtime] Arşivlenmiş package güncellenemez: {pid}"
                )
                return False

            # Bölümü güncelle
            setattr(package, section, data)

            # Metadata'yı güncelle
            package.metadata.updated_at = datetime.now(timezone.utc).isoformat()

            # Hash'i yenile
            package._integrity_hash = package.compute_hash()

            # Diske kaydet
            self._save_to_disk(package)

            logger.info(
                f"📝 [Package Runtime] '{section}' bölümü güncellendi: {pid}"
            )
            return True

    # ── Package Kapatma ──────────────────────────────────────────────────

    async def close(self, pid: str) -> bool:
        """Production Package'i COMPLETED durumuna getirir.

        Package silinemez (Temel İlke #3), yalnızca kapatılır.
        Kapatma işlemi metadata'ya completed_at damgası ekler.

        Args:
            pid: Kapatılacak package'in PID'si.

        Returns:
            True: İşlem başarılı.
            False: PID bulunamadı.
        """
        async with self._lock:
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
                if package:
                    self._packages[pid] = package

            if package is None:
                logger.warning(
                    f"⚠️ [Package Runtime] Kapatma başarısız — "
                    f"PID bulunamadı: {pid}"
                )
                return False

            now = datetime.now(timezone.utc).isoformat()
            package.metadata.status = PackageStatus.COMPLETED.value
            package.metadata.completed_at = now
            package.metadata.updated_at = now
            package._integrity_hash = package.compute_hash()

            self._save_to_disk(package)

            logger.info(f"🔒 [Package Runtime] Package kapatıldı: {pid}")
            return True

    # ── Package Arşivleme ────────────────────────────────────────────────

    async def archive(self, pid: str) -> bool:
        """Production Package'i arşive taşır.

        Package silinemez (Temel İlke #3), yalnızca arşivlenebilir.
        Arşivleme işlemi:
        1. Package dosyasını archive/ alt dizinine taşır
        2. Metadata'ya archived_at damgası ekler
        3. Durumu ARCHIVED olarak günceller

        Args:
            pid: Arşivlenecek package'in PID'si.

        Returns:
            True: İşlem başarılı.
            False: PID bulunamadı.
        """
        async with self._lock:
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
                if package:
                    self._packages[pid] = package

            if package is None:
                # Zaten arşivde olabilir
                package = self._load_from_disk(self._archive_path(pid))
                if package:
                    logger.info(
                        f"📦 [Package Runtime] Package zaten arşivde: {pid}"
                    )
                    return True
                logger.warning(
                    f"⚠️ [Package Runtime] Arşivleme başarısız — "
                    f"PID bulunamadı: {pid}"
                )
                return False

            now = datetime.now(timezone.utc).isoformat()
            package.metadata.status = PackageStatus.ARCHIVED.value
            package.metadata.archived_at = now
            package.metadata.updated_at = now
            package._integrity_hash = package.compute_hash()

            # Arşiv dizinine kaydet (_save_to_disk ile aynı format —
            # to_dict + _integrity_hash; _load_from_disk bunu bekler)
            archive_path = self._archive_path(pid)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            data = package.to_dict()
            data["_integrity_hash"] = package._integrity_hash
            archive_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # Orijinal dosyayı temizle (arşive taşındı)
            pkg_path = self._package_path(pid)
            try:
                if pkg_path.exists():
                    pkg_path.unlink()
            except OSError:
                pass

            # Registry'den kaldır (arşivde)
            self._packages.pop(pid, None)

            logger.info(f"📦 [Package Runtime] Package arşivlendi: {pid}")
            return True

    # ── Metadata Yönetimi ────────────────────────────────────────────────

    async def get_metadata(self, pid: str) -> Optional[dict]:
        """Production Package metadata'sını döndürür.

        Args:
            pid: Sorgulanacak package'in PID'si.

        Returns:
            Metadata sözlüğü veya None.
        """
        package = await self.load(pid)
        if package is None:
            return None
        return package.metadata.to_dict()

    async def update_status(self, pid: str, status: PackageStatus) -> bool:
        """Production Package durumunu günceller.

        Yalnızca geçerli durum geçişlerine izin verilir:
        CREATED → BUILDING → READY → PRODUCING → COMPLETED
        Herhangi bir durum → FAILED
        COMPLETED → ARCHIVED

        Args:
            pid: Güncellenecek package'in PID'si.
            status: Yeni durum.

        Returns:
            True: İşlem başarılı.
            False: PID bulunamadı.
        """
        async with self._lock:
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
                if package:
                    self._packages[pid] = package

            if package is None:
                return False

            if package.metadata.status == PackageStatus.ARCHIVED.value:
                logger.warning(
                    f"⚠️ [Package Runtime] Arşivlenmiş package durumu "
                    f"değiştirilemez: {pid}"
                )
                return False

            old_status = package.metadata.status
            package.metadata.status = status.value
            package.metadata.updated_at = datetime.now(timezone.utc).isoformat()
            package._integrity_hash = package.compute_hash()

            self._save_to_disk(package)

            logger.info(
                f"🔄 [Package Runtime] Durum güncellendi: {pid} "
                f"({old_status} → {status.value})"
            )
            return True

    # ── Yeniden Üretim (Re-Production) İşlemleri ───────────────────────────

    async def find_package(self, query: str) -> Optional[ProductionPackage]:
        """PID veya ürün adına göre Production Package bulur.

        Yönetici tarafından başlatılan yeniden üretim prosedüründe kullanılır.
        Önce query'yi PID olarak doğrular; değilse aktif ve arşivlenmiş
        package'ların brief/scenario alanlarında arama yapar.

        Args:
            query: PID veya ürün adı/marka/senaryo başlığı parçası.

        Returns:
            En uygun ProductionPackage veya None.
        """
        if not query or not query.strip():
            return None

        query_clean = query.strip()

        # Adım 1: PID olarak doğrula (kilit almadan — deadlock önlemi)
        from services.pid_runtime import pid_runtime

        pid_validation = await pid_runtime.validate(query_clean)
        if pid_validation.is_valid:
            package = await self.load(query_clean)
            if package is not None:
                return package

        # Adım 2: Ürün adı / marka / senaryo başlığında ara
        query_lower = query_clean.lower()
        candidates: list[tuple[ProductionPackage, str]] = []

        search_dirs = [
            _GC_PACKAGE_STORAGE_DIR,
            _GC_PACKAGE_STORAGE_DIR / _GC_PACKAGE_ARCHIVE_DIR_NAME,
        ]

        async with self._lock:
            searched = 0
            for directory in search_dirs:
                if not directory.exists():
                    continue
                for path in directory.glob("*.json"):
                    if searched >= _GC_REPRODUCE_SEARCH_LIMIT:
                        break
                    searched += 1
                    package = self._load_from_disk(path)
                    if package is None:
                        continue

                    # Eşleşme skoru: product_name > brand > scenario.title
                    score = 0
                    brief = package.brief or {}
                    scenario = package.scenario or {}
                    product_name = str(brief.get("product_name", "")).lower()
                    brand = str(brief.get("brand", "")).lower()
                    scenario_title = str(scenario.get("title", "")).lower()

                    if product_name and query_lower in product_name:
                        score = 3
                    elif brand and query_lower in brand:
                        score = 2
                    elif scenario_title and query_lower in scenario_title:
                        score = 1

                    if score > 0:
                        candidates.append((package, package.metadata.updated_at))

        if not candidates:
            return None

        # En güncel adayı döndür
        candidates.sort(key=lambda x: x[1] or "", reverse=True)
        return candidates[0][0]

    async def prepare_for_reproduction(
        self, pid: str, procedure: str
    ) -> bool:
        """Production Package'i yeniden üretim için hazırlar.

        Prosedüre göre package durumunu ve task'ları ayarlar;
        revision_history'ye kayıt ekler.

        Args:
            pid: Production ID.
            procedure: HLK Runtime tarafından belirlenen prosedür.
                       RESUME | RETRY | REPLAY | START_AS_NEW

        Returns:
            True: Hazırlık başarılı.
            False: Package bulunamadı veya arşivlenmiş.
        """
        from services.pid_runtime import pid_runtime

        procedure = (procedure or "RESUME").upper()
        now = datetime.now(timezone.utc).isoformat()

        async with self._lock:
            package = self._packages.get(pid)
            if package is None:
                package = self._load_from_disk(self._package_path(pid))
                if package is None:
                    package = self._load_from_disk(self._archive_path(pid))
                if package:
                    self._packages[pid] = package

            if package is None:
                logger.warning(
                    f"⚠️ [Package Runtime] Reproduction hazırlığı başarısız — "
                    f"PID bulunamadı: {pid}"
                )
                return False

            if package.metadata.status == PackageStatus.ARCHIVED.value:
                logger.warning(
                    f"⚠️ [Package Runtime] Arşivlenmiş package yeniden "
                    f"üretilemez: {pid}"
                )
                return False

            previous_status = package.metadata.status

            # Revision history kaydı
            revision_entry = {
                "type": "reproduction",
                "procedure": procedure,
                "timestamp": now,
                "previous_status": previous_status,
            }
            if not isinstance(package.revision_history, list):
                package.revision_history = []
            package.revision_history.append(revision_entry)

            # Metadata güncelle
            package.metadata.production_type = "reproduction"
            package.metadata.updated_at = now

            # Task'ları prosedüre göre ayarla
            task_packages = package.task_packages or []
            for task in task_packages:
                if not isinstance(task, dict):
                    continue
                if procedure == "REPLAY":
                    task["status"] = "PENDING"
                    task["completed_at"] = ""
                    task["error_detail"] = ""
                elif procedure == "RETRY":
                    if task.get("status") in ("FAILED", "TIMEOUT"):
                        task["status"] = "PENDING"
                        task["completed_at"] = ""
                        task["error_detail"] = ""
                # RESUME / START_AS_NEW: task'lar dokunulmaz

            # REPLAY durumunda final/delivery geçici temizlik
            if procedure == "REPLAY":
                package.metadata.status = PackageStatus.READY.value
                package.final_video = {}
                package.delivery_info = {}
            else:
                package.metadata.status = PackageStatus.PRODUCING.value

            package._integrity_hash = package.compute_hash()
            self._save_to_disk(package)

            logger.info(
                f"🔄 [Package Runtime] Reproduction hazır: {pid} "
                f"({previous_status} → {package.metadata.status}, "
                f"procedure={procedure})"
            )
            return True

    async def load_full_production_context(self, pid: str) -> dict:
        """Yeniden üretim için gerekli anayasal kayıtları toplar.

        Production Package, Workflow, State Engine kayıtları, Olay Kayıt
        Merkezi, Dijital Varlık Arşivi/Katalog, Sahne Kayıt Defteri ve
        Karar Gerekçesi kayıtlarını birleştirir.

        Args:
            pid: Production ID.

        Returns:
            HLK Runtime değerlendirmesi için context sözlüğü.
        """
        package = await self.load(pid)
        if package is None:
            return {"pid": pid, "error": "Production Package bulunamadı"}

        # Task durumlarını analiz et
        task_packages = package.task_packages or []
        total_tasks = len(task_packages)
        completed_tasks = sum(
            1 for t in task_packages
            if isinstance(t, dict) and t.get("status") in ("COMPLETED", "SUCCESS")
        )
        failed_tasks = sum(
            1 for t in task_packages
            if isinstance(t, dict) and t.get("status") in ("FAILED", "TIMEOUT")
        )
        pending_tasks = total_tasks - completed_tasks - failed_tasks

        last_error = ""
        failed_step = ""
        for task in task_packages:
            if isinstance(task, dict) and task.get("status") in ("FAILED", "TIMEOUT"):
                last_error = task.get("error_detail", "")
                failed_step = task.get("task_id", "")
                break

        last_successful_step = ""
        for task in reversed(task_packages):
            if isinstance(task, dict) and task.get("status") in ("COMPLETED", "SUCCESS"):
                last_successful_step = task.get("task_id", "")
                break

        brief = package.brief or {}
        scenario = package.scenario or {}
        metadata = package.metadata or ProductionMetadata()

        return {
            "pid": pid,
            "package_status": metadata.status,
            "production_type": metadata.production_type,
            "product_name": brief.get("product_name", ""),
            "brand": brief.get("brand", ""),
            "created_at": metadata.created_at,
            "updated_at": metadata.updated_at,
            "completed_at": metadata.completed_at,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "pending_tasks": pending_tasks,
            "last_error": last_error,
            "failed_step": failed_step,
            "last_successful_step": last_successful_step,
            # Anayasal kayıt mekanizmaları
            "workflow": {
                "task_packages": task_packages,
            },
            "state_engine_records": {
                "package_status": metadata.status,
            },
            "event_logs": package.event_logs or [],
            "digital_asset_archive": package.digital_assets or [],
            "digital_asset_catalog": package.digital_assets or [],
            "scene_registry": {
                "scenario": scenario,
                "storyboard": package.storyboard or {},
            },
            "decision_history": package.decision_history or [],
            "revision_history": package.revision_history or [],
        }

    # ── Bütünlük Doğrulama ───────────────────────────────────────────────

    async def verify_integrity(self, pid: str) -> tuple[bool, str]:
        """Package bütünlüğünü SHA-256 hash ile doğrular.

        Args:
            pid: Doğrulanacak package'in PID'si.

        Returns:
            (True/False, açıklama mesajı)
        """
        package = await self.load(pid)
        if package is None:
            return False, f"PID bulunamadı: {pid}"

        current_hash = package.compute_hash()
        stored_hash = package._integrity_hash

        if not stored_hash:
            return False, "Bütünlük hash'i mevcut değil"

        if current_hash == stored_hash:
            return True, f"Bütünlük doğrulandı (SHA-256: {current_hash[:16]}...)"
        else:
            return False, (
                f"Bütünlük hatası! "
                f"Kayıtlı: {stored_hash[:16]}..., "
                f"Hesaplanan: {current_hash[:16]}..."
            )

    async def get_package_count(self) -> dict:
        """Sistemdeki toplam package sayısını ve durum dağılımını döndürür."""
        async with self._lock:
            counts = {
                "total": 0,
                "by_status": {},
                "active": 0,
                "archived": 0,
            }

            # Aktif dizindeki package'leri say
            pkg_dir = _GC_PACKAGE_STORAGE_DIR
            if pkg_dir.exists():
                for p in pkg_dir.glob("*.json"):
                    counts["total"] += 1
                    try:
                        data = json.loads(p.read_text(encoding="utf-8"))
                        status = data.get("metadata", {}).get("status", "UNKNOWN")
                        counts["by_status"][status] = (
                            counts["by_status"].get(status, 0) + 1
                        )
                    except Exception:
                        counts["by_status"]["CORRUPT"] = (
                            counts["by_status"].get("CORRUPT", 0) + 1
                        )

            counts["active"] = counts["total"]

            # Arşivdekileri say
            archive_dir = _GC_PACKAGE_STORAGE_DIR / _GC_PACKAGE_ARCHIVE_DIR_NAME
            if archive_dir.exists():
                for p in archive_dir.glob("*.json"):
                    counts["total"] += 1
                    counts["archived"] += 1
                    counts["by_status"]["ARCHIVED"] = (
                        counts["by_status"].get("ARCHIVED", 0) + 1
                    )

            return counts

    # ── Persistence ──────────────────────────────────────────────────────

    def _save_to_disk(self, package: ProductionPackage) -> None:
        """Production Package'i diske kaydeder.

        Atomik yazım: önce .tmp dosyaya yaz, sonra rename.
        """
        pkg_path = self._package_path(package.pid)
        pkg_path.parent.mkdir(parents=True, exist_ok=True)

        data = package.to_dict()
        data["_integrity_hash"] = package._integrity_hash

        try:
            tmp_path = pkg_path.with_suffix(".tmp")
            tmp_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            tmp_path.replace(pkg_path)
        except Exception as e:
            logger.error(f"❌ [Package Runtime] Kaydedilemedi {package.pid}: {e}")

    @staticmethod
    def _load_from_disk(path: Path) -> Optional[ProductionPackage]:
        """Diskten Production Package yükler."""
        if not path.exists():
            return None
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            package = ProductionPackage.from_dict(data)
            package._integrity_hash = data.get("_integrity_hash", "")
            return package
        except Exception as e:
            logger.warning(f"⚠️ [Package Runtime] Diskten yükleme hatası {path}: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MODÜL YARDIMCI FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def validate_pid_format_static(pid: str) -> bool:
    """Statik PID format doğrulaması — registry'den bağımsız.

    Production Package oluşturmadan önce hızlı format kontrolü için kullanılır.

    Args:
        pid: Doğrulanacak PID string'i.

    Returns:
        True: PID formatı geçerli.
    """
    from services.pid_runtime import validate_pid_static
    result = validate_pid_static(pid)
    return result.is_valid


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

package_runtime = ProductionPackageRuntime()
"""AR-002_58: Global Production Package Runtime singleton'ı.

Tüm modüller bu singleton üzerinden Production Package işlemlerini
gerçekleştirir. Hiçbir modül kendi ProductionPackageRuntime instance'ını
oluşturamaz.

Production garantileri:
- asyncio.Lock: Tüm state mutasyonları atomik
- Disk persistence: Her package JSON dosyası olarak saklanır
- PID ↔ Production Package birebir ilişkisi korunur
"""
