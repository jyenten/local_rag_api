import json
import uuid

from fastapi.testclient import TestClient

from experiments.dev_loop.adapters import LAB, DemoWorker, PytestChecker
from experiments.dev_loop.api import create_app

TOKEN = "test-token-with-at-least-24-characters"


def test_authenticated_http_roundtrip_and_durable_idempotency(tmp_path):
    app = create_app(DemoWorker(), PytestChecker(), tmp_path, TOKEN)
    client = TestClient(app)
    body = {"request_id": str(uuid.uuid4()), "task_id": "normalize-question"}
    headers = {"X-Dev-Loop-Token": TOKEN}
    assert client.get("/health").json()["backend"] == "demo"
    assert client.post("/runs", json=body).status_code == 401
    first = client.post("/runs", json=body, headers=headers)
    assert first.status_code == 200
    assert first.json()["status"] == "review_ready"
    assert first.json()["attempts"] == 2
    again = TestClient(create_app(DemoWorker(), PytestChecker(), tmp_path, TOKEN))
    assert again.post("/runs", json=body, headers=headers).json() == first.json()


def test_api_does_not_accept_arbitrary_commands_or_prompts(tmp_path):
    client = TestClient(create_app(DemoWorker(), PytestChecker(), tmp_path, TOKEN))
    response = client.post("/runs", headers={"X-Dev-Loop-Token": TOKEN},
                           json={"request_id": str(uuid.uuid4()), "command": "anything"})
    assert response.status_code == 422
    assert list(tmp_path.iterdir()) == []


def test_n8n_workflow_calls_bridge_once_and_has_no_credentials():
    workflow = json.loads((LAB / "n8n-workflow.json").read_text(encoding="utf-8"))
    calls = [n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base.httpRequest"]
    assert len(calls) == 1
    node = calls[0]
    assert node["retryOnFail"] is False
    assert node["parameters"]["url"].endswith("/runs")
    assert node["parameters"]["genericAuthType"] == "httpHeaderAuth"
    assert "credentials" not in node
    assert workflow["active"] is False
