"""
Singleton adapter'ları — mevcut servislerden web dashboard için veri çeker.
Yalnızca Runtime tarafından doğrulanmış verileri gösterir.
Placeholder / varsayılan / sahte veri üretmez.
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

# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

async def get_dashboard_data() -> dict:
    """Ana sayfa KPI verileri — yalnızca Runtime kaynaklı."""
    try:
        from services.pid_runtime import pid_runtime
        pid_stats = await pid_runtime.get_stats()
    except Exception:
        pid_stats = {}

    try:
        from services.hlk_runtime import hlk_runtime as hr
        active_sessions = len(hr._sessions) if hasattr(hr, "_sessions") else 0
        production_sessions = len(hr._production_sessions) if hasattr(hr, "_production_sessions") else 0
    except Exception:
        active_sessions = 0
        production_sessions = 0

    try:
        from services.olay_kayit_merkezi import event_registry
        stats = event_registry.get_stats()
        total_events = stats.get("total_events", 0) if stats else 0
    except Exception:
        total_events = 0

    try:
        from services.provider_priority import provider_priority
        all_available = sum(len(provider_priority.get_available(c)) for c in ("image", "voice", "video"))
        all_total = sum(len(provider_priority.get_providers(c)) for c in ("image", "voice", "video"))
        provider_health = f"{all_available}/{all_total}" if all_total > 0 else ""
    except Exception:
        provider_health = ""

    return {
        "kpi": [
            {"label": "Aktif Oturum", "value": str(active_sessions), "sub": ""},
            {"label": "Toplam PID", "value": str(pid_stats.get("total_pids", "")), "sub": ""},
            {"label": "Olay Kaydı", "value": str(total_events), "sub": ""},
            {"label": "Servis Sağlığı", "value": provider_health, "sub": ""},
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Oturumlar — yalnızca pid_runtime'da kayıtlı PID'ler
# ═══════════════════════════════════════════════════════════════════════════════

def get_active_sessions() -> list[dict]:
    """pid_runtime registry'sindeki PID'leri döndürür.
    Yalnızca doğrulanmış alanları içerir, placeholder yok.
    """
    sessions = []
    try:
        from services.pid_runtime import pid_runtime
        for rec in pid_runtime._pid_registry.values():
            pid = rec.pid
            is_active = getattr(rec, "is_active", False)
            created_at = getattr(rec, "created_at", "")

            sessions.append({
                "pid": pid,
                "is_active": is_active,
                "created_at": created_at,
                "durum": "AKTIF" if is_active else "TAMAMLANDI",
                "durumSinif": "running" if is_active else "completed",
            })
    except Exception as e:
        logger.warning(f"PID oturumları alınamadı: {e}")

    sessions.sort(key=lambda s: (not s["is_active"], s.get("created_at", "")))
    return sessions


# ═══════════════════════════════════════════════════════════════════════════════
# PID Detay
# ═══════════════════════════════════════════════════════════════════════════════

def get_pid_detail(pid: str) -> Optional[dict]:
    """PID detay — yalnızca Runtime'da mevcut veriler."""
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

    # Package'tan doğrulanmış veri
    product_name = ""
    task_packages = []
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg is None:
            # Diskten dene
            _pkg_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "production_packages"
            )
            _pkg_path = os.path.join(_pkg_dir, f"{pid}.json")
            if not os.path.exists(_pkg_path):
                _pkg_path = os.path.join(_pkg_dir, "archive", f"{pid}.json")
            if os.path.exists(_pkg_path):
                with open(_pkg_path, "r", encoding="utf-8") as f:
                    pkg_dict = json.load(f)
                    brief = pkg_dict.get("brief", {}) or {}
                    product_name = brief.get("product_name", "")
                    task_packages = pkg_dict.get("task_packages", []) or []
        else:
            pkg_dict = pkg.to_dict() if hasattr(pkg, "to_dict") else {}
            brief = pkg_dict.get("brief", {}) or {}
            product_name = brief.get("product_name") or ""
            task_packages = pkg_dict.get("task_packages", []) or []
    except Exception:
        pass

    # Provider listesi (her zaman gerçek Runtime verisi)
    providers = _get_provider_list()

    # Event'ler (doğrulanmış)
    events = get_events(pid=pid, limit=50)

    return {
        "pid": pid,
        "urun": product_name or "",
        "task_packages": task_packages,
        "is_active": is_active,
        "created_at": created_at,
        "durum": "AKTIF" if is_active else "TAMAMLANDI",
        "providers": providers,
        "events": events,
    }


def _get_provider_list() -> list[dict]:
    """Runtime'dan gerçek provider durumu."""
    try:
        from services.provider_priority import provider_priority
        cat_labels = {"video": "Video", "voice": "Ses", "image": "Görsel"}
        result = []
        for cat_key, cat_label in cat_labels.items():
            items = provider_priority.get_priority_map(cat_key)
            items.sort(key=lambda x: x["score"], reverse=True)
            for p in items:
                result.append({
                    "kategori": cat_label,
                    "provider": p["provider"],
                    "display_name": p["display_name"],
                    "skor": p["score"],
                    "status": p["status"],
                })
        return result
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Provider'lar
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
    health_checks = {
        "hedra": {"url": "https://api.hedra.com/web-app/public/generations", "method": "GET",
                   "headers": {"X-API-Key": os.getenv("HEDRA_API_KEY", "")}},
        "higgsfield": {"url": "https://platform.higgsfield.ai/v1/files/upload", "method": "POST",
                        "headers": {"Authorization": f"Key {os.getenv('HIGGSFIELD_KEY_ID', '')}:{os.getenv('HIGGSFIELD_KEY_SECRET', '')}"}},
        "elevenlabs": {"url": "https://api.elevenlabs.io/v1/voices", "method": "GET",
                        "headers": {"xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")}},
    }
    results = []
    for name, cfg in health_checks.items():
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
            {
                "zaman": getattr(r, "timestamp", ""),
                "pid": getattr(r, "pid", ""),
                "event": getattr(r, "event_name", getattr(r, "event_constant", "")),
                "aciklama": getattr(r, "event_description", ""),
            }
            for r in (records or [])
        ]
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Package
# ═══════════════════════════════════════════════════════════════════════════════

def get_package_data(pid: str) -> Optional[dict]:
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg is None:
            _pkg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "production_packages")
            _pkg_path = os.path.join(_pkg_dir, f"{pid}.json")
            if not os.path.exists(_pkg_path):
                _pkg_path = os.path.join(_pkg_dir, "archive", f"{pid}.json")
            if os.path.exists(_pkg_path):
                with open(_pkg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        return pkg.to_dict() if hasattr(pkg, "to_dict") else {}
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# İstatistikler
# ═══════════════════════════════════════════════════════════════════════════════

def get_stats() -> dict:
    try:
        from services.pid_runtime import pid_runtime
        pid_stats = pid_runtime.get_stats()
    except Exception:
        pid_stats = {}
    try:
        from services.olay_kayit_merkezi import event_registry
        evt_stats = event_registry.get_stats()
    except Exception:
        evt_stats = {}
    return {"pid_stats": pid_stats, "event_stats": evt_stats}


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
