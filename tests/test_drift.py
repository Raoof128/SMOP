import numpy as np

from backend.engines.drift_detector import DriftDetector


def test_psi_no_drift():
    threshold = 5.0
    detector = DriftDetector(threshold=threshold)
    baseline = np.array([0.1, 0.2, 0.3, 0.4])
    detector.set_baseline(baseline)
    score = detector.score(np.array([0.15, 0.25, 0.35, 0.45]))
    assert score < threshold
