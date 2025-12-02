"""Simple file-based model registry with signatures, approvals, and deployment state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import joblib

from backend.engines.model_signer import ModelSigner
from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)


REGISTRY_FILE = Path("models/registry.json")
REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class ModelRecord:
    run_id: str
    path: str
    metrics: Dict[str, float]
    signature: str
    metadata: Dict[str, str]
    approved: bool = False


class ModelRegistry:
    """Local registry storing model metadata and approval state."""

    def __init__(self) -> None:
        self.signer = ModelSigner()
        self._ensure_registry()

    def _ensure_registry(self) -> None:
        """Create an empty registry file when missing."""

        if not REGISTRY_FILE.exists():
            REGISTRY_FILE.write_text(
                json.dumps({"models": [], "deployed_run_id": None}, indent=2)
            )

    def _load_registry(self) -> Dict:
        """Load registry content from disk."""

        registry = json.loads(REGISTRY_FILE.read_text())
        # Older registries may not track deployed state; normalize here.
        registry.setdefault("deployed_run_id", None)
        registry.setdefault("models", [])
        return registry

    def _save_registry(self, registry: Dict) -> None:
        """Persist registry content to disk."""

        REGISTRY_FILE.write_text(json.dumps(registry, indent=2))

    def save_model(self, model, run_id: str) -> Path:
        """Serialize a trained model to disk and return the path."""

        path = Path(f"models/model_{run_id}.joblib")
        joblib.dump(model, path)
        return path

    def register_model(
        self,
        run_id: str,
        model_path: Path,
        metrics: Dict[str, float],
        signature: str,
        metadata: Dict[str, str],
    ) -> None:
        """Add a new model entry to the registry with signature and metadata."""

        registry = self._load_registry()
        registry["models"].append(
            ModelRecord(
                run_id=run_id,
                path=str(model_path),
                metrics=metrics,
                signature=signature,
                metadata=metadata,
                approved=False,
            ).__dict__
        )
        self._save_registry(registry)
        audit_event("registry", "model_registered", f"run_id={run_id}")

    def list_models(self) -> List[ModelRecord]:
        """Return all models stored in the registry."""

        registry = self._load_registry()
        return [ModelRecord(**item) for item in registry.get("models", [])]

    def latest_model(self) -> Optional[ModelRecord]:
        """Return the newest model if any exist."""

        models = self.list_models()
        return models[-1] if models else None

    def get_model(self, run_id: str) -> Optional[ModelRecord]:
        """Lookup a specific model run by identifier."""

        for model in self.list_models():
            if model.run_id == run_id:
                return model
        return None

    def approve(self, run_id: str) -> bool:
        """Mark the specified run_id as approved for deployment."""

        registry = self._load_registry()
        updated = False
        for item in registry.get("models", []):
            if item["run_id"] == run_id:
                item["approved"] = True
                updated = True
        if updated:
            self._save_registry(registry)
            audit_event("registry", "approved", f"run_id={run_id}")
        return updated

    def verify_run(self, run_id: str) -> bool:
        """Validate the signature of a specific model run to guard against tampering."""

        model = self.get_model(run_id)
        if not model:
            logger.error("Model not found for verification: %s", run_id)
            return False
        path = Path(model.path)
        if not path.exists():
            logger.error("Model path missing: %s", path)
            return False
        return self.signer.verify_model(path, model.signature)

    def verify_latest(self) -> bool:
        """Validate the signature of the latest model to guard against tampering."""

        model = self.latest_model()
        if not model:
            return False
        return self.verify_run(model.run_id)

    def mark_deployed(self, run_id: str) -> bool:
        """Mark an approved run as the active deployed model."""

        registry = self._load_registry()
        selected = None
        for item in registry.get("models", []):
            if item.get("run_id") == run_id:
                selected = item
                break
        if not selected:
            logger.warning("Attempted to deploy unknown run_id=%s", run_id)
            return False
        if not selected.get("approved"):
            logger.warning("Attempted to deploy unapproved run_id=%s", run_id)
            return False
        registry["deployed_run_id"] = run_id
        self._save_registry(registry)
        audit_event("registry", "deployed", f"run_id={run_id}")
        return True

    def deployed_model(self) -> Optional[ModelRecord]:
        """Return the currently deployed model if set."""

        registry = self._load_registry()
        deployed_id = registry.get("deployed_run_id")
        if not deployed_id:
            return None
        return self.get_model(deployed_id)
