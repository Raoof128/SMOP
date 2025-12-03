"""Population Stability Index drift detection."""

from __future__ import annotations

import numpy as np

from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)


def population_stability_index(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Compute PSI between expected and actual distributions."""

    bin_count = max(2, min(bins, len(expected)))
    hist_expected, bin_edges = np.histogram(expected, bins=bin_count)
    hist_actual, _ = np.histogram(actual, bins=bin_edges)
    # Convert counts to probabilities with smoothing
    hist_expected = hist_expected + 1e-6
    hist_actual = hist_actual + 1e-6
    hist_expected = hist_expected / hist_expected.sum()
    hist_actual = hist_actual / hist_actual.sum()
    psi = np.sum((hist_expected - hist_actual) * np.log(hist_expected / hist_actual))
    return float(psi)


class DriftDetector:
    """Detects distribution drift using PSI."""

    def __init__(self, threshold: float = 0.2) -> None:
        self.threshold = threshold
        self.baseline: np.ndarray | None = None

    def set_baseline(self, data: np.ndarray) -> None:
        """Store baseline distribution for future drift comparisons."""

        self.baseline = data

    def score(self, new_data: np.ndarray) -> float:
        """Calculate PSI against the baseline, defaulting to no drift when unset."""

        if self.baseline is None:
            self.baseline = new_data
            return 0.0
        psi = population_stability_index(self.baseline, new_data)
        audit_event("drift", "computed", f"psi={psi:.3f}")
        return psi

    def is_drifted(self, new_data: np.ndarray) -> bool:
        """Determine whether the PSI exceeds the configured threshold."""

        psi = self.score(new_data)
        return psi > self.threshold
