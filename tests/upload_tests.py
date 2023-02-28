import json
import random
import secrets
import faker
import pathlib


class UploadTests(object):
    def __init__(self, client) -> None:
        self.client = client

        self.static_path = pathlib.Path(__file__).absolute()

        self.login_data = {"username": "string", "password": "string"}
        self.upload_file()

    def upload_file(self):
        token = self.client.post("/users/token", data=self.login_data)
        assert token.status_code == 200
        token_data = json.loads(token.content)
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "Bearer"

        headers = {"accept": "application/json"}
        params = {"ipfs_flag": "true"}

        print(self.static_path)

        files = {"files": open(self.static_path, "rb")}

        response = self.client.post(
            "/storage/compress/image",
            params=params,
            headers=headers,
            files=files,
        )
