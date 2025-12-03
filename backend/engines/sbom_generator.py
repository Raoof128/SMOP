"""Generate CycloneDX-style SBOM (mock)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)

SBOM_DIR = Path("sbom")
SBOM_DIR.mkdir(exist_ok=True)


class SBOMGenerator:
    """Create minimal SBOM for dependency visibility."""

    def generate(self, components: List[Dict[str, str]], run_id: str) -> Path:
        """Create a CycloneDX-like SBOM document for given components."""

        sbom_content = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "metadata": {"component": {"name": "secure-mlops", "version": run_id}},
            "components": components,
        }
        path = SBOM_DIR / f"sbom_{run_id}.json"
        path.write_text(json.dumps(sbom_content, indent=2))
        audit_event("sbom", "generated", f"path={path}")
        return path
