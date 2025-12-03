"""Simulated model signing utilities."""

from __future__ import annotations

from pathlib import Path

from backend.utils.hash_utils import sha256_file, sign_blob, verify_signature
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ModelSigner:
    """Handle model hashing and signing."""

    def sign_model(self, model_path: Path) -> str:
        """Return a simulated signature for the provided model file."""

        digest = sha256_file(model_path)
        signature = sign_blob(digest.encode())
        logger.info("Model %s signed with digest %s", model_path.name, digest)
        return signature

    def verify_model(self, model_path: Path, signature: str) -> bool:
        """Check whether the provided signature matches the model digest."""

        digest = sha256_file(model_path)
        return verify_signature(digest.encode(), signature)
