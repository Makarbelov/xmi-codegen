from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

SAMPLE_XMI = Path(__file__).resolve().parent.parent / "examples" / "sample.xmi"


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Приложение с чистой БД в памяти (в ней уже есть готовые шаблоны)."""
    with TestClient(create_app("sqlite://")) as test_client:
        yield test_client


@pytest.fixture()
def sample_xmi() -> Path:
    return SAMPLE_XMI
