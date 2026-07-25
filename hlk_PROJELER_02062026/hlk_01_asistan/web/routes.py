"""
Web sayfa route'ları — Jinja2 template'leri render eder.
"""
import os as _os
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from .auth import require_operator

logger = logging.getLogger(__name__)
router = APIRouter()

_TEMPLATE_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "templates")

# Jinja2 kurulumu
try:
    from jinja2 import Environment, FileSystemLoader
    _jinja = Environment(loader=FileSystemLoader(_TEMPLATE_DIR), autoescape=True)
except ImportError:
    _jinja = None


def _render(template_name: str, request: Request, **kwargs) -> HTMLResponse:
    """Jinja2 template render yardımcısı."""
    if _jinja is None:
        return HTMLResponse("<h1>Jinja2 yuklu degil</h1>", status_code=500)

    ctx = {
        "request": request,
        "token": request.query_params.get("token", ""),
        "active_page": "",
        **kwargs,
    }
    template = _jinja.get_template(template_name)
    return HTMLResponse(template.render(**ctx))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    require_operator(request)
    return _render("pages/home.html", request, active_page="home")


@router.get("/sessions", response_class=HTMLResponse)
async def sessions_page(request: Request):
    require_operator(request)
    return _render("pages/sessions.html", request, active_page="sessions")


@router.get("/pid/{pid}", response_class=HTMLResponse)
async def pid_detail_page(request: Request, pid: str):
    require_operator(request)
    return _render("pages/pid_detail.html", request, active_page="productions", pid=pid)


@router.get("/productions", response_class=HTMLResponse)
async def productions_page(request: Request):
    require_operator(request)
    return _render("pages/productions.html", request, active_page="productions")


@router.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    require_operator(request)
    return _render("pages/events.html", request, active_page="events")


@router.get("/providers", response_class=HTMLResponse)
async def providers_page(request: Request):
    require_operator(request)
    return _render("pages/providers.html", request, active_page="providers")


@router.get("/packages", response_class=HTMLResponse)
async def packages_page(request: Request):
    require_operator(request)
    return _render("pages/packages.html", request, active_page="packages")


@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    require_operator(request)
    return _render("pages/stats.html", request, active_page="stats")


@router.get("/debug/{pid}", response_class=HTMLResponse)
async def debug_console_page(request: Request, pid: str):
    """Production Debug Console — 14 adım accordion."""
    require_operator(request)
    return _render("pages/debug_console.html", request, active_page="productions", pid=pid)
