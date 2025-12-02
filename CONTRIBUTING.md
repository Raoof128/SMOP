# Contributing

Thank you for improving the Secure MLOps pipeline! Please follow the steps below to keep contributions safe and reviewable.

## Development Workflow
1. Fork or branch from `main`.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
3. Run quality checks before opening a PR:
   ```bash
   ruff check .
   black --check .
   pytest
   ```
4. Ensure docs are updated for behavior changes (README, API, architecture, governance, runbook).
5. Submit a pull request with a clear summary, risks, and testing evidence.

## Coding Standards
- Use type hints and docstrings for all public functions/classes.
- Add logging around I/O boundaries; never swallow exceptions silently.
- Do not hard-code secrets; configuration should be env-driven where applicable.
- Keep tests deterministic; prefer synthetic data only.

## Security & Privacy
- Run `/scan_sbom` when adding dependencies; avoid known dangerous packages.
- Validate inputs rigorously and prefer least-privilege defaults (non-root containers).
- Report vulnerabilities responsibly via the process in [SECURITY.md](SECURITY.md).

## Commit Messages
- Use clear, imperative messages (e.g., "Add drift detector guard").
- Reference issues where relevant.
