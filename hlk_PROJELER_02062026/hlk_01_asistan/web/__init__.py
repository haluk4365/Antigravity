"""
HLK Local Web Operasyon Merkezi — FastAPI uygulamasi.

Bu paket, Telegram bot ile aynı asyncio event loop'ta çalışan
local web dashboard'u sağlar.
"""
from .app import create_app, start_web_server

__all__ = ["create_app", "start_web_server"]
