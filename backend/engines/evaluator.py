"""Model evaluation utilities."""

from __future__ import annotations

from typing import Dict

from sklearn.metrics import accuracy_score, f1_score

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _safe_metric(metric_func, y_true, y_pred) -> float:
    """Execute a metric function with defensive error handling."""

    try:
        return float(metric_func(y_true, y_pred))
    except Exception as exc:  # pragma: no cover - defensive programming
        logger.error("Metric computation failed: %s", exc)
        return 0.0


class Evaluator:
    """Calculate evaluation metrics."""

    def evaluate(self, y_true, y_pred) -> Dict[str, float]:
        """Compute accuracy and F1 metrics with safety guards."""

        return {
            "accuracy": _safe_metric(accuracy_score, y_true, y_pred),
            "f1": _safe_metric(f1_score, y_true, y_pred),
        }
