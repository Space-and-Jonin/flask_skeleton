import uuid


class MockAuthService:

    tokens = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # noqa: E501
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # noqa: E501
    }

    def get_token(self, request_data):
        return self.tokens

    def refresh_token(self, refresh_token):
        return self.tokens

    def create_user(self, data):
        token = self.tokens
        token["id"] = str(uuid.uuid4())
        return token

    def get_keycloak_access_token(self):
        return

    def reset_password(self, param):
        return True
