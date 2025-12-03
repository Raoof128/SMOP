# API Reference

Base URL: `http://localhost:8000`

## Health
- **GET** `/health`
- Returns service status for probes.

## Training
- **POST** `/train`
- Body: `{ "records": [ { "feature1": 0.1, "feature2": 0.2, "feature3": 0.3, "label": 0 }, ... ] }`
- Validates schema/PII/anomalies, trains model, runs fairness and adversarial checks, signs artifact, registers entry, and sets drift baseline.
- Response: `{ "run_id": "...", "metrics": {...}, "signature": "...", "validation": {...} }`

## Approval
- **POST** `/approve_model`
- Body: `{ "run_id": "<run_id>" }`
- Marks the model as approved for deployment (2-step governance simulated in logs).

## Deployment
- **POST** `/deploy`
- Body: `{ "run_id": "<approved_run_id>" }`
- Verifies signatures and approval, marks the run as the active deployment, logs governance event, and returns deployment status.

## Prediction
- **POST** `/predict`
- Body: `{ "feature1": 0.2, "feature2": 0.4, "feature3": 0.6 }`
- Uses the active deployed model only; returns prediction and drift score. Drift alerts are logged.

## Registry
- **GET** `/model/latest`
- Returns metadata for the most recent model.

## Metrics
- **GET** `/metrics`
- Returns evaluation metrics for the deployed model; 404 if no deployment is active.

## Rollback
- **POST** `/rollback`
- Rolls back to previous model if available and logs governance event.

## SBOM & Container Hardening
- **POST** `/scan_sbom`
- Body: `{ "components": [{ "name": "fastapi", "version": "0.110.0" }, ...] }`
- Generates Dockerfile, SBOM, runs policy checks, and returns file locations plus issues/warnings.

## Dashboard
- **GET** `/dashboard`
- Returns registry, approvals, deployed run ID, last metrics for the deployed model, and drift score snapshot for the UI.

## Approvals + Governance Flow
1. Train → review validation/metrics/fairness/adversarial outputs.
2. Approve → run `/approve_model` once policy satisfied; governance logs are stored.
3. Deploy → signature verified; drift baseline set from training data.
4. Rollback → triggered manually or via drift/adversarial alert (recorded in audit log).
