"""
Singleton adapter'ları — mevcut servislerden web dashboard için veri çeker.
KURAL: Sadece Runtime'dan doğrulanmış veri. Placeholder / varsayılan YOK.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Optional

import requests as _requests

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
