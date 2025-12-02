"""Handles rollback logic for deployments."""

from __future__ import annotations

from backend.engines.model_registry import ModelRegistry
from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)

MIN_HISTORY_LENGTH = 2


class RollbackEngine:
    """Rollback to previous approved model."""

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def rollback(self) -> bool:
        """Simulate rollback to the previous model entry when available."""

        models = self.registry.list_models()
        if len(models) < MIN_HISTORY_LENGTH:
            logger.warning("No previous model to rollback to")
            return False

        # Pick the most recent approved model before the latest entry.
        previous_model = None
        for model in reversed(models[:-1]):
            if model.approved and self.registry.verify_run(model.run_id):
                previous_model = model
                break

        if previous_model is None:
            logger.warning("No approved historical model available for rollback")
            return False

        if not self.registry.mark_deployed(previous_model.run_id):
            logger.error("Failed to mark rollback target %s as deployed", previous_model.run_id)
            return False

        audit_event("rollback", "initiated", f"to={previous_model.run_id}")
        return True
