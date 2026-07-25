"""
WebSocket bağlantı yönetimi ve EEC event bridge.
"""
import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# EEC bridge flag'i — sadece bir kere kurulur
_bridge_installed = False


class WebSocketManager:
    """WebSocket bağlantı havuzu ve broadcast yöneticisi."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}  # pid -> [ws, ...]

    async def connect(self, websocket: WebSocket, pid: str = "*"):
        """Yeni WebSocket bağlantısını kabul et."""
        await websocket.accept()
        if pid not in self._connections:
            self._connections[pid] = []
        self._connections[pid].append(websocket)
        logger.info(f"🔌 WS bağlandı: pid={pid}, toplam={len(self._connections[pid])}")

        try:
            while True:
                # Client'tan mesaj bekle (subscribe/unsubscribe)
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    action = msg.get("subscribe")
                    if action:
                        # PID değiştir
                        self._connections[pid].remove(websocket)
                        if not self._connections[pid]:
                            del self._connections[pid]
                        new_pid = action if action != "*" else "*"
                        if new_pid not in self._connections:
                            self._connections[new_pid] = []
                        self._connections[new_pid].append(websocket)
                        pid = new_pid
                        logger.debug(f"🔌 WS subscribe: {pid}")
                except json.JSONDecodeError:
                    pass
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.debug(f"WS hata: {e}")
        finally:
            await self._remove(websocket, pid)

    async def _remove(self, websocket: WebSocket, pid: str):
        """Bağlantıyı havuzdan çıkar."""
        if pid in self._connections:
            try:
                self._connections[pid].remove(websocket)
            except ValueError:
                pass
            if not self._connections[pid]:
                del self._connections[pid]
        logger.debug(f"🔌 WS koptu: pid={pid}")

    async def broadcast(self, event_data: dict, pid: Optional[str] = None):
        """Event'i ilgili tüm WebSocket bağlantılarına gönder."""
        targets = set()

        # Hedef PID'e abone olanlar
        if pid and pid in self._connections:
            targets.update(self._connections[pid])

        # Global dinleyiciler (*)
        if "*" in self._connections:
            targets.update(self._connections["*"])

        if not targets:
            return

        payload = json.dumps(event_data, ensure_ascii=False, default=str)
        dead = []
        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        # Ölü bağlantıları temizle
        for ws in dead:
            for p, conns in list(self._connections.items()):
                try:
                    conns.remove(ws)
                except ValueError:
                    pass
                if not conns:
                    del self._connections[p]


# Global singleton
ws_manager = WebSocketManager()


def install_eec_bridge():
    """EEC emit_event metodunu WebSocket broadcast ile sarar.

    Bu fonksiyon bir kere çağrılır (post_init sırasında).
    """
    global _bridge_installed
    if _bridge_installed:
        return

    try:
        from services.execution_event_collector import execution_event_collector, EECEventType
        _original_emit = execution_event_collector.emit_event

        async def _bridge_emit(*args, **kwargs):
            event = _original_emit(*args, **kwargs)
            if event:
                try:
                    event_dict = {
                        "zaman": getattr(event, "timestamp", ""),
                        "pid": getattr(event, "pid", ""),
                        "event": getattr(event, "event_constant", ""),
                        "aciklama": getattr(event, "event_description", ""),
                        "phase": getattr(event, "execution_phase", ""),
                        "result": getattr(event, "result", ""),
                        "durum": "OK",
                        "durumSinif": "active",
                    }
                    await ws_manager.broadcast(event_dict, pid=event_dict.get("pid"))
                except Exception as e:
                    logger.debug(f"EEC bridge broadcast hatası: {e}")
            return event

        execution_event_collector.emit_event = _bridge_emit
        _bridge_installed = True
        logger.info("🔗 EEC → WebSocket bridge kuruldu")
    except ImportError:
        logger.debug("EEC bulunamadı, WebSocket bridge kurulmadı")
    except Exception as e:
        logger.warning(f"EEC bridge kurulamadı: {e}")
