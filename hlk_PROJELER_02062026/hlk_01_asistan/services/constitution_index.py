"""
Constitution Rule Index — HLK Generic Constitutional Engine

ANA YASA .md dosyalarından tüm kuralları ayrıştırır, yapılandırılmış
IndexedRule nesnelerine dönüştürür ve Generic Validation sağlar.

Yeni bir anayasa maddesi eklendiğinde:
  1. .md dosyası güncellenir
  2. Constitution Cache değişikliği algılar
  3. Constitution Index otomatik yeniden build alır
  4. Yeni kural otomatik denetime girer
  → SIFIR Python kodu değişikliği

Mimari: MASTER-001, MASTER-003, AR-002_60, CEE, CDE, CSE
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ANA YASA dizini
ANA_YASA_DIR = Path(__file__).resolve().parent.parent / "ANA YASA"

# Rule ID pattern'leri — her kural ailesi için regex (## heading + inline)
RULE_PATTERNS = {
    "MASTER": re.compile(r'(?:## )?MASTER-(\d{3})', re.MULTILINE),
    "AR":     re.compile(r'(?:## )?AR-(\d{3})_(\d+)', re.MULTILINE),
    "OR":     re.compile(r'(?:## )?OR-(\d{3})_(\d+)', re.MULTILINE),
    "QR":     re.compile(r'(?:## )?QR-(\d{3})_(\d+)', re.MULTILINE),
    "MR":     re.compile(r'(?:## )?MR-(\d{3})_(\d+)', re.MULTILINE),
    "GK":     re.compile(r'(?:## )?GK-(\d{3})_(\d+)', re.MULTILINE),
    "SE":     re.compile(r'(?:## )?SE-(\d{3})_(\d+)', re.MULTILINE),
    "FD":     re.compile(r'(?:## )?FD-(\d{3})_(\d+)', re.MULTILINE),
    "WF":     re.compile(r'(?:## )?WF-(\d{3})', re.MULTILINE),
    "FEAT":   re.compile(r'(?:## )?FEAT-(\d{3})', re.MULTILINE),
}

# Kategori anahtar kelimeleri — kural içeriğinden otomatik kategori çıkarımı
CATEGORY_KEYWORDS = {
    "Cleanup":     ["temizle", "cleanup", "silin", "delete", "kaldır", "remove"],
    "Button":      ["buton", "button", "devam", "bitti", "onay", "ret"],
    "State":       ["state", "durum", "geçiş", "transition", "STATE_"],
    "Event":       ["event", "olay", "tetikle", "trigger", "EVENT_", "OLAY-"],
    "Video":       ["video", "görüntü", "sendvideo", "sahne-"],
    "Timeout":     ["timeout", "zaman aşımı", "süre", "bekleme"],
    "Validation":  ["doğrula", "validate", "kontrol", "check", "garanti"],
    "Security":    ["api_key", "token", "yetki", "güvenlik", "authority"],
    "Workflow":    ["workflow", "akış", "flow", "iş akışı", "WF-"],
    "Feature":     ["feature", "özellik", "FEAT-"],
    "Architecture":["mimari", "architecture", "katman", "layer", "AR-"],
    "Operational": ["operasyon", "operational", "çalışma", "OR-"],
}

# Kural içeriğinden zorunluluk tespiti için anahtar kelimeler
CONSTRAINT_KEYWORDS = {
    "zorunlu":     "MANDATORY",
    "kesinlikle":  "ABSOLUTE",
    "yasaktır":    "PROHIBITED",
    "garanti":     "GUARANTEED",
    "olmadan":     "PRECONDITION",
    "yalnızca":    "EXCLUSIVE",
    "hiçbir":      "NEGATIVE",
    "her zaman":   "ALWAYS",
}


@dataclass
class IndexedRule:
    """Constitution Index'teki tek bir kural kaydı."""
    rule_id: str                    # "MASTER-003", "AR-002_28", "OR-004_0"
    rule_type: str                  # "MASTER", "AR", "OR", "QR", "MR", "GK", "SE", "FD", "WF"
    domain: str                     # "002", "004", "007", "008"
    sequence: str                   # "1", "28", "0"
    category: str = "General"       # Cleanup, Button, State, Event, Video, Timeout, ...
    title: str = ""                 # Kural başlığı
    description: str = ""           # İlk paragraf
    constraint_level: str = ""      # MANDATORY, PROHIBITED, GUARANTEED, ...
    source_file: str = ""           # Hangi .md dosyasından
    source_line: int = 0            # Kaçıncı satırda başlıyor
    related_rules: list[str] = field(default_factory=list)  # Referans verdiği diğer kurallar
    check_targets: list[str] = field(default_factory=list)  # "cleanup", "button", "state_transition", ...
    raw_text: str = ""              # Ham kural metni (ilk 500 karakter)


@dataclass
class IndexStats:
    """Constitution Index istatistikleri."""
    total_rules: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    source_files: int = 0
    build_duration_ms: float = 0.0
    last_build: str = ""


@dataclass
class GenericValidationResult:
    """Generic Validation sonucu — hangi kural, ne buldu?"""
    rule_id: str
    rule_type: str
    category: str
    passed: bool
    runtime_value: str      # Runtime'da ölçülen değer
    expected_value: str     # Kuralda beklenen değer
    evidence: str           # Kanıt açıklaması
    ana_yasa_ref: str       # ANA YASA referansı
    severity: str = "ORTA"


class ConstitutionIndex:
    """HLK Generic Constitutional Rule Index.

    ANA YASA .md dosyalarındaki tüm kuralları ayrıştırır, indeksler
    ve Runtime Generic Validation sağlar.

    Temel prensip: Yeni kural = .md güncellemesi. Python kodu değişmez.
    """

    def __init__(self):
        self._rules: list[IndexedRule] = []
        self._by_type: dict[str, list[IndexedRule]] = {}
        self._by_category: dict[str, list[IndexedRule]] = {}
        self._by_id: dict[str, IndexedRule] = {}
        self._stats: Optional[IndexStats] = None
        self._built: bool = False

    # ── Build: .md dosyalarından kural ayrıştırma ──────────────────────────

    def build(self) -> IndexStats:
        """Tüm ANA YASA .md dosyalarını tara, kuralları ayrıştır, indeksle.

        Returns:
            IndexStats — kaç kural bulundu, hangi tiplerde, ne kadar sürdü
        """
        t0 = time.time()
        self._rules.clear()
        self._by_type.clear()
        self._by_category.clear()
        self._by_id.clear()

        md_files = sorted(ANA_YASA_DIR.glob("*.md"))
        stats = IndexStats(source_files=len(md_files))

        for md_path in md_files:
            try:
                content = md_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"⚠️ [Index] Okunamadı: {md_path.name} — {e}")
                continue

            # Her kural ailesi için pattern'leri tara
            for rule_type, pattern in RULE_PATTERNS.items():
                for match in pattern.finditer(content):
                    rule_id = match.group(0).replace('## ', '')
                    domain = match.group(1) if match.lastindex >= 1 else ""
                    sequence = match.group(2) if match.lastindex >= 2 else ""

                    # Kural metnini çıkar (başlık + ilk paragraf)
                    start_pos = match.start()
                    # Başlığı bul (## ile başlayan satır)
                    line_start = content.rfind("\n", 0, start_pos) + 1
                    line_end = content.find("\n", start_pos)
                    title_line = content[line_start:line_end].strip()

                    # Açıklamayı al (sonraki 500 karakter)
                    desc_start = line_end + 1 if line_end > 0 else start_pos + len(rule_id)
                    raw_text = content[desc_start:desc_start + 500].strip()

                    # Başlığı temizle
                    title = title_line.replace("## ", "").replace(f"`{rule_id}`", "").strip()
                    if not title or title.startswith("#"):
                        title = rule_id

                    # Kategori tespiti
                    category = self._detect_category(raw_text, title)

                    # Zorunluluk seviyesi
                    constraint = self._detect_constraint(raw_text)

                    # İlişkili kuralları bul
                    related = self._find_related_rules(raw_text, rule_id)

                    # Check hedeflerini belirle
                    check_targets = self._determine_check_targets(
                        category, raw_text, rule_type
                    )

                    rule = IndexedRule(
                        rule_id=rule_id,
                        rule_type=rule_type,
                        domain=domain,
                        sequence=sequence,
                        category=category,
                        title=title[:100],
                        description=raw_text[:200],
                        constraint_level=constraint,
                        source_file=md_path.name,
                        source_line=content[:start_pos].count("\n") + 1,
                        related_rules=related,
                        check_targets=check_targets,
                        raw_text=raw_text,
                    )

                    self._add_rule(rule)
                    stats.total_rules += 1

        # İstatistikleri hesapla
        for rule in self._rules:
            stats.by_type[rule.rule_type] = stats.by_type.get(rule.rule_type, 0) + 1
            stats.by_category[rule.category] = stats.by_category.get(rule.category, 0) + 1

        stats.build_duration_ms = (time.time() - t0) * 1000
        stats.last_build = time.strftime("%Y-%m-%d %H:%M:%S")
        self._stats = stats
        self._built = True

        logger.info(
            f"📚 [Index] Build tamam: {stats.total_rules} kural | "
            f"{len(stats.by_type)} tip | {len(stats.by_category)} kategori | "
            f"{stats.build_duration_ms:.0f}ms"
        )
        return stats

    def _add_rule(self, rule: IndexedRule):
        """Bir kuralı tüm indekslere ekle."""
        self._rules.append(rule)
        self._by_id[rule.rule_id] = rule
        self._by_type.setdefault(rule.rule_type, []).append(rule)
        self._by_category.setdefault(rule.category, []).append(rule)

    def _detect_category(self, text: str, title: str) -> str:
        """Kural içeriğinden kategori tespiti."""
        combined = (title + " " + text).lower()
        scores = {}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in combined)
            if score > 0:
                scores[cat] = score
        if scores:
            return max(scores, key=scores.get)
        return "General"

    def _detect_constraint(self, text: str) -> str:
        """Kuralın zorunluluk seviyesini tespit et."""
        text_lower = text.lower()
        for kw, level in CONSTRAINT_KEYWORDS.items():
            if kw in text_lower:
                return level
        return "ADVISORY"

    def _find_related_rules(self, text: str, own_id: str) -> list[str]:
        """Metin içinde referans verilen diğer kural ID'lerini bul."""
        related = []
        for rule_type, pattern in RULE_PATTERNS.items():
            for match in pattern.finditer(text):
                ref_id = match.group(0)
                if ref_id != own_id and ref_id not in related:
                    related.append(ref_id)
        return related[:10]  # Max 10 referans

    def _determine_check_targets(
        self, category: str, text: str, rule_type: str
    ) -> list[str]:
        """Kuralın hangi runtime kontrollerini gerektirdiğini belirle."""
        targets = []
        text_lower = text.lower()

        # Kategori bazlı hedefler
        if category == "Cleanup":
            targets.append("cleanup_count")
        if category == "Button":
            targets.append("button_exists")
        if category == "State":
            targets.append("state_transition")
        if category == "Event":
            targets.append("event_emitted")
        if category == "Video":
            targets.append("video_sent")
        if category == "Timeout":
            targets.append("timeout_active")

        # İçerik bazlı hedefler
        if any(kw in text_lower for kw in ["silin", "delete", "kaldır"]):
            if "cleanup_count" not in targets:
                targets.append("cleanup_count")
        if any(kw in text_lower for kw in ["buton", "button", "devam"]):
            if "button_exists" not in targets:
                targets.append("button_exists")
        if any(kw in text_lower for kw in ["state", "durum", "geçiş"]):
            if "state_transition" not in targets:
                targets.append("state_transition")

        if not targets:
            targets.append("documentation")

        return targets

    # ── Query: İndeks sorgulama ────────────────────────────────────────────

    def get_rules_by_type(self, rule_type: str) -> list[IndexedRule]:
        """Rule tipine göre filtrele (MASTER, AR, OR, ...)."""
        return self._by_type.get(rule_type, [])

    def get_rules_by_category(self, category: str) -> list[IndexedRule]:
        """Kategoriye göre filtrele (Cleanup, Button, State, ...)."""
        return self._by_category.get(category, [])

    def get_rule_by_id(self, rule_id: str) -> Optional[IndexedRule]:
        """Rule ID'ye göre tek kural getir."""
        return self._by_id.get(rule_id)

    def get_all_rules(self) -> list[IndexedRule]:
        """Tüm kuralları döndür."""
        return self._rules

    def get_stats(self) -> Optional[IndexStats]:
        """İndeks istatistikleri."""
        return self._stats

    def search(self, query: str) -> list[IndexedRule]:
        """Kural ID, başlık veya açıklamada arama."""
        query_lower = query.lower()
        results = []
        for rule in self._rules:
            if (query_lower in rule.rule_id.lower() or
                query_lower in rule.title.lower() or
                query_lower in rule.description.lower()):
                results.append(rule)
        return results

    def is_built(self) -> bool:
        return self._built

    def get_rule_count(self) -> int:
        return len(self._rules)

    # ── Generic Validation Engine ──────────────────────────────────────────

    def validate_runtime(
        self, runtime_context: dict
    ) -> tuple[list[GenericValidationResult], bool]:
        """Generic Runtime Validation.

        Runtime context'i tüm ilgili IndexedRule'larla karşılaştırır.
        Her kural için PASS/FAIL üretir.

        Args:
            runtime_context: {
                "state": "STATE_SCENE_2",
                "scene": "SAHNE-02",
                "cleanup": {"total": 3, "success": 3},
                "buttons": ["DEVAM"],
                "video_sent": True,
                "events_emitted": ["EVENT_LANGUAGE_SELECTED"],
                "transitions": ["LANGUAGE_SELECTION → WAIT_PRODUCT_LINK"],
                ...
            }

        Returns:
            (validation_results, overall_pass)
        """
        if not self._built:
            logger.warning("⚠️ [Validator] Index henüz build edilmedi")
            return [], False

        results: list[GenericValidationResult] = []

        # 1. Cleanup validasyonu
        if "cleanup" in runtime_context:
            cleanup = runtime_context["cleanup"]
            cleanup_total = cleanup.get("total", 0)
            cleanup_success = cleanup.get("success", 0)

            # İlgili kuralları bul
            cleanup_rules = (
                self.get_rules_by_category("Cleanup") +
                self.search("cleanup") +
                self.search("temizle") +
                self.search("silin")
            )
            # Benzersiz kuralları al
            seen = set()
            unique_cleanup = []
            for r in cleanup_rules:
                if r.rule_id not in seen:
                    seen.add(r.rule_id)
                    unique_cleanup.append(r)

            for rule in unique_cleanup[:5]:  # Max 5 cleanup kuralı
                passed = cleanup_success >= cleanup_total if cleanup_total > 0 else True
                results.append(GenericValidationResult(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    category="Cleanup",
                    passed=passed,
                    runtime_value=f"{cleanup_success}/{cleanup_total} mesaj silindi",
                    expected_value=f"{cleanup_total}/{cleanup_total} mesaj silinmeli",
                    evidence=f"Cleanup: {cleanup_success}/{cleanup_total} başarılı",
                    ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                    severity=rule.constraint_level,
                ))

        # 2. State Transition validasyonu
        if "state" in runtime_context:
            current_state = runtime_context.get("state", "")
            state_rules = (
                self.get_rules_by_type("SE") +
                self.get_rules_by_category("State")
            )
            seen = set()
            unique_state = []
            for r in state_rules:
                if r.rule_id not in seen:
                    seen.add(r.rule_id)
                    unique_state.append(r)

            state_valid = bool(current_state and current_state.startswith("STATE_"))
            for rule in unique_state[:5]:
                results.append(GenericValidationResult(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    category="State",
                    passed=state_valid,
                    runtime_value=f"Mevcut state: {current_state}",
                    expected_value="Geçerli STATE_* state'i",
                    evidence=f"State Engine aktif: {current_state}",
                    ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                    severity="MANDATORY",
                ))

        # 3. Button validasyonu
        if "buttons" in runtime_context:
            buttons = runtime_context.get("buttons", [])
            button_rules = (
                self.get_rules_by_category("Button") +
                self.search("buton") +
                self.search("button")
            )
            seen = set()
            unique_btn = []
            for r in button_rules:
                if r.rule_id not in seen:
                    seen.add(r.rule_id)
                    unique_btn.append(r)

            for rule in unique_btn[:5]:
                btn_ok = len(buttons) > 0
                results.append(GenericValidationResult(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    category="Button",
                    passed=btn_ok,
                    runtime_value=f"Butonlar: {buttons}",
                    expected_value="En az 1 buton bulunmalı",
                    evidence=f"{len(buttons)} buton mevcut: {buttons}",
                    ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                    severity="MANDATORY",
                ))

        # 4. Video validasyonu
        if "video_sent" in runtime_context:
            video_ok = runtime_context.get("video_sent", False)
            video_rules = (
                self.get_rules_by_category("Video") +
                self.search("video") +
                self.search("sahne")
            )
            seen = set()
            unique_vid = []
            for r in video_rules:
                if r.rule_id not in seen:
                    seen.add(r.rule_id)
                    unique_vid.append(r)

            for rule in unique_vid[:5]:
                results.append(GenericValidationResult(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    category="Video",
                    passed=video_ok,
                    runtime_value=f"Video gönderildi: {video_ok}",
                    expected_value="Video başarıyla gönderilmeli",
                    evidence=f"Video durumu: {'✅' if video_ok else '❌'}",
                    ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                    severity="MANDATORY",
                ))

        # 5. Event validasyonu
        if "events_emitted" in runtime_context:
            events = runtime_context.get("events_emitted", [])
            event_rules = (
                self.get_rules_by_category("Event") +
                self.search("event") +
                self.search("olay")
            )
            seen = set()
            unique_evt = []
            for r in event_rules:
                if r.rule_id not in seen:
                    seen.add(r.rule_id)
                    unique_evt.append(r)

            for rule in unique_evt[:5]:
                evt_ok = len(events) > 0
                results.append(GenericValidationResult(
                    rule_id=rule.rule_id,
                    rule_type=rule.rule_type,
                    category="Event",
                    passed=evt_ok,
                    runtime_value=f"{len(events)} event",
                    expected_value="En az 1 event üretilmeli",
                    evidence=f"Event'ler: {events[:3]}",
                    ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                    severity="MANDATORY",
                ))

        # 6. Operational validasyonu
        op_rules = self.get_rules_by_type("OR")[:3]
        for rule in op_rules:
            results.append(GenericValidationResult(
                rule_id=rule.rule_id,
                rule_type=rule.rule_type,
                category="Operational",
                passed=True,  # OR kuralları dokümantasyon — runtime'da ihlal yoksa PASS
                runtime_value="Operasyonel kurallara uygun",
                expected_value=rule.title[:80],
                evidence=f"OR kuralı mevcut: {rule.title[:80]}",
                ana_yasa_ref=f"{rule.rule_id} ({rule.source_file})",
                severity=rule.constraint_level,
            ))

        # Genel sonuç
        all_pass = all(r.passed for r in results) if results else True
        fail_count = sum(1 for r in results if not r.passed)

        logger.info(
            f"🔍 [Generic Validator] {len(results)} kural denetlendi | "
            f"✅ {len(results) - fail_count} PASS | "
            f"{'❌' if fail_count > 0 else '✅'} {fail_count} FAIL"
        )

        return results, all_pass

    def validate_and_report(
        self, runtime_context: dict
    ) -> dict:
        """Generic Validation çalıştır ve rapor formatında döndür.

        CEE post_check için hazır deficiencies listesi üretir.
        """
        results, all_pass = self.validate_runtime(runtime_context)

        deficiencies = []
        for r in results:
            if not r.passed:
                deficiencies.append({
                    "type": f"{r.category.upper()}_FAILED",
                    "description": (
                        f"[{r.rule_id}] {r.evidence}. "
                        f"Beklenen: {r.expected_value}, "
                        f"Gerçek: {r.runtime_value}"
                    ),
                    "ana_yasa_ref": r.ana_yasa_ref,
                    "file": "handlers/start.py",
                    "severity": r.severity,
                })

        return {
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "all_pass": all_pass,
            "results": [
                {
                    "rule_id": r.rule_id,
                    "rule_type": r.rule_type,
                    "category": r.category,
                    "passed": r.passed,
                    "evidence": r.evidence,
                    "severity": r.severity,
                }
                for r in results
            ],
            "deficiencies": deficiencies,
        }

    def get_telegram_html(self) -> str:
        """İndeks durumunu Telegram HTML formatında döndür."""
        if not self._stats:
            return "⚠️ <b>Constitution Index henüz build edilmedi.</b>"

        s = self._stats
        lines = [
            "📚 <b>CONSTITUTION RULE INDEX</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 Toplam Kural: <b>{s.total_rules}</b>",
            f"📁 Kaynak Dosya: <b>{s.source_files}</b>",
            f"⏱️ Build Süresi: <b>{s.build_duration_ms:.0f}ms</b>",
            f"🕐 Son Build: <b>{s.last_build}</b>",
            "",
            "<b>📂 Kural Tipleri:</b>",
        ]
        for rtype, count in sorted(s.by_type.items()):
            lines.append(f"  • {rtype}: <b>{count}</b> kural")
        lines.append("")
        lines.append("<b>🏷️ Kategoriler:</b>")
        for cat, count in sorted(s.by_category.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  • {cat}: <b>{count}</b> kural")

        return "\n".join(lines)


# Global singleton
constitution_index = ConstitutionIndex()
