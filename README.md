# Secure MLOps Pipeline

A production-grade, educational Secure MLOps reference that demonstrates data validation, responsible training, registry governance, supply-chain safeguards, and monitored FastAPI serving. Everything is self-contained—no external cloud services.

## Highlights
- **Validated ingestion**: Pydantic schemas, synthetic PII heuristics, anomaly detection, data quality scoring, dataset fingerprinting.
- **Secure training**: Sklearn baseline model with adversarial/fairness checks, leakage guards, signed artifacts, and rich metadata.
- **Governed registry**: Versioned entries, SHA256 + signature verification, approval workflow, rollback helper, and audit logging.
- **Supply-chain hardening**: Dockerfile generation, SBOM (CycloneDX JSON), dependency policy checks, simulated signing, non-root runtime guidance.
- **Resilient serving**: FastAPI endpoints for train/approve/deploy/predict/rollback/scan, drift detection (PSI), governance events, and dashboard state.
- **Monitoring & incidents**: Drift and adversarial alerts, latency/error logging, automated rollback trigger, mock webhook notifications (simulated via audit log).
- **Documentation & testing**: Comprehensive docs, runbook, governance mapping, API reference, examples, CI (lint + tests), and pytest coverage.

## Repository Structure
```
.
├── backend/                # FastAPI service and engines
├── docs/                   # Architecture, API, governance, runbook
├── frontend/               # Dashboard assets
├── models/                 # Stored models and registry
├── pipelines/              # Simulated CI/CD pipeline
├── sbom/                   # Generated SBOMs (git-kept)
├── logs/                   # Audit logs (git-kept)
├── tests/                  # Pytest suite
├── examples/               # Sample payloads
└── .github/workflows/      # CI configuration
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Alternatively, use the provided Makefile helpers:
```bash
make install   # create venv + install dev deps
make lint      # ruff + black checks
make test      # pytest suite
make run       # uvicorn backend.main:app --reload
```

### Dev Container
Open the repository in VS Code and select "Reopen in Container" to use `.devcontainer/devcontainer.json`, which auto-installs development dependencies and enables format-on-save.

## Running the API
```bash
uvicorn backend.main:app --reload
```
Then visit `http://localhost:8000/health` or call the endpoints described in [docs/API.md](docs/API.md). Sample payloads live in `examples/`.

### Docker
Build and run the secure FastAPI service in a non-root container:
```bash
docker build -t secure-mlops .
docker run --rm -p 8000:8000 secure-mlops
```

## Linting & Tests
```bash
ruff check .
black --check .
pytest
```
CI runs the same steps via GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)), and the simulated pipeline at [pipelines/ci_cd_simulated.yml](pipelines/ci_cd_simulated.yml) mirrors those lint/test/service checks for offline validation.

### Pre-commit
Install git hooks to keep formatting and linting consistent:
```bash
pip install pre-commit
pre-commit install
```

## Architecture & Governance
- Architecture diagram and component roles: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Governance mappings (NIST AI RMF, ISO/IEC 42001, ACSC Essential 8, Privacy Act ADM): [docs/GOVERNANCE.md](docs/GOVERNANCE.md)
- Operational runbook: [docs/RUNBOOK.md](docs/RUNBOOK.md)
- API reference: [docs/API.md](docs/API.md)

## Usage Examples
Train, approve, and deploy a model:
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d @examples/train_payload.json

curl -X POST http://localhost:8000/approve_model \
  -H "Content-Type: application/json" \
  -d '{"run_id": "<RUN_ID_FROM_TRAIN>"}'

curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{"run_id": "<RUN_ID_FROM_TRAIN>"}'
```

> Models must be approved before deployment; predictions and metrics are only available for the active deployed run.

Request a prediction after deployment:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @examples/predict_payload.json
```

## Security & Responsible AI
- Input validation everywhere (Pydantic + schema guards) and synthetic PII hints.
- Signed artifacts with SHA256 verification prior to deployment and rollback on drift.
- SBOM + dependency policy checks and non-root container defaults.
- Fairness proxy metrics and adversarial robustness scoring captured in model metadata.
- Central audit log at `logs/secure_mlops.log` for governance evidence.

## Support & Contributions
See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution flow and [SECURITY.md](SECURITY.md) for vulnerability reporting. A standard code of conduct applies (see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)).
