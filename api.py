import json
import requests


class API:
    session_token: str = None
    remember_token: str = None
    dxlink_token: str = None
    headers: dict = {}
    user_data: dict = {}

    def __init__(self, config):
        self.headers["Content-Type"] = "application/json"
        self.headers["Accept"] = "application/json"
        self.config = config
        self.url = self.config.url

    def post(self, endpoint: str = None, body: dict = None, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.post(self.url + endpoint, data=json.dumps(body), headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error {response.status_code}")
            print(f"Endpoint: {endpoint}")
            print(f"Body: {body}")
            print(f"Headers: {headers}")
            print(f"Response: {response.text}")
            return None

    def get(self, endpoint: str = None, body: dict = {}, headers: dict = None,
            params: dict = None) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.get(self.url + endpoint, data=json.dumps(body), headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}")
            print(f"Endpoint: {endpoint}")
            print(f"Body: {body}")
            print(f"Headers: {headers}")
            print(f"Response: {response.text}")
            return None

    def delete(self, endpoint: str = None, body: dict = {}, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.delete(self.url + endpoint, data=json.dumps(body), headers=headers)
        if response.status_code == 204:
            return response
        else:
            print(f"Error {response.status_code}")
            print(f"Endpoint: {endpoint}")
            print(f"Body: {body}")
            print(f"Headers: {headers}")
            print(f"Response: {response.text}")
            return None

    def login(self):
        body = {
            "login": self.config.data["personal-data"]["login"],
            "password": self.config.data["personal-data"]["password"],
            "remember-me": True
        }
        response = self.post(endpoint="/sessions", body=body)
        if response is None:
            raise Exception("Could not login")
        else:
            self.user_data = response["data"]["user"]
            self.session_token = response["data"]["session-token"]
            self.headers["Authorization"] = self.session_token

    def logout(self):
        self.delete("/sessions")

    def get_dxlink(self):
        response = self.get(endpoint="/api-quote-tokens")
        if response is None:
            raise Exception("Could not get dxlink tokens")
        else:
            self.dxlink_token = response["data"]["token"]
            self.dxlink_url = response["data"]["dxlink-url"]


class Config:
    url: str = None

    def __init__(self, prod: bool = False):
        with open("config.json") as f:
            self.data = json.load(f)
        if prod == False:
            self.url = self.data["api-info"]["cert"]
        else:
            self.url = self.data["api-info"]["prod"]