"""Input validasyonu ve veri kontrol fonksiyonları."""

import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    URL geçerli mi kontrol et.

    Args:
        url: Kontrol edilecek URL

    Returns:
        URL geçerli ise True, değilse False
    """
    try:
        # URL regex pattern'i
        url_pattern = re.compile(
            r'^https?://'  # http:// veya https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return bool(url_pattern.match(url))

    except Exception as _e:
        return False


def is_valid_telegram_user_id(user_id: str) -> bool:
    """
    Telegram user ID geçerli mi kontrol et.

    Args:
        user_id: Kontrol edilecek user ID

    Returns:
        Valid ise True, değilse False
    """
    try:
        int(user_id)
        return len(user_id) > 0
    except ValueError:
        return False
