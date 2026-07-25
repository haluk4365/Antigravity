"""
Singleton adapter'ları — mevcut servislerden web dashboard için veri çeker.

Bu modül:
- Karar vermez (HLK Runtime'ın görevi)
- Veri değiştirmez (read-only)
- Yalnızca mevcut singleton'lardan veri okur ve formatlar
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

def get_dashboard_data() -> dict:
    """Ana sayfa KPI verileri."""
    try:
        from services.pid_runtime import pid_runtime
        pid_stats = pid_runtime.get_stats()
    except Exception:
        pid_stats = {"total_pids": 0, "active_pids": 0, "daily_count": 0}

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
        total_events = stats.get("total_events", 0)
    except Exception:
        total_events = 0

    try:
        from services.provider_priority import provider_priority
        all_available = sum(
            len(provider_priority.get_available(cat))
            for cat in ("image", "voice", "video")
        )
        all_total = sum(
            len(provider_priority.get_providers(cat))
            for cat in ("image", "voice", "video")
        )
        provider_health = f"{all_available}/{all_total}"
    except Exception:
        provider_health = "?/?"

    return {
        "kpi": [
            {"label": "Aktif Oturum", "value": str(active_sessions),
             "sub": f"{production_sessions} üretimde"},
            {"label": "Toplam PID", "value": str(pid_stats.get("total_pids", 0)),
             "sub": f"Bugün: {pid_stats.get('daily_count', 0)}"},
            {"label": "Olay Kaydı", "value": str(total_events),
             "sub": "Tüm zamanlar"},
            {"label": "Servis Sağlığı", "value": provider_health,
             "sub": "servis aktif"},
        ],
        "active_pid": _get_active_pid(),
    }


def _get_active_pid() -> str:
    """Şu an aktif olan PID (varsa)."""
    try:
        from services.pid_runtime import pid_runtime
        for rec in pid_runtime._pid_registry.values():
            if getattr(rec, "is_active", False):
                return rec.pid
    except Exception:
        pass
    return "--"


# ═══════════════════════════════════════════════════════════════════════════════
# Oturumlar
# ═══════════════════════════════════════════════════════════════════════════════

def get_active_sessions() -> list[dict]:
    """Aktif PID'leri ve oturum bilgilerini döndürür."""
    sessions = []
    try:
        from services.pid_runtime import pid_runtime
        from services.hlk_runtime import hlk_runtime as hr

        for rec in pid_runtime._pid_registry.values():
            pid = rec.pid
            is_active = getattr(rec, "is_active", False)
            sessions.append({
                "pid": pid,
                "kullanici": str(_get_pid_user(pid)),
                "dil": "TR",
                "state": _get_pid_state(pid),
                "baslangic": getattr(rec, "created_at", "--")[-8:] if getattr(rec, "created_at", "") else "--",
                "durum": "🟢 Çalışıyor" if is_active else "⚫ Tamamlandı",
                "durumSinif": "running" if is_active else "completed",
                "is_active": is_active,
            })
    except Exception as e:
        logger.warning(f"Oturumlar alınamadı: {e}")

    # Aktif olanları üste al
    sessions.sort(key=lambda s: (not s["is_active"], s.get("baslangic", "")))
    return sessions


def _get_pid_user(pid: str) -> str:
    """PID'e ait kullanıcı ID'sini package'tan okur."""
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg:
            brief = getattr(pkg, "brief", {}) or {}
            return str(brief.get("user_id", brief.get("username", "?")))
    except Exception:
        pass
    return "?"


def _get_pid_state(pid: str) -> str:
    """PID'in mevcut state'ini döndürür."""
    try:
        from services.pid_runtime import pid_runtime
        rec = pid_runtime._pid_registry.get(pid)
        if rec:
            return "STATE_VIDEO_PRODUCTION" if getattr(rec, "is_active", False) else "STATE_COMPLETED"
    except Exception:
        pass
    return "STATE_UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# PID Detay
# ═══════════════════════════════════════════════════════════════════════════════

def get_pid_detail(pid: str) -> Optional[dict]:
    """PID'e ait tüm detayları döndürür."""
    # Package verisi
    package_data = {}
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg is None:
            # async load'ı dene
            pass
        if pkg:
            package_data = pkg.to_dict() if hasattr(pkg, "to_dict") else {}
    except Exception as e:
        logger.debug(f"Package load failed ({pid}): {e}")

    # Event log
    events = get_events(pid=pid, limit=30)

    # PID kaydı
    pid_record = None
    try:
        from services.pid_runtime import pid_runtime
        pid_record = pid_runtime._pid_registry.get(pid)
    except Exception:
        pass

    # Lifecycle
    lifecycle = get_pid_lifecycle(pid)

    # Hazırlık raporu
    hazirlik = get_hazirlik_raporu(pid)

    return {
        "pid": pid,
        "is_active": getattr(pid_record, "is_active", False) if pid_record else False,
        "created_at": getattr(pid_record, "created_at", "--") if pid_record else "--",
        "package": package_data,
        "events": events,
        "lifecycle": lifecycle,
        "hazirlik_raporu": hazirlik,
    }


def get_pid_lifecycle(pid: str) -> list[dict]:
    """PID yaşam döngüsü adımlarını döndürür."""
    lifecycle_steps = [
        ("/start", "PID Oluşturuldu"),
        ("Kullanıcı Doğrulandı", "Doğrulama"),
        ("Ürün Linki", "Link Bekleniyor"),
        ("Ürün Analizi", "Analiz"),
        ("Marka Analizi", "Marka"),
        ("Görsel Araştırması", "Görsel"),
        ("Servis Sağlayıcı", "Provider Seçimi"),
        ("Üretim Hazırlık Raporu", "Hazırlık Raporu"),
        ("Production Package", "Package"),
        ("Video Üretimi", "Video"),
        ("Render", "Render"),
        ("Telegram Teslimi", "Teslim"),
        ("Oturum Tamamlandı", "Tamamlandı"),
    ]

    # Event log'dan tamamlanan adımları tespit et
    completed_steps = set()
    try:
        events = get_events(pid=pid, limit=100)
        for e in events:
            event_name = e.get("event", "")
            if "PRODUCTION_STARTED" in event_name or "TASK_STARTED" in event_name:
                completed_steps.add("/start")
            if "LINK" in event_name or "VALIDATED" in event_name:
                completed_steps.add("Ürün Linki")
            if "DECISION" in event_name or "PROVIDER" in event_name:
                completed_steps.add("Servis Sağlayıcı")
            if "VIDEO" in event_name or "PRODUCTION" in event_name:
                completed_steps.add("Video Üretimi")
            if "DELIVERY" in event_name or "COMPLETED" in event_name:
                completed_steps.add("Telegram Teslimi")
            if "SESSION_COMPLETED" in event_name or "TERMINAL" in event_name:
                completed_steps.add("Oturum Tamamlandı")
    except Exception:
        pass

    steps = []
    for step_key, step_name in lifecycle_steps:
        if step_key in completed_steps:
            status, color = "✅ Tamamlandı", "#16a34a"
        elif step_key == lifecycle_steps[-1][0]:
            status, color = "⏳ Bekliyor", "#64748b"
        else:
            status, color = "⏳ Bekliyor", "#64748b"
        steps.append({"isim": step_name, "durum": status, "renk": color})

    return steps


def get_hazirlik_raporu(pid: str) -> dict:
    """HLK Üretim Hazırlık Raporu — provider değerlendirmesi."""
    try:
        from services.provider_priority import provider_priority
        categories = {
            "video": "🎬 VİDEO ÜRETİM SERVİS SAĞLAYICILARI",
            "voice": "🔊 SES ÜRETİM SERVİS SAĞLAYICILARI",
            "image": "🖼 GÖRSEL ÜRETİM SERVİS SAĞLAYICILARI",
        }
        report = {}
        for cat_key, cat_label in categories.items():
            items = provider_priority.get_priority_map(cat_key)
            # Skora göre sırala
            items.sort(key=lambda x: x["score"], reverse=True)
            report[cat_key] = {
                "label": cat_label,
                "providers": [
                    {
                        "provider": p["provider"],
                        "display_name": p["display_name"],
                        "gorev": _get_provider_task(cat_key, p["provider"]),
                        "skor": p["score"],
                        "confidence": p["confidence"],
                        "status": p["status"],
                        "justification": p["justification"],
                    }
                    for p in items
                ],
            }
        return report
    except Exception as e:
        logger.warning(f"Hazırlık raporu alınamadı: {e}")
        return {}


def _get_provider_task(category: str, provider: str) -> str:
    """Provider'ın yapacağı görevi döndürür."""
    tasks = {
        ("video", "hedra"): "Konuşan Video Üretimi (Lip-Sync)",
        ("video", "higgsfield"): "Konuşan Video Üretimi (Lip-Sync)",
        ("voice", "elevenlabs"): "AI Seslendirme (TTS)",
        ("image", "fal.ai"): "Görsel Üretimi",
        ("image", "kie.ai"): "Görsel Üretimi",
    }
    return tasks.get((category, provider), f"{category} üretimi")


# ═══════════════════════════════════════════════════════════════════════════════
# Provider'lar
# ═══════════════════════════════════════════════════════════════════════════════

def get_providers_status() -> list[dict]:
    """Tüm provider'ların durumunu döndürür."""
    try:
        from services.provider_priority import provider_priority
        result = []
        for cat in ("image", "voice", "video"):
            for p in provider_priority.get_priority_map(cat):
                result.append(p)
        return result
    except Exception as e:
        logger.warning(f"Provider durumu alınamadı: {e}")
        return []


async def check_providers_health() -> list[dict]:
    """Provider'lara canlı HTTP ping atarak sağlık durumunu kontrol eder."""
    health_checks = {
        "hedra": {"url": "https://api.hedra.com/web-app/public/generations", "method": "GET",
                   "headers": {"X-API-Key": os.getenv("HEDRA_API_KEY", "")}},
        "higgsfield": {"url": "https://platform.higgsfield.ai/v1/files/upload", "method": "POST",
                        "headers": {"Authorization": f"Key {os.getenv('HIGGSFIELD_KEY_ID', '')}:{os.getenv('HIGGSFIELD_KEY_SECRET', '')}"}},
        "elevenlabs": {"url": "https://api.elevenlabs.io/v1/voices", "method": "GET",
                        "headers": {"xi-api-key": os.getenv("ELEVENLABS_API_KEY", "")}},
    }

    results = []
    for provider_name, cfg in health_checks.items():
        try:
            if cfg["method"] == "GET":
                resp = await asyncio.to_thread(
                    _requests.get, cfg["url"], headers=cfg.get("headers", {}),
                    timeout=10
                )
            else:
                resp = await asyncio.to_thread(
                    _requests.post, cfg["url"], headers=cfg.get("headers", {}),
                    timeout=10
                )
            is_healthy = resp.status_code in (200, 401, 403)  # 401/403 = auth var ama yetki yok = servis canlı
            is_healthy = resp.status_code < 500  # 5xx = servis down
            results.append({
                "provider": provider_name,
                "status_code": resp.status_code,
                "healthy": is_healthy,
                "latency_ms": round(resp.elapsed.total_seconds() * 1000),
            })
        except Exception as e:
            results.append({
                "provider": provider_name,
                "status_code": 0,
                "healthy": False,
                "error": str(e)[:100],
            })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Event'ler
# ═══════════════════════════════════════════════════════════════════════════════

def get_events(pid: Optional[str] = None, limit: int = 50) -> list[dict]:
    """Event log kayıtlarını döndürür."""
    try:
        from services.olay_kayit_merkezi import event_registry
        if pid:
            records = event_registry.get_by_pid(pid, limit)
        else:
            records = event_registry.get_recent(limit)

        return [
            {
                "zaman": getattr(r, "timestamp", "--"),
                "pid": getattr(r, "pid", "--"),
                "event": getattr(r, "event_name", getattr(r, "event_constant", "--")),
                "aciklama": getattr(r, "event_description", ""),
                "durum": "OK",
                "durumSinif": "active",
            }
            for r in (records or [])
        ]
    except Exception as e:
        logger.debug(f"Event'ler alınamadı: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Package
# ═══════════════════════════════════════════════════════════════════════════════

def get_package_data(pid: str) -> Optional[dict]:
    """Production package JSON verisini döndürür."""
    try:
        from services.production_package_runtime import package_runtime
        pkg = package_runtime.load_sync(pid) if hasattr(package_runtime, "load_sync") else None
        if pkg is None:
            # Diskten doğrudan okumayı dene
            _pkg_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "production_packages"
            )
            _pkg_path = os.path.join(_pkg_dir, f"{pid}.json")
            if not os.path.exists(_pkg_path):
                _pkg_path = os.path.join(_pkg_dir, "archive", f"{pid}.json")
            if os.path.exists(_pkg_path):
                with open(_pkg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        return pkg.to_dict() if hasattr(pkg, "to_dict") else {}
    except Exception as e:
        logger.debug(f"Package verisi alınamadı ({pid}): {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# İstatistikler
# ═══════════════════════════════════════════════════════════════════════════════

def get_stats() -> dict:
    """İstatistik özeti."""
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

    try:
        from services.provider_priority import provider_priority
        provider_data = {}
        for cat in ("image", "voice", "video"):
            available = len(provider_priority.get_available(cat))
            total = len(provider_priority.get_providers(cat))
            provider_data[cat] = {"available": available, "total": total}
    except Exception:
        provider_data = {}

    return {
        "pid_stats": pid_stats,
        "event_stats": evt_stats,
        "provider_stats": provider_data,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Operatör Kontrol
# ═══════════════════════════════════════════════════════════════════════════════

async def execute_control_action(pid: str, action: str) -> dict:
    """Operatör kontrol aksiyonunu çalıştırır."""
    action = action.lower().strip()

    if action == "dur":
        try:
            from services.production_runtime import production_runtime
            await production_runtime.cancel(pid)
            _log_operator_action(pid, "DUR", "Operatör üretimi durdurdu")
            return {"ok": True, "action": "dur", "message": f"{pid} durduruldu"}
        except Exception as e:
            return {"ok": False, "action": "dur", "error": str(e)}

    elif action == "devam":
        try:
            from services.production_runtime import production_runtime
            await production_runtime.recover(pid)
            _log_operator_action(pid, "DEVAM", "Operatör üretime devam etti")
            return {"ok": True, "action": "devam", "message": f"{pid} devam ediyor"}
        except Exception as e:
            return {"ok": False, "action": "devam", "error": str(e)}

    elif action == "yenile":
        try:
            from services.decision_engine import decision_engine
            from services.selection_architecture import selection_architecture
            selection_architecture.invalidate_cache()
            _log_operator_action(pid, "YENILE", "Operatör provider'ları yeniden değerlendirdi")
            return {"ok": True, "action": "yenile", "message": "Provider'lar yeniden değerlendirildi"}
        except Exception as e:
            return {"ok": False, "action": "yenile", "error": str(e)}

    raise ValueError(f"Bilinmeyen aksiyon: {action}")


def _log_operator_action(pid: str, action: str, description: str):
    """Operatör aksiyonunu event log'a kaydeder."""
    try:
        from services.olay_kayit_merkezi import event_registry, EventRecord
        from datetime import datetime, timezone
        record = EventRecord(
            event_id=f"OPS-{int(time.time())}",
            event_name=f"OPERATOR_{action}",
            event_constant=action,
            event_description=description,
            pid=pid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_state="WEB_OPS",
            producer="WebOperasyonMerkezi",
            lac_visible=True,
        )
        event_registry.register(record)
    except Exception as e:
        logger.warning(f"Operator aksiyonu loglanamadi: {e}")
