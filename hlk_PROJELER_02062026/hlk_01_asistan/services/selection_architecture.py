"""
AR-002_49: Selection Architecture — Ortak Seçim Mimarisi.

HLK içerisinde gerçekleştirilen TÜM seçim işlemleri için ortak standart.
Decision Engine tarafından provider seçimi için kullanılır.

8 adımlı seçim prosedürü (AR-002_49):
1. Görev analiz edilir
2. Adaylar belirlenir (Provider Priority List'ten)
3. Değerlendirme kriterleri uygulanır
4. En uygun aday seçilir
5. Seçim sonucu kayıt altına alınır
6. Cache süresi boyunca aynı seçim yeniden kullanılır
7. Cache süresi dolduğunda prosedür yeniden çalıştırılır
8. Daha uygun aday bulunursa kayıt güncellenir

Bu modül:
- Provider Priority List'i kullanarak adayları belirler
- Değerlendirme kriterlerini uygular
- Her kategori için öncelik sıralı ProviderRef listesi üretir
- Decision Engine'e seçim sonucunu döndürür

Bu modül:
- Karar vermez (Decision Engine'in görevi)
- Provider'ların durumunu değiştirmez (Provider Priority List'in görevi)
- Provider'ları çalıştırmaz (Executor'un görevi)

Mimari Dayanak:
- AR-002_49: Selection Architecture
- AR-002_75: Provider Selection
- AR-002_3: Dinamik öncelik sıralaması
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from services.decision_packet import ProviderRef

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SELECTION RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SelectionResult:
    """Selection Architecture'ın bir kategori için ürettiği seçim sonucu."""
    category: str = ""
    primary: ProviderRef | None = None
    fallback: ProviderRef | None = None
    all_candidates: list[dict] = field(default_factory=list)
    selection_timestamp: str = ""
    cache_valid_until: str = ""

    def __post_init__(self):
        if not self.selection_timestamp:
            self.selection_timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def has_primary(self) -> bool:
        return self.primary is not None

    @property
    def has_fallback(self) -> bool:
        return self.fallback is not None

    def to_provider_refs(self) -> tuple[ProviderRef, ...]:
        """Seçim sonucunu immutable ProviderRef tuple'ına dönüştürür."""
        refs = []
        if self.primary:
            refs.append(self.primary)
        if self.fallback:
            refs.append(self.fallback)
        return tuple(refs)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SELECTION ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════

class SelectionArchitecture:
    """AR-002_49: Ortak seçim mimarisi.

    HLK'nın tüm seçim işlemleri için tek standart.
    Decision Engine provider seçimi yaparken bu mimariyi kullanır.

    Çalışma prensibi:
    - Provider Priority List'ten aday listesini alır
    - AR-002_3 kriterlerine göre değerlendirir
    - Birincil ve yedek provider'ları belirler
    - Sonucu ProviderRef olarak döndürür
    """

    def __init__(self):
        self._selection_cache: dict[str, SelectionResult] = {}
        self._cache_duration_s: float = 300.0  # 5 dakika

    # ═══════════════════════════════════════════════════════════════════════
    # Adım 1-2: Görev Analizi + Aday Belirleme
    # ═══════════════════════════════════════════════════════════════════════

    def select_providers(self, category: str) -> SelectionResult:
        """AR-002_49 Adım 1-5: Bir kategori için provider seçimi yapar.

        Args:
            category: "image", "voice", veya "video"

        Returns:
            SelectionResult — birincil ve yedek provider'ları içerir.
        """
        from services.provider_priority import provider_priority

        # Adım 6: Cache kontrolü
        cached = self._get_cached(category)
        if cached is not None:
            logger.info(
                f"📋 [Selection] Cache hit: {category} → "
                f"birincil={cached.primary.provider if cached.primary else 'yok'}"
            )
            return cached

        # Adım 2: Aday listesini al
        priority_map = provider_priority.get_priority_map(category)

        if not priority_map:
            logger.warning(f"⚠️ [Selection] {category}: hiç aday yok")
            return SelectionResult(category=category)

        # Adım 3-4: Değerlendir ve seç
        result = self._evaluate_and_select(category, priority_map)

        # Adım 5: Kayıt altına al
        self._cache_result(category, result)

        logger.info(
            f"✅ [Selection] {category}: "
            f"birincil={result.primary.provider if result.primary else 'yok'}, "
            f"yedek={result.fallback.provider if result.fallback else 'yok'}"
        )

        return result

    # ═══════════════════════════════════════════════════════════════════════
    # Adım 3-4: Değerlendirme + Seçim
    # ═══════════════════════════════════════════════════════════════════════

    def _evaluate_and_select(
        self, category: str, priority_map: list[dict]
    ) -> SelectionResult:
        """AR-002_49 Adım 3-4: Adayları değerlendir, en uygun olanı seç.

        Değerlendirme kriterleri (AR-002_3):
        1. API durumu (AVAILABLE > diğerleri) — Provider Priority List zaten filtreler
        2. Güven skoru (yüksek > düşük)
        3. Maliyet (düşük > yüksek)
        4. Gecikme (düşük > yüksek)

        Provider Priority List'in sıralaması esas alınır.
        Selection Architecture yeni bir sıralama algoritması ÇALIŞTIRMAZ.
        """
        available = [p for p in priority_map if p["status"] == "AVAILABLE"]

        if not available:
            # Hiçbir provider kullanılabilir değil
            logger.error(f"🚨 [Selection] {category}: kullanılabilir provider yok!")
            return SelectionResult(
                category=category,
                all_candidates=priority_map,
            )

        # Birincil: en yüksek skorlu
        primary_candidate = available[0]
        primary = ProviderRef(
            category=category,
            provider=primary_candidate["provider"],
            priority=1,
            confidence=primary_candidate["confidence"],
            justification=primary_candidate["justification"],
        )

        # Yedek: ikinci en yüksek skorlu (varsa)
        fallback = None
        if len(available) > 1:
            fb_candidate = available[1]
            fallback = ProviderRef(
                category=category,
                provider=fb_candidate["provider"],
                priority=2,
                confidence=fb_candidate["confidence"],
                justification=fb_candidate["justification"],
            )

        return SelectionResult(
            category=category,
            primary=primary,
            fallback=fallback,
            all_candidates=priority_map,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # Adım 6-8: Cache yönetimi
    # ═══════════════════════════════════════════════════════════════════════

    def _get_cached(self, category: str) -> SelectionResult | None:
        """Cache'te geçerli bir seçim sonucu var mı kontrol eder."""
        cached = self._selection_cache.get(category)
        if cached is None:
            return None
        # Cache süresi kontrolü
        try:
            cached_time = datetime.fromisoformat(cached.selection_timestamp)
            now = datetime.now(timezone.utc)
            # Zaman dilimi farkını normalize et
            if cached_time.tzinfo is None:
                cached_time = cached_time.replace(tzinfo=timezone.utc)
            elapsed = (now - cached_time).total_seconds()
            if elapsed < self._cache_duration_s:
                return cached
        except (ValueError, TypeError):
            pass
        # Cache expired — temizle
        self._selection_cache.pop(category, None)
        return None

    def _cache_result(self, category: str, result: SelectionResult) -> None:
        """Seçim sonucunu cache'ler."""
        self._selection_cache[category] = result

    def invalidate_cache(self, category: str | None = None) -> None:
        """Cache'i temizler (provider durumu değiştiğinde çağrılır)."""
        if category:
            self._selection_cache.pop(category, None)
            logger.info(f"🔄 [Selection] Cache temizlendi: {category}")
        else:
            self._selection_cache.clear()
            logger.info("🔄 [Selection] Tüm cache temizlendi")

    # ═══════════════════════════════════════════════════════════════════════
    # Tüm kategoriler için toplu seçim
    # ═══════════════════════════════════════════════════════════════════════

    def select_all(self) -> dict[str, SelectionResult]:
        """Tüm kategoriler (image, voice, video) için provider seçimi yapar.

        Decision Engine'in ana giriş noktası.
        """
        return {
            "image": self.select_providers("image"),
            "voice": self.select_providers("voice"),
            "video": self.select_providers("video"),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

selection_architecture = SelectionArchitecture()
"""Global Selection Architecture singleton'ı.

Decision Engine tarafından provider seçimi için kullanılır.
"""
