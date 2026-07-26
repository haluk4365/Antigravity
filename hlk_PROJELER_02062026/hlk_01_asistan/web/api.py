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
        return await get_dashboard_data()
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


@router.get("/pid/{pid}/workflow-tree")
async def api_workflow_tree(request: Request, pid: str):
    """Explainable Workflow Explorer — tam workflow ağacı verisi."""
    _check_auth(request)
    try:
        from .data_providers import get_workflow_tree
        result = get_workflow_tree(pid)
        if result is None:
            raise HTTPException(404, f"PID bulunamadı: {pid}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow tree alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


@router.get("/session/{session_id}/workflows")
async def api_session_workflows(request: Request, session_id: str):
    """AR-002_59: Session ID bazlı pre-PID workflow durumları.

    PID oluşmadan önceki WF-001…WF-007 aralığındaki workflow'ların
    session olayları üzerinden durumunu döndürür.
    """
    _check_auth(request)
    try:
        from .data_providers import get_events
        from services.hlk_runtime import hlk_runtime as _hr
        events = get_events(session_id=session_id, limit=200)
        # Session'ı bul ve bağlı PID varsa onu da döndür
        pid = ""
        for ctx in getattr(_hr, '_sessions', {}).values():
            if hasattr(ctx, 'session_id') and ctx.session_id == session_id:
                pid = getattr(ctx, 'production_pid', '')
                break
        return {
            "session_id": session_id,
            "pid": pid or None,
            "events": events,
            "event_count": len(events),
        }
    except Exception as e:
        logger.error(f"Session workflows alınamadı ({session_id}): {e}")
        raise HTTPException(500, str(e))


@router.get("/pid/{pid}/compliance")
async def api_compliance_report(request: Request, pid: str):
    """PID için anayasal uyumluluk özet raporu."""
    _check_auth(request)
    try:
        from .constitution_scanner import get_scanner
        from .data_providers import _read_package, get_events
        scanner = get_scanner()
        pkg = _read_package(pid)
        if not pkg:
            raise HTTPException(404, f"PID bulunamadı: {pid}")
        results = {}
        for wf_id in scanner.get_all_wf_ids():
            results[wf_id] = {
                "verdict": scanner.evaluate_compliance(wf_id, pkg).verdict,
                "basis": {
                    "arch_rules": len(scanner.get_constitution_context(wf_id).get("arch_rules", [])),
                    "oper_rules": len(scanner.get_constitution_context(wf_id).get("oper_rules", [])),
                },
            }
        return {"pid": pid, "compliance": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance raporu alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


@router.get("/constitution/article/{article_id}")
async def api_constitution_article(request: Request, article_id: str):
    """Tek bir anayasa maddesinin tam detayını döndürür."""
    _check_auth(request)
    try:
        from .constitution_scanner import get_scanner
        scanner = get_scanner()
        detail = scanner.get_article_detail(article_id)
        if not detail:
            raise HTTPException(404, f"Madde bulunamadı: {article_id}")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Madde detayı alınamadı ({article_id}): {e}")
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
async def api_events(request: Request, pid: str = "", session_id: str = "", limit: int = 50):
    """Event log (PID veya session_id filtresi opsiyonel)."""
    _check_auth(request)
    try:
        from .data_providers import get_events
        return {"events": get_events(pid=pid or None, session_id=session_id or None, limit=limit)}
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


# ═══════════════════════════════════════════════════════════════════════════════
# Production Debug Console
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/debug/{pid}")
async def api_debug(request: Request, pid: str):
    """14 adımlık debug verisi."""
    _check_auth(request)
    try:
        from .data_providers import get_debug_data
        result = get_debug_data(pid)
        if result is None:
            raise HTTPException(404, f"PID bulunamadı: {pid}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug verisi alınamadı ({pid}): {e}")
        raise HTTPException(500, str(e))


@router.post("/debug/{pid}/breakpoint/{step_id}")
async def api_toggle_breakpoint(request: Request, pid: str, step_id: str):
    """Breakpoint ekle/kaldır."""
    _check_auth(request)
    try:
        from .data_providers import has_breakpoint, set_breakpoint, remove_breakpoint
        if has_breakpoint(pid, step_id):
            remove_breakpoint(pid, step_id)
            return {"ok": True, "action": "removed", "step_id": step_id}
        else:
            set_breakpoint(pid, step_id)
            return {"ok": True, "action": "added", "step_id": step_id}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/debug/{pid}/health")
async def api_health(request: Request, pid: str):
    """Health Panel verisi."""
    _check_auth(request)
    try:
        from .data_providers import get_health_data
        return get_health_data(pid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/debug/{pid}/rollback/{step_id}")
async def api_rollback(request: Request, pid: str, step_id: str):
    """Adımı rollback et."""
    _check_auth(request)
    try:
        from .data_providers import rerun_step
        return rerun_step(pid, step_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/debug/{pid}/resume-from/{step_id}")
async def api_resume_from(request: Request, pid: str, step_id: str):
    """Seçili adımdan itibaren devam et."""
    _check_auth(request)
    try:
        from .data_providers import _read_package, _write_package
        step_order = {"08": 0, "09": 1, "10": 2, "11": 3}
        target = step_order.get(step_id, 0)
        pkg = _read_package(pid)
        if not pkg:
            raise ValueError(f"Package bulunamadı: {pid}")
        tasks = pkg.get("task_packages", []) or []
        task_agents = {"08": "ImageGenerator", "09": "ImageGenerator", "10": "VideoRenderer", "11": "VideoRenderer"}
        for t in tasks:
            agent = t.get("agent", "")
            for sid, sagent in task_agents.items():
                if agent == sagent and step_order.get(sid, 99) >= target:
                    t["status"] = "PENDING"
                    t.pop("completed_at", None)
                    t.pop("output", None)
        pkg["task_packages"] = tasks
        _write_package(pid, pkg)
        return {"ok": True, "message": f"{step_id} ve sonrası PENDING yapıldı"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/debug/{pid}/evidence")
async def api_evidence_package(request: Request, pid: str):
    """Evidence Package — tüm kanıtları tek JSON'da indir."""
    _check_auth(request)
    try:
        from .data_providers import get_evidence_package
        return get_evidence_package(pid)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.patch("/pid/{pid}/brief")
async def api_update_brief(request: Request, pid: str):
    """Brief düzenleme — operatör product_name vb. düzeltir."""
    _check_auth(request)
    try:
        body = await request.json()
        from .data_providers import update_brief
        return update_brief(pid, body)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/debug/{pid}/rerun/{step_id}")
async def api_rerun_step(request: Request, pid: str, step_id: str):
    """Adımı yeniden çalıştır — task status'unu PENDING yapar."""
    _check_auth(request)
    try:
        from .data_providers import rerun_step
        return rerun_step(pid, step_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
