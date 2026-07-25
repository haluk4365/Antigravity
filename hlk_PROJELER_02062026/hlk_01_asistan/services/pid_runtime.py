"""
AR-002_71 PID Runtime Architecture — PID Runtime Implementation

HLK'nın Production Runtime sırasında Production ID (PID) oluşturma sürecini
anayasal kurallara uygun şekilde yürüten tek yetkili runtime katmanı.

Bu modül:
- PID üretir (AR-002_57 format standardına göre)
- PID doğrular
- PID benzersizliğini kontrol eder
- PID bilgisini ilgili Workflow'a döndürür

Bu modül:
- Production Package oluşturmaz (AR-002_58, AR-002_72)
- Executor çalıştırmaz (AR-002_76)
- Video Production başlatmaz (AR-002_70)
- Karar vermez (MASTER-004)
- State Engine yerine geçmez (SE-007)
- Yeni Event üretmez (14_OLAY_KAYIT_MERKEZI.md)
- Yeni Workflow oluşturmaz (09_WORKFLOW_MANIFEST.md)
- Yeni Feature oluşturmaz (10_FEATURE_REGISTRY.md)
- Anayasa değiştirmez (MASTER-001)

Production Güvenceleri:
- asyncio.Lock: Tüm state mutasyonları kilit altında atomiktir
- Counter persistence: Günlük sayaç diskte saklanır, restart sonrası duplicate PID
  üretilmez (AR-002_57: "Aynı PID birden fazla üretim için kullanılamaz")
- Registry persistence: PID kayıtları diskte saklanır, restart sonrası uniqueness
  kontrolü çalışmaya devam eder (AR-002_57: PID Tekillik Kuralı)

Mimari Dayanak:
- AR-002_57: PID Mimari Standardı — format, tekillik, merkeziyet, zorunluluk
- AR-002_71: PID Runtime Architecture — çalışma sırası ve bütünlük kuralları
- 01_Global_Configuration.md: GC_PID_PREFIX, GC_PID_DATE_FORMAT,
  GC_PID_SEQUENCE_LENGTH, GC_PID_SEQUENCE_START
- MASTER-004: Karar Mekanizması — PID Runtime karar vermez
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Cross-Process File Lock (stdlib only — no external dependencies)
#
# Unix (Railway production): fcntl.flock(LOCK_EX) — kernel-enforced advisory
#   lock, released automatically on process exit or fd close.
# Windows (dev): msvcrt.locking(LK_LOCK) — byte-range lock on a dedicated
#   region of the lock file, released automatically on process exit or fd close.
#
# Her iki platformda da OS seviyesinde gerçek kilit kullanılır.
# Kilit dosyasına holder bilgisi (PID, timestamp) yazılarak stale lock
# tespiti ve otomatik recovery sağlanır.
#
# İki katmanlı güvenlik:
#   Katman 1 — asyncio.Lock: intra-process (coroutine) sıralama
#   Katman 2 — OS file lock:  inter-process (worker) mutual exclusion
# ═══════════════════════════════════════════════════════════════════════════════

# Lock staleness timeout — bu süreden uzun süredir tutulan kilit
# stale kabul edilir ve otomatik kırılır (holder process crash olmuşsa).
_GC_PID_LOCK_TIMEOUT = float(os.getenv("GC_PID_LOCK_TIMEOUT", "30.0"))


def _write_lock_info(lock_path: Path) -> None:
    """Kilit dosyasına holder bilgisi yazar (stale lock tespiti için)."""
    try:
        info = json.dumps({
            "holder_pid": os.getpid(),
            "acquired_at": time.time(),
            "acquired_iso": datetime.now(timezone.utc).isoformat(),
        })
        lock_path.write_text(info, encoding="utf-8")
    except Exception as _e:
        pass  # info yazılamazsa kilit hâlâ geçerli — best-effort


def _read_lock_info(lock_path: Path) -> Optional[dict]:
    """Kilit dosyasından holder bilgisini okur."""
    try:
        if lock_path.exists():
            raw = lock_path.read_text(encoding="utf-8")
            return json.loads(raw)
    except Exception as _e:
        pass
    return None


def _is_lock_stale(lock_path: Path, timeout: float = None) -> bool:
    """Kilidin stale (geçersiz) olup olmadığını kontrol eder.

    Bir kilit, holder bilgisi mevcutsa ve GC_PID_LOCK_TIMEOUT süresinden
    uzun süredir tutuluyorsa stale kabul edilir. Holder process'in crash
    olması durumunda OS seviyesindeki kilit (flock/msvcrt) process exit
    ile otomatik serbest kalır — bu durumda lock_path yalnızca info dosyası
    olarak kalır. Bu metod, OS kilidi serbest kalmış fakat info dosyası
    hâlâ mevcut olan artık kilitleri temizlemek için kullanılır.
    """
    if timeout is None:
        timeout = _GC_PID_LOCK_TIMEOUT
    info = _read_lock_info(lock_path)
    if info is None:
        # Info yoksa dosya eskimiş olabilir — stat ile kontrol et
        try:
            mtime = lock_path.stat().st_mtime
            return (time.time() - mtime) > timeout
        except OSError:
            return False
    acquired = info.get("acquired_at", 0)
    return (time.time() - acquired) > timeout


def _break_stale_lock(lock_path: Path) -> bool:
    """Unix: Stale lock dosyasını kırar (temizler).

    Returns:
        True: Stale lock temizlendi veya lock yoktu.
        False: Lock stale değil, kırılamaz.
    """
    if not lock_path.exists():
        return True
    if _is_lock_stale(lock_path):
        logger.warning(
            f"⏰ [PID Runtime] Stale lock tespit edildi: {lock_path} — "
            f"holder process crash olmuş olabilir, kilit kırılıyor."
        )
        try:
            lock_path.unlink()
        except OSError:
            pass
        return True
    return False


def _break_stale_lock_dir(lock_dir: Path) -> bool:
    """Windows: Stale lock dizinini ve içeriğini temizler.

    Returns:
        True: Stale lock temizlendi veya lock yoktu.
        False: Lock stale değil, kırılamaz.
    """
    holder_file = lock_dir / "holder.json"
    if not lock_dir.exists():
        return True
    if _is_lock_stale(holder_file):
        logger.warning(
            f"⏰ [PID Runtime] Stale lock tespit edildi: {lock_dir} — "
            f"holder process crash olmuş olabilir, kilit kırılıyor."
        )
        try:
            # Dizin içeriğini ve dizini temizle
            for item in lock_dir.iterdir():
                item.unlink()
            lock_dir.rmdir()
        except OSError:
            pass
        return True
    return False


def _cross_process_lock_acquire(lock_path: Path, timeout: float = None) -> None:
    """Cross-process özel (exclusive) kilit alır.

    Platform stratejileri (her ikisi de OS seviyesinde gerçek kilit):
    - Unix (Railway production): fcntl.flock(LOCK_EX) — kernel-enforced,
      process exit'te otomatik serbest. En güvenilir yöntem.
    - Windows: msvcrt.locking(LK_LOCK) — byte-range lock,
      process exit'te otomatik serbest. mkdir'a göre çok daha güvenilir.

    Her iki platformda da lock_path dosyasına holder bilgisi yazılır.
    Bu bilgi; stale lock tespiti, debugging ve crash recovery için kullanılır.

    Staleness koruması:
    - OS kilidi (flock/msvcrt) process exit'te otomatik serbest kalır.
    - Kilit alınamazsa, mevcut lock'un stale olup olmadığı kontrol edilir.
    - Stale ise kırılır ve yeniden denenir.

    Args:
        lock_path: Kilit dosyası yolu.
        timeout: Maksimum bekleme süresi (saniye). None ise GC_PID_LOCK_TIMEOUT.

    Returns:
        Unix: file descriptor (release için gerekli).
        Windows: file descriptor (release için gerekli).

    Raises:
        RuntimeError: Timeout aşımı — kilit alınamadı.
    """
    if timeout is None:
        timeout = _GC_PID_LOCK_TIMEOUT

    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if os.name != "nt":
        # ═══════════════════════════════════════════════════════════════════
        # Unix (Railway production): fcntl.flock
        # ═══════════════════════════════════════════════════════════════════
        import fcntl

        deadline = time.time() + timeout
        last_error = None

        while True:
            # Stale lock kontrolü ve temizliği
            _break_stale_lock(lock_path)

            try:
                fd = open(lock_path, "w")
                fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Kilit alındı — holder bilgisini doğrudan bu fd'ye yaz
                info = json.dumps({
                    "holder_pid": os.getpid(),
                    "acquired_at": time.time(),
                    "acquired_iso": datetime.now(timezone.utc).isoformat(),
                })
                fd.write(info)
                fd.flush()
                return fd
            except (BlockingIOError, OSError) as e:
                last_error = e
                if fd:
                    try:
                        fd.close()
                    except Exception as _e:
                        pass
                if time.time() > deadline:
                    holder_info = _read_lock_info(lock_path)
                    raise RuntimeError(
                        f"PID Runtime cross-process kilit alınamadı: {lock_path} "
                        f"({timeout}s timeout). Holder: {holder_info or 'bilinmiyor'}"
                    )
                time.sleep(0.05)
            except Exception as _e:
                if fd:
                    try:
                        fd.close()
                    except Exception as _e:
                        pass
                raise
    else:
        # ═══════════════════════════════════════════════════════════════════
        # Windows: msvcrt.locking (LK_NBLCK) — non-blocking byte-range lock
        #
        # msvcrt.locking ile LK_NBLCK modu, LK_LOCK'tan farklı olarak
        # hemen döner (blocking yapmaz). Kilit tutuluyorsa IOError fırlatır,
        # biz de kendi retry loop'umuzu çalıştırırız.
        #
        # Kilit, dosya handle'ı (fd) açık kaldığı sürece korunur.
        # Process exit veya fd close ile otomatik serbest kalır.
        # Bu, Unix fcntl.flock ile aynı semantiği sağlar.
        #
        # Production (Railway) Linux kullandığı için bu yol yalnızca
        # geliştirme/test amaçlıdır.
        # ═══════════════════════════════════════════════════════════════════
        import msvcrt

        deadline = time.time() + timeout

        # Lock dosyasını hazırla — yoksa oluştur, en az 1 byte içerik yaz
        # (msvcrt.locking boş dosyada çalışmaz)
        if not lock_path.exists():
            try:
                fd = open(lock_path, "x")
                fd.write(" ")  # placeholder — boş dosyada locking çalışmaz
                fd.close()
            except FileExistsError:
                pass  # race: başka process az önce oluşturdu

        while True:
            # Stale lock kontrolü ve temizliği
            if lock_path.exists():
                if _is_lock_stale(lock_path, timeout):
                    _break_stale_lock(lock_path)
                    # Yeniden oluştur (en az 1 byte içerik ile)
                    if not lock_path.exists():
                        try:
                            fd = open(lock_path, "x")
                            fd.write(" ")
                            fd.close()
                        except FileExistsError:
                            pass

            try:
                fd = open(lock_path, "r+")
                # Non-blocking lock dene — kilit tutuluyorsa hemen IOError
                msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
                # Kilit alındı — holder bilgisini doğrudan bu fd'ye yaz
                # (yeni fd açmak lock'u bozabilir)
                info = json.dumps({
                    "holder_pid": os.getpid(),
                    "acquired_at": time.time(),
                    "acquired_iso": datetime.now(timezone.utc).isoformat(),
                })
                fd.seek(0)
                fd.truncate()
                fd.write(info)
                fd.flush()
                return fd  # fd'yi döndür, release kapatacak
            except (OSError, IOError):
                # Kilit başka process'te — fd'yi kapat, bekle, tekrar dene
                if fd:
                    try:
                        fd.close()
                    except Exception as _e:
                        pass
                if time.time() > deadline:
                    holder_info = _read_lock_info(lock_path)
                    raise RuntimeError(
                        f"PID Runtime cross-process kilit alınamadı: {lock_path} "
                        f"({timeout}s timeout). Holder: {holder_info or 'bilinmiyor'}"
                    )
                time.sleep(0.01)  # 10ms — daha hızlı retry
            except Exception as _e:
                if fd:
                    try:
                        fd.close()
                    except Exception as _e:
                        pass
                raise


def _cross_process_lock_release(lock_path: Path, lock_fd=None) -> None:
    """Cross-process kilidi serbest bırakır.

    Platform'a özel kilit serbest bırakma:
    - Unix: fcntl.flock(LOCK_UN) + fd close
    - Windows: msvcrt.locking(LK_UNLCK) + fd close

    Kilit dosyası (lock_path) temizlenmez — holder bilgisi ve
    OS seviyesinde kilidin serbest kaldığının göstergesi olarak kalır.
    Bir sonraki acquire çağrısı lock_path'i yeniden oluşturacaktır.

    Her iki platformda da fd close OS kaynaklarını serbest bırakır.

    Args:
        lock_path: Kilit dosyası yolu (Unix: dosya, Windows: dizin).
        lock_fd: _cross_process_lock_acquire'dan dönen fd.
                 Unix'te file descriptor, Windows'ta None.
    """
    if os.name != "nt":
        # ── Unix: flock serbest bırak + fd kapat ──────────────────────
        if lock_fd is not None:
            import fcntl
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            except Exception as _e:
                pass
            finally:
                try:
                    lock_fd.close()
                except Exception as _e:
                    pass
    else:
        # ── Windows: fd close → msvcrt lock otomatik serbest ──────────
        # msvcrt.locking ile alınan kilit, fd kapatıldığında
        # veya process exit olduğunda otomatik serbest kalır.
        # Unlock + close yerine doğrudan close yeterlidir.
        if lock_fd is not None:
            try:
                lock_fd.close()
            except Exception as _e:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# GC Parameters — 01_Global_Configuration.md
# Hardcoded değer yok. Tüm değerler GC parametrelerinden okunur.
# Env override: GC'deki değer .env üzerinden değiştirilebilir (GC İlkesi).
# ═══════════════════════════════════════════════════════════════════════════════

_GC_PID_PREFIX = os.getenv("GC_PID_PREFIX", "PID")
_GC_PID_DATE_FORMAT = os.getenv("GC_PID_DATE_FORMAT", "YYYYMMDD")
_GC_PID_SEQUENCE_LENGTH = int(os.getenv("GC_PID_SEQUENCE_LENGTH", "4"))
_GC_PID_SEQUENCE_START = int(os.getenv("GC_PID_SEQUENCE_START", "1"))

# Persistence — PID Runtime durum dosyası (bot restart sonrası uniqueness garantisi)
_PID_STATE_DIR = Path(os.getenv("PID_STATE_DIR", "data"))
_PID_STATE_FILE = _PID_STATE_DIR / "pid_runtime_state.json"
# Cross-process lock — Unix: fcntl.flock dosyası, Windows: msvcrt.locking
_PID_LOCK_PATH = _PID_STATE_DIR / "pid_runtime.lock"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERİ MODELLERİ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PIDRecord:
    """AR-002_57: Oluşturulan her PID'nin kaydı.

    PID; üretim paketini, workflow'u, event kayıtlarını ve tüm üretim
    bileşenlerini birbirine bağlayan ortak referans anahtarıdır.
    """
    pid: str
    created_at: str = ""
    date_part: str = ""          # YYYYMMDD
    sequence: int = 0            # Günlük sıra numarası
    is_active: bool = True       # Üretim yaşam döngüsü boyunca aktif
    _created_ts: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """PID kaydını sözlük olarak döndürür."""
        return {
            "pid": self.pid,
            "created_at": self.created_at,
            "date_part": self.date_part,
            "sequence": self.sequence,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PIDRecord:
        """Sözlükten PIDRecord oluşturur (persistence'tan geri yükleme)."""
        return cls(
            pid=data["pid"],
            created_at=data.get("created_at", ""),
            date_part=data.get("date_part", ""),
            sequence=data.get("sequence", 0),
            is_active=data.get("is_active", False),
        )


@dataclass
class PIDValidationResult:
    """PID doğrulama sonucu."""
    is_valid: bool
    pid: str = ""
    error: str = ""
    checks: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "pid": self.pid,
            "error": self.error,
            "checks": self.checks,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PID RUNTIME ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class PIDRuntime:
    """AR-002_71: PID Runtime — Production ID üretiminden sorumlu tek katman.

    PID Runtime:
    - PID üretir (GC parametrelerine göre)
    - PID doğrular (format, tekillik, bütünlük)
    - PID benzersizliğini kontrol eder
    - PID bilgisini döndürür

    PID Runtime:
    - Karar vermez — yalnızca runtime katmanıdır (MASTER-004)
    - Production Package oluşturmaz (AR-002_72)
    - Executor çalıştırmaz (AR-002_76)
    - Hardcoded değer kullanmaz (GC İlkesi)

    Production Güvenceleri:
    - asyncio.Lock ile tüm state mutasyonları atomiktir
    - Günlük sayaç ve registry diskte saklanır
    - Restart sonrası duplicate PID üretilmez
    """

    def __init__(self):
        # ── In-memory state ──────────────────────────────────────────────
        self._pid_registry: dict[str, PIDRecord] = {}
        self._daily_counters: dict[str, int] = {}

        # ── Concurrency control ──────────────────────────────────────────
        # asyncio.Lock: Tüm state okuma/yazma işlemleri bu kilit altında
        # yapılır. Multi-coroutine ortamında race condition ve tutarsız
        # okuma riskini ortadan kaldırır.
        self._lock = asyncio.Lock()

        # ── Persistence'tan geri yükleme ─────────────────────────────────
        self._load_state()

    # ── PID Üretimi ──────────────────────────────────────────────────────

    async def generate(self) -> PIDRecord:
        """AR-002_71 Adım 3: Benzersiz bir PID üretir.

        İki katmanlı kilit altında atomik olarak çalışır:

        Katman 1 — asyncio.Lock (intra-process):
          Aynı process içindeki coroutine'leri sıralar.

        Katman 2 — Cross-process file lock (inter-process):
          Farklı worker process'leri arasında mutual exclusion sağlar.
          Bu kilit altında:
          1. Diskten en güncel state yüklenir (diğer worker'ların PID'leri)
          2. Günlük sıra sayacı bir artırılır
          3. PID string'i oluşturulur
          4. Registry'ye kaydedilir
          5. Durum diske yazılır

        İki worker aynı anda generate() çağırsa bile yalnızca biri
        critical section'a girer. Diğeri kilit serbest kalana kadar bekler
        ve güncel state'i okuyarak devam eder.

        PID formatı (AR-002_57 + GC):
            {GC_PID_PREFIX}-{YYYYMMDD}-{NNNN}

        Returns:
            Oluşturulan PID'nin kaydı.

        Raises:
            RuntimeError: PID üretimi başarısız olursa.
        """
        # Katman 1: Intra-process kilit (coroutine güvenliği)
        async with self._lock:
            # Katman 2: Cross-process kilit (multi-worker güvenliği)
            # Unix: fcntl.flock (kernel-enforced), Windows: msvcrt.locking
            lock_fd = _cross_process_lock_acquire(_PID_LOCK_PATH)
            try:
                # State'i diskten yükle — diğer worker'ların güncellemelerini okur
                self._reload_state_sync()

                today = self._get_today_str()
                sequence = self._next_sequence(today)
                pid = self._build_pid(today, sequence)

                # AR-002_57: Aynı PID ikinci kez üretilemez
                if pid in self._pid_registry:
                    logger.critical(
                        f"🚨 [PID Runtime] DUPLICATE PID tespit edildi: {pid} — "
                        f"bu bir race condition veya persistence hatası göstergesidir"
                    )
                    raise RuntimeError(
                        f"Duplicate PID tespit edildi: {pid}. "
                        f"PID Tekillik Kuralı (AR-002_57) ihlal edildi."
                    )

                record = PIDRecord(
                    pid=pid,
                    date_part=today,
                    sequence=sequence,
                )
                self._pid_registry[pid] = record

                # Diske yaz — cross-process kilit altında, güvenli
                self._save_state()

                logger.info(
                    f"🆔 [PID Runtime] PID oluşturuldu: {pid} "
                    f"(gün: {today}, sıra: {sequence:0{_GC_PID_SEQUENCE_LENGTH}d})"
                )
                return record
            finally:
                _cross_process_lock_release(_PID_LOCK_PATH, lock_fd)

    # ── PID Doğrulama ────────────────────────────────────────────────────

    async def validate(self, pid: str) -> PIDValidationResult:
        """AR-002_71: PID'nin geçerliliğini doğrular.

        Denetimler:
        1. Format kontrolü — GC standartlarına uygunluk
        2. Tarih geçerliliği — YYYYMMDD formatı ve geçerli tarih
        3. Sıra numarası geçerliliği — sayısal ve sıfır dolgulu
        4. Kayıt kontrolü — registry'de mevcut ve aktif

        Kilit altında çalışır — doğrulama anında registry'nin tutarlı
        bir anlık görüntüsünü okur. Diskteki state'ten güncel registry
        yüklenir, böylece diğer worker'ların güncellemeleri de görünür.

        Args:
            pid: Doğrulanacak PID string'i.

        Returns:
            PIDValidationResult — doğrulama sonucu.
        """
        async with self._lock:
            # Diskteki güncel state'i yükle — diğer worker'ların
            # güncellemeleri validate sonucunu etkileyebilir
            self._reload_state_sync()

            checks: dict[str, bool] = {}
            errors: list[str] = []

            # Denetim 1: Format
            checks["format_valid"] = self._check_format(pid)
            if not checks["format_valid"]:
                errors.append(
                    f"PID formatı geçersiz. Beklenen: "
                    f"{_GC_PID_PREFIX}-YYYYMMDD-NNNN, Alınan: {pid}"
                )

            # Denetim 2: Tarih geçerliliği
            checks["date_valid"] = self._check_date(pid)
            if not checks["date_valid"]:
                errors.append(f"PID tarih kısmı geçersiz: {pid}")

            # Denetim 3: Sıra numarası
            checks["sequence_valid"] = self._check_sequence(pid)
            if not checks["sequence_valid"]:
                errors.append(
                    f"PID sıra numarası geçersiz. "
                    f"{_GC_PID_SEQUENCE_LENGTH} haneli sıfır dolgulu olmalı."
                )

            # Denetim 4: Kayıt varlığı ve aktiflik
            checks["registry_check"] = self._check_registry(pid)
            if not checks["registry_check"]:
                errors.append(f"PID kaydı bulunamadı veya pasif: {pid}")

            is_valid = all(checks.values())
            return PIDValidationResult(
                is_valid=is_valid,
                pid=pid,
                error="; ".join(errors) if errors else "",
                checks=checks,
            )

    async def is_unique(self, pid: str) -> bool:
        """AR-002_57: PID tekillik kontrolü.

        Aynı PID'nin daha önce oluşturulup oluşturulmadığını kontrol eder.
        Her PID yalnızca bir üretim paketini temsil eder.

        Multi-worker ortamda güncel sonuç için kontrolden önce diskten
        state'i yeniden yükler. Bu sayede diğer worker'ların oluşturduğu
        PID'ler de görünür olur.

        Kilit altında çalışır — kontrol anında registry'nin tutarlı
        bir anlık görüntüsünü okur.

        Args:
            pid: Kontrol edilecek PID.

        Returns:
            True: PID benzersiz (daha önce oluşturulmamış).
            False: PID zaten mevcut.
        """
        async with self._lock:
            self._reload_state_sync()
            return pid not in self._pid_registry

    # ── PID Sorgulama ────────────────────────────────────────────────────

    async def get_record(self, pid: str) -> Optional[PIDRecord]:
        """PID kaydını döndürür.

        Multi-worker ortamda güncel sonuç için diskten state'i yeniden
        yükler. Bu sayede diğer worker'ların oluşturduğu PID kayıtları
        da görünür olur.

        Kilit altında çalışır — okuma anında registry tutarlıdır.

        Args:
            pid: Sorgulanacak PID.

        Returns:
            PIDRecord veya None (bulunamazsa).
        """
        async with self._lock:
            self._reload_state_sync()
            return self._pid_registry.get(pid)

    async def get_active_pid(self) -> Optional[PIDRecord]:
        """Şu anda aktif olan PID'yi döndürür.

        Multi-worker ortamda güncel sonuç için diskten state'i yeniden
        yükler. Bu sayede diğer worker'ların pasifleştirdiği PID'ler
        bu worker'da da güncel durumda görünür.

        Kilit altında çalışır — iterasyon sırasında dict değişimi
        (RuntimeError: dictionary changed size during iteration) engellenir.

        Returns:
            Aktif PIDRecord veya None (aktif üretim yoksa).
        """
        async with self._lock:
            self._reload_state_sync()
            for record in self._pid_registry.values():
                if record.is_active:
                    return record
            return None

    async def deactivate(self, pid: str) -> bool:
        """PID'yi pasif hale getirir (üretim tamamlandığında).

        PID silinemez — yalnızca pasif hale getirilir (AR-002_57:
        "PID silinemez. Üretim kayıtları arşivlense dahi PID bilgisi korunur.").

        İki katmanlı kilit altında çalışır — deaktivasyon ve persistence
        yazımı atomiktir. Cross-process kilit sayesinde diğer worker'lar
        bu değişikliği diskten okuyabilir.

        Args:
            pid: Pasif hale getirilecek PID.

        Returns:
            True: İşlem başarılı.
            False: PID bulunamadı.
        """
        async with self._lock:
            lock_fd = _cross_process_lock_acquire(_PID_LOCK_PATH)
            try:
                self._reload_state_sync()

                record = self._pid_registry.get(pid)
                if record is None:
                    logger.warning(
                        f"⚠️ [PID Runtime] Pasifleştirme başarısız — "
                        f"PID bulunamadı: {pid}"
                    )
                    return False
                record.is_active = False
                self._save_state()
                logger.info(f"🔒 [PID Runtime] PID pasifleştirildi: {pid}")
                return True
            finally:
                _cross_process_lock_release(_PID_LOCK_PATH, lock_fd)

    # ── Dahili Metodlar ──────────────────────────────────────────────────

    @staticmethod
    def _get_today_str() -> str:
        """GC_PID_DATE_FORMAT'a göre bugünün tarih string'ini döndürür.

        Returns:
            YYYYMMDD formatında tarih string'i.
        """
        return datetime.now(timezone.utc).strftime("%Y%m%d")

    def _next_sequence(self, date_key: str) -> int:
        """Günlük sıra numarasını bir artırır ve döndürür.

        GC_PID_SEQUENCE_START değerinden başlar. Her yeni günde sayaç sıfırlanır.

        UYARI: Bu metod yalnızca _lock altında çağrılmalıdır.
        Tek başına thread-safe değildir.

        Args:
            date_key: YYYYMMDD formatında tarih anahtarı.

        Returns:
            Bir sonraki sıra numarası.
        """
        if date_key not in self._daily_counters:
            self._daily_counters[date_key] = _GC_PID_SEQUENCE_START - 1
        self._daily_counters[date_key] += 1
        return self._daily_counters[date_key]

    def _build_pid(self, date_part: str, sequence: int) -> str:
        """AR-002_57 PID formatına göre PID string'i oluşturur.

        Format: {GC_PID_PREFIX}-{YYYYMMDD}-{NNNN}

        Args:
            date_part: YYYYMMDD formatında tarih.
            sequence: Günlük sıra numarası.

        Returns:
            PID string'i (örn: PID-20260713-0001).
        """
        seq_str = f"{sequence:0{_GC_PID_SEQUENCE_LENGTH}d}"
        return f"{_GC_PID_PREFIX}-{date_part}-{seq_str}"

    def _check_format(self, pid: str) -> bool:
        """PID format kontrolü: {PREFIX}-{8 haneli tarih}-{N haneli sıra}"""
        parts = pid.split("-")
        if len(parts) != 3:
            return False
        prefix, date_part, seq_part = parts
        if prefix != _GC_PID_PREFIX:
            return False
        if len(date_part) != 8 or not date_part.isdigit():
            return False
        if len(seq_part) != _GC_PID_SEQUENCE_LENGTH or not seq_part.isdigit():
            return False
        return True

    @staticmethod
    def _check_date(pid: str) -> bool:
        """PID içindeki tarih kısmının geçerli bir tarih olup olmadığını kontrol eder."""
        try:
            parts = pid.split("-")
            if len(parts) < 2:
                return False
            date_part = parts[1]
            if len(date_part) != 8:
                return False
            datetime.strptime(date_part, "%Y%m%d")
            return True
        except (ValueError, IndexError):
            return False

    def _check_sequence(self, pid: str) -> bool:
        """PID içindeki sıra numarasının geçerli olup olmadığını kontrol eder."""
        try:
            parts = pid.split("-")
            if len(parts) < 3:
                return False
            seq_part = parts[2]
            if len(seq_part) != _GC_PID_SEQUENCE_LENGTH:
                return False
            seq_num = int(seq_part)
            return seq_num >= _GC_PID_SEQUENCE_START
        except (ValueError, IndexError):
            return False

    def _check_registry(self, pid: str) -> bool:
        """PID'nin registry'de kayıtlı ve aktif olup olmadığını kontrol eder.

        UYARI: Bu metod yalnızca _lock altında çağrılmalıdır.
        """
        record = self._pid_registry.get(pid)
        if record is None:
            return False
        return record.is_active

    # ── Durum ve İstatistik ──────────────────────────────────────────────

    async def get_stats(self) -> dict:
        """PID Registry istatistiklerini döndürür.

        Kilit altında tutarlı bir anlık görüntü alır.

        Returns:
            Toplam PID, aktif PID, günlük sayaç bilgileri.
        """
        async with self._lock:
            # Diskteki güncel state'i yükle — diğer worker'ların
            # güncellemeleri istatistiklere yansıtılmalı
            self._reload_state_sync()

            total = len(self._pid_registry)
            active = sum(1 for r in self._pid_registry.values() if r.is_active)
            return {
                "total_pids": total,
                "active_pids": active,
                "daily_counters": dict(self._daily_counters),
                "gc_prefix": _GC_PID_PREFIX,
                "gc_date_format": _GC_PID_DATE_FORMAT,
                "gc_sequence_length": _GC_PID_SEQUENCE_LENGTH,
                "gc_sequence_start": _GC_PID_SEQUENCE_START,
                "state_file": str(_PID_STATE_FILE),
            }

    # ── Persistence ──────────────────────────────────────────────────────

    def _reload_state_sync(self) -> None:
        """Diskten state'i yeniden yükler — cross-worker senkronizasyon.

        Yalnızca cross-process kilit altında çağrılmalıdır. Diğer worker'ların
        diske yazdığı güncellemeleri bellek içi state'e merge eder.

        Merge stratejisi:
        - Sayaçlar: max(değerler) alınır (her iki worker'ın en son değeri)
        - Registry: Bilinmeyen PID'ler eklenir, bilinenler güncellenir
          (başka worker'ın pasifleştirdiği PID'ler bu worker'da da pasif olur)
        """
        if not _PID_STATE_FILE.exists():
            return
        try:
            raw = _PID_STATE_FILE.read_text(encoding="utf-8")
            state = json.loads(raw)

            # Merge counters — max değeri al (sayaçlar yalnızca artar)
            for date_key, count in state.get("daily_counters", {}).items():
                current = self._daily_counters.get(date_key, 0)
                self._daily_counters[date_key] = max(current, int(count))

            # Merge registry — yeni PID'leri ekle, var olanları güncelle
            for entry in state.get("pid_registry", []):
                pid = entry["pid"]
                if pid in self._pid_registry:
                    existing = self._pid_registry[pid]
                    if not entry.get("is_active", True):
                        existing.is_active = False
                else:
                    self._pid_registry[pid] = PIDRecord.from_dict(entry)

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"⚠️ [PID Runtime] State reload başarısız, mevcut state korunuyor: {e}")
        except Exception as e:
            logger.warning(f"⚠️ [PID Runtime] State reload hatası: {e}")

    def _save_state(self) -> None:
        """Mevcut durumu diske yazar.

        Kaydedilen veriler:
        - daily_counters: Günlük sıra sayaçları (restart sonrası duplicate önleme)
        - pid_registry: Tüm PID kayıtları (restart sonrası uniqueness kontrolü)

        UYARI: Bu metod yalnızca _lock altında çağrılmalıdır.
        Disk yazımı senkrondur — kritik bölüm içinde I/O yapılır.
        PID üretimi düşük frekanslı bir işlem olduğu için (üretim başına 1 kez)
        bu kabul edilebilir bir trade-off'tur.

        Retry mekanizması: Windows'ta anti-virüs veya dosya sistemi
        gecikmeleri nedeniyle replace() geçici olarak başarısız olabilir.
        3 deneme, exponential backoff (0.05s → 0.1s → 0.2s).

        Hata durumunda log basar, exception fırlatmaz —
        memory state korunur, yalnızca persistence gecikir.
        """
        state = {
            "daily_counters": dict(self._daily_counters),
            "pid_registry": [
                r.to_dict() for r in self._pid_registry.values()
            ],
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "gc_prefix": _GC_PID_PREFIX,
            "gc_sequence_length": _GC_PID_SEQUENCE_LENGTH,
        }

        _PID_STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp_path = _PID_STATE_FILE.with_suffix(".tmp")

        last_error = None
        for attempt in range(3):
            try:
                # Atomik yazım: önce temp dosyaya yaz, sonra rename
                tmp_path.write_text(
                    json.dumps(state, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                tmp_path.replace(_PID_STATE_FILE)
                return  # başarılı
            except Exception as e:
                last_error = e
                if attempt < 2:
                    time.sleep(0.05 * (2 ** attempt))  # 0.05, 0.1, 0.2

        logger.error(
            f"❌ [PID Runtime] Durum kaydedilemedi (3 deneme): {last_error}"
        )

    def _load_state(self) -> None:
        """Diskten kaydedilmiş durumu geri yükler.

        Restart sonrası çağrılır. Dosya yoksa veya bozuksa boş state ile başlar.

        Yükleme başarılı olduğunda:
        - Günlük sayaçlar geri yüklenir → duplicate PID önlenir
        - PID kayıtları geri yüklenir → uniqueness kontrolü devam eder
        - Tüm PID'ler pasif olarak işaretlenir (önceki üretimler tamamlanmış kabul edilir)
        """
        if not _PID_STATE_FILE.exists():
            logger.info("📋 [PID Runtime] State dosyası bulunamadı, boş state ile başlanıyor.")
            return

        try:
            raw = _PID_STATE_FILE.read_text(encoding="utf-8")
            state = json.loads(raw)

            # Günlük sayaçları geri yükle
            loaded_counters = state.get("daily_counters", {})
            for date_key, count in loaded_counters.items():
                self._daily_counters[date_key] = int(count)

            # PID kayıtlarını geri yükle (tümü pasif — restart sonrası
            # önceki üretimler tamamlanmış kabul edilir)
            loaded_registry = state.get("pid_registry", [])
            for entry in loaded_registry:
                record = PIDRecord.from_dict(entry)
                record.is_active = False  # restart sonrası pasif
                self._pid_registry[record.pid] = record

            prev_updated = state.get("updated_at", "bilinmiyor")
            logger.info(
                f"📋 [PID Runtime] State geri yüklendi: "
                f"{len(loaded_counters)} gün sayacı, "
                f"{len(loaded_registry)} PID kaydı "
                f"(son güncelleme: {prev_updated})"
            )
        except json.JSONDecodeError as e:
            logger.error(
                f"❌ [PID Runtime] State dosyası bozuk, boş state ile başlanıyor: {e}"
            )
        except Exception as e:
            logger.error(
                f"❌ [PID Runtime] State yüklenemedi, boş state ile başlanıyor: {e}"
            )

    # ── Test Yardımcıları ────────────────────────────────────────────────

    async def reset(self) -> None:
        """PID Registry'yi temizler (yalnızca test amaçlı).

        UYARI: Üretim ortamında çağrılmamalıdır. PID'ler silinemez
        (AR-002_57: PID silinemez).
        """
        async with self._lock:
            logger.warning("⚠️ [PID Runtime] Registry sıfırlandı (test amaçlı)")
            self._pid_registry.clear()
            self._daily_counters.clear()
            # Disk state'ini de temizle
            for _p in (_PID_STATE_FILE, _PID_STATE_FILE.with_suffix(".tmp"),
                        _PID_LOCK_PATH):
                try:
                    if _p.exists():
                        if _p.is_dir():
                            _p.rmdir()
                        else:
                            _p.unlink()
                except Exception as _e:
                    pass


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MODÜL YARDIMCI FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def validate_pid_static(pid: str) -> PIDValidationResult:
    """Statik PID doğrulama — registry'den bağımsız, yalnızca format kontrolü.

    PID Runtime instance'ı oluşturmadan hızlı format doğrulaması için kullanılır.
    Registry kontrolü yapmaz — yalnızca format, tarih ve sıra numarası denetimi.

    Bu fonksiyon senkrondur ve lock gerektirmez — immutable GC parametrelerini okur.

    Args:
        pid: Doğrulanacak PID string'i.

    Returns:
        PIDValidationResult — format doğrulama sonucu.
    """
    checks: dict[str, bool] = {}
    errors: list[str] = []

    # Format kontrolü
    parts = pid.split("-")
    checks["format_valid"] = (
        len(parts) == 3
        and parts[0] == _GC_PID_PREFIX
        and len(parts[1]) == 8
        and parts[1].isdigit()
        and len(parts[2]) == _GC_PID_SEQUENCE_LENGTH
        and parts[2].isdigit()
    )
    if not checks["format_valid"]:
        errors.append(
            f"PID formatı geçersiz. Beklenen: "
            f"{_GC_PID_PREFIX}-YYYYMMDD-NNNN"
        )

    # Tarih kontrolü
    checks["date_valid"] = False
    try:
        if len(parts) >= 2:
            datetime.strptime(parts[1], "%Y%m%d")
            checks["date_valid"] = True
    except (ValueError, IndexError):
        errors.append("PID tarih kısmı geçersiz.")

    # Sıra numarası kontrolü
    checks["sequence_valid"] = False
    try:
        if len(parts) >= 3 and len(parts[2]) == _GC_PID_SEQUENCE_LENGTH:
            seq = int(parts[2])
            checks["sequence_valid"] = seq >= _GC_PID_SEQUENCE_START
    except (ValueError, IndexError):
        pass
    if not checks["sequence_valid"]:
        errors.append("PID sıra numarası geçersiz.")

    is_valid = all(checks.values())
    return PIDValidationResult(
        is_valid=is_valid,
        pid=pid,
        error="; ".join(errors) if errors else "",
        checks=checks,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

pid_runtime = PIDRuntime()
"""AR-002_71: Global PID Runtime singleton'ı.

Tüm modüller bu singleton üzerinden PID işlemlerini gerçekleştirir.
Hiçbir modül kendi PIDRuntime instance'ını oluşturamaz
(AR-002_57: PID Merkeziyet Kuralı).

Production garantileri:
- asyncio.Lock: Tüm state mutasyonları atomik
- Disk persistence: Restart sonrası sayaç ve registry korunur
- Duplicate PID önleme: Aynı gün restart olsa bile sayaç devam eder
"""
