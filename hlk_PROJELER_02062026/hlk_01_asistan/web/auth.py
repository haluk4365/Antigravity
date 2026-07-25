"""
Operatör yetkilendirme — basit token bazlı.
"""
import os
import logging
from functools import wraps
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

_TOKEN_HEADER = "X-HLK-Operator"


def get_operator_token() -> str:
    """Aktif operatör token'ını döndürür."""
    return os.getenv("HLK_WEB_OPS_TOKEN", "")


def verify_operator(request: Request) -> bool:
    """Request'in yetkili operatörden geldiğini kontrol eder."""
    token = get_operator_token()
    if not token:
        # Token tanımlanmamışsa herkese açık (local dev)
        return True

    # Önce header'ı kontrol et
    header_token = request.headers.get(_TOKEN_HEADER, "")
    if header_token and header_token == token:
        return True

    # Sonra query param'ı kontrol et
    query_token = request.query_params.get("token", "")
    if query_token and query_token == token:
        return True

    # Cookie kontrolü
    cookie_token = request.cookies.get("hlk_ops_token", "")
    if cookie_token and cookie_token == token:
        return True

    return False


def require_operator(request: Request):
    """Operatör yetkisi yoksa 403 fırlatır."""
    if not verify_operator(request):
        raise HTTPException(status_code=403, detail="Yetkisiz erişim. Operatör token'ı gerekli.")
