# Governance & Compliance

## Framework Mapping
- **NIST AI RMF**
  - Govern: audit logging (`logs/secure_mlops.log`), approvals, rollback evidence.
  - Map: data validation with schema/PII/anomaly checks and dataset fingerprinting.
  - Measure: fairness proxy metrics, adversarial robustness scoring, drift metrics.
  - Manage: rollback workflow, deployment approvals, and incident logging.

- **ISO/IEC 42001**
  - Context & Leadership: security policies in `SECURITY.md`, code of conduct.
  - Planning & Support: SBOM generation, dependency policies, non-root containers.
  - Operation: training/validation gates, approval and deployment flows.
  - Performance Evaluation: metrics endpoint, dashboard, drift monitoring.
  - Improvement: rollback and incident response captured in runbook.

- **ACSC Essential 8 (relevant)**
  - Application control: SBOM visibility, dependency policy checks, minimal base image.
  - Patch management: CI lint/test gates; dependency scanning input via `/scan_sbom`.
  - Logging & monitoring: centralized audit log; drift/adversarial alerts.

- **Privacy Act ADM**
  - Data minimization: PII heuristics flag suspicious columns pre-training.
  - Transparency: validation reports returned in `/train` response; dataset fingerprints logged.

## Governance Controls
- **Approvals**: `/approve_model` simulates a second-person review before `/deploy`.
- **Signatures**: Models are SHA256 hashed and signed; verification gates deployment.
- **Rollback**: `/rollback` reverts to prior model on drift/adversarial signals.
- **Evidence**: Logs, SBOMs, metrics, and model metadata act as audit artifacts.
- **Access & Conduct**: Contributors follow [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).

## Evidence Capture
- Audit log: `logs/secure_mlops.log`
- Model registry: `models/registry.json`
- SBOMs: `sbom/sbom_<run_id>.json`
- Metrics and metadata: model registry metadata + `/metrics` endpoint
- Runbook: [docs/RUNBOOK.md](RUNBOOK.md)
