"""
Live Activity Center (LAC) — FEAT-015

HLK'nın canlı olay izleme merkezi. Olay Kayıt Merkezi'nden (EventRegistry)
gerçek zamanlı Event akışını okur ve görüntülenebilir formatta sunar.

LAC hiçbir zaman karar vermez, Event üretmez, kod değiştirmez.
LAC yalnızca Olay Kayıt Merkezi'nden Event'leri okur ve gösterir.

Mimari: FEAT-015, WF-016, AR-002_61
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class LACEntry:
    """LAC'ta görüntülenen tek bir aktivite satırı."""
    timestamp: str
    pid: str
    event_name: str
    phase: str
    category: str
    duration_ms: float
    result: str
    related_file: str

    def format_line(self, max_name: int = 35) -> str:
        """Tek satırlık LAC gösterimi."""
        emoji = self._result_emoji()
        name = self.event_name[:max_name]
        dur = f"{self.duration_ms:.0f}ms" if self.duration_ms > 0 else "-"
        phase_short = self.phase.replace("PHASE_", "")
        return (
            f"{emoji} {self.timestamp} | {phase_short:10s} | "
            f"{name:{max_name}s} | {dur:>8s} | {self.result[:30]}"
        )

    def _result_emoji(self) -> str:
        r = self.result.upper()
        if "PASS" in r:
            return "✅"
        elif "FAIL" in r:
            return "❌"
        elif "BASLADI" in r or "START" in r:
            return "▶️"
        elif "TAMAMLANDI" in r or "COMPLET" in r:
            return "🏁"
        elif "HATA" in r or "ERROR" in r:
            return "⚠️"
        return "📌"


@dataclass
class LACSummary:
    """LAC özet paneli."""
    total_events: int = 0
    pass_count: int = 0
    fail_count: int = 0
    active_pids: int = 0
    session_duration_s: float = 0.0
    categories: dict[str, int] = field(default_factory=dict)
    recent_events: list[LACEntry] = field(default_factory=list)
    generated_at: str = ""

    def format_panel(self) -> str:
        """LAC panelini formatlanmış metin olarak döndürür."""
        lines = [
            "╔══════════════════════════════════════╗",
            "║     HLK LIVE ACTIVITY CENTER        ║",
            "║         (Salt İzleyici)              ║",
            "╚══════════════════════════════════════╝",
            "",
            f"📊 Toplam Olay: {self.total_events}",
            f"✅ PASS: {self.pass_count}  ❌ FAIL: {self.fail_count}",
            f"👤 Aktif PID: {self.active_pids}",
            f"⏱️  Oturum: {self.session_duration_s:.0f}s",
            f"🕐 Güncelleme: {self.generated_at}",
            "",
        ]

        if self.categories:
            lines.append("📂 Kategoriler:")
            for cat, count in sorted(self.categories.items()):
                lines.append(f"   {cat}: {count}")
            lines.append("")

        if self.recent_events:
            lines.append(f"📜 Son {len(self.recent_events)} Olay:")
            lines.append("─" * 70)
            for entry in self.recent_events:
                lines.append(entry.format_line())
        else:
            lines.append("ℹ️ Henüz kaydedilmiş olay yok.")

        return "\n".join(lines)


class LiveActivityCenter:
    """HLK Live Activity Center (LAC).

    Olay Kayıt Merkezi'nden (EventRegistry) Event'leri okur,
    LACEntry'lere dönüştürür ve LACSummary olarak sunar.

    LAC:
    - Karar vermez (MASTER-004)
    - Event üretmez (EEC'in görevi)
    - Kod değiştirmez
    - Yalnızca OKUR ve GÖSTERİR
    """

    def __init__(self):
        self._last_refresh: float = 0.0
        self._cache: Optional[LACSummary] = None
        self._cache_ttl: float = 2.0  # 2 saniye cache

    def refresh(self, pid: str | None = None, limit: int = 20) -> LACSummary:
        """Olay Kayıt Merkezi'nden güncel veriyi oku, LACSummary üret.

        Args:
            pid: Belirli bir PID için filtrele (None = tümü).
            limit: Gösterilecek maksimum event sayısı.

        Returns:
            LACSummary — formatlanmış özet paneli.
        """
        from services.olay_kayit_merkezi import event_registry
        from datetime import datetime

        # Cache kontrolü
        now = time.time()
        if self._cache and (now - self._last_refresh) < self._cache_ttl:
            return self._cache

        # Olay Kayıt Merkezi'nden veri oku
        stats = event_registry.get_stats()
        feed = event_registry.get_lac_feed(pid=pid, limit=limit)

        # PASS/FAIL say
        pass_count = len(event_registry.get_by_result("PASS"))
        fail_count = len(event_registry.get_by_result("FAIL"))

        # LACEntry'lere dönüştür
        entries = []
        for item in feed:
            entry = LACEntry(
                timestamp=item.get("timestamp", "")[:19],
                pid=item.get("pid", "?")[:20],
                event_name=item.get("event_name", "?"),
                phase=item.get("phase", "?"),
                category=item.get("category", "?"),
                duration_ms=item.get("duration_ms", 0),
                result=item.get("result", "-"),
                related_file=item.get("related_file", ""),
            )
            entries.append(entry)

        summary = LACSummary(
            total_events=stats["total_events"],
            pass_count=pass_count,
            fail_count=fail_count,
            active_pids=stats["active_pids"],
            session_duration_s=stats["session_duration_s"],
            categories=stats.get("events_by_category", {}),
            recent_events=entries,
            generated_at=datetime.now().strftime("%H:%M:%S"),
        )

        # Cache'le
        self._cache = summary
        self._last_refresh = now

        logger.debug(f"🔄 [LAC] Yenilendi: {summary.total_events} olay, "
                     f"{summary.pass_count}P/{summary.fail_count}F")
        return summary

    def get_panel(self, pid: str | None = None, limit: int = 20) -> str:
        """Formatlanmış LAC panelini metin olarak döndürür."""
        summary = self.refresh(pid=pid, limit=limit)
        return summary.format_panel()

    def get_telegram_html(self, pid: str | None = None, limit: int = 10) -> str:
        """Telegram HTML formatında LAC özeti döndürür."""
        summary = self.refresh(pid=pid, limit=limit)

        lines = [
            "🔍 <b>HLK DENETİM RAPORU (LAC)</b>",
            "━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 Toplam Olay: <b>{summary.total_events}</b>",
            f"✅ PASS: <b>{summary.pass_count}</b>  ❌ FAIL: <b>{summary.fail_count}</b>",
            f"👤 Aktif PID: <b>{summary.active_pids}</b>",
            f"⏱️ Oturum: <b>{summary.session_duration_s:.0f}s</b>",
            f"🕐 Güncelleme: <b>{summary.generated_at}</b>",
            "",
        ]

        # Constitution Cache durumu (entegre gösterim)
        try:
            from services.constitution_cache import constitution_cache
            cache_status = constitution_cache.get_status()
            if cache_status:
                const_emoji = "✅" if cache_status.is_valid else "⚠️"
                lines.append(
                    f"📚 <b>Constitution Cache:</b> {const_emoji} "
                    f"{cache_status.cached_files}/{cache_status.total_files} dosya | "
                    f"değişen: {cache_status.changed_files}"
                )
                lines.append("")
        except Exception:
            pass

        if summary.categories:
            lines.append("<b>📂 Kategoriler:</b>")
            for cat, count in sorted(summary.categories.items()):
                lines.append(f"  • {cat}: <b>{count}</b>")
            lines.append("")

        if summary.recent_events:
            lines.append(f"<b>📜 Son {len(summary.recent_events)} Olay:</b>")
            for entry in summary.recent_events:
                emoji = entry._result_emoji()
                dur = f"{entry.duration_ms:.0f}ms" if entry.duration_ms > 0 else "-"
                lines.append(
                    f"  {emoji} <code>{entry.event_name[:35]}</code> | "
                    f"{entry.phase.replace('PHASE_','')} | {dur}"
                )
                if entry.result and entry.result != "-":
                    lines.append(f"     └─ <b>{entry.result[:80]}</b>")
        else:
            lines.append("ℹ️ <i>Henüz kaydedilmiş olay yok.</i>")

        return "\n".join(lines)

    def get_constitutional_html(self) -> str:
        """Anayasal İşletim Sistemi durumunu gösterir.

        Constitution Cache + Boot Manifest + CONSTITUTION_READY durumu.
        """
        try:
            from services.constitution_cache import constitution_cache
            return constitution_cache.get_telegram_html()
        except Exception as e:
            return f"⚠️ Constitution Cache erişilemedi: {e}"

    def invalidate_cache(self):
        """LAC cache'ini temizle (yeni event sonrası çağrılır)."""
        self._cache = None
        self._last_refresh = 0.0


# Global singleton
live_activity_center = LiveActivityCenter()
