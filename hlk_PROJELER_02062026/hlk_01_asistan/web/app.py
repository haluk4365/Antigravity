"""
FastAPI uygulama fabrikasi ve uvicorn başlatma.
"""
import logging
import os
import uuid

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

logger = logging.getLogger(__name__)

_WEB_PORT = int(os.getenv("PORT", os.getenv("HLK_WEB_PORT", "8080")))
_WEB_HOST = os.getenv("HLK_WEB_HOST", "0.0.0.0")
_OPERATOR_TOKEN = os.getenv("HLK_WEB_OPS_TOKEN", "")


def create_app() -> FastAPI:
    """FastAPI uygulamasini olusturur."""
    import os as _os

    app = FastAPI(
        title="HLK Operasyon Merkezi",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
    )

    # ── Static dosyalar ────────────────────────────────────────────────
    _static_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "static")
    if _os.path.isdir(_static_dir):
        app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    # ── Route'ları kaydet ──────────────────────────────────────────────
    from .routes import router as web_router
    app.include_router(web_router)

    from .api import router as api_router
    app.include_router(api_router, prefix="/api")

    # ── WebSocket ──────────────────────────────────────────────────────
    from .websocket_manager import ws_manager

    @app.websocket("/ws")
    async def ws_global(websocket):
        await ws_manager.connect(websocket, pid="*")

    @app.websocket("/ws/{pid}")
    async def ws_pid(websocket, pid: str):
        await ws_manager.connect(websocket, pid=pid)

    return app


async def start_web_server():
    """FastAPI sunucusunu ayni asyncio event loop'ta başlatır."""
    import asyncio

    global _OPERATOR_TOKEN
    if not _OPERATOR_TOKEN:
        _OPERATOR_TOKEN = uuid.uuid4().hex[:16]
        logger.warning("╔══════════════════════════════════════════════════════╗")
        logger.warning("║  HLK WEB OPS TOKEN (otomatik oluşturuldu):          ║")
        logger.warning(f"║  {_OPERATOR_TOKEN}                                  ║")
        logger.warning("║  Kullanım: ?token=TOKEN                              ║")
        logger.warning("╚══════════════════════════════════════════════════════╝")
        os.environ["HLK_WEB_OPS_TOKEN"] = _OPERATOR_TOKEN

    try:
        import uvicorn
        _app = create_app()
        config = uvicorn.Config(
            _app, host=_WEB_HOST, port=_WEB_PORT, log_level="info"
        )
        server = uvicorn.Server(config)
        logger.info(f"🌐 HLK Web Operasyon Merkezi: http://{_WEB_HOST}:{_WEB_PORT}")
        if os.getenv("RAILWAY_PRIVATE_DOMAIN"):
            logger.info(f"🚅 Railway internal: http://{os.getenv('RAILWAY_PRIVATE_DOMAIN')}:{_WEB_PORT}")
        # Sunucuyu arka planda başlat (aynı event loop'ta)
        asyncio.create_task(server.serve())
    except ImportError:
        logger.error("❌ uvicorn yüklü değil. Web sunucusu başlatılamadı.")
    except Exception as e:
        logger.error(f"❌ Web sunucusu başlatılamadı: {e}")
