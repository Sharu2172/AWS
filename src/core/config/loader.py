# core/config/loader.py

from functools import lru_cache
from .settings import Settings
from core.logging.logger import setup_logging


@lru_cache
def get_settings():
    settings = Settings()
    setup_logging(level="DEBUG" if settings.app.debug else "INFO")
    return settings