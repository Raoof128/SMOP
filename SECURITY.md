# Security Policy

## Reporting Vulnerabilities
- Open a security-focused issue or contact maintainers directly. Do **not** include exploit details or sensitive data in public threads.
- We will acknowledge and triage reports within 72 hours.

## Secure Development Practices
- Dependencies are pinned in `requirements.txt` and developer tools in `requirements-dev.txt`.
- SBOMs are generated via `/scan_sbom`; review for vulnerable or disallowed components.
- Containers run as non-root with minimal ports and packages.
- Models are SHA256 hashed, signed, and verified before deployment; tampering triggers rollback.
- Audit logs (`logs/secure_mlops.log`) capture training, approvals, deployments, drift alerts, and rollbacks.

## Hardening Checklist
- Pydantic validation on all inputs and strict schema enforcement.
- No plaintext secrets; configuration must come from environment variables or safe stores.
- Apply principle of least privilege in code, containers, and CI.
- Monitor drift/adversarial alerts and execute rollback when thresholds are exceeded.
- Keep CI green: lint, format, and test prior to merging.
