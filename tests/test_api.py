from http import HTTPStatus

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "ok"


def test_train_rejects_missing_fields():
    payload = {"records": [{"feature1": 0.1, "feature2": 0.2}]}
    response = client.post("/train", json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Schema validation failed" in str(response.json()["detail"])


def test_deploy_requires_approval_and_sets_deployed_model():
    payload = {
        "records": [
            {"feature1": 0.1, "feature2": 0.2, "feature3": 0.3, "label": 0},
            {"feature1": 0.4, "feature2": 0.2, "feature3": 0.6, "label": 1},
            {"feature1": 0.3, "feature2": 0.7, "feature3": 0.5, "label": 0},
            {"feature1": 0.9, "feature2": 0.1, "feature3": 0.4, "label": 1},
            {"feature1": 0.2, "feature2": 0.5, "feature3": 0.8, "label": 0},
        ]
    }
    train_resp = client.post("/train", json=payload)
    assert train_resp.status_code == HTTPStatus.OK
    run_id = train_resp.json()["run_id"]

    # Deployment should be blocked until approval is granted.
    deploy_resp = client.post("/deploy", json={"run_id": run_id})
    assert deploy_resp.status_code == HTTPStatus.FORBIDDEN

    approve_resp = client.post("/approve_model", json={"run_id": run_id})
    assert approve_resp.status_code == HTTPStatus.OK

    deploy_resp = client.post("/deploy", json={"run_id": run_id})
    assert deploy_resp.status_code == HTTPStatus.OK

    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == HTTPStatus.OK
    assert "accuracy" in metrics_resp.json()
