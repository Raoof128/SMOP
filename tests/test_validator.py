import pandas as pd

from backend.engines.data_validator import DataValidator


def test_validator_returns_fingerprint_and_quality():
    validator = DataValidator()
    df = pd.DataFrame(
        [
            {"feature1": 0.1, "feature2": 0.2, "feature3": 0.3, "label": 0},
            {"feature1": 0.2, "feature2": 0.1, "feature3": 0.2, "label": 1},
        ]
    )
    result = validator.validate(df)
    assert result.dataset_fingerprint
    assert 0 <= result.data_quality_score <= 1
