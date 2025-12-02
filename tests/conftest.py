import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def restore_registry_state():
    """Backup and restore the model registry to keep tests isolated."""

    registry_path = ROOT / "models" / "registry.json"
    original = registry_path.read_text() if registry_path.exists() else None
    yield
    if original is not None:
        registry_path.write_text(original)
    for model_file in (ROOT / "models").glob("model_*.joblib"):
        model_file.unlink(missing_ok=True)
