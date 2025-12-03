"""Validate CI and simulated pipeline configuration stays consistent with expectations."""

from pathlib import Path


def test_github_actions_ci_includes_quality_gates() -> None:
    """CI workflow must enforce linting and testing before merging."""

    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    required_fragments = [
        "actions/checkout@v4",
        "actions/setup-python@v5",
        "ruff check .",
        "black --check .",
        "pytest",
    ]
    for fragment in required_fragments:
        assert fragment in workflow, f"Expected '{fragment}' in CI workflow"


def test_simulated_pipeline_covers_lint_test_and_runtime() -> None:
    """Simulated pipeline should mirror CI quality gates and service boot."""

    pipeline = Path("pipelines/ci_cd_simulated.yml").read_text(encoding="utf-8")
    for fragment in ["ruff check", "black --check", "pytest", "backend.main"]:
        assert fragment in pipeline, f"Expected '{fragment}' in simulated pipeline"


def test_makefile_targets_align_with_ci_commands() -> None:
    """Makefile should expose lint and test targets used by pipelines."""

    makefile = Path("Makefile").read_text(encoding="utf-8")
    for target in ["lint:", "test:", "ruff check", "black --check", "pytest"]:
        assert target in makefile, f"Expected '{target}' in Makefile"
