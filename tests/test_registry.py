from backend.engines.model_registry import ModelRegistry


def test_registry_register_and_list(tmp_path):
    registry = ModelRegistry()
    dummy_model = tmp_path / "dummy.joblib"
    dummy_model.write_text("placeholder")
    registry.register_model(
        run_id="runx",
        model_path=dummy_model,
        metrics={"accuracy": 0.9},
        signature="sig",
        metadata={"metrics": "{}"},
    )
    models = registry.list_models()
    assert any(m.run_id == "runx" for m in models)


def test_mark_deployed_tracks_state(tmp_path):
    registry = ModelRegistry()
    dummy_model = tmp_path / "dummy.joblib"
    dummy_model.write_text("placeholder")
    # Use a real signature for verification pathways.
    signer = registry.signer
    signature = signer.sign_model(dummy_model)
    registry.register_model(
        run_id="run-approved",
        model_path=dummy_model,
        metrics={"accuracy": 0.9},
        signature=signature,
        metadata={"metrics": "{}"},
    )
    registry.approve("run-approved")
    assert registry.mark_deployed("run-approved")
    deployed = registry.deployed_model()
    assert deployed is not None
    assert deployed.run_id == "run-approved"
