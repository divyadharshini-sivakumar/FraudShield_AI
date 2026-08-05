"""Simple logger configuration using the standard logging library.

All modules should import the `logger` instance from this file:

    from app.core.logger import logger
"""
import logging
import sys

logger = logging.getLogger("fraudshield")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
