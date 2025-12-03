"""Simulated container builder with policy checks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from backend.engines.sbom_generator import SBOMGenerator
from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)

DOCKERFILE_PATH = Path("Dockerfile")

DANGEROUS_PACKAGES = {"pyyaml", "pillow"}


class ContainerBuilder:
    """Generate Dockerfile, run policy checks, and produce SBOM."""

    def __init__(self) -> None:
        self.sbom_generator = SBOMGenerator()

    def generate_dockerfile(self) -> Path:
        """Create a hardened Dockerfile for the FastAPI service."""

        content = """
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
""".strip()
        DOCKERFILE_PATH.write_text(content)
        audit_event("container", "dockerfile_generated", str(DOCKERFILE_PATH))
        return DOCKERFILE_PATH

    def policy_check(self, components: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Evaluate supplied components for basic supply-chain policy issues."""

        issues: List[str] = []
        warnings: List[str] = []
        for comp in components:
            name = comp.get("name", "").lower()
            version = comp.get("version", "")
            if name in DANGEROUS_PACKAGES:
                issues.append(f"Package {name} flagged for vulnerabilities")
            if name == "root" or comp.get("user") == "root":
                issues.append("Container must not run as root")
            if name == "uvicorn" and version.startswith("0.1"):
                warnings.append("Outdated uvicorn version detected")
        return {"issues": issues, "warnings": warnings}

    def build(self, run_id: str, components: List[Dict[str, str]]) -> Dict[str, str]:
        """Generate Dockerfile, SBOM, and run policy checks for provided components."""

        dockerfile = self.generate_dockerfile()
        policy = self.policy_check(components)
        sbom_path = self.sbom_generator.generate(components, run_id)
        audit_event("container", "build_ready", f"dockerfile={dockerfile} sbom={sbom_path}")
        return {"dockerfile": str(dockerfile), "sbom": str(sbom_path), **policy}
