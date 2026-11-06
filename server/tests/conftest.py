import os
import sys

# app.py reads these when it's imported, so they have to be set first
os.environ["USE_MOCK_DB"] = "1"
os.environ["SKIP_SEED"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

import app as server


@pytest.fixture
def client():
    server.client.drop_database("HardwareCheckout")
    server.app.config["TESTING"] = True
    with server.app.test_client() as c:
        yield c


def sign_up_and_log_in(c, user_id, username):
    c.post("/add_user", json={"username": username, "userId": user_id, "password": "secret"})
    res = c.post("/login", json={"userId": user_id, "password": "secret"})
    assert res.status_code == 200
    return c


@pytest.fixture
def jane(client):
    return sign_up_and_log_in(client, "jane123", "Jane")


@pytest.fixture
def bob(client):
    second_browser = server.app.test_client()
    return sign_up_and_log_in(second_browser, "bob456", "Bob")
