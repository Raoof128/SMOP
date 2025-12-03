"""Synthetic fairness analysis."""

from __future__ import annotations

from typing import Dict

import numpy as np

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class FairnessAnalyzer:
    """Compute synthetic fairness proxy metrics."""

    def analyze(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Produce a simple demographic parity gap proxy metric."""

        # Split by synthetic group (even/odd index)
        group_a = y_pred[::2]
        group_b = y_pred[1::2]
        disparity = abs(group_a.mean() - group_b.mean()) if len(group_b) else 0.0
        return {"demographic_parity_gap": float(disparity)}
