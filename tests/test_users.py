import secrets
import pytest
from faker import Faker

fake = Faker()

import pytest
from fastapi.testclient import TestClient
from nuclei_backend import Nuclei


@pytest.fixture(scope="module")
def client():
    app = Nuclei()
    with TestClient(app) as client:
        yield client


class TestUsers(object):
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client
        self.login_data = {"username": "string", "password": "string"}
        self.false_login_data = {"username": "ng", "password": "g"}
        self.guaranteed_register_data = {
            "username": "string",
            "password": "string",
            "email": "string",
        }
        self.register_unique_data = {
            "username": fake.name(),
            "password": secrets.token_urlsafe(5),
            "email": fake.email(),
        }
        self.guaranteed_registered()
        self.register_unique_user()

    def test_login_for_access_token(self):
        response = self.client.post("/users/token", data=self.login_data)
        assert response.status_code == 200
        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"

    def test_login_for_access_token_failed(self):
        response = self.client.post("/users/token", data=self.false_login_data)
        assert response.status_code == 401

    def test_read_users_me(self):
        access_token = self.get_access_token()
        response = self.client.get(
            "/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

    def test_register_failure(self):
        response = self.client.post(
            "/users/register", data=self.guaranteed_register_data
        )
        assert response.status_code == 401

    def guaranteed_registered(self):
        response = self.client.post(
            "/users/register", data=self.guaranteed_register_data
        )
        assert response.status_code == 200

    def register_unique_user(self):
        response = self.client.post("/users/register", data=self.register_unique_data)
        assert response.status_code == 200

    def get_access_token(self):
        response = self.client.post("/users/token", data=self.login_data)
        return response.json()["access_token"]
