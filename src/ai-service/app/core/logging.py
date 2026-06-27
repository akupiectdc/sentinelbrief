"""Logging configuration."""

from __future__ import annotations

import logging

from app.core.config import Settings

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(settings: Settings) -> None:
    """Configure root logging based on settings."""
    logging.basicConfig(level=settings.log_level.upper(), format=_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
