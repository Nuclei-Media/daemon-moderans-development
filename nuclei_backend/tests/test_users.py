import json
import random
import secrets
import faker

fake = faker.Faker()


class UsersTests(object):
    def __init__(self, client) -> None:
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
        self.test_login_for_access_token()
        self.test_login_for_access_token_failed()
        self.test_read_users_me()

    def test_login_for_access_token(self):
        response = self.client.post("/users/token", data=self.login_data)
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"

    def test_login_for_access_token_failed(self):
        response = self.client.post("/users/token", data=self.false_login_data)
        assert response.status_code == 401

    def test_read_users_me(self):
        response = self.client.post("/users/token", data=self.login_data)
        response_data = json.loads(response.content)
        access_token = response_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.client.get("/users/me", headers=headers)
        assert response.status_code == 200

    def register_failure(self):
        response = self.client.post(
            "/users/register", data=self.guaranteed_register_data
        )
        assert response.status_code == 401

    def guaranteed_registered(self):
        response = self.client.post(
            "/users/register", data=self.guaranteed_register_data
        )
        try:
            assert response.status_code == 200
        except AssertionError as e:
            assert response.status_code == 401

    def register_unique_user(self):
        response = self.client.post("/users/register", data=self.register_unique_data)
        try:
            assert response.status_code == 200
        except AssertionError as a:
            print(a)
            if response.status_code == 401:
                print("user already exists")
                if self.repeated_registration_test():
                    print("register works. its allguddie")

    def repeated_registration_test(self):
        assert (
            self.client.post("/users/register", data=self.register_unique_data)
        ).status_code == 401
