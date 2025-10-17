import os
import pytest
from fastapi.testclient import TestClient

from server.app import app


@pytest.fixture(scope="session")
def client():
    # Ensure a dev key is available for tests
    os.environ.setdefault("ALLOWED_CLIENT_KEYS", "dev-key-1")
    with TestClient(app) as c:
        yield c
