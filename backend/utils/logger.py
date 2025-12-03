"""Structured logger configuration for secure MLOps."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(os.getenv("MLOPS_LOG_FILE", "logs/secure_mlops.log"))
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _create_handler() -> RotatingFileHandler:
    """Create a rotating file handler with sensible defaults."""
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(formatter)
    return handler


def get_logger(name: str) -> logging.Logger:
    """Return a logger pre-configured for the project."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = _create_handler()
        logger.addHandler(handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(handler.formatter)
        logger.addHandler(stream_handler)
    return logger


def audit_event(category: str, action: str, details: str) -> None:
    """Helper to emit standardized audit events."""
    logger = get_logger("audit")
    logger.info("AUDIT | %s | %s | %s", category, action, details)


def governance_event(domain: str, control: str, result: str) -> None:
    """Emit governance events mapped to frameworks."""
    logger = get_logger("governance")
    logger.info("GOVERNANCE | %s | %s | %s", domain, control, result)
