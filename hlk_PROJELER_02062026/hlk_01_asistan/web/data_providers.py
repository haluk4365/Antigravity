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

_PKG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "production_packages")


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
        return getattr(hr, "_constitution_active", False)
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
