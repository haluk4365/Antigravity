"""
REST API endpoint'leri — singleton'lardan gerçek zamanlı veri.
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from .auth import require_operator

logger = logging.getLogger(__name__)
router = APIRouter()


def _check_auth(request: Request):
    require_operator(request)


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard / KPI
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def api_dashboard(request: Request):
    """Ana sayfa KPI özeti."""
    _check_auth(request)
    try:
        from .data_providers import get_dashboard_data
        return get_dashboard_data()
    except Exception as e:
        logger.error(f"Dashboard verisi alınamadı: {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Oturumlar
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/sessions")
async def api_sessions(request: Request):
    """Aktif PID oturumları listesi."""
    _check_auth(request)
    try:
        from .data_providers import get_active_sessions
        return {"sessions": get_active_sessions()}
    except Exception as e:
        logger.error(f"Oturum verisi alınamadı: {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# PID Detay
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/pid/{pid}")
async def api_pid_detail(request: Request, pid: str):
    """PID detay — tam üretim bilgisi."""
    _check_auth(request)
    try:
        from .data_providers import get_pid_detail
        result = get_pid_detail(pid)
        if result is None:
            raise HTTPException(404, f"PID bulunamadı: {pid}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PID detay alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


@router.get("/pid/{pid}/lifecycle")
async def api_pid_lifecycle(request: Request, pid: str):
    """PID yaşam döngüsü adımları."""
    _check_auth(request)
    try:
        from .data_providers import get_pid_lifecycle
        return {"pid": pid, "steps": get_pid_lifecycle(pid)}
    except Exception as e:
        logger.error(f"Lifecycle alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


@router.get("/pid/{pid}/hazirlik-raporu")
async def api_hazirlik_raporu(request: Request, pid: str):
    """HLK Üretim Hazırlık Raporu — provider değerlendirmesi."""
    _check_auth(request)
    try:
        from .data_providers import get_hazirlik_raporu
        return {"pid": pid, "rapor": get_hazirlik_raporu(pid)}
    except Exception as e:
        logger.error(f"Hazırlık raporu alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Provider'lar
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/providers")
async def api_providers(request: Request):
    """Tüm provider'ların güncel durumu."""
    _check_auth(request)
    try:
        from .data_providers import get_providers_status
        return {"providers": get_providers_status()}
    except Exception as e:
        logger.error(f"Provider verisi alınamadı: {e}")
        raise HTTPException(500, str(e))


@router.get("/providers/health")
async def api_providers_health(request: Request):
    """Provider canlı sağlık kontrolü (API ping)."""
    _check_auth(request)
    try:
        from .data_providers import check_providers_health
        return {"health": await check_providers_health()}
    except Exception as e:
        logger.error(f"Provider health check başarısız: {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Event'ler
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/events")
async def api_events(request: Request, pid: str = "", limit: int = 50):
    """Event log (PID filtresi opsiyonel)."""
    _check_auth(request)
    try:
        from .data_providers import get_events
        return {"events": get_events(pid=pid or None, limit=limit)}
    except Exception as e:
        logger.error(f"Event verisi alınamadı: {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Package
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/packages/{pid}")
async def api_package(request: Request, pid: str):
    """Production package JSON içeriği."""
    _check_auth(request)
    try:
        from .data_providers import get_package_data
        result = get_package_data(pid)
        if result is None:
            raise HTTPException(404, f"Package bulunamadı: {pid}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Package verisi alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# İstatistikler
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats")
async def api_stats(request: Request):
    """İstatistik özeti."""
    _check_auth(request)
    try:
        from .data_providers import get_stats
        return get_stats()
    except Exception as e:
        logger.error(f"İstatistik alınamadı: {e}")
        raise HTTPException(500, str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Operatör Kontrol Butonları
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/controls/{pid}/{action}")
async def api_controls(request: Request, pid: str, action: str):
    """Operatör kontrol butonları: devam, dur, yenile."""
    _check_auth(request)
    try:
        from .data_providers import execute_control_action
        result = await execute_control_action(pid, action)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Kontrol aksiyonu başarısız ({pid}/{action}): {e}")
        raise HTTPException(500, str(e))
