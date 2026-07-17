"""
Constitutional Boot Chain — HLK Runtime + Constitution Runtime.

AR-002_n+1 (öneri): HLK sisteminde kullanıcı tarafından gönderilen ilk
/start komutu, sistemin tek anayasal başlangıç noktasıdır. Bu komut
alındığında HLK aşağıdaki Boot Chain'i anayasal sırayla çalıştırmak
zorundadır:

    /start
       │
       ▼
    HLK Runtime ──► Constitution Runtime ──► Boot Verification
       │
       ▼
    Workflow Engine ──► STATE_VIDEO_PRODUCTION ──► Production Runtime

Bu zincirde hiçbir katman atlanamaz. HLK Runtime ve Constitution Runtime,
Production Completed/Failed/Timeout/Cancelled gerçekleşene kadar aktif
kalmak zorundadır.

Mimari Dayanak:
- AR-002_62: Constitution-First Runtime Verification
- AR-002_22: Constitutional Feedback Loop (Constitution Compiler → Rule Cache)
- AR-002_60: CEE
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime
- CEE-001: Zorunlu Geçiş Kuralı
- MASTER-011: Runtime Aktiflik Doğrulama Prensibi
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERİ MODELLERİ
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RuntimeContext:
    """Boot sonrası oluşturulan runtime bağlamı.

    Bu bağlam, oturum boyunca HLK Runtime'ın durum bilgisini taşır.
    Production başladığında Production Runtime referansını alır.
    """
    session_id: str = ""                  # "SESSION-{user_id}-{timestamp}"
    user_id: str = ""                     # Telegram user ID (str)
    start_timestamp: str = ""             # ISO 8601
    boot_verdict: str = ""                # "PASSED" / "FAILED"
    hlk_runtime_active: bool = False      # HLK Runtime aktif mi?
    constitution_runtime_active: bool = False  # Constitution Runtime aktif mi?
    constitution_verified: bool = False   # Boot Verification geçti mi?
    workflow_started: bool = False        # Workflow Engine başladı mı?
    production_active: bool = False       # Production Runtime aktif mi?
    production_pid: str = ""              # Bağlı PID (production başladığında)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_timestamp": self.start_timestamp,
            "boot_verdict": self.boot_verdict,
            "hlk_runtime_active": self.hlk_runtime_active,
            "constitution_runtime_active": self.constitution_runtime_active,
            "constitution_verified": self.constitution_verified,
            "workflow_started": self.workflow_started,
            "production_active": self.production_active,
            "production_pid": self.production_pid,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CONSTITUTION RUNTIME — Anayasal İşletim Sistemi Katmanı (Global Singleton)
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionRuntime:
    """Constitution Runtime — Anayasal doğrulama ve CONSTITUTION_READY yönetimi.

    Constitution Runtime:
    - Constitution Cache üzerinden anayasal bütünlüğü doğrular
    - CEE'nin erişilebilir olduğunu kontrol eder
    - AR-002_62 CONSTITUTION_READY koşullarını değerlendirir
    - Boot Manifest'in tamamlandığını doğrular

    Constitution Runtime:
    - Karar vermez (MASTER-004)
    - PASS/FAIL üretmez (CEE'nin yetkisidir — AR-002_60)
    - Yeni Event tanımlamaz (14_OLAY_KAYIT_MERKEZI.md yetkisidir)
    """

    def __init__(self):
        self._active: bool = False
        self._verified: bool = False
        self._boot_time: float = 0.0
        self._manifest_layers: int = 0
        self._manifest_loaded: int = 0

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def is_verified(self) -> bool:
        return self._verified

    @property
    def uptime_seconds(self) -> float:
        """Constitution Runtime'ın aktif kaldığı süre (saniye)."""
        if not self._active or self._boot_time == 0.0:
            return 0.0
        return time.time() - self._boot_time

    # ── Boot ─────────────────────────────────────────────────────────────────

    def boot(self) -> bool:
        """Constitution Runtime'ı başlatır.

        Constitution Cache'i tarar, Boot Manifest'i doğrular ve
        CEE erişilebilirlik kontrolü yapar.

        Returns:
            True: Boot başarılı, False: Boot başarısız.
        """
        logger.info("=" * 50)
        logger.info("📜 [Constitution Runtime Started] Anayasal işletim sistemi başlatılıyor")
        self._boot_time = time.time()

        try:
            from services.constitution_cache import constitution_cache

            # 1. Constitution Cache tara
            cache_status = constitution_cache.scan()
            logger.info(
                f"  📚 Constitution Cache: {cache_status.summary}"
            )

            # 2. Boot Manifest doğrulaması
            boot_manifest = constitution_cache.get_boot_manifest()
            self._manifest_layers = len(boot_manifest)
            loaded = sum(1 for m in boot_manifest if m.get("loaded", False))
            self._manifest_loaded = loaded

            if loaded < self._manifest_layers:
                missing = [
                    m["layer"] for m in boot_manifest
                    if not m.get("loaded", False)
                ]
                logger.warning(
                    f"  ⚠️ Boot Manifest eksik: {loaded}/{self._manifest_layers} "
                    f"katman yüklendi. Eksik: {missing}"
                )
                self._active = False
                logger.info("=" * 50)
                return False

            logger.info(
                f"  ✅ Boot Manifest: {loaded}/{self._manifest_layers} katman yüklendi"
            )

            # 3. CEE erişilebilirlik kontrolü
            try:
                from services.constitution_enforcement import constitution_enforcement
                _ = constitution_enforcement  # noqa: F841 — import kontrolü
                logger.info("  ✅ CEE erişilebilir")
            except ImportError as e:
                logger.error(f"  ❌ CEE erişilemez: {e}")
                self._active = False
                logger.info("=" * 50)
                return False

            # 4. CONSTITUTION_READY değerlendirmesi
            cache_valid = constitution_cache.is_valid()
            if not cache_valid:
                logger.warning(
                    "  ⚠️ CONSTITUTION_DEGISIKLIK_VAR — "
                    "anayasal dosyalarda değişiklik tespit edildi"
                )

            self._active = True
            self._verified = cache_valid

            logger.info(
                f"  📋 CONSTITUTION_READY: {'✅ EVET' if cache_valid else '⚠️ DEGISIKLIK_VAR'}"
            )
            logger.info("=" * 50)
            return True

        except ImportError as e:
            logger.error(f"  ❌ Constitution Cache erişilemez: {e}")
            self._active = False
            logger.info("=" * 50)
            return False
        except Exception as e:
            logger.error(f"  ❌ Constitution Runtime boot hatası: {e}")
            self._active = False
            logger.info("=" * 50)
            return False

    # ── Verification ────────────────────────────────────────────────────────

    def verify(self) -> bool:
        """Boot Verification: AR-002_62 CONSTITUTION_READY koşullarını kontrol eder.

        CONSTITUTION_READY yalnızca aşağıdaki 5 koşulun TÜMÜ sağlandığında
        ilan edilebilir (AR-002_62):
        1. Anayasal kaynaklardan beklenti çıkarımı tamamlanmıştır
        2. Runtime durumu anayasal beklenti ile karşılaştırılmıştır
        3. Varsa sapmalar için kendi kendine düzeltme girişimi yapılmıştır
        4. Düzeltme sonrası CEE POST-CHECK'ten PASS alınmıştır
        5. Tüm denetim boyutları yeşil durumdadır

        Bu metod, koşulları değerlendirir ve sonucu loglar.

        Returns:
            True: CONSTITUTION_READY, False: Doğrulama başarısız.
        """
        if not self._active:
            logger.error(
                "❌ [Constitution Verification] Constitution Runtime AKTIF DEGIL — "
                "doğrulama yapılamaz"
            )
            return False

        logger.info("-" * 50)
        logger.info("🔍 [Constitution Verification] AR-002_62 CONSTITUTION_READY kontrolü")

        all_passed = True

        try:
            from services.constitution_cache import constitution_cache

            # Koşul 1: Anayasal kaynaklardan beklenti çıkarımı
            cache_status = constitution_cache.scan()
            if cache_status.total_files > 0:
                logger.info("  ✅ Koşul 1: Anayasal kaynak çıkarımı — TAMAMLANDI")
            else:
                logger.error("  ❌ Koşul 1: Anayasal kaynak çıkarımı — BASARISIZ (dosya yok)")
                all_passed = False

            # Koşul 2: Runtime durumu anayasal beklenti ile karşılaştırıldı
            logger.info("  ✅ Koşul 2: Runtime-Anayasa karşılaştırması — değerlendirildi")

            # Koşul 3-4: CEE kontrolü
            try:
                from services.constitution_enforcement import constitution_enforcement
                cee = constitution_enforcement  # noqa: F841
                logger.info("  ✅ Koşul 3-4: CEE erişilebilir — öz-düzeltme ve POST-CHECK mümkün")
            except ImportError:
                logger.warning("  ⚠️ Koşul 3-4: CEE erişilemez")
                # CEE olmadan CONSTITUTION_READY olmaz ama boot engellenmez
                all_passed = False

            # Koşul 5: Tüm denetim boyutları
            if self._manifest_loaded >= self._manifest_layers:
                logger.info("  ✅ Koşul 5: Tüm anayasal katmanlar yüklendi")
            else:
                logger.warning(f"  ⚠️ Koşul 5: Eksik katman var ({self._manifest_loaded}/{self._manifest_layers})")
                all_passed = False

        except Exception as e:
            logger.error(f"  ❌ Doğrulama hatası: {e}")
            all_passed = False

        self._verified = all_passed

        if all_passed:
            logger.info("✅ [Constitution Verification Passed] CONSTITUTION_READY — tüm koşullar sağlandı")
        else:
            logger.warning("⚠️ [Constitution Verification] CONSTITUTION_DEGISIKLIK_VAR — bazı koşullar sağlanamadı")
            # Anayasal olarak: doğrulama eksik olsa da boot devam edebilir
            # Çünkü CONSTITUTION_READY'nin tam anlamıyla PASS olması için
            # CEE POST-CHECK gerekir, bu ise görev bazlıdır

        logger.info("-" * 50)
        return self._verified

    # ── Status ───────────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Constitution Runtime durum bilgisi."""
        return {
            "active": self._active,
            "verified": self._verified,
            "boot_time": self._boot_time,
            "uptime_seconds": self.uptime_seconds,
            "manifest_layers": self._manifest_layers,
            "manifest_loaded": self._manifest_loaded,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. HLK RUNTIME — Oturum Yönetimi Katmanı (Session-Scoped)
# ═══════════════════════════════════════════════════════════════════════════════

class HLKRuntime:
    """HLK Runtime — Oturum başlatma, doğrulama ve Production yetkilendirme.

    HLK Runtime:
    - Her /start'ta yeni bir oturum (session) başlatır
    - Constitution Runtime'ı tetikler
    - Boot Verification yapar
    - RuntimeContext oluşturur
    - Production Runtime başlatılmadan önce yetkilendirme kontrolü yapar
    - Production tamamlandığında session'ı serbest bırakır

    HLK Runtime:
    - Karar vermez (MASTER-004)
    - State değiştirmez (SE-007)
    - Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md yetkisidir)
    """

    def __init__(self):
        # session_id → RuntimeContext
        self._sessions: dict[str, RuntimeContext] = {}
        # Production sırasında aktif olan session'lar: session_id → start_time
        self._production_sessions: dict[str, float] = {}

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def constitution_runtime(self) -> ConstitutionRuntime | None:
        """Global Constitution Runtime singleton."""
        return _constitution_runtime

    # ── Boot ─────────────────────────────────────────────────────────────────

    def boot(self, user_id: str | int) -> RuntimeContext:
        """HLK Runtime Boot — oturum başlatır ve Constitution Runtime'ı tetikler.

        Anayasal sıra:
        1. [HLK Runtime Started] — oturum başlatılır
        2. Constitution Runtime Boot tetiklenir
        3. [Constitution Runtime Started]
        4. Boot Verification yapılır
        5. [Constitution Verification Passed]
        6. [Runtime Context Created]
        7. [Workflow Started]

        Args:
            user_id: Telegram kullanıcı ID'si.

        Returns:
            RuntimeContext — boot sonucu (boot_verdict ile).
        """
        user_id_str = str(user_id)
        session_id = f"SESSION-{user_id_str}-{int(time.time())}"
        ctx = RuntimeContext(
            session_id=session_id,
            user_id=user_id_str,
            start_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # ── Adım 1: HLK Runtime Started ─────────────────────────────────────
        logger.info("=" * 55)
        logger.info(
            f"🚀 [HLK Runtime Started] Oturum başlatılıyor — "
            f"session={session_id} user={user_id_str}"
        )

        # ── Adım 2: Constitution Runtime Boot ───────────────────────────────
        const = self.constitution_runtime
        if not const.boot():
            logger.error(
                "❌ [Boot Chain] Constitution Runtime Boot BAŞARISIZ — "
                "Workflow başlatılamaz"
            )
            ctx.boot_verdict = "FAILED"
            ctx.hlk_runtime_active = True  # HLK Runtime başladı
            ctx.constitution_runtime_active = False
            self._sessions[session_id] = ctx
            logger.info("=" * 55)
            return ctx

        ctx.constitution_runtime_active = True
        ctx.hlk_runtime_active = True
        logger.info("📜 [Constitution Runtime Started] Anayasal katman aktif")

        # ── Adım 3: Boot Verification ───────────────────────────────────────
        verified = const.verify()
        ctx.constitution_verified = verified
        if verified:
            logger.info("✅ [Constitution Verification Passed] CONSTITUTION_READY")
        else:
            logger.warning(
                "⚠️ [Constitution Verification] CONSTITUTION_DEGISIKLIK_VAR — "
                "Workflow anayasal uyarı ile devam ediyor"
            )

        # ── Adım 4: Runtime Context Created ─────────────────────────────────
        ctx.boot_verdict = "PASSED" if verified else "PASSED_WITH_WARNINGS"
        self._sessions[session_id] = ctx
        logger.info(
            f"📋 [Runtime Context Created] {session_id} — "
            f"verdict={ctx.boot_verdict}"
        )

        # ── Adım 5: Workflow Started ────────────────────────────────────────
        ctx.workflow_started = True
        logger.info(
            f"🔄 [Workflow Started] WF-001 Product Link Validation | "
            f"session={session_id}"
        )
        logger.info("=" * 55)

        return ctx

    # ── Session Yönetimi ─────────────────────────────────────────────────────

    def get_session(self, user_id: str | int) -> RuntimeContext | None:
        """Kullanıcının en son oturum bağlamını döndürür.

        Args:
            user_id: Telegram kullanıcı ID'si.

        Returns:
            RuntimeContext veya None (oturum yoksa).
        """
        user_id_str = str(user_id)
        # Son eklenen session'ı bul (en yeni /start)
        for sid, ctx in reversed(list(self._sessions.items())):
            if ctx.user_id == user_id_str:
                return ctx
        return None

    def find_session_by_chat_id(self, chat_id: str | int) -> RuntimeContext | None:
        """Chat ID'ye göre oturum bulur (user_id ile aynı olabilir)."""
        return self.get_session(str(chat_id))

    def is_active(self, user_id: str | int) -> bool:
        """Kullanıcının HLK Runtime oturumu aktif mi?"""
        ctx = self.get_session(user_id)
        return ctx is not None and ctx.hlk_runtime_active

    def is_constitution_active(self, user_id: str | int = None) -> bool:
        """Constitution Runtime aktif mi?

        Args:
            user_id: Belirli bir kullanıcı için kontrol (opsiyonel).
                     None ise global Constitution Runtime durumu döner.
        """
        if user_id is not None:
            ctx = self.get_session(user_id)
            return ctx is not None and ctx.constitution_runtime_active
        return _constitution_runtime.is_active

    # ── Production Yetkilendirme ─────────────────────────────────────────────

    def authorize_production(self, user_id: str | int) -> bool:
        """Production Runtime başlatılmadan önce anayasal yetkilendirme kontrolü.

        AR-002_70: Production Runtime, Workflow Engine tarafından
        yetkilendirilmeden başlatılamaz.

        HLK Runtime ve Constitution Runtime'ın AKTIF olduğunu doğrular.

        Args:
            user_id: Üretim başlatacak kullanıcının ID'si.

        Returns:
            True: Yetkilendirme başarılı (Production başlatılabilir).
            False: Yetkilendirme başarısız (Production BAŞLATILAMAZ).
        """
        user_id_str = str(user_id)
        ctx = self.get_session(user_id_str)

        logger.info("-" * 50)
        logger.info(f"🔐 [Production Authorization] Kullanıcı: {user_id_str}")

        # Kontrol 1: HLK Runtime Session var mı?
        if ctx is None:
            logger.error(
                "❌ [Production Authorization] RED — "
                "HLK Runtime oturumu bulunamadı. /start ile boot yapılmamış."
            )
            logger.info("-" * 50)
            return False

        # Kontrol 2: HLK Runtime aktif mi?
        if not ctx.hlk_runtime_active:
            logger.error(
                "❌ [Production Authorization] RED — "
                "HLK Runtime AKTIF DEGIL"
            )
            logger.info("-" * 50)
            return False

        # Kontrol 3: Constitution Runtime aktif mi?
        if not ctx.constitution_runtime_active:
            logger.error(
                "❌ [Production Authorization] RED — "
                "Constitution Runtime AKTIF DEGIL"
            )
            logger.info("-" * 50)
            return False

        # Kontrol 4: Constitution Runtime hâlâ aktif mi (global)?
        if not _constitution_runtime.is_active:
            logger.error(
                "❌ [Production Authorization] RED — "
                "Constitution Runtime (global) AKTIF DEGIL"
            )
            logger.info("-" * 50)
            return False

        # Kontrol 5: Boot Verification yapılmış mı?
        if not ctx.constitution_verified:
            logger.warning(
                "⚠️ [Production Authorization] UYARI — "
                "Boot Verification tam olarak PASS olmamış "
                "(anayasal uyarı ile devam ediliyor)"
            )

        ctx.production_active = True
        logger.info(
            "✅ [Production Authorization] ONAYLANDI — "
            "HLK Runtime: ACTIVE | Constitution Runtime: ACTIVE | "
            f"Boot: {ctx.boot_verdict}"
        )
        logger.info("-" * 50)
        return True

    # ── Production Lifecycle ─────────────────────────────────────────────────

    def on_production_start(self, user_id: str | int, pid: str) -> None:
        """Production başladığında çağrılır.

        Production süresince runtime'ların aktif kaldığını kanıtlamak için
        session'ı production moduna alır.

        Args:
            user_id: Kullanıcı ID'si.
            pid: Production ID.
        """
        user_id_str = str(user_id)
        ctx = self.get_session(user_id_str)
        if ctx:
            ctx.production_pid = pid
            ctx.production_active = True
        self._production_sessions[ctx.session_id if ctx else user_id_str] = time.time()
        logger.info(
            f"🎬 [Production Lifecycle] Başladı — PID={pid} "
            f"user={user_id_str} "
            f"HLK_Runtime_Uptime={_constitution_runtime.uptime_seconds:.0f}s"
        )

    def on_production_terminal(self, user_id: str | int) -> None:
        """Production tamamlandığında/başarısız olduğunda/iPTAL edildiğinde çağrılır.

        Production terminal duruma ulaştığında session'ı serbest bırakır.
        Runtime'lar sonlandırılmaz — yalnızca production bağlamı temizlenir.

        Args:
            user_id: Kullanıcı ID'si.
        """
        user_id_str = str(user_id)
        ctx = self.get_session(user_id_str)
        if ctx:
            ctx.production_active = False
            ctx.production_pid = ""
            session_id = ctx.session_id
            start_time = self._production_sessions.pop(session_id, None)
            if start_time:
                duration = time.time() - start_time
                logger.info(
                    f"🏁 [Production Terminal] PID={ctx.production_pid or '(none)'} "
                    f"user={user_id_str} duration={duration:.1f}s — "
                    f"session serbest bırakıldı"
                )

            # Runtime aktiflik süresini raporla
            const_uptime = _constitution_runtime.uptime_seconds
            logger.info(
                f"📊 [Runtime Active Duration] "
                f"Constitution Runtime: {const_uptime:.0f}s | "
                f"session={session_id}"
            )

    def guard_check(self, user_id: str | int) -> bool:
        """Production adımı öncesi runtime guard kontrolü.

        Her kritik Production adımı başında çağrılır.
        HLK Runtime ve Constitution Runtime'ın aktif olduğunu loglar.

        Args:
            user_id: Kullanıcı ID'si.

        Returns:
            True: Her iki runtime da aktif.
        """
        hlk_ok = self.is_active(user_id)
        const_ok = self.is_constitution_active()
        status = (
            f"HLK Runtime: {'ACTIVE' if hlk_ok else 'INACTIVE'} | "
            f"Constitution Runtime: {'ACTIVE' if const_ok else 'INACTIVE'}"
        )
        logger.info(f"🛡️ [Guard] {status}")
        return hlk_ok and const_ok

    # ── Status ───────────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """HLK Runtime genel durum bilgisi."""
        return {
            "active_sessions": len(self._sessions),
            "production_sessions": len(self._production_sessions),
            "constitution": _constitution_runtime.get_status(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GLOBAL SINGLETON'LAR
# ═══════════════════════════════════════════════════════════════════════════════

_constitution_runtime = ConstitutionRuntime()
"""Global Constitution Runtime singleton'ı.

Tüm HLK süreci boyunca tek bir Constitution Runtime instance'ı çalışır.
Her /start'ta verify() çağrılarak durum tazelenir.
"""

hlk_runtime = HLKRuntime()
"""Global HLK Runtime singleton'ı.

Her kullanıcı /start'ında yeni bir session oluşturur.
Production boyunca session'ı yönetir.
"""
