"""
Constitution Scanner — LAC için ANA YASA tarayıcı.

Tüm 22 ANA YASA .md dosyasını tarar, her WF için anayasal bağlamı
(maddeler, event'ler, bağımlılıklar, uygunluk) çıkarır.

Mevcut services/constitution_index.py'den bağımsız çalışır —
LAC kendi başına anayasa taraması yapabilmelidir.

Kullanım:
    from web.constitution_scanner import get_scanner
    scanner = get_scanner()
    ctx = scanner.get_constitution_context("WF-001")
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# ── Singleton ────────────────────────────────────────────────────────────────
_scanner: Optional["ConstitutionScanner"] = None


def get_scanner() -> "ConstitutionScanner":
    global _scanner
    if _scanner is None:
        _scanner = ConstitutionScanner()
        _scanner.build_index()
    return _scanner


# ═══════════════════════════════════════════════════════════════════════════════
# VERİ YAPILARI
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConstitutionArticle:
    article_id: str          # "AR-002_57"
    rule_type: str           # "AR" | "MASTER" | "OR" | "QR" | "GK" | "GC"
    title: str               # Başlık
    content: str             # Tam metin (ilk 500 karakter)
    source_file: str         # "03_Architecture_Rules.md"
    related_wfs: list[str] = field(default_factory=list)


@dataclass
class WFEvent:
    event_id: str            # "OLAY-003"
    event_name: str          # "EVENT_PRODUCT_LINK_RECEIVED"
    description: str
    source_state: str
    target_state: str
    result: str


@dataclass
class ConstitutionalBasis:
    wf_id: str
    master_articles: list[ConstitutionArticle] = field(default_factory=list)
    ar_articles: list[ConstitutionArticle] = field(default_factory=list)
    or_articles: list[ConstitutionArticle] = field(default_factory=list)
    qr_articles: list[ConstitutionArticle] = field(default_factory=list)
    gk_articles: list[ConstitutionArticle] = field(default_factory=list)
    gc_params: list[dict] = field(default_factory=list)
    features: list[str] = field(default_factory=list)


@dataclass
class DependencyChain:
    wf_id: str
    feeds_from: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    feeds_to: list[str] = field(default_factory=list)
    feed_descriptions: dict[str, str] = field(default_factory=dict)


@dataclass
class ComplianceResult:
    wf_id: str
    verdict: str                # "COMPLIANT" | "PARTIAL" | "VIOLATION" | "UNKNOWN"
    applied_rules: list[str] = field(default_factory=list)
    missing_rules: list[str] = field(default_factory=list)
    violated_rules: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# ANA TARAYICI
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionScanner:
    """ANA YASA tarayıcı — WF-madde eşleme, anayasal dayanak, uygunluk."""

    def __init__(self):
        self._articles: dict[str, ConstitutionArticle] = {}
        self._wf_basis: dict[str, ConstitutionalBasis] = {}
        self._wf_deps: dict[str, DependencyChain] = {}
        self._wf_events: dict[str, list[WFEvent]] = {}
        self._wf_purposes: dict[str, str] = {}
        self._ar_refs: dict[str, str] = {}   # AR kodu → başlık
        self._gc_params: list[dict] = []
        self._built: bool = False

    # ── Build ────────────────────────────────────────────────────────────────

    def build_index(self) -> bool:
        """Tüm ANA YASA dosyalarını tara ve indeksle."""
        if self._built:
            return True

        ana_yasa_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "ANA YASA"
        )
        if not os.path.isdir(ana_yasa_dir):
            logger.warning(f"ANA YASA dizini bulunamadı: {ana_yasa_dir}")
            return False

        try:
            self._parse_architecture_rules(ana_yasa_dir)
            self._parse_master_rules(ana_yasa_dir)
            self._parse_operational_rules(ana_yasa_dir)
            self._parse_quality_rules(ana_yasa_dir)
            self._parse_general_rules(ana_yasa_dir)
            self._parse_gc_params(ana_yasa_dir)
            self._parse_workflow_manifest(ana_yasa_dir)
            self._parse_workflow_feature_map(ana_yasa_dir)
            self._parse_event_registry(ana_yasa_dir)
            self._build_wf_articles()
            self._build_dependency_chains()
            self._build_wf_purposes()
            self._built = True
            logger.info(
                f"📚 [ConstitutionScanner] Index hazır: "
                f"{len(self._articles)} madde, {len(self._wf_basis)} WF, "
                f"{len(self._wf_events)} event grubu"
            )
        except Exception as e:
            logger.error(f"ConstitutionScanner build hatası: {e}")
            return False
        return True

    # ── Dosya Okuyucu ────────────────────────────────────────────────────────

    def _read_file(self, directory: str, filename: str) -> str:
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # ── AR Maddeleri (03_Architecture_Rules.md) ─────────────────────────────

    def _parse_architecture_rules(self, directory: str) -> None:
        content = self._read_file(directory, "03_Architecture_Rules.md")
        # AR-002_XX başlıklarını bul
        pattern = r'## (AR-\d+_[A-Za-z0-9]+)\s*\n+(?:### .*?\n+)?(?:### Başlık\s*\n+(.*?)\n)?(.*?)(?=\n## AR-|\n---\n## [A-Z]|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            art_id = m.group(1).strip()
            title = (m.group(2) or "").strip()
            body = (m.group(3) or "").strip()
            if not title and body:
                title = body.split("\n")[0].strip()[:120]
            article = ConstitutionArticle(
                article_id=art_id,
                rule_type="AR",
                title=title,
                content=body[:800],
                source_file="03_Architecture_Rules.md",
            )
            self._articles[art_id] = article
            self._ar_refs[art_id] = title or art_id

    # ── MASTER Kuralları (00_HLK_MASTER_RULE_BOOK.md) ───────────────────────

    def _parse_master_rules(self, directory: str) -> None:
        content = self._read_file(directory, "00_HLK_MASTER_RULE_BOOK.md")
        pattern = r'### (MASTER-\d+)\s+(.*?)\n(.*?)(?=\n### MASTER-|\n---|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            art_id = m.group(1).strip()
            title = m.group(2).strip()
            body = m.group(3).strip()
            self._articles[art_id] = ConstitutionArticle(
                article_id=art_id,
                rule_type="MASTER",
                title=title,
                content=body[:800],
                source_file="00_HLK_MASTER_RULE_BOOK.md",
            )

    # ── Operasyonel Kurallar (04_Operational_Rules.md) ───────────────────────

    def _parse_operational_rules(self, directory: str) -> None:
        content = self._read_file(directory, "04_Operational_Rules.md")
        pattern = r'### (OR-\d+_\d+)\s+(.*?)\n(.*?)(?=\n### OR-|\n---|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            art_id = m.group(1).strip()
            title = m.group(2).strip()
            body = m.group(3).strip()
            self._articles[art_id] = ConstitutionArticle(
                article_id=art_id,
                rule_type="OR",
                title=title,
                content=body[:600],
                source_file="04_Operational_Rules.md",
            )

    # ── Kalite Kuralları (05_Quality_Rules.md) ───────────────────────────────

    def _parse_quality_rules(self, directory: str) -> None:
        content = self._read_file(directory, "05_Quality_Rules.md")
        pattern = r'### (QR-\d+_\d+)\s+(.*?)\n(.*?)(?=\n### QR-|\n---|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            art_id = m.group(1).strip()
            title = m.group(2).strip()
            body = m.group(3).strip()
            self._articles[art_id] = ConstitutionArticle(
                article_id=art_id,
                rule_type="QR",
                title=title,
                content=body[:500],
                source_file="05_Quality_Rules.md",
            )

    # ── Genel Kurallar (02_General_Rules.md) ─────────────────────────────────

    def _parse_general_rules(self, directory: str) -> None:
        content = self._read_file(directory, "02_General_Rules.md")
        pattern = r'### (GK-\d+_\d+)\s+(.*?)\n(.*?)(?=\n### GK-|\n---|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            art_id = m.group(1).strip()
            title = m.group(2).strip()
            body = m.group(3).strip()
            self._articles[art_id] = ConstitutionArticle(
                article_id=art_id,
                rule_type="GK",
                title=title,
                content=body[:500],
                source_file="02_General_Rules.md",
            )

    # ── GC Parametreleri (01_Global_Configuration.md) ────────────────────────

    def _parse_gc_params(self, directory: str) -> None:
        content = self._read_file(directory, "01_Global_Configuration.md")
        pattern = r'\|\s*`(GC_\w+)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|'
        for m in re.finditer(pattern, content):
            self._gc_params.append({
                "name": m.group(1).strip(),
                "value": m.group(2).strip(),
                "description": m.group(3).strip(),
            })

    # ── Workflow Manifest (09_WORKFLOW_MANIFEST.md) ──────────────────────────

    def _parse_workflow_manifest(self, directory: str) -> None:
        content = self._read_file(directory, "09_WORKFLOW_MANIFEST.md")
        pattern = (
            r'## (WF-\d+)\s+### Workflow\s+([^\n]+)\s+'
            r'### A[çc]ıklama\s+(.*?)### Durum\s+([^\n]+)'
        )
        for m in re.finditer(pattern, content, re.DOTALL):
            wf_id = m.group(1).strip()
            name = m.group(2).strip()
            description = m.group(3).strip()
            self._wf_purposes[wf_id] = f"{name}: {description}"[:400]

    # ── Workflow Feature Map (11_WORKFLOW_FEATURE_MAP.md) ────────────────────

    def _parse_workflow_feature_map(self, directory: str) -> None:
        content = self._read_file(directory, "11_WORKFLOW_FEATURE_MAP.md")
        # Her WF bloğunu bul
        pattern = r'### (WF-\d+)\s+(.*?)(?=\n### WF-|\Z)'
        for m in re.finditer(pattern, content, re.DOTALL):
            wf_id = m.group(1).strip()
            block = m.group(2)
            # Feature'ları çıkar
            features = []
            for fm in re.finditer(r'\*\s*(FEAT-\d+)\s+(.*?)(?=\n\*|$)', block):
                features.append(f"{fm.group(1).strip()}: {fm.group(2).strip()}")
            if wf_id not in self._wf_basis:
                self._wf_basis[wf_id] = ConstitutionalBasis(wf_id=wf_id)
            self._wf_basis[wf_id].features = features

    # ── Olay Kayıt Merkezi (14_OLAY_KAYIT_MERKEZI.md) ───────────────────────

    def _parse_event_registry(self, directory: str) -> None:
        content = self._read_file(directory, "14_OLAY_KAYIT_MERKEZI.md")
        pattern = (
            r'### (OLAY-\d+)\s+.*?\n\n'
            r'\| Alan \| Değer \|\s*\n\|[-\| ]+\|\s*\n'
            r'(.*?)(?=\n---\n|### OLAY-|\Z)'
        )
        for m in re.finditer(pattern, content, re.DOTALL):
            event_id = m.group(1).strip()
            table = m.group(2)
            fields = {}
            for row in re.finditer(r'\|\s*(.*?)\s*\|\s*(.*?)\s*\|', table):
                key = row.group(1).strip()
                val = row.group(2).strip()
                fields[key] = val

            wf_field = fields.get("İlgili Workflow", "")
            related_wfs = re.findall(r'WF-\d+', wf_field)

            wf_event = WFEvent(
                event_id=event_id,
                event_name=fields.get("Teknik Sabit", fields.get("Olay Adı", event_id)),
                description=fields.get("Açıklama", fields.get("Olay Adı", "")),
                source_state=fields.get("Kaynak Durum", ""),
                target_state=fields.get("Hedef Durum", ""),
                result=fields.get("Sonuç", ""),
            )

            for wf in related_wfs:
                if wf not in self._wf_events:
                    self._wf_events[wf] = []
                self._wf_events[wf].append(wf_event)

    # ── WF-Madde Eşlemesi ────────────────────────────────────────────────────

    def _build_wf_articles(self) -> None:
        """Her WF için ilgili anayasa maddelerini eşle."""
        # WF → keyword eşlemesi (tüm .md dosyalarında tam metin tarama)
        wf_keywords = {
            "WF-001": ("LINK", "DOĞRULAMA", "URL", "VALIDATION", "PRODUCT LINK",
                        "ÜRÜN LİNKİ", "ERİŞİLEBİLİR"),
            "WF-002": ("ARAŞTIRMA", "RESEARCH", "GÖRSEL", "IMAGE", "MARKA",
                        "BRAND", "ARKA PLAN", "BACKGROUND", "ANALİZ"),
            "WF-003": ("BRIEF", "TOPLAMA", "COLLECTION", "PLATFORM", "ÇÖZÜNÜRLÜK",
                        "FORMAT", "SÜRE", "DURATION"),
            "WF-004": ("BRIEF", "ONAY", "APPROVAL", "KONTROL", "DÜZELT"),
            "WF-005": ("SENARYO", "SCENARIO", "ÜRETİM", "GENERATION"),
            "WF-006": ("SENARYO", "SCENARIO", "ONAY", "APPROVAL"),
            "WF-007": ("FİYAT", "PRICING", "ÖDEME", "PAYMENT", "TEKLİF", "OFFER"),
            "WF-008": ("VIDEO", "ÜRETİM", "PRODUCTION", "PID", "PACKAGE",
                        "EXECUTOR", "PROVIDER", "RENDER", "TASK"),
            "WF-009": ("KALİTE", "QUALITY", "KONTROL", "CHECK"),
            "WF-010": ("TESLİM", "DELIVERY", "GÖNDER", "SEND"),
            "WF-015": ("CONSTITUTION", "ENFORCEMENT", "CEE", "DENETİM"),
            "WF-016": ("EVENT", "COLLECTOR", "EEC", "EXECUTION"),
            "WF-017": ("KARAR", "DECISION", "RUNTIME", "TALEP"),
        }

        for wf_id, keywords in wf_keywords.items():
            if wf_id not in self._wf_basis:
                self._wf_basis[wf_id] = ConstitutionalBasis(wf_id=wf_id)
            basis = self._wf_basis[wf_id]

            for art_id, article in self._articles.items():
                text = (article.title + " " + article.content).upper()
                if any(kw.upper() in text for kw in keywords):
                    article.related_wfs.append(wf_id)
                    if article.rule_type == "MASTER":
                        basis.master_articles.append(article)
                    elif article.rule_type == "AR":
                        basis.ar_articles.append(article)
                    elif article.rule_type == "OR":
                        basis.or_articles.append(article)
                    elif article.rule_type == "QR":
                        basis.qr_articles.append(article)
                    elif article.rule_type == "GK":
                        basis.gk_articles.append(article)

            # GC parametrelerini eşle
            for gc in self._gc_params:
                gc_text = (gc["name"] + " " + gc["description"]).upper()
                if any(kw.upper() in gc_text for kw in keywords):
                    basis.gc_params.append(gc)

    # ── Bağımlılık Zinciri ───────────────────────────────────────────────────

    def _build_dependency_chains(self) -> None:
        """WF bağımlılık zincirlerini kur."""
        # Ana iş akışı zinciri
        chain = ["WF-001", "WF-002", "WF-003", "WF-004", "WF-005",
                  "WF-006", "WF-007", "WF-008", "WF-009", "WF-010", "WF-011"]

        wf_outputs = {
            "WF-001": ["Doğrulanmış Ürün Linki", "Ürün Referans Paketi"],
            "WF-002": ["Araştırma Sonuçları", "Ürün Analizi", "Marka Analizi",
                        "Referans Görseller", "Hedef Kitle Analizi", "Fiyat Analizi"],
            "WF-003": ["Platform Seçimi", "Çözünürlük", "Video Süresi",
                        "Tanıtım Tarzı", "Hedef Kitle", "Ses Tercihleri",
                        "Tamamlayıcı Materyaller"],
            "WF-004": ["Onaylanmış ve Kilitlenmiş Brief Verisi"],
            "WF-005": ["Reklam Senaryosu", "Senaryo Onay Formu"],
            "WF-006": ["Onaylanmış Senaryo"],
            "WF-007": ["Yönetici Fiyatlandırma Formu", "Kullanıcı Fiyat Teklif Formu",
                        "Ödeme Doğrulaması"],
            "WF-008": ["PID (Production ID)", "Production Package",
                        "Task Package'ler", "Nihai Reklam Videosu", "Arka Plan Seslendirme"],
            "WF-009": ["Kalite Kontrol Raporu", "PASS/FAIL Kararı"],
            "WF-010": ["Kullanıcıya Teslim Edilen Video", "Arşiv Kopyası",
                        "Digital Asset Kaydı"],
            "WF-011": ["Oturum Kapatma", "Operasyon Hafızası Kaydı"],
        }

        feed_descriptions = {
            "WF-001": {
                "WF-002": "Ürün Referans Paketi ile arka plan araştırmasını başlatır. Doğrulanmış link üzerinden ürün, marka, görsel ve rakip analizi yapar.",
            },
            "WF-002": {
                "WF-003": "Araştırma sonuçları ve referans görseller ile brief toplama ekranlarını doldurur. Kullanıcıya ön bilgi sunar.",
            },
            "WF-003": {
                "WF-004": "Toplanan tüm brief verilerini onay ekranına taşır. Kullanıcıya son kontrol imkanı verir.",
            },
            "WF-004": {
                "WF-005": "Kilitlenmiş brief verisi ile senaryo üretimini başlatır. Değişiklik yapılamaz.",
            },
            "WF-005": {
                "WF-006": "Üretilen senaryoyu kullanıcı onayına sunar.",
            },
            "WF-006": {
                "WF-007": "Onaylanmış senaryo ile fiyatlandırma sürecini başlatır.",
            },
            "WF-007": {
                "WF-008": "Ödeme onayı sonrası video üretimini başlatır. PID oluşturulur, Production Package hazırlanır.",
            },
            "WF-008": {
                "WF-009": "Üretilen video ve ses çıktılarını kalite kontrol sürecine iletir.",
            },
            "WF-009": {
                "WF-010": "Kalite kontrolünden geçen videoyu teslim sürecine aktarır.",
            },
            "WF-010": {
                "WF-011": "Teslim kaydı ile oturumu başarıyla kapatır.",
            },
        }

        for i, wf_id in enumerate(chain):
            feeds_from = [chain[i - 1]] if i > 0 else []
            feeds_to = [chain[i + 1]] if i < len(chain) - 1 else []
            self._wf_deps[wf_id] = DependencyChain(
                wf_id=wf_id,
                feeds_from=feeds_from,
                produces=wf_outputs.get(wf_id, []),
                feeds_to=feeds_to,
                feed_descriptions=feed_descriptions.get(wf_id, {}),
            )

    # ── WF Amaçları ──────────────────────────────────────────────────────────

    def _build_wf_purposes(self) -> None:
        """Her WF için anayasal amaç metni oluştur."""
        defaults = {
            "WF-001": "Kullanıcıdan alınan ürün linkinin doğrulanması. GK-001_1..12 kurallarına göre link erişilebilirliği, ürün bilgisi yeterliliği ve güven puanı kontrol edilir. Doğrulanmamış link ile hiçbir alt süreç başlatılamaz.",
            "WF-002": "Doğrulanmış ürün linki üzerinden arka plan araştırması. AR-002_13 Ürün Referans Paketi ve AR-002_20 Görsel Araştırma mimarilerine göre ürün, marka, görsel, rakip ve fiyat analizi yapılır. Bilgi Açığı Analizi ile eksik veriler tespit edilir.",
            "WF-003": "Kullanıcıdan reklam üretimi için gerekli teknik parametrelerin toplanması. OR-004_2/3/4 kurallarına göre platform, çözünürlük, süre, tanıtım tarzı, hedef kitle ve ses tercihleri belirlenir.",
            "WF-004": "Toplanan brief verilerinin kullanıcı tarafından kontrol edilip onaylanması. OR-004_5'e göre tik-düzeltme mekanizması ile son kontroller yapılır. Onay sonrası brief kilitlenir.",
            "WF-005": "Onaylı brief kullanılarak reklam senaryosunun oluşturulması. AR-002_44 Scenario Approval Architecture ve QR-004_3 kalite kurallarına göre üretilir.",
            "WF-006": "Oluşturulan senaryonun kullanıcı onayına sunulması. Onay → WF-007; Ret → STATE_SESSION_CLOSED.",
            "WF-007": "Video üretimi için fiyat teklifinin hazırlanması ve ödeme süreci. AR-002_45 Pricing Architecture kapsamında yönetici fiyatlandırması, kullanıcı teklifi ve ödeme doğrulaması yapılır.",
            "WF-008": "Onaylanan senaryoya göre reklam videosunun üretilmesi. AR-002_70 Production Runtime, AR-002_57 PID standardı, AR-002_76 Executor mimarisine göre PID oluşturulur, Production Package hazırlanır ve task'lar yürütülür.",
            "WF-009": "Üretilen video ve çıktılar için kalite kontrol süreci. QR-004_4/7/8 kurallarına göre görüntü, ses ve format doğrulaması yapılır.",
            "WF-010": "Üretilen videonun kullanıcıya teslim edilmesi. Dijital varlık arşivleme ve operasyon hafızası kaydı yapılır.",
            "WF-015": "CEE tarafından yürütülen anayasal uygulatma ve denetim akışı. PRE-CHECK → EXECUTE → POST-CHECK → PASS/FAIL. Her geliştirme görevi öncesi ve sonrası otomatik tetiklenir.",
            "WF-016": "EEC tarafından yürütülen Executor işlemlerinin gerçek zamanlı Event'e dönüştürülmesi. LISTEN → TRANSFORM → REGISTER. 6 kategoride 28 Event tipi ile çalışır.",
            "WF-017": "Yürütme katmanlarında karar gerektiren durumlarda uygulanan zorunlu karar talep akışı. MASTER-013, AR-002_81, OR-004_12'ye göre yürütme durdurulur, HLK Runtime karar üretir.",
        }
        for wf_id, purpose in defaults.items():
            if wf_id not in self._wf_purposes:
                self._wf_purposes[wf_id] = purpose

    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════════

    def get_constitution_context(self, wf_id: str) -> dict:
        """Bir WF için tüm anayasal bağlamı döndürür."""
        if not self._built:
            self.build_index()

        basis = self._wf_basis.get(wf_id)
        deps = self._wf_deps.get(wf_id)
        events = self._wf_events.get(wf_id, [])

        return {
            "wf_id": wf_id,
            "purpose": self._wf_purposes.get(wf_id, f"{wf_id} — Anayasa'da tanımlı değil"),
            "master_rules": [
                {"id": a.article_id, "title": a.title, "content": a.content[:300]}
                for a in (basis.master_articles if basis else [])
            ],
            "arch_rules": [
                {"id": a.article_id, "title": a.title, "content": a.content[:300]}
                for a in (basis.ar_articles if basis else [])
            ],
            "oper_rules": [
                {"id": a.article_id, "title": a.title, "content": a.content[:300]}
                for a in (basis.or_articles if basis else [])
            ],
            "quality_rules": [
                {"id": a.article_id, "title": a.title, "content": a.content[:300]}
                for a in (basis.qr_articles if basis else [])
            ],
            "general_rules": [
                {"id": a.article_id, "title": a.title, "content": a.content[:300]}
                for a in (basis.gk_articles if basis else [])
            ],
            "gc_params": [
                {"name": g["name"], "value": g["value"], "description": g["description"]}
                for g in (basis.gc_params if basis else [])
            ],
            "features": basis.features if basis else [],
            "events": [
                {
                    "id": e.event_id, "name": e.event_name,
                    "description": e.description, "result": e.result,
                }
                for e in events
            ],
            "input_from": deps.feeds_from if deps else [],
            "outputs": deps.produces if deps else [],
            "feeds_to": deps.feeds_to if deps else [],
            "feed_descriptions": deps.feed_descriptions if deps else {},
            "ar_references": self._ar_refs,
        }

    def get_wf_basis(self, wf_id: str) -> Optional[ConstitutionalBasis]:
        """WF'in anayasal dayanak maddelerini döndürür."""
        if not self._built:
            self.build_index()
        return self._wf_basis.get(wf_id)

    def get_wf_deps(self, wf_id: str) -> Optional[DependencyChain]:
        """WF'in bağımlılık zincirini döndürür."""
        if not self._built:
            self.build_index()
        return self._wf_deps.get(wf_id)

    def get_article(self, article_id: str) -> Optional[ConstitutionArticle]:
        """Tek bir anayasa maddesini ID ile döndürür."""
        if not self._built:
            self.build_index()
        return self._articles.get(article_id)

    def get_article_detail(self, article_id: str) -> Optional[dict]:
        """Anayasa maddesinin tam detayını döndürür."""
        article = self.get_article(article_id)
        if not article:
            return None
        return {
            "id": article.article_id,
            "type": article.rule_type,
            "title": article.title,
            "content": article.content,
            "source_file": article.source_file,
            "related_wfs": article.related_wfs,
        }

    def evaluate_compliance(self, wf_id: str, package: Optional[dict]) -> ComplianceResult:
        """Bir WF için anayasal uygunluk değerlendirmesi yapar."""
        if not self._built:
            self.build_index()

        basis = self._wf_basis.get(wf_id)
        if not basis:
            return ComplianceResult(wf_id=wf_id, verdict="UNKNOWN")

        applied = []
        missing = []

        # Package varsa, anayasa maddelerinin uygulanıp uygulanmadığını kontrol et
        if package:
            pkg_str = str(package).upper()

            # AR maddelerini kontrol et
            for art in basis.ar_articles:
                art_text = (art.title + " " + art.content[:200]).upper()
                # Basit kanıt kontrolü: package'te ilgili anahtar kelimeler var mı?
                keywords = self._extract_keywords(art.article_id)
                if any(kw.upper() in pkg_str for kw in keywords):
                    applied.append(art.article_id)
                else:
                    missing.append(art.article_id)

            # OR maddelerini kontrol et
            for art in basis.or_articles:
                art_text = (art.title + " " + art.content[:200]).upper()
                keywords = self._extract_keywords(art.article_id)
                if any(kw.upper() in pkg_str for kw in keywords):
                    applied.append(art.article_id)
                else:
                    missing.append(art.article_id)
        else:
            missing = [a.article_id for a in basis.ar_articles + basis.or_articles]

        if not applied and not missing:
            verdict = "UNKNOWN"
        elif missing and not applied:
            verdict = "VIOLATION"
        elif missing:
            verdict = "PARTIAL"
        else:
            verdict = "COMPLIANT"

        return ComplianceResult(
            wf_id=wf_id,
            verdict=verdict,
            applied_rules=applied,
            missing_rules=missing,
        )

    def _extract_keywords(self, article_id: str) -> list[str]:
        """Anayasa maddesi ile ilişkili anahtar kelimeleri döndürür."""
        article = self._articles.get(article_id)
        if not article:
            return [article_id]
        text = (article.title + " " + article.content[:400]).upper()
        # Noktalama işaretlerini temizle, boşluğa göre böl
        words = re.findall(r'[A-Z0-9_]{3,}', text)
        return list(set(words))[:10]

    def get_all_wf_ids(self) -> list[str]:
        """Tüm business WF'leri döndürür."""
        return ["WF-001", "WF-002", "WF-003", "WF-004", "WF-005",
                "WF-006", "WF-007", "WF-008", "WF-009", "WF-010",
                "WF-011", "WF-015", "WF-016", "WF-017"]

    # ── Güven Puanı ───────────────────────────────────────────────────────

    def calculate_trust_score(self, wf_id: str, package: Optional[dict]) -> dict:
        """İş Akışı Güven Puanı hesapla (0-100)."""
        if not self._built:
            self.build_index()

        scores = {"karar_kaniti": 0, "anayasal_uyum": 0, "cikti_butunlugu": 0,
                   "bagimlilik_kontrol": 0, "kod_uyumu": 0}

        if package:
            pkg_str = str(package).upper()
            tasks = package.get("task_packages", []) or []
            decisions = package.get("decision_history", []) or []
            events_count = len(self._wf_events.get(wf_id, []))

            # Karar Kanıtı: Decision var mı? (max 20)
            if decisions:
                scores["karar_kaniti"] = min(20, len(decisions) * 10)

            # Anayasal Uyum: Package'te anayasa referansı var mı? (max 20)
            basis = self._wf_basis.get(wf_id)
            if basis:
                total_rules = len(basis.ar_articles) + len(basis.or_articles) + len(basis.qr_articles)
                if total_rules > 0:
                    applied = sum(1 for a in basis.ar_articles
                                  if any(kw.upper() in pkg_str for kw in self._extract_keywords(a.article_id)[:5]))
                    scores["anayasal_uyum"] = min(20, int((applied / max(total_rules, 1)) * 20))

            # Çıktı Bütünlüğü: Beklenen çıktılar mevcut mu? (max 20)
            deps = self._wf_deps.get(wf_id)
            if deps and deps.produces:
                present = 0
                for o in deps.produces:
                    if any(kw.upper() in pkg_str for kw in o.upper().split()):
                        present += 1
                scores["cikti_butunlugu"] = min(20, int((present / len(deps.produces)) * 20))

            # Bağımlılık Kontrolü: Beslendiği WF'lerden veri gelmiş mi? (max 20)
            if deps and deps.feeds_from:
                scores["bagimlilik_kontrol"] = 15
                if events_count > 0:
                    scores["bagimlilik_kontrol"] = 20

            # Kod Uyumu: Task'lar tamamlanmış mı? (max 20)
            if tasks:
                completed = sum(1 for t in tasks if t.get("status") in ("COMPLETED", "SUCCESS"))
                scores["kod_uyumu"] = min(20, int((completed / max(len(tasks), 1)) * 20))

        total = sum(scores.values())
        return {
            "total": total,
            "max": 100,
            "breakdown": scores,
            "label": "Yüksek Güven" if total >= 85 else "Orta Güven" if total >= 60
            else "Düşük Güven" if total >= 30 else "Güven Yetersiz",
        }

    def get_wf_summary(self, wf_id: str, package: Optional[dict]) -> dict:
        """Yönetici Özeti için hızlı istatistikler."""
        if not self._built:
            self.build_index()
        compliance = self.evaluate_compliance(wf_id, package)
        deps = self._wf_deps.get(wf_id)
        trust = self.calculate_trust_score(wf_id, package)
        outputs_count = len(deps.produces) if deps else 0
        feeds_to_count = len(deps.feeds_to) if deps else 0

        status = "completed"
        if package:
            pkg_status = (package.get("metadata", {}) or {}).get("status", "")
            if pkg_status == "FAILED":
                status = "failed"
            elif pkg_status in ("COMPLETED", "SUCCESS"):
                status = "completed"
            elif any(t.get("status") in ("PRODUCING", "PROCESSING") for t in
                     (package.get("task_packages", []) or [])):
                status = "running"
            else:
                status = "pending"

        return {
            "status": status,
            "duration": "—",
            "trust_score": trust["total"],
            "trust_label": trust["label"],
            "output_count": outputs_count,
            "feeds_to_count": feeds_to_count,
            "violation_count": len(compliance.violated_rules),
            "compliance_verdict": compliance.verdict,
        }

    def get_article_status(self, article_id: str, wf_id: str,
                           package: Optional[dict]) -> dict:
        """Bir anayasa maddesinin bu WF'teki durumunu değerlendir."""
        article = self._articles.get(article_id)
        if not article:
            return {"status": "not_found", "label": "Bulunamadı"}

        if not package:
            return {"status": "not_evaluated", "label": "Değerlendirilmedi"}

        pkg_str = str(package).upper()
        keywords = self._extract_keywords(article_id)
        evidence_found = any(kw.upper() in pkg_str for kw in keywords)

        # Event kontrolü
        wf_events = self._wf_events.get(wf_id, [])
        event_evidence = [e.event_id for e in wf_events
                          if any(kw.upper() in e.description.upper() for kw in keywords[:3])]

        decisions = package.get("decision_history", []) or []
        decision_ids = [d.get("decision_id", "") for d in decisions[:5]]

        tasks = package.get("task_packages", []) or []
        task_ids = [t.get("task_id", "") for t in tasks[:5]]

        if evidence_found and event_evidence:
            status = "applied"
            label = "Uygulandı"
        elif evidence_found:
            status = "partial"
            label = "Kısmi Uyum"
        else:
            status = "not_applied"
            label = "Uygulanmadı"

        return {
            "article_id": article_id,
            "title": article.title,
            "content": article.content,
            "status": status,
            "label": label,
            "evidence": {
                "decision_ids": decision_ids,
                "task_ids": task_ids,
                "event_ids": event_evidence,
            },
            "related": [a.article_id for a in self._articles.values()
                       if a.article_id != article_id and
                       any(kw.upper() in article.content.upper() for kw in
                           self._extract_keywords(a.article_id)[:3])][:5],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MODÜL DÜZEYİNDE KOLAYLIK FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════════

def get_constitution_context(wf_id: str) -> dict:
    return get_scanner().get_constitution_context(wf_id)


def invalidate_cache() -> None:
    global _scanner
    _scanner = None
    logger.info("🔄 ConstitutionScanner cache temizlendi")
