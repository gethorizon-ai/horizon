import requests


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def register_user(self, username, email, password):
        data = {"username": username, "email": email, "password": password}
        response = requests.post(
            f"{self.base_url}/api/users/register", json=data)
        return response.json()

    def authenticate_user(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(
            f"{self.base_url}/api/users/authenticate", json=data)
        return response.json()

    def get_user(self, user_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/users/{user_id}", headers=headers)
        return response.json()
