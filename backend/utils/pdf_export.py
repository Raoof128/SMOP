"""Export utilities (placeholder for future PDF exports)."""

from __future__ import annotations

from pathlib import Path

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def export_text(content: str, path: Path) -> Path:
    """Persist provided text content to the target path."""

    path.write_text(content)
    logger.info("Exported content to %s", path)
    return path
