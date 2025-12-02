"""Data validation and risk assessment engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError, validator

from backend.utils.hash_utils import fingerprint_dataset
from backend.utils.logger import audit_event, get_logger

ANOMALY_Z_THRESHOLD = 3

logger = get_logger(__name__)


class InputRecord(BaseModel):
    """Schema representing a single training record."""

    feature1: float
    feature2: float
    feature3: float
    label: int

    @validator("label")
    def validate_label(cls, value: int) -> int:
        if value not in (0, 1):
            raise ValueError("label must be 0 or 1")
        return value


@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str]
    data_quality_score: float
    risk_score: float
    recommended_actions: List[str]
    dataset_fingerprint: str


class DataValidator:
    """Perform schema checks, PII detection, anomaly detection and quality scoring."""

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Run schema checks, PII detection, anomaly detection, and quality scoring."""

        issues: List[str] = []
        recommended: List[str] = []

        # Schema validation
        try:
            for record in df.to_dict(orient="records"):
                InputRecord(**record)
        except ValidationError as exc:  # pragma: no cover - Pydantic own tests
            issues.append(f"Schema validation failed: {exc}")

        # PII detection (synthetic: look for email-like patterns)
        pii_columns = [col for col in df.columns if df[col].astype(str).str.contains("@").any()]
        if pii_columns:
            issues.append(f"Possible PII detected in columns: {pii_columns}")
            recommended.append("Remove or hash PII columns before training")

        # Anomaly detection using z-score threshold
        numeric_df = df.select_dtypes(include=[np.number])
        std = numeric_df.std(ddof=0).replace(0, 1e-6)
        z_scores = np.abs((numeric_df - numeric_df.mean()) / std)
        anomalies = (z_scores > ANOMALY_Z_THRESHOLD).sum().sum()
        if anomalies > 0:
            issues.append(f"Detected {anomalies} potential anomalies via z-score > 3")
            recommended.append("Inspect outliers and consider clipping or normalization")

        # Data quality score as inverse of issues and anomalies
        quality_penalty = len(issues) * 0.1 + anomalies * 0.01
        data_quality_score = max(0.0, 1.0 - quality_penalty)

        # Risk score combines PII and anomalies
        risk_score = min(1.0, 0.2 * len(pii_columns) + anomalies * 0.005)

        fingerprint = fingerprint_dataset(df.to_csv(index=False).encode())

        audit_event(
            category="data_validation",
            action="completed",
            details=f"issues={len(issues)} quality={data_quality_score:.2f} risk={risk_score:.2f}",
        )
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            data_quality_score=round(data_quality_score, 3),
            risk_score=round(risk_score, 3),
            recommended_actions=recommended or ["Proceed to training"],
            dataset_fingerprint=fingerprint,
        )
