import pandas as pd

from backend.engines.model_registry import ModelRegistry
from backend.engines.trainer import Trainer


def sample_df():
    return pd.DataFrame(
        [
            {"feature1": 0.1, "feature2": 0.2, "feature3": 0.3, "label": 0},
            {"feature1": 0.5, "feature2": 0.6, "feature3": 0.7, "label": 1},
            {"feature1": 0.4, "feature2": 0.2, "feature3": 0.9, "label": 1},
            {"feature1": 0.9, "feature2": 0.8, "feature3": 0.2, "label": 0},
        ]
    )


def test_training_pipeline():
    registry = ModelRegistry()
    trainer = Trainer(registry)
    df = sample_df()
    output = trainer.train(df, run_id="test123")
    assert output.metrics["accuracy"] >= 0
