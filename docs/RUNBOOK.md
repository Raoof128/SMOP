# Runbook

## Normal Operations
1. **Validate & Train**
   - POST `/train` with validated records (see `examples/train_payload.json`).
   - Review `validation` output and metrics in the response.
   - Confirm dataset fingerprint is logged in `logs/secure_mlops.log`.
2. **Approval**
   - Verify metrics/fairness/adversarial scores meet policy.
   - POST `/approve_model` with the `run_id` returned by training.
   - Record approval in governance log (automatically emitted).
3. **Deploy**
   - POST `/deploy` with the approved `run_id`.
   - Confirm deployment status and monitor `/metrics` and `/dashboard`.

## Monitoring & Alerts
- **Drift**: When PSI > threshold, audit log contains a `drift` alert. Investigate data distribution and consider rollback.
- **Adversarial**: Adversarial tester scores are stored in metadata; unexpected spikes trigger governance alerts.
- **Latency/Errors**: Review `logs/secure_mlops.log` for error spikes; restart service if necessary.

## Incident & Rollback
1. Trigger `/rollback` if drift/adversarial scores spike or metrics regress.
2. Verify previous model is active via `/model/latest` and `/metrics`.
3. Capture incident details and timestamps from `logs/secure_mlops.log` for audit evidence.
4. Re-run `/train` with remediated dataset; re-approve and redeploy following normal flow.

## Supply-Chain & Image Checks
- Use `/scan_sbom` with dependency list to produce SBOM and policy violations.
- Ensure generated Dockerfile retains non-root user and minimal surface area.

## Backup & Recovery
- **Registry**: Back up `models/registry.json` and corresponding `model_*.joblib` files.
- **Logs**: Rotate and retain `logs/secure_mlops.log` for compliance.
- **SBOMs**: Archive `sbom/*.json` alongside release artifacts.
