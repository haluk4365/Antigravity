"""
eCom Reklam Otomasyonu — Standard Logger
=========================================
- INFO ve üzeri çalışır (level parametresi ile değiştirilebilir)
- Exception stack trace'leri korunur
- Tüm Railway projelerinde aynı format
"""

import logging
import sys

# Configure stdout and stderr to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')



def get_logger(name, level=logging.INFO):
    """
    Antigravity V2 Standard Logger.

    Args:
        name: Logger adı (modül/servis ismi)
        level: Log seviyesi (varsayılan: INFO)
    """
    logger = logging.getLogger(name)

    # Birden fazla handler eklenmesini önle
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)

        # Format: 2026-04-11 19:30:21 - module_name - INFO - Mesaj
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
