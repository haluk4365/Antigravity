"""
Singleton adapter'ları — mevcut servislerden web dashboard için veri çeker.
KURAL: Sadece Runtime'dan doğrulanmış veri. Placeholder / varsayılan YOK.

LAC Constitution Compliance Monitor — 13 bölümlü WF yapısı.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Optional

import requests as _requests

# Constitution Scanner — ANA YASA tarayıcı
from .constitution_scanner import get_scanner as _get_scanner

logger = logging.getLogger(__name__)

_PKG_DIR = os.getenv("GC_PACKAGE_STORAGE_DIR") or os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "production_packages"
)


def _read_package(pid: str) -> Optional[dict]:
    """Production package'i diskten okur (sync, web dashboard uyumlu)."""
    for sub in ("", "archive"):
        path = os.path.join(_PKG_DIR, sub, f"{pid}.json") if sub else os.path.join(_PKG_DIR, f"{pid}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg and hasattr(pkg, "to_dict"):
            return pkg.to_dict()
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard KPI
# ═══════════════════════════════════════════════════════════════════════════════

async def get_dashboard_data() -> dict:
    try:
        from services.pid_runtime import pid_runtime
        ps = await pid_runtime.get_stats()
        pid_total = ps.get("total_pids", 0)
        pid_active = ps.get("active_pids", 0)
    except Exception:
        pid_total, pid_active = 0, 0

    try:
        from services.hlk_runtime import hlk_runtime as hr
        sessions = len(hr._sessions) if hasattr(hr, "_sessions") else 0
    except Exception:
        sessions = 0

    try:
        from services.provider_priority import provider_priority
        ok = sum(len(provider_priority.get_available(c)) for c in ("image", "voice", "video"))
        total = sum(len(provider_priority.get_providers(c)) for c in ("image", "voice", "video"))
    except Exception:
        ok, total = 0, 0

    return {
        "kpi": [
            {"label": "Aktif Oturum", "value": str(sessions)},
            {"label": "Toplam PID", "value": str(pid_total)},
            {"label": "Aktif PID", "value": str(pid_active)},
            {"label": "Servis", "value": f"{ok}/{total}" if total else "0/0"},
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PID Listesi
# ═══════════════════════════════════════════════════════════════════════════════

def get_active_sessions() -> list[dict]:
    """pid_runtime registry'sindeki tüm PID'ler."""
    sessions = []
    try:
        from services.pid_runtime import pid_runtime
        for rec in pid_runtime._pid_registry.values():
            pid = rec.pid
            is_active = getattr(rec, "is_active", False)
            created_at = getattr(rec, "created_at", "")

            # Package'tan durum oku
            pkg = _read_package(pid)
            status = _derive_status(pkg) if pkg else ("Veri Bekleniyor" if is_active else "TAMAMLANDI")
            status_class = _status_class(status)

            sessions.append({
                "pid": pid,
                "is_active": is_active,
                "created_at": created_at,
                "durum": status,
                "durumSinif": status_class,
            })
    except Exception as e:
        logger.warning(f"PID listesi alınamadı: {e}")

    sessions.sort(key=lambda s: (not s["is_active"], s.get("created_at", "")), reverse=True)
    return sessions


def _derive_status(pkg: dict) -> str:
    """Package metadata + task'lardan gerçek durumu çıkar."""
    meta = pkg.get("metadata", {}) or {}
    pkg_status = meta.get("status", "")
    tasks = pkg.get("task_packages", []) or []

    if pkg_status == "COMPLETED":
        return "Tamamlandı"
    if pkg_status == "FAILED":
        return "Hata"
    if pkg_status == "CREATED" and not any(t.get("status") not in ("PENDING", "") for t in tasks):
        return "Hazırlanıyor"

    # Aktif task'ı bul
    for t in tasks:
        ts = t.get("status", "")
        if ts in ("PRODUCING", "PROCESSING"):
            agent = t.get("agent", "")
            if agent == "ImageGenerator": return "Görsel Üretiliyor"
            if agent == "VoiceGenerator": return "Ses Üretiliyor"
            if agent == "VideoRenderer": return "Video Üretiliyor"
            return "Üretiliyor"
        if ts == "PENDING" and any(tt.get("status") in ("COMPLETED", "SUCCESS") for tt in tasks):
            # Bu task henüz başlamamış ama öncekiler tamam
            agent = t.get("agent", "")
            if agent == "VoiceGenerator": return "Ses Bekleniyor"
            if agent == "VideoRenderer": return "Video Bekleniyor"
            if agent == "DeliveryAgent": return "Teslim Bekleniyor"

    # Hepsi COMPLETED?
    if all(t.get("status") in ("COMPLETED", "SUCCESS") for t in tasks):
        return "Tamamlandı"
    if any(t.get("status") == "FAILED" for t in tasks):
        return "Hata"
    return pkg_status or "Veri Bekleniyor"


def _status_class(status: str) -> str:
    if status in ("Tamamlandı",):
        return "completed"
    if status in ("Hata",):
        return "error"
    if status in ("Hazırlanıyor", "Veri Bekleniyor"):
        return "waiting"
    return "running"


# ═══════════════════════════════════════════════════════════════════════════════
# PID Detay
# ═══════════════════════════════════════════════════════════════════════════════

def get_pid_detail(pid: str) -> Optional[dict]:
    """PID detay — yalnızca Runtime kaynaklı doğrulanmış veri."""
    pkg = _read_package(pid)
    brief = (pkg.get("brief", {}) or {}) if pkg else {}
    tasks = (pkg.get("task_packages", []) or []) if pkg else []
    meta = (pkg.get("metadata", {}) or {}) if pkg else {}

    # PID kaydı
    is_active = False
    created_at = ""
    try:
        from services.pid_runtime import pid_runtime
        rec = pid_runtime._pid_registry.get(pid)
        if rec:
            is_active = getattr(rec, "is_active", False)
            created_at = getattr(rec, "created_at", "")
    except Exception:
        pass

    # Ürün / Marka / Platform — package brief'ten
    product_name = brief.get("product_name", "") or ""
    brand = brief.get("brand", "") or ""
    platform = brief.get("platform", "") or ""
    url = brief.get("url", "") or ""

    # URL'den platform çıkar (brief'te yoksa)
    if not platform and url:
        platform = _extract_platform(url)

    # Durum
    status = _derive_status(pkg) if pkg else ("Veri Bekleniyor" if is_active else "TAMAMLANDI")

    # Mevcut aşama
    stage = _derive_stage(tasks, status)

    # Provider listesi — sadece Decision Engine seçim yaptıysa
    providers = _get_pid_providers(pkg) if pkg else []

    # Event'ler
    events = get_events(pid=pid, limit=50)

    # Buton aktifliği — Runtime bağlantısı var mı?
    runtime_connected = _is_runtime_connected()

    return {
        "pid": pid,
        "urun": product_name or "Bilinmiyor",
        "marka": brand or "Bilinmiyor",
        "platform": platform or "Bilinmiyor",
        "durum": status,
        "asama": stage,
        "is_active": is_active,
        "created_at": created_at,
        "url": url,
        "providers": providers,
        "events": events,
        "runtime_connected": runtime_connected,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Workflow Tree (Explainable Workflow Explorer)
# ═══════════════════════════════════════════════════════════════════════════════

_WF_MANIFEST_CACHE: dict = {}
"""Workflow Manifest cache — modül yüklemesinde parse edilir."""


def _parse_workflow_manifest() -> dict:
    """ANA YASA/09_WORKFLOW_MANIFEST.md dosyasından WF listesini parse eder.
    Returns: {wf_id: {name, description, status}}"""
    if _WF_MANIFEST_CACHE:
        return _WF_MANIFEST_CACHE

    import re as _re
    try:
        manifest_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ANA YASA", "09_WORKFLOW_MANIFEST.md"
        )
        if not os.path.exists(manifest_path):
            logger.warning(f"Workflow Manifest bulunamadı: {manifest_path}")
            return {}

        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # WF-001 ... WF-010'u parse et
        pattern = r'## (WF-\d+)\s+### Workflow\s+([^\n]+)\s+### A[çc]ıklama\s+([^#]+)'
        for match in _re.finditer(pattern, content, _re.DOTALL):
            wf_id = match.group(1).strip()
            name = match.group(2).strip()
            description = match.group(3).strip()
            # Sadece WF-001 ... WF-010 (business workflow'lar)
            wf_num = int(wf_id.split("-")[1]) if "-" in wf_id else 0
            if 1 <= wf_num <= 10:
                _WF_MANIFEST_CACHE[wf_id] = {
                    "name": name,
                    "description": description,
                }

        logger.debug(f"Workflow Manifest parse edildi: {len(_WF_MANIFEST_CACHE)} workflow")
    except Exception as e:
        logger.error(f"Workflow Manifest parse hatası: {e}")

    return _WF_MANIFEST_CACHE


def _make_node(node_type: str, title: str, status: str = "pending",
               summary: str = "", source: str = "", detail: dict = None,
               reference: str = "") -> dict:
    """Standart düğüm oluşturucu."""
    return {
        "type": node_type,
        "baslik": title,
        "durum": status,
        "aciklama": summary,
        "kaynak": source,
        "referans": reference or "",
        "alt_dugumler": [],
        "detail": detail or {},
    }


def _find_events(events: list, *keywords: str) -> list:
    """Keyword bazlı event filtreleme."""
    if not events:
        return []
    result = []
    for e in events:
        text = (e.get("event", "") + " " + e.get("aciklama", "")).upper()
        if any(kw.upper() in text for kw in keywords):
            result.append(e)
    return result[:30]


def get_workflow_tree(pid: str) -> Optional[dict]:
    """Explainable Workflow Explorer için tam workflow ağacı verisi.

    Tüm veriler mevcut anayasal kayıtlardan okunur. LAC karar vermez, üretmez.
    """
    pkg = _read_package(pid)
    if not pkg:
        return None

    manifest = _parse_workflow_manifest()
    if not manifest:
        return None

    brief = pkg.get("brief", {}) or {}
    meta = pkg.get("metadata", {}) or {}
    tasks = pkg.get("task_packages", []) or []
    decisions = pkg.get("decision_history", []) or []
    research = pkg.get("research_results", {}) or {}
    refs = pkg.get("reference_images", []) or []
    final_video = pkg.get("final_video", {}) or {}
    delivery = pkg.get("delivery_info", {}) or {}
    quality = pkg.get("quality_reports", {}) or {}
    agent_logs = pkg.get("agent_logs", []) or []

    events = get_events(pid=pid, limit=200) or []

    # Summary
    product_name = brief.get("product_name", "") or ""
    brand = brief.get("brand", "") or ""
    platform = brief.get("platform", "")
    if not platform:
        platform = _extract_platform(brief.get("url", ""))

    created = meta.get("created_at", "")
    completed = meta.get("completed_at", "")
    pkg_status = meta.get("status", "")

    # Genel durum
    if pkg_status == "COMPLETED":
        overall = "COMPLETED"
    elif any(t.get("status") == "FAILED" for t in tasks):
        overall = "FAILED"
    elif any(t.get("status") in ("PRODUCING", "PROCESSING") for t in tasks):
        overall = "IN_PROGRESS"
    elif any(t.get("status") in ("COMPLETED", "SUCCESS") for t in tasks):
        overall = "IN_PROGRESS"
    else:
        overall = "WAITING"

    # PID registry'den
    is_active = False
    try:
        from services.pid_runtime import pid_runtime
        rec = pid_runtime._pid_registry.get(pid)
        if rec:
            is_active = getattr(rec, "is_active", False)
    except Exception:
        pass

    # Workflow sıralaması (WF-001 ... WF-010)
    wf_order = sorted(manifest.keys())

    # ── Workflow Status Hesaplama ─────────────────────────────────────────
    def _wf_status(wf_id: str) -> str:
        """Workflow'un durumunu package verilerinden çıkar."""
        has_url = bool(brief.get("url"))
        has_product = bool(product_name and brand)
        has_research = bool(research or refs)
        has_scenario = bool(pkg.get("scenario"))

        # Task'lara göre durum
        task_by_agent = {}
        for t in tasks:
            agent = t.get("agent", "")
            task_by_agent[agent] = t.get("status", "")

        img_status = task_by_agent.get("ImageGenerator", "")
        voice_status = task_by_agent.get("VoiceGenerator", "")
        video_status = task_by_agent.get("VideoRenderer", "")
        delivery_status = task_by_agent.get("DeliveryAgent", "")

        all_prod_tasks = [img_status, voice_status, video_status, delivery_status]

        wf_status_map = {
            "WF-001": "completed" if has_url else "pending",
            "WF-002": "completed" if has_research else ("pending" if has_url else "inactive"),
            "WF-003": "completed" if has_product else ("pending" if has_url else "inactive"),
            "WF-004": "completed" if has_product else ("pending" if has_product else "inactive"),
            "WF-005": "completed" if has_scenario else ("pending" if has_product else "inactive"),
            "WF-006": "completed" if has_scenario else ("pending" if has_product else "inactive"),
            "WF-007": "completed" if decisions else ("pending" if has_scenario else "inactive"),
            "WF-008": (
                "completed" if all(s in ("COMPLETED", "SUCCESS") for s in all_prod_tasks if s)
                else "failed" if any(s == "FAILED" for s in all_prod_tasks)
                else "running" if any(s in ("PRODUCING", "PROCESSING") for s in all_prod_tasks)
                else "pending" if has_scenario
                else "inactive"
            ),
            "WF-009": (
                "completed" if quality.get("verdict")
                else "failed" if quality.get("verdict") == "FAIL"
                else "pending" if any(s in ("COMPLETED", "SUCCESS") for s in all_prod_tasks if s)
                else "inactive"
            ),
            "WF-010": (
                "completed" if delivery.get("delivered")
                else "failed" if delivery_status == "FAILED"
                else "running" if delivery_status in ("PRODUCING", "PROCESSING")
                else "pending" if any(s in ("COMPLETED", "SUCCESS") for s in all_prod_tasks if s)
                else "inactive"
            ),
        }
        return wf_status_map.get(wf_id, "inactive")

    # ── Workflow Node'larını Oluştur ──────────────────────────────────────
    workflows = []

    # Tüm event verisini workflow keyword'lerine göre önceden indeksle
    def _event_matches(event, keywords):
        text = (event.get("event", "") + " " + event.get("aciklama", "")
                + " " + event.get("event_name", "") + " " + event.get("event_type", "")).upper()
        return any(kw.upper() in text for kw in keywords)

    WF_EVENT_KEYWORDS = {
        "WF-001": ("LINK", "URL", "WEBSITE", "VALIDAT"),
        "WF-002": ("RESEARCH", "IMAGE", "GORSEL", "BACKGROUND", "REFERENCE"),
        "WF-003": ("BRIEF", "PRODUCT", "COLLECT"),
        "WF-004": ("BRIEF", "APPROVAL", "ONAY"),
        "WF-005": ("SCENARIO", "GENERAT"),
        "WF-006": ("SCENARIO", "APPROVAL", "ONAY"),
        "WF-007": ("PRICING", "FIYAT", "TEKLIF", "COST"),
        "WF-008": ("VIDEO", "PRODUCT", "TASK", "PROVIDER", "RENDER", "EXECUT",
                   "IMAGE", "VOICE", "REPRODUCTION", "CEE"),
        "WF-009": ("QUALITY", "CEE", "CHECK", "ENFORCE"),
        "WF-010": ("DELIVER", "SEND", "TELEGRAM", "TESLIM"),
    }

    for wf_id in wf_order:
        wf_info = manifest.get(wf_id, {})
        wf_name = wf_info.get("name", wf_id)
        wf_desc = wf_info.get("description", "")
        status = _wf_status(wf_id)

        # Workflow'a ait tüm verileri topla
        wf_tasks = _find_tasks_for_wf(wf_id, tasks)
        wf_decisions = _find_decisions_for_wf(wf_id, decisions, events)

        # Event'leri filtrele
        keywords = WF_EVENT_KEYWORDS.get(wf_id, (wf_id, wf_name.upper()))
        wf_events = [e for e in events if _event_matches(e, keywords)]

        api_refs = _get_api_refs_for_wf(wf_id)

        # WF-008 içinse tüm task'ları da göster
        if wf_id == "WF-008":
            wf_tasks = tasks  # Tüm task'lar
            # WF-008 için tüm event'leri göster
            wf_events = events

        nodes = []

        # ── LAC Anayasal Uygunluk ve Denetim Merkezi: 14 bölümlü yapı ──
        scanner = _get_scanner()
        ctx = scanner.get_constitution_context(wf_id)
        wf_summary = scanner.get_wf_summary(wf_id, pkg)
        trust = scanner.calculate_trust_score(wf_id, pkg)

        # 0. YÖNETİCİ ÖZETİ — Tek bakışta okunabilir özet
        status_emoji = {"completed": "🟢", "running": "🔵", "failed": "🔴", "pending": "🟡"}
        compliance_emoji = {"COMPLIANT": "🟢", "PARTIAL": "🟡", "VIOLATION": "🔴", "UNKNOWN": "⚫"}
        summary_lines = [
            f"Durum: {status_emoji.get(wf_summary['status'], '⚪')} {wf_summary['status']}",
            f"Anayasal Uyum: {compliance_emoji.get(wf_summary['compliance_verdict'], '⚫')} %{trust['total']}",
            f"Üretilen Çıktı: {wf_summary['output_count']} | Beslenen İş Akışı: {wf_summary['feeds_to_count']}",
            f"İhlal: {wf_summary['violation_count']} | Güven: {trust['total']}/100 ({trust['label']})",
        ]
        nodes.append(_make_node("executive_summary", "0. Yönetici Özeti",
                                status=wf_summary['status'],
                                summary=" | ".join(summary_lines),
                                source="Anayasa Tarayıcısı (Constitution Scanner)",
                                detail={"summary": wf_summary, "trust_score": trust}))

        # 1. AMAÇ — Anayasa maddelerinden türetilir
        nodes.append(_make_node("purpose", "1. Amaç",
                                status="completed" if ctx.get("purpose") else "pending",
                                summary=ctx.get("purpose", f"{wf_id} — Anayasa'da tanımlı değil")[:400],
                                source="ANA YASA",
                                reference=wf_id))

        # 2. ANAYASAL DAYANAK — İnteraktif Anayasa Gezgini
        article_statuses = []
        for cat, label in [("arch_rules", "AR"), ("oper_rules", "OR"),
                            ("quality_rules", "QR"), ("general_rules", "GK")]:
            for art in ctx.get(cat, [])[:8]:
                art_status = scanner.get_article_status(art["id"], wf_id, pkg)
                article_statuses.append({
                    "id": art["id"], "title": art["title"], "type": label,
                    "status": art_status["status"], "label": art_status["label"],
                    "decision_ids": art_status["evidence"]["decision_ids"],
                    "task_ids": art_status["evidence"]["task_ids"],
                    "event_ids": art_status["evidence"]["event_ids"],
                })
        # MASTER kuralları
        for art in ctx.get("master_rules", [])[:3]:
            art_status = scanner.get_article_status(art["id"], wf_id, pkg)
            article_statuses.append({
                "id": art["id"], "title": art["title"], "type": "MASTER",
                "status": art_status["status"], "label": art_status["label"],
                "decision_ids": art_status["evidence"]["decision_ids"],
                "task_ids": art_status["evidence"]["task_ids"],
                "event_ids": art_status["evidence"]["event_ids"],
            })

        status_icons = {"applied": "🟢", "partial": "🟡", "not_applied": "🔴", "not_evaluated": "⚫"}
        basis_summary = " | ".join(
            f"{status_icons.get(a['status'],'⚫')} {a['id']}: {a['title'][:60]}"
            for a in article_statuses[:10]
        )
        basis_node = _make_node("constitutional_basis", "2. Anayasal Dayanak",
                                status="completed" if article_statuses else "pending",
                                summary=basis_summary[:500] if basis_summary
                                else "Anayasa'da tanımlı değil",
                                source="ANA YASA + Constitution Scanner",
                                detail={"articles": article_statuses,
                                        "gc_params": ctx.get("gc_params", [])})
        nodes.append(basis_node)

        # 3. HLK KARARI
        if wf_decisions:
            latest_d = wf_decisions[-1]
            decision_id = latest_d.get("decision_id", "RTD-?")
            verdict = latest_d.get("verdict", str(latest_d.get("result", "")))
            justification = latest_d.get("justification", "")
            if isinstance(justification, dict):
                justification = justification.get("summary", str(justification))
            hlk_node = _make_node("hlk_decision", "3. HLK Kararı",
                                  status="completed",
                                  summary=f"{decision_id}: {verdict}"[:200],
                                  source="Karar Geçmişi (Decision History)",
                                  detail={"decision_id": decision_id, "verdict": verdict,
                                          "full_decision": latest_d},
                                  reference=decision_id)
            if justification:
                hlk_node["alt_dugumler"].append(
                    _make_node("rationale", "Karar Gerekçesi",
                               status="completed",
                               summary=str(justification)[:300],
                               source="decision.justification",
                               reference=decision_id))
            for i, d in enumerate(wf_decisions[:-1]):
                did = d.get("decision_id", f"RTD-{i}")
                hlk_node["alt_dugumler"].append(
                    _make_node("decision", f"Karar #{i+1}",
                               status="completed",
                               summary=f"{did}: {d.get('verdict','')}"[:200],
                               source="Karar Geçmişi (Decision History)", detail=d))
        else:
            hlk_node = _make_node("hlk_decision", "3. HLK Kararı",
                                  status="pending" if status in ("pending", "running") else "inactive",
                                  summary="Henüz karar üretilmedi" if status != "inactive"
                                  else "Bu aşamada karar üretilmez",
                                  source="Karar Geçmişi (Decision History)")
        nodes.append(hlk_node)

        # 4. YAPILAN İŞLEMLER
        ops = []
        if wf_id == "WF-001":
            if brief.get("url"): ops.append(("done", "Ürün linki alındı"))
            if decisions: ops.append(("done", "Link doğrulandı"))
            else: ops.append(("pending", "Link doğrulama bekleniyor"))
        elif wf_id == "WF-002":
            if research: ops.append(("done", "Ürün araştırması tamamlandı"))
            if refs: ops.append(("done", f"{len(refs) if isinstance(refs, list) else 0} referans görsel toplandı"))
            if brief.get("brand"): ops.append(("done", "Marka tespit edildi"))
            else: ops.append(("pending", "Marka analizi bekleniyor"))
        elif wf_id == "WF-003":
            if brief.get("platform"): ops.append(("done", "Platform seçildi"))
            if brief.get("resolution"): ops.append(("done", "Çözünürlük belirlendi"))
            if brief.get("style"): ops.append(("done", "Tanıtım tarzı seçildi"))
            else: ops.append(("pending", "Brief toplama devam ediyor"))
        elif wf_id == "WF-004":
            ops.append(("done", "Brief onaylandı") if status == "completed" else ("pending", "Brief onayı bekleniyor"))
        elif wf_id == "WF-005":
            if pkg.get("scenario"): ops.append(("done", "Senaryo oluşturuldu"))
            else: ops.append(("pending", "Senaryo üretimi bekleniyor"))
        elif wf_id == "WF-006":
            ops.append(("done", "Senaryo onaylandı") if status == "completed" else ("pending", "Senaryo onayı bekleniyor"))
        elif wf_id == "WF-007":
            if decisions: ops.append(("done", "Fiyatlandırma yapıldı"))
            if delivery.get("delivered") is not None: ops.append(("done", "Ödeme doğrulandı"))
            else: ops.append(("pending", "Ödeme bekleniyor"))
        elif wf_id == "WF-008":
            for t in tasks:
                t_status = t.get("status", "")
                mark = "done" if t_status in ("COMPLETED", "SUCCESS") else "failed" if t_status == "FAILED" else "running"
                ops.append((mark, f"{t.get('agent', 'Görev')}: {t_status}"))
        elif wf_id in ("WF-009", "WF-010"):
            if delivery.get("delivered"): ops.append(("done", "Teslim edildi"))
            else: ops.append(("pending", "Teslim bekleniyor"))
        else:
            ops.append(("pending", "Henüz işlem yapılmadı"))

        ops_summary = " | ".join(
            f"{'✅' if m == 'done' else '❌' if m == 'failed' else '⏳' if m == 'running' else '○'} {t}"
            for m, t in ops[:12]
        )
        nodes.append(_make_node("operations", "4. Yapılan İşlemler",
                                status="completed" if all(m == "done" for m, _ in ops)
                                else "running" if any(m in ("running", "pending") for m, _ in ops) else "pending",
                                summary=ops_summary or "Henüz işlem kaydı yok",
                                source="Üretim Paketi + Görevler",
                                detail={"operations": [{"status": m, "text": t} for m, t in ops]}))

        # 5. ÜRETİLEN ÇIKTILAR
        outputs = ctx.get("outputs", [])
        outputs_verified = []
        for o in outputs:
            has_evidence = False
            if "Link" in o and brief.get("url"): has_evidence = True
            if "PID" in o and pid: has_evidence = True
            if "Video" in o and (final_video or {}).get("path"): has_evidence = True
            if "Görsel" in o and (refs or research): has_evidence = True
            if "Araştırma" in o and research: has_evidence = True
            if "Marka" in o and brief.get("brand"): has_evidence = True
            outputs_verified.append({"name": o, "exists": has_evidence})
        nodes.append(_make_node("outputs", "5. Üretilen Çıktılar",
                                status="completed" if outputs_verified and all(o["exists"] for o in outputs_verified)
                                else "running" if any(o["exists"] for o in outputs_verified) else "pending",
                                summary=f"{len(outputs_verified)} çıktı — "
                                f"{sum(1 for o in outputs_verified if o['exists'])} mevcut"
                                if outputs_verified else "Anayasa'da tanımlı değil",
                                source="Anayasa Tarayıcısı (Constitution Scanner)",
                                detail={"outputs": outputs_verified}))

        # 6. BU ÇIKTILARI KULLANACAK İŞ AKIŞLARI
        feeds_to = ctx.get("feeds_to", [])
        consumers_detail = []
        for fw in feeds_to:
            fw_ctx = scanner.get_constitution_context(fw) if fw != wf_id else {}
            consumers_detail.append({
                "wf_id": fw,
                "purpose": (fw_ctx.get("purpose", "") or "")[:120],
            })
        nodes.append(_make_node("consumers", "6. Bu Çıktıları Kullanacak İş Akışları",
                                status="completed" if feeds_to else "inactive",
                                summary=" → ".join(feeds_to) if feeds_to
                                else "Son İş Akışı — başka İş Akışı beslemez",
                                source="Anayasa Tarayıcısı (Constitution Scanner)",
                                detail={"consumers": consumers_detail}))

        # 7. SONRAKİ İŞ AKIŞLARI BU ÇIKTILARI NASIL KULLANACAK?
        feed_descriptions = ctx.get("feed_descriptions", {})
        feed_items = []
        for fw, desc in feed_descriptions.items():
            feed_items.append({"wf_id": fw, "description": desc})
        nodes.append(_make_node("feed_descriptions", "7. Sonraki İş Akışları Kullanım Açıklaması",
                                status="completed" if feed_items else "inactive",
                                summary=f"{len(feed_items)} İş Akışı için kullanım açıklaması mevcut"
                                if feed_items else "Anayasa'da tanımlı değil",
                                source="Anayasa Tarayıcısı (Constitution Scanner)",
                                detail={"feeds": feed_items}))

        # 8. İŞ AKIŞI BAĞIMLILIKLARI
        input_from = ctx.get("input_from", [])
        dep_nodes = []
        if input_from:
            dep_nodes.append(_make_node("dep_input", f"← {', '.join(input_from)}",
                                       status="completed",
                                       summary="Beslendiği İş Akışları"))
        dep_nodes.append(_make_node("dep_self", f"● {wf_id}",
                                    status=status,
                                    summary=f"Çıktı: {', '.join(outputs[:5])}" if outputs else "Çıktı üretilmedi"))
        for fw in feeds_to:
            dep_nodes.append(_make_node("dep_output", f"→ {fw}",
                                       status="pending" if status not in ("completed",)
                                       else "completed",
                                       summary=feed_descriptions.get(fw, f"{fw}'e veri aktarılır")[:200]))
        dep_node = _make_node("dependencies", "8. İş Akışı Bağımlılıkları",
                              status="completed" if dep_nodes else "pending",
                              summary=f"← {', '.join(input_from)} → {', '.join(feeds_to)}"
                              if input_from or feeds_to else "Bağımlılık zinciri kurulamadı",
                              source="Anayasa Tarayıcısı (Constitution Scanner)",
                              detail={"chain": {
                                  "input_from": input_from,
                                  "outputs": outputs,
                                  "feeds_to": feeds_to,
                              }})
        dep_node["alt_dugumler"] = dep_nodes
        nodes.append(dep_node)

        # 9. ANAYASAL UYGUNLUK
        compliance = scanner.evaluate_compliance(wf_id, pkg)
        comp_status_map = {"COMPLIANT": "completed", "PARTIAL": "running",
                            "VIOLATION": "failed", "UNKNOWN": "pending"}
        comp_label_map = {"COMPLIANT": "🟢 Anayasa Uyumlu", "PARTIAL": "🟡 Kısmi Uyum",
                           "VIOLATION": "🔴 Anayasa İhlali", "UNKNOWN": "⚫ Değerlendirilmedi"}
        comp_node = _make_node("compliance", "9. Anayasal Uygunluk",
                               status=comp_status_map.get(compliance.verdict, "pending"),
                               summary=comp_label_map.get(compliance.verdict, compliance.verdict),
                               source="Anayasa Tarayıcısı (Constitution Scanner)",
                               detail={
                                   "verdict": compliance.verdict,
                                   "applied": compliance.applied_rules,
                                   "missing": compliance.missing_rules,
                                   "violated": compliance.violated_rules,
                                   "trust_score": trust,
                               })
        if compliance.missing_rules:
            comp_node["alt_dugumler"].append(
                _make_node("compliance_detail", "Eksik veya İhlal Edilen Maddeler",
                           status="failed",
                           summary=f"{len(compliance.missing_rules)} madde: {', '.join(compliance.missing_rules[:10])}",
                           source="ANA YASA"))
        if compliance.applied_rules:
            comp_node["alt_dugumler"].append(
                _make_node("compliance_detail", "Uygulanan Maddeler",
                           status="completed",
                           summary=f"{len(compliance.applied_rules)} madde kanıtlandı",
                           source="Paket Doğrulama"))
        # Güven Puanı alt kırılımı
        comp_node["alt_dugumler"].append(
            _make_node("trust_score", f"İş Akışı Güven Puanı: {trust['total']}/100",
                       status="completed" if trust["total"] >= 60 else "failed",
                       summary=f"Karar: {trust['breakdown']['karar_kaniti']} | "
                       f"Uyum: {trust['breakdown']['anayasal_uyum']} | "
                       f"Çıktı: {trust['breakdown']['cikti_butunlugu']} | "
                       f"Bağımlılık: {trust['breakdown']['bagimlilik_kontrol']} | "
                       f"Kod: {trust['breakdown']['kod_uyumu']}",
                       source="Anayasa Tarayıcısı (Constitution Scanner)",
                       detail={"trust_score": trust}))
        nodes.append(comp_node)

        # 10. KANITLAR
        evidence_all = []
        if wf_id == "WF-002" and refs:
            evidence_all.append(_make_node("evidence", "Referans Görseller",
                                           status="completed",
                                           summary=f"{len(refs) if isinstance(refs, list) else 0} görsel",
                                           detail={"images": refs if isinstance(refs, list) else []}))
        if wf_id == "WF-008" and final_video:
            evidence_all.append(_make_node("evidence", "Nihai Video",
                                           status="completed" if final_video.get("path") else "pending",
                                           summary=str(final_video.get("path", "Üretilmedi"))[:200],
                                           detail=final_video))
        if wf_id == "WF-009" and quality:
            evidence_all.append(_make_node("evidence", "Kalite Raporu",
                                           status="completed" if quality.get("verdict") else "pending",
                                           summary=f"Karar: {quality.get('verdict', 'Bekleniyor')}",
                                           detail=quality))
        if wf_id == "WF-010" and delivery:
            evidence_all.append(_make_node("evidence", "Teslim Kaydı",
                                           status="completed" if delivery.get("delivered") else "pending",
                                           summary=f"Teslim: {'Evet' if delivery.get('delivered') else 'Hayır'}",
                                           detail=delivery))
        if evidence_all:
            ev_parent = _make_node("evidence", "10. Kanıtlar",
                                   status="completed",
                                   summary=f"{len(evidence_all)} kanıt paketi",
                                   detail={})
            ev_parent["alt_dugumler"] = evidence_all
            nodes.append(ev_parent)
        else:
            nodes.append(_make_node("evidence", "10. Kanıtlar",
                                    status="pending" if status not in ("inactive",)
                                    else "inactive",
                                    summary="Henüz kanıt üretilmedi — bu İş Akışına ait çıktı dosyaları (görsel, video, ses) henüz oluşturulmadı veya Production Package'e kaydedilmedi"))

        # 11. OLAYLAR
        if wf_events:
            evt_node = _make_node("events", "11. Olaylar",
                                  status="completed",
                                  summary=f"{len(wf_events)} olay",
                                  detail={"count": len(wf_events)})
            for e in wf_events[:15]:
                evt_node["alt_dugumler"].append(
                    _make_node("event", e.get("event_name", e.get("event_type", e.get("event", "Olay"))),
                               status="completed",
                               summary=e.get("description", e.get("aciklama", ""))[:200],
                               source="Olay Kayıt Merkezi",
                               detail=e))
        else:
            evt_node = _make_node("events", "11. Olaylar",
                                  status="pending" if status not in ("inactive",)
                                  else "inactive",
                                  summary="Henüz olay kaydı yok — bu İş Akışına ait EEC (Execution Event Collector) veya Olay Kayıt Merkezi tarafından kaydedilmiş bir olay bulunmuyor")
        nodes.append(evt_node)

        # 12. KAYITLAR
        if agent_logs and wf_id in ("WF-002", "WF-005", "WF-008", "WF-009"):
            log_node = _make_node("logs", "12. Kayıtlar",
                                  status="completed",
                                  summary=f"{len(agent_logs)} kayıt satırı",
                                  detail={"log_count": len(agent_logs)})
            for le in agent_logs[:8]:
                if isinstance(le, dict):
                    log_node["alt_dugumler"].append(
                        _make_node("log", le.get("level", "INFO"),
                                   status="completed",
                                   summary=str(le.get("message", ""))[:200],
                                   detail=le))
        else:
            log_node = _make_node("logs", "12. Kayıtlar",
                                  status="pending",
                                  summary="Kayıt bulunamadı — bu İş Akışına ait agent log kayıtları (çalışma günlüğü) henüz oluşturulmadı" if wf_id in ("WF-008",)
                                  else "Bu aşamada kayıt üretilmez")
        nodes.append(log_node)

        # 13. API
        api_refs = _get_api_refs_for_wf(wf_id)
        if api_refs:
            api_node = _make_node("api", "13. API",
                                  status="completed",
                                  summary=f"{len(api_refs)} endpoint",
                                  detail={"endpoints": api_refs})
            for ar_item in api_refs:
                api_node["alt_dugumler"].append(
                    _make_node("api_ref", ar_item.get("name", "API"),
                               status="completed",
                               summary=ar_item.get("url", "") or ar_item.get("module", ""),
                               source=ar_item.get("module", ""),
                               detail=ar_item))
        else:
            api_node = _make_node("api", "13. API",
                                  status="pending",
                                  summary="Bu aşamada API referansı yok")
        nodes.append(api_node)
        # 14. SONUC (Workflow Result)
        recs = scanner.generate_recommendations(wf_id, pkg)
        is_success = recs["is_success"]
        result_emoji = "\U0001f7e2" if is_success else "\U0001f534"
        result_label = "Basarili (Success)" if is_success else "Basarisiz (Failed)"
        result_reasons = recs["success_reasons"] if is_success else recs["failure_reasons"]
        result_verdict_icon = {"COMPLIANT": "\U0001f7e2", "PARTIAL": "\U0001f7e1", "VIOLATION": "\U0001f534", "UNKNOWN": "\u26ab"}
        result_summary_lines = [f"{result_emoji} {result_label}"]
        for r in result_reasons[:5]:
            result_summary_lines.append(f"\u2022 {r}")
        result_summary_lines.append(
            f"Anayasal Uyum: {result_verdict_icon.get(recs['compliance_verdict'], '\u26ab')} "
            f"{recs['compliance_verdict']}"
        )
        result_node = _make_node("workflow_result", "14. Sonuc (Workflow Result)",
                                 status="completed" if is_success else "failed",
                                 summary=" | ".join(result_summary_lines)[:500],
                                 source="Anayasa Tarayicisi (Constitution Scanner)",
                                 detail={
                                     "is_success": is_success,
                                     "reasons": result_reasons,
                                     "compliance_verdict": recs["compliance_verdict"],
                                     "affected_workflows": recs["affected_workflows"],
                                 })
        nodes.append(result_node)

        # 15. YAPILMASI GEREKENLER (Recommended Actions)
        rec_parts = []
        if recs["auto_actions"]:
            rec_parts.append(f"A. HLK Otomatik: {'; '.join(recs['auto_actions'][:4])}"[:300])
        if recs["admin_actions"]:
            rec_parts.append(f"B. Yonetici: {'; '.join(recs['admin_actions'][:3])}"[:300])
        if recs["affected_workflows"]:
            rec_parts.append(f"C. Etkilenen: {', '.join(recs['affected_workflows'][:5])}")
        rerun = recs.get("rerun", {})
        rec_parts.append(f"D. Tekrar: {'\u2713 Mumkun' if rerun.get('possible') else '\u2717 Mumkun Degil'} - {rerun.get('condition', '-')}")
        if recs.get("estimated_fix_seconds", 0) > 0:
            rec_parts.append(f"E. Tahmini: ~{recs['estimated_fix_seconds']}sn, Basari: %{recs['estimated_success_rate']}")
        rec_node = _make_node("recommended_actions", "15. Yapilmasi Gerekenler (Recommended Actions)",
                              status="completed" if is_success else "running",
                              summary=" | ".join(rec_parts)[:500],
                              source="Anayasa Tarayicisi (Constitution Scanner)",
                              detail={
                                  "is_success": recs["is_success"],
                                  "auto_actions": recs["auto_actions"],
                                  "admin_actions": recs["admin_actions"],
                                  "affected_workflows": recs["affected_workflows"],
                                  "rerun": recs["rerun"],
                                  "estimated_fix_seconds": recs.get("estimated_fix_seconds", 0),
                                  "estimated_success_rate": recs.get("estimated_success_rate", 0),
                              })
        nodes.append(rec_node)

        workflows.append({
            "wf_id": wf_id,
            "wf_name": wf_name,
            "description": wf_desc,
            "status": status,
            "is_root_cause": False,
            "affected_by_root_cause": False,
            "nodes": nodes,
        })

    # ── Root Cause Detection ──────────────────────────────────────────────
    root_cause_found = False
    for wf in workflows:
        if root_cause_found:
            # Bu workflow root cause'tan sonra → etkilendi
            if wf["status"] in ("pending", "inactive"):
                wf["affected_by_root_cause"] = True
            continue

        if wf["status"] == "failed":
            wf["is_root_cause"] = True
            root_cause_found = True
            # Alt node'larda da ilk failed olanı bul
            for node in wf["nodes"]:
                if node["durum"] == "failed":
                    node["is_root_cause_node"] = True
                    break

    return {
        "pid": pid,
        "summary": {
            "product_name": product_name or "Bilinmiyor",
            "brand": brand or "Bilinmiyor",
            "platform": platform or "Bilinmiyor",
            "status": overall,
            "status_label": _derive_status(pkg) if pkg else "Veri Bekleniyor",
            "stage": _derive_stage(tasks, ""),
            "is_active": is_active,
            "created_at": created,
            "completed_at": completed,
        },
        "workflows": workflows,
    }


def _derive_wf_result(wf_id: str, brief: dict, tasks: list, decisions: list,
                      events: list, delivery: dict, final_video: dict,
                      quality: dict) -> str:
    """Workflow sonuç özetini üretir."""
    results = {
        "WF-001": f"URL doğrulandı: {brief.get('url', 'Veri bekleniyor')[:80]}" if brief.get("url")
                  else "Henüz URL alınmadı",
        "WF-002": f"{len(brief.get('product_name','') or '')} ürün analiz edildi" if brief.get("product_name")
                  else "Araştırma bekleniyor",
        "WF-003": f"Brief: {brief.get('product_name','')} / {brief.get('brand','')}" if brief.get("product_name")
                  else "Brief toplanmadı",
        "WF-004": "Brief onaylandı" if brief.get("product_name") else "Onay bekleniyor",
        "WF-005": "Senaryo oluşturuldu" if brief.get("product_name") else "Senaryo bekleniyor",
        "WF-006": "Senaryo onaylandı" if brief.get("product_name") else "Onay bekleniyor",
        "WF-007": f"{len(decisions)} karar üretildi" if decisions else "Fiyatlandırma bekleniyor",
        "WF-008": _summarize_production(tasks),
        "WF-009": quality.get("verdict", "Kalite kontrol bekleniyor") if quality else "Kalite kontrol bekleniyor",
        "WF-010": f"Teslim: {'Tamam' if delivery.get('delivered') else 'Bekleniyor'}" if delivery else "Teslim bekleniyor",
    }
    return results.get(wf_id, "")


def _summarize_production(tasks: list) -> str:
    """Üretim task'larının özetini çıkarır."""
    if not tasks:
        return "Henüz başlamadı"
    statuses = {}
    for t in tasks:
        agent = t.get("agent", "Unknown")
        s = t.get("status", "PENDING")
        statuses[agent] = s

    completed = sum(1 for s in statuses.values() if s in ("COMPLETED", "SUCCESS"))
    failed = sum(1 for s in statuses.values() if s == "FAILED")
    running = sum(1 for s in statuses.values() if s in ("PRODUCING", "PROCESSING"))

    parts = []
    if completed:
        parts.append(f"{completed} tamamlandı")
    if failed:
        parts.append(f"{failed} başarısız")
    if running:
        parts.append(f"{running} devam ediyor")
    return ", ".join(parts) if parts else "Bekleniyor"


def _find_decisions_for_wf(wf_id: str, decisions: list, events: list) -> list:
    """Workflow'a ait kararları bulur."""
    if not decisions:
        return []

    # Tüm WF'ler için genel karar döndür (şimdilik son kararı döndür)
    wf_decision_map = {
        "WF-001": decisions[:1] if decisions else [],
        "WF-007": decisions,  # Pricing kararları
        "WF-008": decisions,  # Production kararları
    }
    # Varsayılan: son karar
    return wf_decision_map.get(wf_id, decisions[-1:] if decisions else [])


def _find_tasks_for_wf(wf_id: str, tasks: list) -> list:
    """Workflow'a ait task'ları bulur."""
    if not tasks:
        return []

    wf_task_map = {
        "WF-001": [],  # Link doğrulama — task yok
        "WF-002": [t for t in tasks if t.get("agent") == "ImageGenerator"],
        "WF-005": tasks,  # Tüm task'lar scenario aşamasıyla ilgili
        "WF-007": [],  # Pricing — karar bazlı, task yok
        "WF-008": tasks,  # Tüm üretim task'ları
        "WF-009": [],  # QC — CEE bazlı
        "WF-010": [t for t in tasks if t.get("agent") == "DeliveryAgent"],
    }
    return wf_task_map.get(wf_id, [])


def _extract_candidates(decisions: list) -> dict:
    """Decision history'den aday provider'ları çıkarır."""
    if not decisions:
        return {}

    latest = decisions[-1]
    candidates = {}
    for cat in ("image", "voice", "video"):
        provs = latest.get(f"{cat}_providers", []) or []
        if provs:
            candidates[cat] = provs
    return candidates


def _extract_selected_providers(decisions: list) -> dict:
    """Seçilen primary provider'ları çıkarır."""
    if not decisions:
        return {}

    latest = decisions[-1]
    selected = {}
    for cat in ("image", "voice", "video"):
        key = f"primary_{cat}_provider"
        sp = latest.get(key) or {}
        if sp and (isinstance(sp, dict) and sp.get("provider")):
            selected[cat] = sp
    return selected


def _find_events_for_wf(wf_id: str, events: list) -> list:
    """Workflow'a ait event'leri keyword bazlı filtreler."""
    if not events:
        return []

    keyword_map = {
        "WF-001": ("LINK", "URL", "WEBSITE", "VALIDATION"),
        "WF-002": ("RESEARCH", "IMAGE", "GORSEL", "BACKGROUND"),
        "WF-003": ("BRIEF", "PRODUCT", "COLLECTION"),
        "WF-004": ("BRIEF", "APPROVAL", "ONAY"),
        "WF-005": ("SCENARIO", "GENERATION"),
        "WF-006": ("SCENARIO", "APPROVAL", "ONAY"),
        "WF-007": ("PRICING", "FIYAT", "TEKLIF", "COST"),
        "WF-008": ("VIDEO", "PRODUCTION", "TASK", "PROVIDER", "RENDER"),
        "WF-009": ("QUALITY", "CEE", "CHECK", "ENFORCE"),
        "WF-010": ("DELIVER", "SEND", "TELEGRAM", "TESLIM"),
    }
    keywords = keyword_map.get(wf_id, ("*",))
    return _find_events(events, *keywords)


def _get_api_refs_for_wf(wf_id: str) -> list:
    """Workflow ile ilgili API referanslarını döndürür."""
    ref_map = {
        "WF-001": [
            {"name": "handle_website_link", "module": "handlers.website", "url": "/start (Telegram)"},
        ],
        "WF-002": [
            {"name": "research_orchestrator.research", "module": "services.research_orchestrator"},
        ],
        "WF-008": [
            {"name": "Hedra API", "module": "services.hedra_generator", "url": "https://api.hedra.com/..."},
            {"name": "Higgsfield API", "module": "services.higgsfield_generator", "url": "https://platform.higgsfield.ai/..."},
            {"name": "ElevenLabs API", "module": "services.voice_generator", "url": "https://api.elevenlabs.io/..."},
            {"name": "Fal.ai API", "module": "services.image_generator", "url": "https://fal.ai/..."},
        ],
        "WF-009": [
            {"name": "Constitution Enforcement", "module": "services.constitution_enforcement"},
        ],
        "WF-010": [
            {"name": "Scene Delivery", "module": "services.scene_delivery", "url": "Telegram Bot API"},
        ],
    }
    return ref_map.get(wf_id, [])


def _extract_platform(url: str) -> str:
    """URL'den platform adını çıkar."""
    if not url:
        return ""
    u = url.lower()
    if "trendyol" in u: return "Trendyol"
    if "amazon" in u: return "Amazon"
    if "hepsiburada" in u: return "Hepsiburada"
    if "n11" in u: return "N11"
    if "laraari" in u: return "Laraari"
    if "aliexpress" in u: return "AliExpress"
    if "etsy" in u: return "Etsy"
    if "shopier" in u: return "Shopier"
    if "instagram" in u: return "Instagram"
    if "tiktok" in u: return "TikTok"
    return ""


def _derive_stage(tasks: list, status: str) -> str:
    """Mevcut aşamayı task durumlarından çıkar."""
    if not tasks:
        return "Link Bekleniyor" if status != "TAMAMLANDI" else ""

    for t in tasks:
        ts = t.get("status", "")
        agent = t.get("agent", "")
        if ts in ("PRODUCING", "PROCESSING"):
            return _agent_stage(agent)
        if ts == "PENDING":
            # Bu task'tan öncekiler tamamlanmış mı?
            return _agent_stage(agent)

    # Hepsi tamamlandı mı?
    if all(t.get("status") in ("COMPLETED", "SUCCESS") for t in tasks):
        last = tasks[-1].get("agent", "")
        if last == "DeliveryAgent": return "Telegram Gönderimi"
        return "Tamamlandı"

    if any(t.get("status") == "FAILED" for t in tasks):
        return "Hata"

    return status or "Veri Bekleniyor"


def _agent_stage(agent: str) -> str:
    return {
        "ImageGenerator": "Görsel Üretimi",
        "VoiceGenerator": "Ses Üretimi",
        "VideoRenderer": "Video Üretimi",
        "DeliveryAgent": "Telegram Gönderimi",
    }.get(agent, agent or "Veri Bekleniyor")


def _get_pid_providers(pkg: dict) -> list[dict]:
    """PID'e ait Decision Engine tarafından seçilmiş provider'ları döndür.
    Sadece decision_history varsa göster, yoksa boş liste.
    """
    decisions = pkg.get("decision_history", []) or []
    if not decisions:
        return []

    # En son kararı al
    latest = decisions[-1] if decisions else {}
    result = []

    for cat_key, cat_label in (("video", "Video"), ("voice", "Ses"), ("image", "Görsel")):
        providers = latest.get(f"{cat_key}_providers", []) or []
        for p in providers:
            name = p.get("provider", "")
            # Runtime'dan güncel durumu kontrol et
            runtime_status = _get_provider_runtime_status(cat_key, name)
            result.append({
                "kategori": cat_label,
                "provider": name,
                "priority": p.get("priority", 0),
                "confidence": p.get("confidence", 0),
                "status": runtime_status,
                "gorev": _provider_task(cat_key, name),
            })

    if result:
        result.sort(key=lambda x: x.get("priority", 99))
    return result


def _get_provider_runtime_status(category: str, name: str) -> str:
    """Provider'ın Runtime durumu."""
    try:
        from services.provider_priority import provider_priority, ProviderStatus
        rec = provider_priority.get_provider(name)
        if rec:
            return rec.status.value
    except Exception:
        pass
    return "UNKNOWN"


def _provider_task(category: str, name: str) -> str:
    tasks = {
        ("video", "hedra"): "Konuşan Video Üretimi",
        ("video", "higgsfield"): "Konuşan Video Üretimi",
        ("voice", "elevenlabs"): "AI Seslendirme",
        ("image", "fal.ai"): "Görsel Üretimi",
        ("image", "kie.ai"): "Görsel Üretimi",
    }
    return tasks.get((category, name), f"{category} üretimi")


def _is_runtime_connected() -> bool:
    """HLK Runtime aktif mi?"""
    try:
        from services.hlk_runtime import hlk_runtime as hr
        return bool(getattr(hr, '_sessions', {}))
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Provider'lar (genel liste)
# ═══════════════════════════════════════════════════════════════════════════════

def get_providers_status() -> list[dict]:
    try:
        from services.provider_priority import provider_priority
        result = []
        for cat in ("image", "voice", "video"):
            for p in provider_priority.get_priority_map(cat):
                result.append(p)
        return result
    except Exception:
        return []


async def check_providers_health() -> list[dict]:
    checks = {
        "hedra": {"url": "https://api.hedra.com/web-app/public/generations", "method": "GET",
                   "headers": {"X-API-Key": os.getenv("HEDRA_API_KEY", "")}},
        "higgsfield": {"url": "https://platform.higgsfield.ai/v1/files/upload", "method": "POST",
                        "headers": {"Authorization": f"Key {os.getenv('HIGGSFIELD_KEY_ID', '')}:{os.getenv('HIGGSFIELD_KEY_SECRET', '')}"}},
        "elevenlabs": {"url": "https://api.elevenlabs.io/v1/voices", "method": "GET",
                        "headers": {"xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")}},
    }
    results = []
    for name, cfg in checks.items():
        try:
            if cfg["method"] == "GET":
                resp = await asyncio.to_thread(_requests.get, cfg["url"], headers=cfg.get("headers", {}), timeout=10)
            else:
                resp = await asyncio.to_thread(_requests.post, cfg["url"], headers=cfg.get("headers", {}), timeout=10)
            results.append({"provider": name, "status_code": resp.status_code, "healthy": resp.status_code < 500,
                            "latency_ms": round(resp.elapsed.total_seconds() * 1000)})
        except Exception as e:
            results.append({"provider": name, "status_code": 0, "healthy": False, "error": str(e)[:100]})
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Event'ler
# ═══════════════════════════════════════════════════════════════════════════════

def get_events(pid: Optional[str] = None, limit: int = 50) -> list[dict]:
    try:
        from services.olay_kayit_merkezi import event_registry
        records = event_registry.get_by_pid(pid, limit) if pid else event_registry.get_recent(limit)
        return [
            {"zaman": getattr(r, "timestamp", ""), "pid": getattr(r, "pid", ""),
             "event": getattr(r, "event_name", getattr(r, "event_constant", "")),
             "aciklama": getattr(r, "event_description", "")}
            for r in (records or [])
        ]
    except Exception:
        return []


def get_package_data(pid: str) -> Optional[dict]:
    return _read_package(pid)


def get_stats() -> dict:
    try:
        from services.pid_runtime import pid_runtime
        ps = pid_runtime.get_stats()
    except Exception:
        ps = {}
    try:
        from services.olay_kayit_merkezi import event_registry
        es = event_registry.get_stats()
    except Exception:
        es = {}
    return {"pid_stats": ps, "event_stats": es}


# ═══════════════════════════════════════════════════════════════════════════════
# Operatör Kontrol
# ═══════════════════════════════════════════════════════════════════════════════

async def execute_control_action(pid: str, action: str) -> dict:
    action = action.lower().strip()
    if action == "dur":
        try:
            from services.production_runtime import production_runtime
            await production_runtime.cancel(pid)
            return {"ok": True, "action": "dur", "message": f"{pid} durduruldu"}
        except Exception as e:
            return {"ok": False, "action": "dur", "error": str(e)}
    elif action == "devam":
        try:
            from services.production_runtime import production_runtime
            await production_runtime.recover(pid)
            return {"ok": True, "action": "devam", "message": f"{pid} devam ediyor"}
        except Exception as e:
            return {"ok": False, "action": "devam", "error": str(e)}
    elif action == "yenile":
        try:
            from services.selection_architecture import selection_architecture
            selection_architecture.invalidate_cache()
            return {"ok": True, "action": "yenile", "message": "Provider cache temizlendi"}
        except Exception as e:
            return {"ok": False, "action": "yenile", "error": str(e)}
    raise ValueError(f"Bilinmeyen aksiyon: {action}")


# ═══════════════════════════════════════════════════════════════════════════════
# Production Debug Console — 14 adım debug verisi
# ═══════════════════════════════════════════════════════════════════════════════

def get_debug_data(pid: str) -> Optional[dict]:
    """Production Debug Console için 14 adımlık debug verisi.
    Package, provider list, event registry, decision history'den toplanır.
    """
    pkg = _read_package(pid)
    if not pkg:
        return None

    brief = pkg.get("brief", {}) or {}
    meta = pkg.get("metadata", {}) or {}
    tasks = pkg.get("task_packages", []) or []
    decisions = pkg.get("decision_history", []) or []
    events = get_events(pid=pid, limit=200) or []
    delivery = pkg.get("delivery_info", {}) or {}
    final_video = pkg.get("final_video", {}) or {}

    # Her task'ın output'unu indeksle
    task_outputs = {}
    for t in tasks:
        tid = t.get("task_id", "")
        agent = t.get("agent", "")
        out = t.get("output") or {}
        task_outputs[agent] = {"task_id": tid, "status": t.get("status", ""),
                                "output": out, "completed_at": t.get("completed_at", ""),
                                "description": t.get("description", "")}

    steps = []

    # 01 Ürün Linki
    url = brief.get("url", "")
    steps.append(_step("01", "Ürün Linki",
        status="completed" if url else "pending",
        general={"modül": "handlers.website", "fonksiyon": "handle_website_link",
                  "provider": "—", "model": "—", "url": url or "Veri Bekleniyor"},
        request={"endpoint": url, "method": "Telegram Message"} if url else {},
        events=_filter_events(events, "LINK", "URL", "WEBSITE")))

    # 02 Ürün Analizi
    product_name = brief.get("product_name", "")
    brand = brief.get("brand", "")
    steps.append(_step("02", "Ürün Analizi",
        status="completed" if product_name else "pending",
        general={"modül": "handlers.website", "fonksiyon": "analyze_product",
                  "ürün": product_name or "Veri Bekleniyor",
                  "marka": brand or "Veri Bekleniyor",
                  "platform": brief.get("platform", "")},
        events=_filter_events(events, "PRODUCT", "ANALYSIS", "ANALIZ")))

    # 03 Görsel Araştırması
    research = pkg.get("research_results", {}) or {}
    refs = pkg.get("reference_images", []) or []
    steps.append(_step("03", "Görsel Araştırması",
        status="completed" if research or refs else "pending",
        general={"modül": "services.research", "fonksiyon": "image_research",
                  "görsel_sayısı": str(len(refs)) if refs else "0"},
        files=[{"path": r, "type": "image"} for r in (refs if isinstance(refs, list) else [])],
        events=_filter_events(events, "IMAGE", "RESEARCH", "GORSEL")))

    # 04 Production Package
    steps.append(_step("04", "Production Package",
        status="completed" if meta.get("created_at") else "pending",
        general={"modül": "services.production_package_runtime",
                  "fonksiyon": "create",
                  "oluşturma": meta.get("created_at", ""),
                  "versiyon": meta.get("version", ""),
                  "tip": meta.get("production_type", "")},
        decision=_format_decision(decisions[0]) if decisions else "",
        events=_filter_events(events, "PACKAGE", "CREATE")))

    # 05 Provider Adayları
    try:
        from services.provider_priority import provider_priority
        candidates = provider_priority.evaluate_all()
    except Exception:
        candidates = {}
    steps.append(_step("05", "Provider Adayları",
        status="completed" if candidates else "pending",
        general={"modül": "services.provider_priority", "fonksiyon": "evaluate_all",
                  "adaylar": _format_candidates(candidates)} if candidates else {},
        events=_filter_events(events, "PROVIDER", "CANDIDATE", "SELECTION")))

    # 06 Provider Puanlaması
    latest_decision = decisions[-1] if decisions else {}
    scoring = {}
    for cat in ("image", "voice", "video"):
        provs = latest_decision.get(f"{cat}_providers", []) or []
        for p in provs:
            scoring[f"{cat}/{p.get('provider','')}"] = {
                "priority": p.get("priority", 0),
                "confidence": f"{p.get('confidence', 0)*100:.0f}%",
                "justification": p.get("justification", "")}
    steps.append(_step("06", "Provider Puanlaması",
        status="completed" if scoring else "pending",
        general={"modül": "services.decision_engine", "fonksiyon": "decide",
                  "puanlama": scoring} if scoring else {},
        decision=_format_decision(latest_decision),
        events=_filter_events(events, "DECISION", "SCORE", "SELECTION")))

    # 07 Provider Seçimi
    selected = {}
    for cat in ("image", "voice", "video"):
        key = f"primary_{cat}_provider"
        sp = latest_decision.get(key, {}) or {}
        if isinstance(sp, dict):
            selected[cat] = sp.get("provider", "") or ""
    steps.append(_step("07", "Provider Seçimi",
        status="completed" if any(selected.values()) else "pending",
        general={"modül": "services.decision_engine", "fonksiyon": "decide",
                  "seçilen": selected} if selected else {},
        decision=_format_decision(latest_decision),
        events=_filter_events(events, "DECISION", "SELECTED")))

    # 08 Provider Request (ImageGenerator task)
    img = task_outputs.get("ImageGenerator", {})
    steps.append(_build_task_step("08", "Provider Request (Görsel)", img, events,
                                   "task_image", "ImageGenerator"))

    # 09 Provider Response (ImageGenerator sonucu)
    steps.append(_build_task_step("09", "Provider Response (Görsel)", img, events,
                                   "task_image_result", "ImageGenerator", is_response=True))

    # 10 Video Job Takibi
    vid = task_outputs.get("VideoRenderer", {})
    steps.append(_build_task_step("10", "Video Job Takibi", vid, events,
                                   "task_video", "VideoRenderer"))

    # 11 Video Download
    steps.append(_step("11", "Video Download",
        status="completed" if final_video.get("path") else "pending",
        general={"modül": "services.production_pipeline", "fonksiyon": "task_video",
                  "video_path": final_video.get("path", "") or "Veri Bekleniyor",
                  "delivered": str(final_video.get("delivered", False))},
        files=[{"path": final_video.get("path", ""), "type": "video/mp4"}] if final_video.get("path") else []))

    # 12 Video Doğrulama
    cee_verdict = ""
    try:
        cee = pkg.get("quality_reports", {}) or {}
        cee_verdict = cee.get("verdict", "") if isinstance(cee, dict) else ""
    except Exception:
        pass
    steps.append(_step("12", "Video Doğrulama",
        status="completed" if cee_verdict else ("pending" if final_video.get("path") else "waiting"),
        general={"modül": "services.constitution_enforcement",
                  "fonksiyon": "enforce_post_check",
                  "CEE_verdict": cee_verdict or "Veri Bekleniyor"},
        events=_filter_events(events, "CEE", "POST_CHECK", "ENFORCE")))

    # 13 Telegram Gönderimi
    steps.append(_step("13", "Telegram Gönderimi",
        status="completed" if delivery.get("delivered") else "pending",
        general={"modül": "services.scene_delivery", "fonksiyon": "send_video",
                  "chat_id": str(delivery.get("chat_id", "")),
                  "teslim_zamanı": delivery.get("delivered_at", ""),
                  "video_var": str(delivery.get("video", False))},
        events=_filter_events(events, "DELIVER", "SEND", "TELEGRAM")))

    # 14 Session Kapatılması
    steps.append(_step("14", "Session Kapatılması",
        status="completed" if meta.get("completed_at") else ("pending" if meta.get("created_at") else "waiting"),
        general={"modül": "services.production_runtime", "fonksiyon": "_run_managed",
                  "başlangıç": meta.get("created_at", ""),
                  "bitiş": meta.get("completed_at", ""),
                  "durum": meta.get("status", ""),
                  "versiyon": meta.get("version", "")},
        events=_filter_events(events, "COMPLETED", "SESSION", "TERMINAL")))

    # Breakpoint'leri yükle
    breakpoints = _get_breakpoints(pid)

    return {"pid": pid, "steps": steps, "breakpoints": list(breakpoints)}


def _step(step_id: str, name: str, status: str = "pending",
          general: dict = None, request: dict = None, response: dict = None,
          files: list = None, events: list = None, decision: str = "") -> dict:
    return {
        "id": step_id, "name": name, "status": status,
        "general": general or {},
        "request": request or {},
        "response": response or {},
        "files": files or [],
        "events": events or [],
        "decision": decision or "",
        "has_breakpoint": False,
    }


def _build_task_step(step_id: str, name: str, task_info: dict,
                      events: list, func_name: str, agent: str,
                      is_response: bool = False) -> dict:
    """Task bazlı adım oluşturur."""
    out = task_info.get("output", {}) or {}
    status = task_info.get("status", "PENDING")
    if status in ("COMPLETED", "SUCCESS"):
        step_status = "completed"
    elif status in ("PRODUCING", "PROCESSING"):
        step_status = "running"
    elif status == "FAILED":
        step_status = "failed"
    elif status == "PENDING":
        step_status = "pending"
    else:
        step_status = "waiting"

    generated = out.get("generated", None)
    artifact = out.get("artifact", "") or ""

    general = {
        "modül": f"services.production_pipeline",
        "fonksiyon": func_name,
        "agent": agent,
        "task_id": task_info.get("task_id", ""),
        "task_status": status,
        "generated": str(generated) if generated is not None else "",
        "artifact": artifact,
        "tamamlanma": task_info.get("completed_at", ""),
    }

    req = {}
    resp = {}
    if is_response:
        resp = {"generated": str(generated), "artifact": artifact,
                 "task_id": task_info.get("task_id", "")}
    else:
        req = {"task_id": task_info.get("task_id", ""),
               "agent": agent, "description": task_info.get("description", "")}

    return _step(step_id, name, status=step_status, general=general,
                 request=req, response=resp,
                 files=[{"path": artifact, "type": "output"}] if artifact else [],
                 events=_filter_events(events, agent.upper(), func_name.upper()))


def _filter_events(events: list, *keywords: str) -> list:
    """Event'leri anahtar kelimelere göre filtrele."""
    if not events:
        return []
    result = []
    for e in events:
        text = (e.get("event", "") + " " + e.get("aciklama", "")).upper()
        if any(kw.upper() in text for kw in keywords):
            result.append(e)
    return result[:20]


def _format_decision(decision: dict) -> str:
    """Karar dict'ini okunabilir metne çevir."""
    if not decision:
        return ""
    parts = [f"Decision ID: {decision.get('decision_id', '?')}"]
    for cat in ("image", "voice", "video"):
        providers = decision.get(f"{cat}_providers", []) or []
        names = [p.get("provider", "?") for p in providers]
        if names:
            parts.append(f"{cat}: {' → '.join(names)}")
    return "\n".join(parts)


def _format_candidates(candidates: dict) -> str:
    """Provider adaylarını okunabilir metne çevir."""
    if not candidates:
        return ""
    lines = []
    for cat, provs in candidates.items():
        names = [f"{p.get('provider','?')}(skor:{p.get('score',0)})" for p in provs[:3]]
        lines.append(f"{cat}: {', '.join(names)}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# Breakpoint Store (in-memory)
# ═══════════════════════════════════════════════════════════════════════════════

_breakpoints: dict[str, set] = {}

def _get_breakpoints(pid: str) -> set:
    return _breakpoints.get(pid, set())

def set_breakpoint(pid: str, step_id: str) -> bool:
    if pid not in _breakpoints:
        _breakpoints[pid] = set()
    _breakpoints[pid].add(step_id)
    return True

def remove_breakpoint(pid: str, step_id: str) -> bool:
    if pid in _breakpoints:
        _breakpoints[pid].discard(step_id)
    return True

def has_breakpoint(pid: str, step_id: str) -> bool:
    return step_id in _breakpoints.get(pid, set())


def get_health_data(pid: str) -> dict:
    """Health Panel verisi."""
    try:
        from services.hlk_runtime import hlk_runtime as hr
        sessions = len(getattr(hr, '_sessions', {}))
        productions = len(getattr(hr, '_production_sessions', {}))
    except Exception:
        sessions = productions = 0

    try:
        from services.provider_priority import provider_priority
        available = sum(len(provider_priority.get_available(c)) for c in ("image", "voice", "video"))
        total = sum(len(provider_priority.get_providers(c)) for c in ("image", "voice", "video"))
    except Exception:
        available = total = 0

    pkg = _read_package(pid) or {}
    tasks = pkg.get("task_packages", []) or []
    failed = sum(1 for t in tasks if t.get("status") == "FAILED")
    completed = sum(1 for t in tasks if t.get("status") in ("COMPLETED", "SUCCESS"))

    risk = "DÜŞÜK"
    if failed > 0:
        risk = "YÜKSEK"
    elif completed == 0:
        risk = "ORTA"
    elif completed < len(tasks):
        risk = "ORTA"

    bp_count = len(_get_breakpoints(pid))

    return {
        "production": "AKTİF" if productions > 0 else "PASİF",
        "production_ok": productions > 0,
        "runtime": "AKTİF" if sessions > 0 else "PASİF",
        "runtime_ok": sessions > 0,
        "provider": f"{available}/{total}",
        "provider_ok": available > 0,
        "risk": risk,
        "risk_level": risk,
        "pending_interventions": bp_count,
        "open_errors": failed,
        "tasks_total": len(tasks),
        "tasks_completed": completed,
        "tasks_failed": failed,
    }


def get_evidence_package(pid: str) -> dict:
    """PID'e ait tüm kanıtları tek bir pakette toplar."""
    pkg = _read_package(pid)
    events = get_events(pid=pid, limit=500)
    return {
        "pid": pid,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "package": pkg,
        "events": events,
        "breakpoints": list(_get_breakpoints(pid)),
    }


def update_brief(pid: str, data: dict) -> dict:
    """Package brief'ini günceller (operatör düzeltmesi)."""
    pkg = _read_package(pid)
    if not pkg:
        raise ValueError(f"Package bulunamadı: {pid}")

    brief = pkg.get("brief", {}) or {}
    allowed = ("product_name", "brand", "platform", "url", "voice_language")
    for k in allowed:
        if k in data:
            brief[k] = data[k]

    pkg["brief"] = brief
    # Diske yaz
    _write_package(pid, pkg)
    return {"ok": True, "brief": brief}


def _write_package(pid: str, data: dict) -> bool:
    """Package'i diske yazar."""
    path = os.path.join(_PKG_DIR, f"{pid}.json")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp, path)
        return True
    except Exception as e:
        logger.error(f"Package yazılamadı ({pid}): {e}")
        return False


def rerun_step(pid: str, step_id: str) -> dict:
    """İlgili adımı yeniden çalıştır (task status'unu PENDING yap)."""
    step_agent_map = {
        "08": "ImageGenerator", "09": "ImageGenerator",
        "10": "VideoRenderer", "11": "VideoRenderer",
    }
    agent = step_agent_map.get(step_id)
    if not agent:
        raise ValueError(f"Bu adım yeniden çalıştırılamaz: {step_id}")

    pkg = _read_package(pid)
    if not pkg:
        raise ValueError(f"Package bulunamadı: {pid}")

    tasks = pkg.get("task_packages", []) or []
    updated = False
    for t in tasks:
        if t.get("agent") == agent and t.get("status") in ("COMPLETED", "SUCCESS", "FAILED"):
            t["status"] = "PENDING"
            t.pop("completed_at", None)
            t.pop("output", None)
            updated = True

    if updated:
        pkg["task_packages"] = tasks
        _write_package(pid, pkg)

    return {"ok": updated, "step_id": step_id, "agent": agent, "message": "Adım PENDING yapıldı" if updated else "Değişiklik yok"}
