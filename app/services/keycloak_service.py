import os
import requests

from app import constants
from app.core.exceptions import AppException
from app.core.service_interfaces.auth_service_interface import (
    AuthServiceInterface,
)

CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
URI = os.getenv("KEYCLOAK_URI")
REALM = os.getenv("KEYCLOAK_REALM")
REALM_PREFIX = "/auth/realms/"
AUTH_ENDPOINT = "/protocol/openid-connect/token/"
REALM_URL = "/auth/admin/realms/"


class AuthService(AuthServiceInterface):
    headers = None
    roles = []

    def get_token(self, request_data):
        """
        Login to keycloak and return token
        :param request_data: {dict} a dictionary containing username and password
        :return: {dict} a dictionary containing token and refresh token
        """
        data = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": request_data.get("username"),
            "password": request_data.get("password"),
        }

        # create keycloak uri for token login
        url = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT

        response = requests.post(url, data=data)

        # handle error if its anything more than a 200 as a 200 response is the
        # only expected response
        if response.status_code != 200:
            raise AppException.KeyCloakAdminException(
                {constants.KEYCLOAK_ERROR: ["Error in username or password"]},
                status_code=response.status_code,
            )

        tokens_data = response.json()
        result = {
            "access_token": tokens_data["access_token"],
            "refresh_token": tokens_data["refresh_token"],
        }

        return result

    def refresh_token(self, refresh_token):
        """

        :param refresh_token: a {str} containing the refresh token
        :return: {dict} a dictionary containing the token and refresh token
        """
        request_data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }

        url = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT

        response = requests.post(url, data=request_data)

        if response.status_code != requests.codes.ok:
            raise AppException.BadRequest({"error": ["Error in refresh token"]})

        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
        }

    def create_user(self, request_data):
        data = {
            "email": request_data.get("email"),
            "username": request_data.get("username"),
            "firstName": request_data.get("first_name"),
            "lastName": request_data.get("last_name"),
            "credentials": [
                {
                    "value": request_data.get("password"),
                    "type": "password",
                    "temporary": False,
                }
            ],
            "enabled": True,
            "emailVerified": True,
            "access": {
                "manageGroupMembership": True,
                "view": True,
                "mapRoles": True,
                "impersonate": True,
                "manage": True,
            },
        }

        endpoint = "/users"
        # create user
        self.keycloak_post(endpoint, data)

        # get user details from keycloak
        user = self.get_keycloak_user(request_data.get("username"))
        user_id = user.get("id")

        # assign keycloak role
        self.roles = request_data.get("permissions")
        roles = self.get_all_roles()
        required_roles = filter(self.filter_func, roles)
        mapped_roles = list(map(self.map_func, required_roles))
        self.assign_role(user_id, mapped_roles)

        # login user and return token
        token_data = self.get_token(
            {
                "username": request_data.get("username"),
                "password": request_data.get("password"),
            }
        )
        token_data["id"] = user_id
        return token_data

    def filter_func(self, val):
        if val.get("name") in self.roles:
            return val

    def map_func(self, val):  # noqa
        return {"id": val.get("id"), "name": val.get("name")}

    def get_all_roles(self):
        url = URI + REALM_URL + REALM + "/roles"
        response = requests.get(url, headers=self.get_keycloak_headers())

        if response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"message": [response.json().get("errorMessage")]},
                status_code=response.status_code,
            )
        return response.json()

    def get_keycloak_user(self, username):
        url = URI + REALM_URL + REALM + "/users?username=" + username
        response = requests.get(url, headers=self.get_keycloak_headers())
        if response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {"message": [response.json().get("errorMessage")]},
                status_code=response.status_code,
            )
        user = response.json()
        if len(user) == 0:
            return None
        else:
            return user[0]

    def assign_role(self, user_id, roles):
        url = "/users/" + user_id + "/role-mappings/realm"
        data = roles
        self.keycloak_post(url, data)

    def reset_password(self, data):
        user_id = data.get("user_id")
        new_password = data.get("new_password")
        assert user_id, "user_id is required"
        assert new_password, "new_password is required"
        url = "/users/" + user_id + "/reset-password"

        data = {"type": "password", "value": new_password, "temporary": False}

        self.keycloak_put(url, data)

    def keycloak_post(self, endpoint, data):
        """
        Make a POST request to Keycloak
        :param {string} endpoint Keycloak endpoint
        :data {object} data Keycloak data object
        :return {Response} request response object
        """
        url = URI + REALM_URL + REALM + endpoint
        headers = self.headers or self.get_keycloak_headers()
        response = requests.post(url, headers=headers, json=data)
        if response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {constants.KEYCLOAK_ERROR: [response.json().get("errorMessage")]},
                status_code=response.status_code,
            )
        return response

    def keycloak_put(self, endpoint, data):
        """
        Make a POST request to Keycloak
        :param {string} endpoint Keycloak endpoint
        :data {object} data Keycloak data object
        :return {Response} request response object
        """
        url = URI + REALM_URL + REALM + endpoint
        headers = self.headers or self.get_keycloak_headers()
        response = requests.put(url, headers=headers, json=data)
        if response.status_code >= 300:
            raise AppException.KeyCloakAdminException(
                {constants.KEYCLOAK_ERROR: [response.json().get("errorMessage")]},
                status_code=response.status_code,
            )
        return response

    # noinspection PyMethodMayBeStatic
    def get_keycloak_access_token(self):
        """
        :returns {string} Keycloak admin user access_token
        """
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": os.getenv("KEYCLOAK_ADMIN_USER"),
            "password": os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
        }

        url = URI + REALM_PREFIX + REALM + AUTH_ENDPOINT

        response = requests.post(
            url,
            data=data,
        )
        if response.status_code != requests.codes.ok:
            raise AppException.KeyCloakAdminException(
                {constants.KEYCLOAK_ERROR: [response.text]}, status_code=500
            )
        data = response.json()
        return data.get("access_token")

    def get_keycloak_headers(self):
        """

        :return {object}  Object of keycloak headers
        """

        if self.headers:
            return self.headers

        headers = {
            "Authorization": "Bearer " + self.get_keycloak_access_token(),
            "Content-Type": "application/json",
        }
        self.headers = headers
        return headers
