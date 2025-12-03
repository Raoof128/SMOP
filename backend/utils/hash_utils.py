"""Hashing and fingerprint utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return SHA256 hash of a file."""
    hash_obj = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def fingerprint_dataset(content: bytes) -> str:
    """Fingerprint dataset bytes."""
    return hashlib.sha256(content).hexdigest()


def sign_blob(content: bytes, key: str = "local-demo-key") -> str:
    """Create a simulated signature for a blob using a shared secret."""
    digest = hashlib.sha256(key.encode() + content).hexdigest()
    return digest


def verify_signature(content: bytes, signature: str, key: str = "local-demo-key") -> bool:
    """Verify signature produced by sign_blob."""
    expected = sign_blob(content, key)
    return expected == signature
