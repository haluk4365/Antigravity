"""
Constitution Cache Manager — HLK Anayasal İşletim Sistemi

ANA YASA/*.md dosyalarını SHA-256 hash'ler, bellekte önbellekler.
Sonraki kontrollerde yalnızca değişen dosyaları yeniden okur.

Mimari: MASTER-001, MASTER-003, CSE, CDE
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ANA YASA dizini
ANA_YASA_DIR = Path(__file__).resolve().parent.parent / "ANA YASA"

# 18 katmanlı Constitutional Boot sırası
BOOT_LAYERS = [
    ("01_Global_Configuration.md",    "Global Configuration"),
    ("02_General_Rules.md",           "General Rules"),
    ("03_Architecture_Rules.md",      "Architecture Rules"),
    ("04_Operational_Rules.md",       "Operational Rules"),
    ("05_Quality_Rules.md",           "Quality Rules"),
    ("06_Module_Rule.md",             "Module Rules"),
    ("07_HLK_STATE_ENGINE.md",        "State Engine"),
    ("08_HLK_FLOW_DIAGRAM.md",        "Flow Diagram"),
    ("09_WORKFLOW_MANIFEST.md",       "Workflow Manifest"),
    ("10_FEATURE_REGISTRY.md",        "Feature Registry"),
    ("11_WORKFLOW_FEATURE_MAP.md",    "Workflow Feature Map"),
    ("12_DIGITAL_ASSET_ARCHIVE.md",   "Digital Asset Archive"),
    ("13_DIGITAL_ASSET_CATALOG.md",   "Digital Asset Catalog"),
    ("14_OLAY_KAYIT_MERKEZI.md",      "Olay Kayıt Merkezi"),
    ("18_CONSTITUTION_DIFF_ENGINE.md","Constitution Diff Engine"),
    ("19_CONSTITUTION_SCAN_ENGINE.md","Constitution Scan Engine"),
    ("20_TASK_ENGINE.md",             "Task Engine"),
    ("00_HLK_MASTER_RULE_BOOK.md",    "HLK Master Rule Book"),
]


@dataclass
class FileEntry:
    """Tek bir ANA YASA dosyasının cache girişi."""
    filename: str
    path: Path
    size_bytes: int = 0
    sha256: str = ""
    mtime: float = 0.0
    loaded: bool = False
    changed: bool = False
    error: str = ""
    content: str = ""  # Dosyanın UTF-8 metin içeriği (hash hesaplanırken doldurulur)

    def compute_hash(self) -> str:
        """Dosyanın SHA-256 hash'ini hesapla ve içeriği önbellekle."""
        try:
            if not self.path.exists():
                self.error = "Dosya bulunamadı"
                return ""
            raw = self.path.read_bytes()
            self.size_bytes = len(raw)
            self.mtime = self.path.stat().st_mtime
            self.sha256 = hashlib.sha256(raw).hexdigest()
            # Metin içeriğini de sakla — runtime sorgulamaları için (MASTER-008)
            try:
                self.content = raw.decode("utf-8")
            except UnicodeDecodeError:
                self.content = raw.decode("utf-8", errors="replace")
            self.error = ""
            return self.sha256
        except Exception as e:
            self.error = str(e)
            return ""

    def check_changed(self) -> bool:
        """Dosya değişmiş mi? (hash veya mtime farklı)."""
        if not self.path.exists():
            return True  # Dosya silinmiş = değişiklik
        try:
            current_mtime = self.path.stat().st_mtime
            current_size = self.path.stat().st_size
            if current_mtime != self.mtime or current_size != self.size_bytes:
                return True
            # Derin kontrol: hash karşılaştır
            current_hash = hashlib.sha256(self.path.read_bytes()).hexdigest()
            return current_hash != self.sha256
        except Exception:
            return True


@dataclass
class CacheStatus:
    """Constitution Cache durum raporu."""
    total_files: int = 0
    cached_files: int = 0
    changed_files: int = 0
    new_files: int = 0
    missing_files: int = 0
    total_size_kb: float = 0.0
    is_valid: bool = False
    scan_duration_ms: float = 0.0
    entries: list[FileEntry] = field(default_factory=list)
    boot_ready: bool = False

    @property
    def summary(self) -> str:
        return (
            f"Cache: {self.cached_files}/{self.total_files} dosya | "
            f"{self.total_size_kb:.0f} KB | "
            f"değişen: {self.changed_files} | "
            f"yeni: {self.new_files} | "
            f"{self.scan_duration_ms:.0f}ms"
        )


class ConstitutionCache:
    """HLK Constitution Cache Manager.

    ANA YASA/*.md dosyalarını tarar, SHA-256 hash'lerini hesaplar,
    bellekte önbellekler. Sonraki kontrollerde yalnızca değişen
    dosyaları yeniden okur.

    Performans: 23 dosya × ~634 KB = ilk tarama ~50ms, sonraki ~2ms.
    """

    def __init__(self):
        self._entries: dict[str, FileEntry] = {}
        self._status: Optional[CacheStatus] = None
        self._initialized: bool = False

    # ── Tarama ───────────────────────────────────────────────────────────

    def scan(self) -> CacheStatus:
        """Tüm ANA YASA .md dosyalarını tara, hash'le, önbellekle.

        İlk çalıştırmada tüm dosyaları okur.
        Sonraki çalıştırmalarda sadece değişenleri yeniden okur.

        Returns:
            CacheStatus — tarama sonucu
        """
        t0 = time.time()
        status = CacheStatus()
        status.boot_ready = True

        if not ANA_YASA_DIR.exists():
            logger.error(f"❌ [Cache] ANA YASA dizini bulunamadı: {ANA_YASA_DIR}")
            status.is_valid = False
            self._status = status
            return status

        md_files = sorted(ANA_YASA_DIR.glob("*.md"))
        status.total_files = len(md_files)

        for md_path in md_files:
            filename = md_path.name
            entry = self._entries.get(filename)

            if entry is None:
                # Yeni dosya — ilk kez taranıyor
                entry = FileEntry(filename=filename, path=md_path)
                entry.compute_hash()
                entry.loaded = True
                entry.changed = False
                self._entries[filename] = entry
                status.new_files += 1
                logger.debug(f"  🆕 [Cache] Yeni: {filename} ({entry.size_bytes} bytes)")
            elif entry.check_changed():
                # Değişmiş — yeniden tara
                old_hash = entry.sha256[:8]
                entry.compute_hash()
                entry.loaded = True
                entry.changed = True
                status.changed_files += 1
                logger.info(f"  🔄 [Cache] Değişti: {filename} "
                           f"({old_hash}... → {entry.sha256[:8]}...)")
            else:
                # Değişmemiş — cache'ten kullan
                entry.loaded = True
                entry.changed = False
                status.cached_files += 1

            if entry.error:
                status.missing_files += 1

        status.cached_files = status.total_files - status.new_files - status.changed_files
        status.total_size_kb = sum(e.size_bytes for e in self._entries.values()) / 1024
        status.scan_duration_ms = (time.time() - t0) * 1000
        status.entries = list(self._entries.values())
        status.is_valid = status.missing_files == 0 and status.total_files > 0
        self._status = status
        self._initialized = True

        logger.info(
            f"📚 [Cache] Tarama tamam: {status.summary}"
        )

        # Auto-build Constitution Index (Generic Engine)
        try:
            from services.constitution_index import constitution_index
            idx_stats = constitution_index.build()
            logger.info(f"📚 [Index] Auto-build: {idx_stats.total_rules} kural indekslendi")
        except Exception as e:
            logger.warning(f"⚠️ [Index] Auto-build başarısız: {e}")

        return status

    # ── Durum Sorgulama ───────────────────────────────────────────────────

    def is_valid(self) -> bool:
        """Cache geçerli mi? (herhangi bir dosya değişmiş mi?)"""
        if not self._initialized:
            return False
        for entry in self._entries.values():
            if entry.check_changed():
                return False
        return True

    def refresh(self) -> CacheStatus:
        """Sadece değişen dosyaları yeniden oku. Değişmeyenleri cache'ten al."""
        if not self._initialized:
            return self.scan()
        return self.scan()  # scan() zaten sadece değişenleri okur

    def get_status(self) -> Optional[CacheStatus]:
        """Son tarama durumunu döndür."""
        return self._status

    # ── Katman Erişimi ────────────────────────────────────────────────────

    def get_layer(self, filename: str) -> Optional[FileEntry]:
        """Dosya adına göre cache girişini döndür."""
        return self._entries.get(filename)

    def get_boot_manifest(self) -> list[dict]:
        """Constitutional Boot için 18 katmanlı manifest.

        Her katman için: dosya adı, katman adı, durum (cached/changed/new/missing)
        """
        manifest = []
        for filename, layer_name in BOOT_LAYERS:
            entry = self._entries.get(filename)
            if entry is None:
                manifest.append({
                    "layer": layer_name,
                    "filename": filename,
                    "status": "missing",
                    "size_kb": 0,
                    "hash": "",
                    "loaded": False,
                })
            else:
                status = "cached" if not entry.changed else "changed"
                if entry.error:
                    status = "error"
                manifest.append({
                    "layer": layer_name,
                    "filename": filename,
                    "status": status,
                    "size_kb": entry.size_bytes / 1024,
                    "hash": entry.sha256[:12] + "..." if entry.sha256 else "",
                    "loaded": entry.loaded,
                })
        return manifest

    def get_all_entries(self) -> list[FileEntry]:
        """Tüm cache girişlerini döndür."""
        return list(self._entries.values())

    def get_file_count(self) -> int:
        """Toplam dosya sayısı."""
        return len(self._entries)

    # ── Flow Diagram Erişimi ───────────────────────────────────────────────

    def get_flow_section(self, scene_ref: str) -> dict | None:
        """08_HLK_FLOW_DIAGRAM.md'den belirtilen sahnenin operasyonel
        talimatlarını yapılandırılmış olarak döndürür.

        Flow Diagram tek anayasal kaynaktır (FD-008_1). Bu metod içeriği
        kopyalamaz; yalnızca runtime'ın erişebileceği bir görünüm sunar.

        Args:
            scene_ref: "SAHNE-02", "SAHNE-03" gibi sahne referansı.

        Returns:
            Yapılandırılmış sahne davranışları dict, veya None.
        """
        entry = self._entries.get("08_HLK_FLOW_DIAGRAM.md")
        if not entry or not entry.content:
            logger.warning(f"⚠️ [FlowCache] Flow Diagram içeriği cache'te yok")
            return None

        content = entry.content
        marker = f"🟦 {scene_ref}"

        # Sahne bölümünü bul
        idx = content.find(marker)
        if idx == -1:
            logger.warning(f"⚠️ [FlowCache] {scene_ref} Flow Diagram'da bulunamadı")
            return None

        # Bölüm başlangıcından itibaren içeriği al
        section_start = idx + len(marker)
        rest = content[section_start:]

        # Sonraki SAHNE veya FD-008_2 sınırına kadar al
        end_markers = []
        # Sonraki SAHNE-'leri tara
        for i in range(1, 20):
            next_scene = f"🟦 SAHNE-{i:02d}"
            pos = rest.find(next_scene)
            if pos > 0:
                end_markers.append(pos)
        # FD-008_2 sınırı
        fd_pos = rest.find("## FD-008_2")
        if fd_pos > 0:
            end_markers.append(fd_pos)
        # EKRAN SİLİNİR sonrası yeni bölüm
        es_pos = rest.find("\n-EKRAN SİLİNİR.\n🟦")
        if es_pos > 0:
            end_markers.append(es_pos)

        if end_markers:
            section_end = min(end_markers)
            section_text = rest[:section_end].strip()
        else:
            section_text = rest.strip()

        return self._parse_flow_section(scene_ref, section_text)

    def _parse_flow_section(self, scene_id: str, section_text: str) -> dict:
        """Flow Diagram sahne bölümünü yapılandırılmış dict'e dönüştürür.

        Hiçbir operasyonel davranışı kod içerisine kopyalamaz.
        Flow Diagram tek kaynaktır — bu metod yalnızca ayrıştırma yapar.
        """
        lines = section_text.split("\n")
        result: dict = {
            "scene_id": scene_id,
            "presentation_mode": "plain_text",
            "purpose": "",
            "speech_directive": "",
            "tone": "",
            "cleanup_rules": [],
            "selection_type": "single",
            "branch_options": [],
            "special_behaviors": [],
            "material_categories": [],
            "raw_section": section_text,
        }

        speech_parts: list[str] = []
        in_speech = False
        seen_states: set[str] = set()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # ── Sunum yöntemi ──
            if "daktilo formunda yazı baloncuğu" in stripped:
                result["presentation_mode"] = "typewriter_bubble"
            elif "Native Video" in stripped or "hlk_sahne" in stripped.lower():
                if result["presentation_mode"] == "plain_text":
                    result["presentation_mode"] = "native_video"

            # ── İletişim tonu ──
            if "uygun bir dille" in stripped and not result["tone"]:
                result["tone"] = "uygun_bir_dille"
            elif "nazik bir dille" in stripped:
                result["tone"] = "nazik_bir_dille"

            # ── Amaç tespiti ──
            for purpose_keyword in ["İSTER", "SEÇMESİNİ", "BELİRLEMESİNİ",
                                     "BELİRLENMESİN", "SEÇİMİ"]:
                if purpose_keyword in stripped and not result["purpose"]:
                    # Amaç cümlesini çıkar (tırnak içindeki veya tire sonrası)
                    result["purpose"] = stripped.lstrip("-").strip()
                    break

            # ── Konuşma yönergesi ──
            if stripped.startswith('-"') or stripped.startswith('-"'):
                in_speech = True
                speech_parts.append(stripped.lstrip('-').strip('"').rstrip('"'))
            elif in_speech and ('"gibi' in stripped or '"benzer' in stripped
                                 or 'tarzında' in stripped or 'gibi' in stripped):
                clean = stripped.rstrip('"').rstrip('gibi').strip('"').strip()
                if clean:
                    speech_parts.append(clean)
                result["speech_directive"] = " ".join(speech_parts)
                in_speech = False
                speech_parts = []
            elif in_speech:
                clean = stripped.strip('"')
                if clean:
                    speech_parts.append(clean)

            # ── Seçim tipi ──
            if "Tek Seçim Yapılabilir" in stripped:
                result["selection_type"] = "single"
            elif "Birden Fazla Seçim" in stripped or "Birden Fazla Seçim Yapılabilir" in stripped:
                result["selection_type"] = "multi"

            # ── VAR/YOK ikili seçim ──
            if stripped in ("Ⅰ. VAR", "Ⅱ. YOK", "VAR", "YOK"):
                result["selection_type"] = "binary"

            # ── State hedefleri ──
            if stripped.startswith("STATE_"):
                state_name = stripped.split()[0] if " " in stripped else stripped
                state_name = state_name.rstrip(",")
                if state_name not in seen_states:
                    seen_states.add(state_name)
                    # Bu state'i branch_options'a ekle
                    result["branch_options"].append({
                        "target_state": state_name,
                    })

            # ── Sonraki sahne yönlendirmesi ──
            if "SAHNE-" in stripped and ("►" in stripped or "─" in stripped):
                for word in stripped.split():
                    if "SAHNE-" in word:
                        # Ok ve çizgi karakterlerini temizle, SAHNE- referansını al
                        scene_target = word
                        for ch in "►└─│":
                            scene_target = scene_target.lstrip(ch)
                        scene_target = scene_target.strip()
                        if scene_target.startswith("SAHNE-"):
                            result["branch_options"].append({
                                "target_scene": scene_target,
                            })

            # ── Temizlik kuralları ──
            if "EKRAN SİLİNİR" in stripped.upper():
                if "HER EK METERYAL" in stripped.upper():
                    result["cleanup_rules"].append("on_each_material")
                    result["special_behaviors"].append("her_ek_materyal_alininca_ekran_silinir")
                else:
                    result["cleanup_rules"].append("on_exit")

            # ── Özel davranışlar ──
            if "Bitti" in stripped and "butonu" in stripped:
                result["special_behaviors"].append("bitti_butonu")
            if "kaç meteryal" in stripped.lower() or "kaç materyal" in stripped.lower():
                result["special_behaviors"].append("materyal_sayisi_ve_suresi_bilgisi")
            if "ilk meteryal" in stripped.lower() or "ilk materyal" in stripped.lower():
                result["special_behaviors"].append("ilk_materyal_bilgilendirmesi")

            # ── Materyal kategorileri ──
            for emoji_cat in ["📷", "🎥", "📚", "📄", "📦"]:
                if stripped.startswith(emoji_cat):
                    cat = stripped.strip()
                    if cat not in result["material_categories"]:
                        result["material_categories"].append(cat)

            # ── SAHNE amacını düzelt (daha spesifik) ──
            if "EK MATERYAL" in stripped.upper() and "İSTER" in stripped.upper():
                result["purpose"] = "EK_MATERYAL_ISTER"
            elif "VİDEO FORMATINI" in stripped.upper():
                result["purpose"] = "VIDEO_FORMAT_SECIMI"
            elif "ÇÖZÜNÜRLÜK" in stripped.upper():
                result["purpose"] = "COZUNURLUK_SECIMI"
            elif "VİDEO" in stripped.upper() and ("SÜRESİNİ" in stripped.upper() or "SÜRESİ" in stripped.upper()):
                result["purpose"] = "VIDEO_SURESI_SECIMI"
            elif "TANITIM TARZI" in stripped.upper():
                result["purpose"] = "TANITIM_TARZI_SECIMI"
            elif "HEDEF KİTLESİ" in stripped.upper():
                result["purpose"] = "HEDEF_KITLE_SECIMI"
            elif "SESLİ/SESSİZ" in stripped.upper() or ("SES" in stripped.upper() and "SEÇİMİNİZ" in stripped.upper()):
                result["purpose"] = "SES_SECIMI"
            elif "SESLENDİRME DİLİ" in stripped.upper():
                result["purpose"] = "SESLENDIRME_DILI_SECIMI"
            elif "SES KARAKTER" in stripped.upper():
                result["purpose"] = "SES_KARAKTER_SECIMI"
            elif "VURGULANACAKLAR" in stripped.upper():
                result["purpose"] = "VURGULANACAKLAR_SECIMI"
            elif "PLATFORM" in stripped.upper() and ("SEÇ" in stripped.upper() or "İSTE" in stripped.upper()):
                result["purpose"] = "PLATFORM_SECIMI"

        # Temizlik kuralları yoksa ve "EKRAN SİLİNİR" raw'da geçiyorsa
        if not result["cleanup_rules"] and "-EKRAN SİLİNİR." in section_text:
            result["cleanup_rules"].append("on_exit")

        # Konuşma yönergesi yakalanamadıysa ham metinden çıkar
        if not result["speech_directive"]:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('-"') and '"gibi' in stripped:
                    result["speech_directive"] = stripped.lstrip('-').strip('"').split('"gibi')[0].strip('"').strip()
                    break

        return result

    # ── Yardımcı ──────────────────────────────────────────────────────────

    def invalidate(self):
        """Tüm cache'i temizle (yeniden başlatma için)."""
        count = len(self._entries)
        self._entries.clear()
        self._status = None
        self._initialized = False
        logger.info(f"🗑️ [Cache] Temizlendi: {count} dosya")

    def get_telegram_html(self) -> str:
        """Constitution Cache durumunu Telegram HTML formatında döndür."""
        if not self._status:
            return "⚠️ <b>Constitution Cache henüz taranmadı.</b>"

        s = self._status
        lines = [
            "📚 <b>CONSTITUTION CACHE DURUMU</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📁 Toplam Dosya: <b>{s.total_files}</b>",
            f"💾 Cache'lenen: <b>{s.cached_files}</b>",
            f"🔄 Değişen: <b>{s.changed_files}</b>",
            f"🆕 Yeni: <b>{s.new_files}</b>",
            f"❌ Eksik: <b>{s.missing_files}</b>",
            f"📦 Toplam Boyut: <b>{s.total_size_kb:.0f} KB</b>",
            f"⏱️ Tarama Süresi: <b>{s.scan_duration_ms:.0f}ms</b>",
            f"✅ Geçerli: <b>{'EVET' if s.is_valid else 'HAYIR'}</b>",
            f"🚀 Boot Ready: <b>{'EVET' if s.boot_ready else 'HAYIR'}</b>",
        ]

        # Değişen dosyaları göster
        changed = [e for e in s.entries if e.changed]
        if changed:
            lines.append("")
            lines.append("<b>🔄 Değişen Dosyalar:</b>")
            for e in changed:
                lines.append(f"  • <code>{e.filename}</code> ({e.size_bytes} bytes)")

        return "\n".join(lines)


# Global singleton
constitution_cache = ConstitutionCache()
