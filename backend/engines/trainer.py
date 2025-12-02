"""Training pipeline implementation with security gates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from backend.engines.adversarial_tests import AdversarialTester
from backend.engines.evaluator import Evaluator
from backend.engines.fairness import FairnessAnalyzer
from backend.engines.model_registry import ModelRegistry
from backend.engines.model_signer import ModelSigner
from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)

MIN_CLASSES = 2


@dataclass
class TrainingOutput:
    model_path: Path
    metrics: Dict[str, float]
    metadata: Dict[str, str]
    signature: str


class Trainer:
    """Full training pipeline orchestrator."""

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry
        self.signer = ModelSigner()
        self.evaluator = Evaluator()
        self.adversarial_tester = AdversarialTester()
        self.fairness_analyzer = FairnessAnalyzer()

    def _prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Extract feature matrix and labels from the training DataFrame."""

        required_columns = {"feature1", "feature2", "feature3", "label"}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        features = df[["feature1", "feature2", "feature3"]].values
        labels = df["label"].values
        if len(set(labels)) < MIN_CLASSES:
            raise ValueError("Training data must contain at least two classes for classification")
        return features, labels

    def train(self, df: pd.DataFrame, run_id: str) -> TrainingOutput:
        """Run the full training workflow including evaluation and registry updates."""

        X, y = self._prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LogisticRegression(max_iter=200)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        metrics = self.evaluator.evaluate(y_test, predictions)

        adv_score = self.adversarial_tester.score(model, X_test, y_test)
        fairness_report = self.fairness_analyzer.analyze(y_test, predictions)

        metadata = {
            "run_id": run_id,
            "metrics": json.dumps(metrics),
            "adversarial_score": str(adv_score),
            "fairness": json.dumps(fairness_report),
        }

        model_path = self.registry.save_model(model, run_id)
        signature = self.signer.sign_model(model_path)

        self.registry.register_model(
            run_id=run_id,
            model_path=model_path,
            metrics=metrics,
            signature=signature,
            metadata=metadata,
        )

        audit_event("training", "completed", f"run_id={run_id} accuracy={metrics['accuracy']:.3f}")
        return TrainingOutput(
            model_path=model_path, metrics=metrics, metadata=metadata, signature=signature
        )
