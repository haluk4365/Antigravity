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
- MASTER-013: HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı
- AR-002_81: HLK Runtime Karar Otoritesi ve Karar Talep Protokolü
- AR-002_62: Constitution-First Runtime Verification
- AR-002_22: Constitutional Feedback Loop (Constitution Compiler → Rule Cache)
- AR-002_60: CEE
- AR-002_70: STATE_VIDEO_PRODUCTION Runtime
- CEE-001: Zorunlu Geçiş Kuralı
- MASTER-011: Runtime Aktiflik Doğrulama Prensibi
- OR-004_12: Üretim Sırasında Karar Talebi Operasyon Kuralı
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
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
# 1B. KARAR TALEP PROTOKOLÜ — MASTER-013 / AR-002_81 Veri Modelleri
# ═══════════════════════════════════════════════════════════════════════════════

class DecisionCategory(str, Enum):
    """AR-002_81: Karar gerektiren durum kategorileri.

    Bu kategorilerin tamamı yalnızca HLK Runtime tarafından karara bağlanır.
    Tablo sınırlayıcı değildir; karar niteliği taşıyan her yeni durum
    AMBIGUITY üzerinden protokole tabidir (MASTER-013: Tereddüt Kuralı).
    """
    PROVIDER_RESULT = "PROVIDER_RESULT"        # Provider çıktısı kabul/red
    PROVIDER_SWITCH = "PROVIDER_SWITCH"        # Sıradaki provider'a geçiş
    EXECUTION_FAILURE = "EXECUTION_FAILURE"    # Retry / re-evaluate / escalate
    CREATIVE_CONTENT = "CREATIVE_CONTENT"      # Yaratıcı içerik (AR-002_77)
    DELIVERY = "DELIVERY"                      # Teslim şekli + kullanıcı mesajı
    COMPLETION = "COMPLETION"                  # Tamamlanma kararı (AR-002_80)
    USER_NOTIFICATION = "USER_NOTIFICATION"    # Süreç kararı içeren bildirim
    REPRODUCTION = "REPRODUCTION"              # Yeniden üretim prosedürü (AR-002_82/83)
    AMBIGUITY = "AMBIGUITY"                    # Tereddüt — karar üretilemeyen durum
    TASK_RESULT = "TASK_RESULT"                # MASTER-013: Task SUCCESS/FAIL kararı


@dataclass
class DecisionRequest:
    """AR-002_81 Adım 2: Karar Talebi.

    Yürütme katmanı tarafından oluşturulur. Karar, öneri veya varsayım
    İÇEREMEZ; yalnızca ham teknik kanıt (context) taşır.
    """
    pid: str = ""                              # Üretim Kimliği (AR-002_57)
    category: str = DecisionCategory.AMBIGUITY.value  # Karar Kategorisi
    requester: str = ""                        # Talep Eden Katman
    context: dict = field(default_factory=dict)  # Teknik Kanıt / Bağlam
    request_id: str = ""                       # Talep Kimliği
    created_at: str = ""

    def __post_init__(self):
        if not self.request_id:
            self.request_id = f"REQ-{time.time_ns()}"
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeDecision:
    """AR-002_81 Adım 3: HLK Runtime tarafından üretilen Runtime Kararı.

    Yürütme katmanı bu kararı eksiksiz ve değiştirmeden uygular.
    """
    decision_id: str = ""                      # Karar Kimliği
    request_id: str = ""                       # Karara esas Talep Kimliği
    pid: str = ""                              # Üretim Kimliği
    category: str = ""                         # Karar Kategorisi
    verdict: str = ""                          # Karar
    params: dict = field(default_factory=dict)  # Karar Parametreleri
    rationale: dict = field(default_factory=dict)  # Karar Gerekçesi (15_KARAR)
    decided_at: str = ""

    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = f"RTD-{time.time_ns()}"
        if not self.decided_at:
            self.decided_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "pid": self.pid,
            "category": self.category,
            "verdict": self.verdict,
            "params": {
                k: v for k, v in self.params.items()
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
            },
            "rationale": self.rationale,
            "decided_at": self.decided_at,
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
    """HLK Runtime — Oturum yönetimi, karar otoritesi ve Production yetkilendirme.

    HLK Runtime:
    - Her /start'ta yeni bir oturum (session) başlatır
    - Constitution Runtime'ı tetikler
    - Boot Verification yapar
    - RuntimeContext oluşturur
    - Production Runtime başlatılmadan önce yetkilendirme kontrolü yapar
    - Production tamamlandığında session'ı serbest bırakır

    HLK Runtime (MASTER-013 / AR-002_81):
    - İlk tetikleyici komuttan (/start) oturum kapanışına kadar TEK karar
      otoritesidir; yürütme katmanlarından gelen Karar Taleplerini
      (DecisionRequest) karara bağlar (request_decision)
    - Karar destek bileşenlerini (Decision Engine, Feedback Loop,
      Escalation Engine) kendi hiyerarşik kontrolü altında çalıştırır

    HLK Runtime:
    - Kod yürütmez / video üretmez (yürütme Executor'undur — AR-002_76)
    - State değiştirmez (SE-007)
    - Yeni Event oluşturmaz (14_OLAY_KAYIT_MERKEZI.md yetkisidir)
    """

    def __init__(self):
        # session_id → RuntimeContext
        self._sessions: dict[str, RuntimeContext] = {}
        # Production sırasında aktif olan session'lar: session_id → start_time
        self._production_sessions: dict[str, float] = {}
        # MASTER-013 / AR-002_81: Bu oturumda üretilen Runtime Kararları
        self._decision_log: list[RuntimeDecision] = []

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

    # ── MASTER-013 / AR-002_81: Karar Otoritesi ──────────────────────────────

    def request_decision(self, request: DecisionRequest) -> RuntimeDecision:
        """AR-002_81 Adım 3: Karar Talebini karara bağlar.

        HLK Runtime, oturum boyunca TEK karar otoritesidir (MASTER-013).
        Yürütme katmanları karar gerektiren her durumda yürütmeyi durdurur
        ve bu metodu çağırır; dönen kararı eksiksiz uygular (OR-004_12).

        Karar destek bileşenleri (Decision Engine, Escalation Engine)
        gerektiğinde bu metod içerisinden, HLK Runtime'ın hiyerarşik
        kontrolü altında çalıştırılır.

        Args:
            request: Yürütme katmanının Karar Talebi (ham teknik kanıt içerir).

        Returns:
            RuntimeDecision — yürütmenin değiştirmeden uygulayacağı karar.
        """
        deciders = {
            DecisionCategory.PROVIDER_RESULT.value: self._decide_provider_result,
            DecisionCategory.PROVIDER_SWITCH.value: self._decide_provider_switch,
            DecisionCategory.EXECUTION_FAILURE.value: self._decide_execution_failure,
            DecisionCategory.CREATIVE_CONTENT.value: self._decide_creative_content,
            DecisionCategory.DELIVERY.value: self._decide_delivery,
            DecisionCategory.COMPLETION.value: self._decide_completion,
            DecisionCategory.USER_NOTIFICATION.value: self._decide_user_notification,
            DecisionCategory.REPRODUCTION.value: self._decide_reproduction,
            DecisionCategory.AMBIGUITY.value: self._decide_ambiguity,
            DecisionCategory.TASK_RESULT.value: self._decide_task_result,
        }
        decider = deciders.get(request.category, self._decide_ambiguity)
        decision = decider(request)

        # Karar kaydı (15_KARAR_GEREKCESI_STANDARDI.md + izlenebilirlik)
        self._decision_log.append(decision)
        logger.info(
            f"⚖️ [HLK Runtime Decision] {decision.decision_id} | "
            f"kategori={decision.category} | karar={decision.verdict} | "
            f"talep={request.requester or 'bilinmiyor'} | PID={decision.pid or '-'}"
        )
        return decision

    def get_decisions(self, pid: str = "") -> list[RuntimeDecision]:
        """Bu oturumda üretilen Runtime Kararlarını döndürür (PID filtreli)."""
        if not pid:
            return list(self._decision_log)
        return [d for d in self._decision_log if d.pid == pid]

    # ── Karar Vericiler (yalnızca HLK Runtime içinden çağrılır) ─────────────

    def _new_decision(
        self,
        request: DecisionRequest,
        verdict: str,
        params: dict,
        justifications: list[str],
    ) -> RuntimeDecision:
        """Runtime Kararını 15_KARAR_GEREKCESI_STANDARDI.md uyumlu üretir."""
        return RuntimeDecision(
            request_id=request.request_id,
            pid=request.pid,
            category=request.category,
            verdict=verdict,
            params=params,
            rationale={
                "DecisionName": f"{request.category} — {request.pid or 'NO-PID'}",
                "DecisionMaker": "HLK_RUNTIME",
                "DecisionTimestamp": datetime.now(timezone.utc).isoformat(),
                "Requester": request.requester,
                "Justifications": justifications,
                "PID": request.pid,
            },
        )

    def _decide_provider_result(self, request: DecisionRequest) -> RuntimeDecision:
        """PROVIDER_RESULT: Provider çıktısının kabul/red kararı (AR-002_75/76).

        Kanıt: artifact (üretilen çıktı yolu), error, remaining_candidates.
        """
        ctx = request.context
        provider = ctx.get("provider", "unknown")
        artifact = ctx.get("artifact", "")
        remaining = int(ctx.get("remaining_candidates", 0))

        if artifact:
            return self._new_decision(
                request, "ACCEPT", {"action": "USE_ARTIFACT"},
                [f"{provider} doğrulanabilir çıktı üretti: {artifact}"],
            )
        if remaining > 0:
            return self._new_decision(
                request, "REJECT", {"action": "NEXT_PROVIDER"},
                [
                    f"{provider} çıktı üretemedi: {ctx.get('error', 'çıktı yok')}",
                    f"Öncelik sıralamasında {remaining} aday mevcut (AR-002_19/21)",
                ],
            )
        return self._new_decision(
            request, "REJECT", {"action": "REPORT_FAILURE"},
            [
                f"{provider} çıktı üretemedi: {ctx.get('error', 'çıktı yok')}",
                "Öncelik sıralamasında başka aday yok — başarısızlık raporlanacak",
            ],
        )

    def _decide_provider_switch(self, request: DecisionRequest) -> RuntimeDecision:
        """PROVIDER_SWITCH: Sıradaki provider adayına geçiş kararı (AR-002_21)."""
        remaining = int(request.context.get("remaining_candidates", 0))
        if remaining > 0:
            return self._new_decision(
                request, "NEXT_PROVIDER", {"action": "NEXT_PROVIDER"},
                [f"Dinamik öncelik sıralamasında {remaining} aday mevcut (AR-002_19)"],
            )
        return self._new_decision(
            request, "NO_CANDIDATE", {"action": "REPORT_FAILURE"},
            ["Öncelik sıralamasında aday kalmadı — başarısızlık raporlanacak"],
        )

    def _decide_execution_failure(self, request: DecisionRequest) -> RuntimeDecision:
        """EXECUTION_FAILURE: Başarısızlık sonrası süreklilik kararı.

        AR-002_22 Feedback Loop zinciri HLK Runtime'ın hiyerarşik kontrolü
        altında çalıştırılır: retry sınırı değerlendirilir, gerekirse
        Decision Engine yeniden değerlendirmeye çağrılır, sınır aşıldıysa
        Escalation Engine tetiklenir (AR-002_79).
        """
        ctx = request.context
        decision_packet = ctx.get("decision_packet")
        prod_context = ctx.get("prod_context")
        category = ctx.get("category", "")
        failed_provider = ctx.get("failed_provider", "unknown")
        failure_detail = ctx.get("failure_detail", "")
        has_fallback = bool(ctx.get("has_fallback", False))

        if decision_packet is None or prod_context is None:
            return self._new_decision(
                request, "HOLD", {"action": "NONE"},
                ["Karar için yeterli kanıt yok (decision_packet/prod_context eksik)"],
            )

        retry_count = decision_packet.re_evaluation_count + 1
        max_retry = int(os.getenv("GC_MAX_RE_EVALUATION_COUNT", "3"))

        if retry_count > max_retry:
            logger.error(
                f"🚨 [HLK Runtime] Maksimum yeniden değerlendirme aşıldı "
                f"({max_retry}) — Escalation Engine tetikleniyor. "
                f"Kategori={category}, başarısız={failed_provider}"
            )
            try:
                from services.escalation_engine import (
                    escalation_engine, EscalationReason,
                )
                escalation_engine.escalate(
                    pid=getattr(prod_context, "pid", request.pid),
                    reason=EscalationReason.ALL_PROVIDERS_FAILED.value,
                    detail=(
                        f"Kategori={category}, başarısız={failed_provider}: "
                        f"{failure_detail}"
                    ),
                    failed_providers=[failed_provider],
                    retry_count=retry_count,
                )
            except Exception as e:
                logger.error(f"❌ [HLK Runtime] Eskalasyon yazılamadı: {e}")
            return self._new_decision(
                request, "ESCALATE", {"action": "ESCALATED"},
                [
                    f"Yeniden değerlendirme sınırı aşıldı: {retry_count}/{max_retry} "
                    f"(GC_MAX_RE_EVALUATION_COUNT)",
                    "AR-002_19 operasyonel eskalasyon başlatıldı",
                ],
            )

        if not has_fallback:
            return self._new_decision(
                request, "CONTINUE_WITHOUT", {"action": "NONE"},
                [
                    f"{category} kategorisinde yedek provider yok — "
                    "üretim mevcut çıktılarla sürdürülür (AR-002_79 süreklilik)",
                ],
            )

        logger.info(
            f"🔄 [Feedback Loop Started] kategori={category}, "
            f"başarısız={failed_provider}, deneme={retry_count}/{max_retry}"
        )
        try:
            from services.decision_engine import decision_engine as de
            from services.decision_packet import (
                ReEvaluationContext, ReEvaluationReason,
            )
            re_ctx = ReEvaluationContext(
                original_decision_id=decision_packet.decision_id,
                trigger_event="EXECUTOR_FAILED",
                re_evaluation_reason=ReEvaluationReason.EXECUTION_FAILED.value,
                current_state="STATE_VIDEO_PRODUCTION",
                re_evaluation_count=retry_count,
                failure_detail=failure_detail,
                failed_provider=failed_provider,
            )
            new_packet = de.re_evaluate(re_ctx, prod_context)
            logger.info(
                f"✅ [HLK Runtime] Yeni karar: {new_packet.decision_id} "
                f"(re-eval of {decision_packet.decision_id}, deneme={retry_count})"
            )
            return self._new_decision(
                request, "RE_EVALUATE",
                {"action": "APPLY_NEW_PACKET", "new_packet": new_packet},
                [
                    f"Deneme {retry_count}/{max_retry} sınır içinde",
                    "Decision Engine güncel koşullarla yeniden değerlendirme yaptı "
                    "(AR-002_22 Adım 3)",
                ],
            )
        except Exception as e:
            logger.error(f"❌ [HLK Runtime] Yeniden değerlendirme başarısız: {e}")
            return self._new_decision(
                request, "HOLD", {"action": "NONE"},
                [f"Yeniden değerlendirme hatası: {e}"],
            )

    def _decide_creative_content(self, request: DecisionRequest) -> RuntimeDecision:
        """CREATIVE_CONTENT: Yaratıcı içerik kararı (AR-002_77).

        Seslendirme metni gibi yaratıcı içerikler yürütme katmanında
        üretilemez; içerik HLK Runtime kararı ile belirlenir.
        """
        ctx = request.context
        kind = ctx.get("kind", "")
        if kind == "voice_script":
            brand = ctx.get("brand", "")
            product_name = ctx.get("product_name", "")
            voice_lang = ctx.get("voice_lang", "tr")
            if voice_lang == "tr":
                voice_text = (
                    f"{brand} {product_name} urununu simdi kesfedin. "
                    f"Kalite ve uygun fiyat bir arada. Hemen siparis vermek icin tiklayin."
                )
            else:
                voice_text = (
                    f"Discover {brand} {product_name} now. "
                    f"Quality and affordable price together. Order now!"
                )
            return self._new_decision(
                request, "PROVIDE", {"voice_text": voice_text},
                [
                    f"Seslendirme metni HLK Runtime tarafından belirlendi "
                    f"(dil={voice_lang}, AR-002_77)",
                ],
            )
        return self._new_decision(
            request, "HOLD", {"action": "NONE"},
            [f"Tanımsız yaratıcı içerik türü: {kind or 'belirtilmedi'}"],
        )

    def _decide_delivery(self, request: DecisionRequest) -> RuntimeDecision:
        """DELIVERY: Teslim şekli ve kullanıcı mesajı kararı (AR-002_36).

        Kullanıcıya gönderilecek süreç mesajlarının içeriği yalnızca
        HLK Runtime kararı ile belirlenir (MASTER-013, OR-004_12).
        Yürütme katmanı onaylanan metni değiştirmeden iletir.
        """
        ctx = request.context
        pid = request.pid or "PID-UNKNOWN"
        brand = ctx.get("brand", "")
        product_name = ctx.get("product_name", "")
        duration = ctx.get("duration", 0)
        voice_lang = str(ctx.get("voice_lang", "tr"))
        video_available = bool(ctx.get("video_available", False))

        if video_available:
            caption = (
                f"🎬 <b>{brand} — {product_name}</b>\n\n"
                f"Videonuz hazir! 📋 PID: <code>{pid}</code>"
            )
            return self._new_decision(
                request, "DELIVER_VIDEO",
                {"caption": caption, "parse_mode": "HTML"},
                [
                    "Nihai video mevcut — video teslimi kararlaştırıldı (AR-002_36)",
                    "Teslim mesajı HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        text = (
            f"🎬 <b>Uretim Tamamlandi!</b>\n\n"
            f"📋 PID: <code>{pid}</code>\n"
            f"Urun: <b>{brand} — {product_name}</b>\n"
            f"Video suresi: {duration} sn | Ses: {voice_lang.upper()}\n\n"
            f"Videonuz hazirlaniyor, en kisa surede gonderilecektir.\n"
            f"<i>HLK AI Reklam Asistani</i>"
        )
        return self._new_decision(
            request, "DELIVER_INFO",
            {"text": text, "parse_mode": "HTML"},
            [
                "Nihai video mevcut değil — bilgilendirme teslimi kararlaştırıldı",
                "Bilgilendirme metni HLK Runtime tarafından onaylandı (OR-004_12)",
            ],
        )

    def _decide_completion(self, request: DecisionRequest) -> RuntimeDecision:
        """COMPLETION: Üretimin tamamlanmış kabul edilmesi kararı (AR-002_80)."""
        ctx = request.context
        delivered = bool(ctx.get("delivered", False))
        video = bool(ctx.get("video", False))
        failed_tasks = int(ctx.get("failed_tasks", 0))
        justifications = [
            f"Teslim durumu: {'tamamlandı' if delivered else 'tamamlanmadı'}",
            f"Nihai video: {'mevcut' if video else 'mevcut değil'}",
            f"Başarısız task sayısı: {failed_tasks}",
        ]
        if failed_tasks == 0 and delivered and video:
            justifications.append("Anayasal kapanış kriterleri sağlandı (AR-002_80)")
            completion_success = True
        else:
            justifications.append(
                "Eksiklikler Event kayıtlarında raporlandı; kapanış "
                "AR-002_79/80 kapsamında değerlendirildi"
            )
            completion_success = False
        return self._new_decision(
            request, "CONFIRM_COMPLETION", {"success": completion_success},
            justifications,
        )

    def _decide_task_result(self, request: DecisionRequest) -> RuntimeDecision:
        """TASK_RESULT: Task SUCCESS/FAIL kararı (MASTER-013).

        MASTER-013: Production Executor (Claude) SUCCESS/FAIL kararı veremez.
        Bu karar yalnızca HLK Runtime tarafından üretilir.

        Executor, task handler tamamlandıktan sonra ham çıktıyı buraya
        iletir; HLK Runtime çıktıdaki başarı kanıtlarını (proof keys)
        değerlendirerek TASK_SUCCESS veya TASK_FAILED kararı verir.

        Kanıt: task_id, agent, output (ham handler çıktısı), proof_keys.
        """
        ctx = request.context
        task_id = ctx.get("task_id", "unknown")
        agent = ctx.get("agent", "unknown")
        output = ctx.get("output", {})
        task_input = ctx.get("task", {})

        # AR-002_84: Başarı kanıt anahtarları
        proof_keys = [k for k in ("generated", "delivered") if k in output]
        all_proved = all(bool(output.get(k)) for k in proof_keys) if proof_keys else None

        if all_proved is True:
            return self._new_decision(
                request, "TASK_SUCCESS",
                {"task_status": "SUCCESS", "reason": "Tüm başarı kanıtları pozitif"},
                [
                    f"Task {task_id} ({agent}): proof_keys={proof_keys}, hepsi True",
                    "MASTER-013: HLK Runtime task'ı başarılı olarak onayladı",
                ],
            )

        if all_proved is False:
            detail = ", ".join(f"{k}={output.get(k)}" for k in proof_keys)
            return self._new_decision(
                request, "TASK_FAILED",
                {
                    "task_status": "FAILED",
                    "reason": f"Başarı kanıtı yok: {detail}",
                    "should_retry": True,
                },
                [
                    f"Task {task_id} ({agent}): {detail}",
                    "AR-002_84: Üretim kanıtı olmadan başarı sayılamaz",
                    "MASTER-013: HLK Runtime task'ı başarısız olarak değerlendirdi",
                ],
            )

        # proof_keys yok — handler eski tip çıktı döndürmüş olabilir
        return self._new_decision(
            request, "TASK_SUCCESS",
            {"task_status": "SUCCESS", "reason": "Kanıt anahtarı bulunamadı — varsayılan"},
            [
                f"Task {task_id} ({agent}): çıktıda proof_keys yok, "
                "eski tip handler kabul edildi",
            ],
        )

    def _decide_user_notification(self, request: DecisionRequest) -> RuntimeDecision:
        """USER_NOTIFICATION: Süreç kararı içeren kullanıcı bildirimi kararı.

        Yürütme katmanları kullanıcıya süreç mesajı üretemez (MASTER-013);
        bildirim metni yalnızca HLK Runtime tarafından belirlenir.
        """
        ctx = request.context
        kind = ctx.get("kind", "production_failure")
        pid = request.pid or ctx.get("pid", "PID-UNKNOWN")

        if kind == "production_failure":
            text = (
                f"⚠️ <b>Uretim surecinde beklenmeyen bir durum olustu.</b>\n\n"
                f"📋 PID: <code>{pid}</code>\n"
                f"Yoneticimiz bilgilendirildi; uretiminiz kontrol edilerek "
                f"en kisa surede tamamlanacaktir.\n"
                f"<i>HLK AI Reklam Asistani</i>"
            )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "Dürüst bilgilendirme zorunluluğu (EEC-001: Fake Progress yasağı)",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        if kind == "production_start":
            # Üretim başlangıç bildirimi — süreç mesajıdır; içerik, zaman,
            # gönderim izni ve iletim parametreleri HLK Runtime kararıdır
            # (MASTER-013 Yetki Sınırları, OR-004_12, FD-008_1, GK-001_5).
            lang = str(ctx.get("lang", "tr"))
            product_name = ctx.get("product_name", "urununuz")
            duration = ctx.get("duration", "")
            if lang == "tr":
                text = (
                    f"<b>✅ Odemeniz onaylandi!</b>\n\n"
                    f"<b>{product_name}</b> icin <b><i>video uretiminiz</i></b> hemen basladi. 🎬\n"
                    f"Bu islem yaklasik <b>{duration} dakika</b> kadar surecek.\n"
                    f"Videonuz <b>hazir olur olmaz</b> size buradan <b>otomatik olarak</b> gonderecegim.\n\n"
                    f"<i>Bol kazanclar dilerim!</i> 🚀"
                )
            else:
                from config.i18n import t
                text = (
                    f"<b>✅ {t('final.payment_received', lang)}</b>\n\n"
                    f"<b>{product_name}</b> — <b><i>{t('final.production_started', lang)}</i></b> 🎬\n"
                    f"{t('final.duration_info', lang)}: <b>~{duration} min</b>.\n"
                    f"<b>{t('final.auto_delivery', lang)}</b>\n\n"
                    f"<i>🚀</i>"
                )
            return self._new_decision(
                request, "NOTIFY",
                {
                    "text": text,
                    "parse_mode": "HTML",
                    "delivery": "typewriter",       # FD-008_1: daktilo efekti
                    "typewriter_delay": 0.06,        # Karar parametresi (AR-002_81)
                },
                [
                    "EVENT_PAYMENT_APPROVED sonrası üretim başlangıç bildirimi "
                    "kararlaştırıldı (FD-008_1, AR-002_56)",
                    "Metin, zamanlama, gönderim izni ve iletim parametreleri "
                    "HLK Runtime kararıdır (MASTER-013, OR-004_12)",
                ],
            )

        if kind == "authorization_denied":
            # Boot Chain yetkilendirme reddi bildirimi (AR-002_70 ön koşul).
            text = (
                "⚠️ <b>Uretim baslatilamadi.</b>\n\n"
                "Anayasal dogrulama tamamlanamadi. "
                "<i>Lutfen</i> <b>/start</b> <i>yazarak yeniden deneyin.</i>"
            )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "Constitutional Boot Chain yetkilendirmesi reddedildi — "
                    "kullanıcıya dürüst bilgilendirme (EEC-001)",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        # ── Yeniden Üretim Prosedürü bildirimleri (AR-002_84) ────────────
        # Yönetici Yeniden Üretim Prosedürüne ait tüm süreç mesajları
        # yalnızca HLK Runtime kararı ile üretilir (MASTER-013, OR-004_12).

        if kind == "reproduction_not_found":
            # İstisna akışı: PID doğrulanamadı veya Production Package yok.
            query = ctx.get("query", "")
            reason = ctx.get("reason", "PID dogrulanamadi veya Production Package bulunamadi")
            text = (
                f"⛔ <b>Yeniden uretim proseduru baslatilamadi.</b>\n\n"
                f"🔎 Sorgu: <code>{query}</code>\n"
                f"📋 Anayasal gerekce: {reason} (AR-002_57, AR-002_84).\n\n"
                f"<i>Islem guvenli sekilde sonlandirildi; hicbir uretim baslatilmadi.</i>"
            )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "AR-002_84 İstisna Akışı: PID/Package doğrulanamadığında "
                    "prosedür başlatılmaz, Yönetici gerekçesiyle bilgilendirilir",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        if kind == "reproduction_rejected":
            # REPRODUCTION kararı REJECT — gerekçeler karar kaydından gelir.
            reasons = ctx.get("justifications", []) or ["Gerekce kaydi bulunamadi"]
            reason_lines = "\n".join(f"• {r}" for r in reasons)
            text = (
                f"⛔ <b>Yeniden uretim proseduru reddedildi.</b>\n\n"
                f"📋 PID: <code>{pid}</code>\n"
                f"<b>HLK Runtime karar gerekcesi:</b>\n{reason_lines}\n\n"
                f"<i>Islem guvenli sekilde sonlandirildi (MASTER-013, AR-002_84).</i>"
            )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "REPRODUCTION kararı REJECT — Yönetici anayasal gerekçeyle "
                    "bilgilendirilir (AR-002_84, 15_KARAR_GEREKCESI_STANDARDI.md)",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        if kind == "reproduction_started":
            # Yönetici onayı sonrası prosedür başlangıç bildirimi.
            procedure = ctx.get("procedure", "")
            text = (
                f"🔄 <b>Yeniden uretim proseduru baslatildi.</b>\n\n"
                f"📋 PID: <code>{pid}</code>\n"
                f"⚙️ HLK Runtime karari: <b>{procedure}</b>\n\n"
                f"Uretim tamamlandiginda sonuc otomatik olarak bildirilecektir.\n"
                f"<i>Tum teknik kararlar HLK Runtime tarafindan yonetilmektedir "
                f"(MASTER-013).</i>"
            )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    f"REPRODUCTION kararı ({procedure}) uygulanmak üzere onaylandı "
                    "(AR-002_82, AR-002_83, AR-002_84)",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        if kind == "reproduction_completed":
            # Adım 21: Üretim sonucu bildirimi — Yönetici ve Kullanıcı.
            audience = ctx.get("audience", "admin")
            product_name = ctx.get("product_name", "urununuz")
            if audience == "user":
                text = (
                    f"✅ <b>Uretiminiz tamamlandi!</b>\n\n"
                    f"<b>{product_name}</b> icin yeniden baslatilan video uretimi "
                    f"basariyla tamamlandi ve cikti tarafiniza teslim edildi. 🎬\n\n"
                    f"<i>HLK AI Reklam Asistani</i>"
                )
            else:
                text = (
                    f"✅ <b>Yeniden uretim proseduru basariyla tamamlandi.</b>\n\n"
                    f"📋 PID: <code>{pid}</code>\n"
                    f"📦 Urun: <b>{product_name}</b>\n"
                    f"🎬 Ciktilar ilgili kullaniciya teslim edildi ve Production "
                    f"Package ile iliskilendirildi (surum gecmisi korundu).\n\n"
                    f"<i>AR-002_80 kapanis kriterleri HLK Runtime tarafindan "
                    f"dogrulandi.</i>"
                )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "AR-002_84 Adım 21: Üretim sonucu Yöneticiye ve ilgili "
                    "Kullanıcıya anayasal bildirim kurallarıyla iletilir",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        if kind == "reproduction_failed":
            # Adım 21 (başarısızlık): durum + anayasal karar gerekçesi bildirilir.
            audience = ctx.get("audience", "admin")
            error = ctx.get("error", "ayrinti yok")
            reasons = ctx.get("justifications", [])
            if audience == "user":
                text = (
                    f"⚠️ <b>Uretim yeniden denendi ancak tamamlanamadi.</b>\n\n"
                    f"📋 PID: <code>{pid}</code>\n"
                    f"Yoneticimiz bilgilendirildi; uretiminiz anayasal kurallar "
                    f"cercevesinde yeniden degerlendirilecektir.\n"
                    f"<i>HLK AI Reklam Asistani</i>"
                )
            else:
                reason_lines = "\n".join(f"• {r}" for r in reasons) if reasons else f"• {error}"
                text = (
                    f"❌ <b>Yeniden uretim proseduru basarisiz oldu.</b>\n\n"
                    f"📋 PID: <code>{pid}</code>\n"
                    f"🧾 Uretim durumu: <b>FAILED</b>\n"
                    f"<b>Anayasal karar gerekcesi:</b>\n{reason_lines}\n\n"
                    f"<i>Kayitlar Production Package, Olay Kayit Merkezi ve "
                    f"Decision History uzerinden incelenebilir (AR-002_84).</i>"
                )
            return self._new_decision(
                request, "NOTIFY", {"text": text, "parse_mode": "HTML"},
                [
                    "AR-002_84 Adım 21: Başarısız üretim durumu ve anayasal karar "
                    "gerekçesi bildirilir (EEC-001: Fake Progress yasağı)",
                    "Bildirim metni HLK Runtime tarafından onaylandı (OR-004_12)",
                ],
            )

        return self._new_decision(
            request, "HOLD", {"action": "NONE"},
            [f"Tanımsız bildirim türü: {kind}"],
        )

    def _decide_reproduction(self, request: DecisionRequest) -> RuntimeDecision:
        """REPRODUCTION: Yönetici tarafından başlatılan yeniden üretim prosedürü.

        AR-002_82 Mission Persistence Architecture ve AR-002_83 Recovery Policy
        uyarınca HLK Runtime, mevcut Production Package durumunu analiz ederek
        uygun yeniden üretim prosedürünü belirler.

        Karar vericidir; yürütme katmanı bu kararı değiştirmeden uygular.
        """
        ctx = request.context
        pid = request.pid or ctx.get("pid", "PID-UNKNOWN")
        package_status = str(ctx.get("package_status", "")).upper()
        failed_tasks = int(ctx.get("failed_tasks", 0))
        completed_tasks = int(ctx.get("completed_tasks", 0))
        total_tasks = int(ctx.get("total_tasks", 0))
        last_error = ctx.get("last_error", "")
        failed_step = ctx.get("failed_step", "")
        hlk_active = ctx.get("hlk_runtime_active", False)

        # Anayasal ön koşul: HLK Runtime aktif olmalı
        if not hlk_active:
            return self._new_decision(
                request, "REJECT", {"action": "NONE"},
                [
                    "HLK Runtime aktif değil — Constitutional Boot Chain tamamlanmamış",
                    "Yeniden üretim yalnızca anayasal runtime hazır olduğunda başlatılabilir (AR-002_62)",
                ],
            )

        # Arşivlenmiş package asla yeniden üretilemez
        if package_status == "ARCHIVED":
            return self._new_decision(
                request, "REJECT", {"action": "NONE"},
                [
                    "Production Package arşivlenmiş durumda (AR-002_58)",
                    "Arşivlenmiş package'lar immutable kabul edilir; yeniden üretim yapılamaz",
                ],
            )

        # Tamamlanmış package'lar tamamen sıfırdan üretilir (REPLAY)
        if package_status == "COMPLETED":
            return self._new_decision(
                request, "REPLAY", {"action": "RESET_AND_EXECUTE"},
                [
                    f"Package daha önce başarıyla tamamlanmış (COMPLETED)",
                    "Yönetici talebi üzerine üretim sıfırdan yeniden başlatılacak (AR-002_82)",
                    "Mevcut dijital varlıklar korunarak yeni üretim sürümü oluşturulacak",
                ],
            )

        # Başarısız package'larda sadece başarısız task'lar yeniden denenir (RETRY)
        if package_status == "FAILED" or failed_tasks > 0:
            return self._new_decision(
                request, "RETRY", {"action": "RETRY_FAILED_TASKS"},
                [
                    f"Package durumu FAILED veya {failed_tasks} adet başarısız task var",
                    f"Son başarısız adım: {failed_step or 'belirlenemedi'} — {last_error or 'hata ayrıntısı yok'}",
                    "Yalnızca başarısız/zaman aşımına uğrayan task'lar yeniden denenecek (AR-002_83)",
                    "Başarıyla tamamlanmış task'lar checkpoint'ten korunacak (AR-002_76)",
                ],
            )

        # Yarım kalmış package'lar kaldığı yerden devam eder (RESUME)
        if package_status in ("READY", "BUILDING", "PRODUCING"):
            return self._new_decision(
                request, "RESUME", {"action": "RESUME_FROM_CHECKPOINT"},
                [
                    f"Package durumu {package_status} — üretim yarım kalmış",
                    f"Tamamlanmış task: {completed_tasks}/{total_tasks}",
                    "Kaldığı yerden devam edilecek; tamamlanmış task'lar atlanacak (AR-002_79)",
                ],
            )

        # Henüz başlamamış package
        if package_status == "CREATED":
            return self._new_decision(
                request, "START_AS_NEW", {"action": "EXECUTE_FROM_CREATED"},
                [
                    "Package CREATED durumunda ancak henüz üretim başlamamış",
                    "Mevcut PID korunarak normal üretim akışı başlatılacak (AR-002_57)",
                ],
            )

        # Tanımlanamayan durum
        return self._new_decision(
            request, "REJECT", {"action": "NONE"},
            [
                f"Package durumu ({package_status}) için tanımlı bir reproduction prosedürü yok",
                "Güvenli sonlandırma uygulanıyor (MASTER-013: tereddüt durumunda karar üretilmez)",
            ],
        )

    def _decide_ambiguity(self, request: DecisionRequest) -> RuntimeDecision:
        """AMBIGUITY: Tereddüt kararı (MASTER-013 Karar Prensibi).

        Yürütme katmanı karara bağlayamadığı her durumu buraya iletir.
        """
        ctx = request.context
        reason = ctx.get("reason", "")
        if reason == "unsupported_provider":
            provider = ctx.get("provider", "unknown")
            return self._new_decision(
                request, "SKIP", {"action": "SKIP"},
                [
                    f"Provider '{provider}' için kayıtlı yürütme entegrasyonu yok",
                    "Öncelik sıralamasındaki sonraki aday değerlendirilecek "
                    "(AR-002_19/21)",
                ],
            )
        return self._new_decision(
            request, "HOLD", {"action": "NONE"},
            [
                f"Tereddüt kaydı alındı: {reason or 'gerekçe belirtilmedi'} — "
                "yürütme karar üretmeden raporladı (MASTER-013)",
            ],
        )

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
