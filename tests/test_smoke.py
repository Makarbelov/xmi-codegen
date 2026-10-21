"""Базовые проверки API (ЛР№3). Полный набор тестов - в ЛР№4."""
from pathlib import Path

from fastapi.testclient import TestClient


def test_ready_templates_are_available(client: TestClient) -> None:
    assert len(client.get("/templates").json()) == 4


def test_create_template(client: TestClient) -> None:
    content = "{% for c in classes %}class {{ c.name }}: pass\n{% endfor %}"
    payload = {"name": "Мой шаблон", "content": content, "profile_id": 1}
    response = client.post("/templates", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Мой шаблон"


def test_generate_python_code(client: TestClient, sample_xmi: Path) -> None:
    with sample_xmi.open("rb") as f:
        response = client.post("/generate", files={"file": f}, data={"template_id": 1})
    assert response.status_code == 200
    assert "class Customer:" in response.json()["code"]


def test_unknown_template_returns_404(client: TestClient) -> None:
    assert client.get("/templates/999").status_code == 404
