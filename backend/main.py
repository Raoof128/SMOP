"""FastAPI application exposing secure MLOps controls."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from backend.engines.compliance_engine import ComplianceEngine
from backend.engines.container_builder import ContainerBuilder
from backend.engines.data_validator import DataValidator, ValidationResult
from backend.engines.drift_detector import DriftDetector
from backend.engines.model_registry import ModelRecord, ModelRegistry
from backend.engines.rollback_engine import RollbackEngine
from backend.engines.trainer import Trainer
from backend.utils.logger import audit_event, get_logger

app = FastAPI(title="Secure MLOps Pipeline", version="1.0.0")

logger = get_logger(__name__)
registry = ModelRegistry()
data_validator = DataValidator()
trainer = Trainer(registry)
container_builder = ContainerBuilder()
drift_detector = DriftDetector()
rollback_engine = RollbackEngine(registry)
compliance_engine = ComplianceEngine()


class TrainRequest(BaseModel):
    """Schema for training data payloads."""

    records: List[Dict[str, float]]

    @classmethod
    def validate_non_empty(cls, value: List[Dict[str, float]]) -> List[Dict[str, float]]:
        if not value:
            raise ValueError("records must contain at least one row")
        return value

    _records_not_empty = validator("records", allow_reuse=True)(validate_non_empty)


class DeployRequest(BaseModel):
    """Request body for deployment operations."""

    run_id: str


class ApprovalRequest(BaseModel):
    """Request body for approving a specific model run."""

    run_id: str


class SBOMScanRequest(BaseModel):
    """SBOM scanning request containing dependency components."""

    components: List[Dict[str, str]]


class PredictRequest(BaseModel):
    """Prediction input schema expected by the model service."""

    feature1: float
    feature2: float
    feature3: float


class PredictionResponse(BaseModel):
    """Response returned after predictions including drift score."""

    prediction: int
    drift_score: float


class DashboardState(BaseModel):
    """Aggregated dashboard view returned to the frontend."""

    registry: List[ModelRecord]
    latest_metrics: Dict[str, Any]
    drift_score: float
    approvals: List[str]
    deployed_run_id: Optional[str]


def _load_dataframe(records: List[Dict[str, float]]) -> pd.DataFrame:
    """Convert list of feature dictionaries into a DataFrame."""

    return pd.DataFrame(records)


def _load_deployed_model() -> Optional[Any]:
    """Load the active deployed model from the registry if it exists."""

    deployed = registry.deployed_model()
    if not deployed:
        return None
    try:
        return joblib.load(deployed.path)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.error("Failed to load deployed model %s: %s", deployed.path, exc)
        return None


@app.get("/health")
def health() -> Dict[str, str]:
    """Simple health probe for uptime checks."""

    return {"status": "ok"}


@app.post("/train")
def train_endpoint(request: TrainRequest) -> Dict[str, Any]:
    """Trigger the training pipeline after validating incoming data."""

    df = _load_dataframe(request.records)
    validation: ValidationResult = data_validator.validate(df)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.issues)

    run_id = str(int(time.time()))
    try:
        output = trainer.train(df, run_id)
    except ValueError as exc:
        logger.error("Training failed validation for run %s: %s", run_id, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    drift_detector.set_baseline(df[["feature1"]].values.flatten())

    compliance_engine.record_event("NIST_AI_RMF", "Training completed")
    return {
        "run_id": run_id,
        "metrics": output.metrics,
        "signature": output.signature,
        "validation": validation.__dict__,
    }


@app.post("/approve_model")
def approve_model(request: ApprovalRequest) -> Dict[str, Any]:
    """Mark a specific run as approved for deployment."""

    success = registry.approve(request.run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"approved": True}


@app.post("/deploy")
def deploy(request: DeployRequest) -> Dict[str, Any]:
    """Deploy the latest approved model if signatures are valid."""

    model = registry.latest_model()
    if not model or model.run_id != request.run_id:
        raise HTTPException(status_code=400, detail="Run not latest or missing")
    if not model.approved:
        raise HTTPException(status_code=403, detail="Model not approved")
    if not registry.verify_latest():
        raise HTTPException(status_code=400, detail="Signature invalid")
    if not registry.mark_deployed(request.run_id):
        raise HTTPException(status_code=400, detail="Unable to mark deployment")
    audit_event("deploy", "initiated", f"run_id={request.run_id}")
    return {"status": "deployed", "run_id": request.run_id}


@app.post("/rollback")
def rollback() -> Dict[str, Any]:
    """Rollback to the previous model version if available."""

    success = rollback_engine.rollback()
    if not success:
        raise HTTPException(status_code=400, detail="No previous model")
    return {"rolled_back": True}


@app.post("/scan_sbom")
def scan_sbom(request: SBOMScanRequest) -> Dict[str, Any]:
    """Generate Dockerfile, SBOM, and policy evaluation for supplied components."""

    results = container_builder.build(run_id=str(int(time.time())), components=request.components)
    return results


@app.get("/model/latest")
def latest_model() -> Dict[str, Any]:
    """Return metadata for the most recent model in the registry."""

    model = registry.latest_model()
    if not model:
        raise HTTPException(status_code=404, detail="No models")
    return model.__dict__


@app.get("/metrics")
def metrics() -> Dict[str, Any]:
    """Expose stored evaluation metrics for the latest model."""

    model = registry.deployed_model()
    if not model:
        raise HTTPException(status_code=404, detail="No deployed model")
    metrics_data = json.loads(model.metadata.get("metrics", "{}"))
    return metrics_data


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictRequest) -> PredictionResponse:
    """Perform prediction using the latest model and evaluate drift."""

    model = _load_deployed_model()
    if model is None:
        raise HTTPException(status_code=404, detail="No deployed model")
    features = np.array([[request.feature1, request.feature2, request.feature3]])
    pred = int(model.predict(features)[0])
    drift_score = drift_detector.score(features.flatten())
    if drift_detector.is_drifted(features.flatten()):
        audit_event("drift", "alert", f"score={drift_score}")
    return PredictionResponse(prediction=pred, drift_score=drift_score)


@app.get("/dashboard", response_model=DashboardState)
def dashboard() -> DashboardState:
    """Provide aggregate dashboard state for the frontend."""

    models = registry.list_models()
    approvals = [m.run_id for m in models if m.approved]
    deployed = registry.deployed_model()
    latest_metrics = json.loads(deployed.metadata.get("metrics", "{}")) if deployed else {}
    drift_score = 0.0
    return DashboardState(
        registry=models,
        latest_metrics=latest_metrics,
        drift_score=drift_score,
        approvals=approvals,
        deployed_run_id=deployed.run_id if deployed else None,
    )
