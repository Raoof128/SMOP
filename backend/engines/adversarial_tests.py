"""Lightweight adversarial robustness checks."""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AdversarialTester:
    """Simulate adversarial perturbations and score robustness."""

    def score(self, model: BaseEstimator, X: np.ndarray, y_true: np.ndarray) -> float:
        """Estimate robustness by adding noise and comparing predictions to ground truth."""

        noise = np.random.normal(0, 0.1, size=X.shape)
        perturbed = X + noise
        try:
            preds = model.predict(perturbed)
            robustness = float((preds == y_true).mean())
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Adversarial test failed: %s", exc)
            robustness = 0.0
        return robustness
