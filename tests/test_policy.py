from backend.engines.container_builder import ContainerBuilder


def test_policy_flags_dangerous_packages():
    builder = ContainerBuilder()
    components = [
        {"name": "pyyaml", "version": "6.0"},
        {"name": "uvicorn", "version": "0.10.0", "user": "root"},
    ]
    results = builder.policy_check(components)
    assert any("flagged" in issue for issue in results["issues"])
    assert "root" in " ".join(results["issues"])
