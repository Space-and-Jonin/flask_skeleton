import random
import uuid

import pytz
from datetime import datetime, timedelta
from core import Result, Notifier
from core import AppException

# from core import AuthServiceInterface
from app.models import Token
from app.notifications import SMSNotificationHandler
from app.repositories import EmployeeRepository, TokenRepository

utc = pytz.UTC


class EmployeeController(Notifier):
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        token_repository: TokenRepository,
        auth_service,
    ):
        self.repository = employee_repository
        self.auth_service = auth_service
        self.token_repository = token_repository

    def create(self, data):
        permissions = []
        phone_number = data.get("phone_number")
        email = data.get("email_address")

        assert phone_number, "Phone number is missing"
        assert email, "Email is missing"

        # Check if account with same phone number exists
        existing_employee = self.repository.find({"phone_number": phone_number})
        if existing_employee:
            raise AppException.ResourceExists(
                f"Employee with phone number {phone_number} exists"
            )

        # Check if account with same email address exists
        existing_employee = self.repository.find({"email_address": email})
        if existing_employee:
            raise AppException.ResourceExists(
                f"Employee with phone number {email} exists"
            )

        if data.get("create_retailer"):
            permissions.append("distributor_create_retailer")

        if data.get("create_secondary_user"):
            permissions.append("distributor_create_employee")

        # Check if keycloak server is up by logging in to Keycloak
        self.auth_service.get_keycloak_access_token()  # noqa
        # Remove password from as employee model does not require password

        employee_id = uuid.uuid4()
        data["username"] = str(employee_id)
        data["permissions"] = permissions
        auth_result = self.auth_service.create_user(data)
        auth_service_id = auth_result.get("id")
        data["auth_service_id"] = auth_service_id
        data["id"] = data.pop("username")
        data.pop("password")
        data.pop("permissions")
        self.repository.create(data)
        return Result(auth_result, status_code=201)

    def login(self, data):
        phone_number = data.get("phone_number")
        pin = data.get("password")
        employee = self.repository.find({"phone_number": phone_number})
        if not employee:
            raise AppException.NotFoundException("user does not exist")

        access_token = self.auth_service.get_token(
            {"username": employee.id, "password": pin}
        )

        return Result(access_token, 200)

    def request_password_reset(self, data):
        """
        Request password reset. This method sends a six digit token to the user
        in addition to return the user_id if the user is valid. The token sent,
        together with the user_id will be used together as keys for a
        subsequent request to reset the password

        """
        phone_number = data.get("phone_number")
        employee = self.repository.find({"phone_number": phone_number})

        if not employee:
            raise AppException.NotFoundException("User not found")

        auth_token = random.randint(100000, 999999)
        auth_token_expiration = datetime.now() + timedelta(minutes=5)
        token = self.token_repository.create(
            {
                "employee_id": employee.id,
                "token": auth_token,
                "expiration": auth_token_expiration,
            }
        )
        self.notify(
            SMSNotificationHandler(
                recipient=employee.phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": token.id}, 200)

    def resend_token(self, token_id):
        token = self.token_repository.find_by_id(token_id)
        auth_token = random.randint(100000, 999999)
        expiration = datetime.now() + timedelta(minutes=5)
        token = self.token_repository.create(
            {
                "employee_id": token.employee_id,
                "token": auth_token,
                "expiration": expiration,
            }
        )

        self.notify(
            SMSNotificationHandler(
                recipient=token.employee.phone_number,
                details={"verification_code": auth_token},
                meta={"type": "sms_notification", "subtype": "otp"},
            )
        )
        return Result({"id": token.id}, 200)

    def change_password(self, data):
        """
        Change the current password of the user. This assumes that the user
        is already logged in.

        """
        employee_id = data.get("employee_id")
        new_pin = data.get("new_password")
        old_pin = data.get("old_password")
        employee = self.repository.find_by_id(employee_id)
        if not employee:
            raise AppException.NotFoundException("user does not exist")

        self.auth_service.get_token({"username": str(employee.id), "password": old_pin})

        self.auth_service.reset_password(
            {
                "user_id": str(employee.auth_service_id),
                "new_password": new_pin,
            }
        )
        return Result({}, 204)

    def reset_password(self, data):
        """
        Reset the password of the user. This assumes that the user has received
        an authentication token and is making a password reset request
        token.
        """
        token = data.get("token")
        new_pin = data.get("new_password")
        token_id = data.get("token_id")

        auth_token: Token = self.token_repository.find_by_id(token_id)

        assert auth_token.token == token, "Wrong token"

        if utc.localize(datetime.now()) > auth_token.expiration:  # noqa
            raise AppException.ExpiredTokenException("token expired")

        employee = auth_token.employee

        self.auth_service.reset_password(
            {"user_id": str(employee.auth_service_id), "new_password": new_pin}
        )
        self.notify(
            SMSNotificationHandler(
                recipient=employee.phone_number,
                details={"name": employee.first_name},
                meta={"type": "sms_notification", "subtype": "successful_pin_change"},
            )
        )

        return Result(None, 204)

    def update(self, employee_id, data):
        employee = self.repository.update_by_id(employee_id, data)
        return Result(employee, status_code=200)

    def show(self, employee_id):
        employee = self.repository.find_by_id(employee_id)
        return Result(employee, 200)

    def index(self):
        employees = self.repository.index()
        return Result(employees, 200)

    def delete(self, employee_id):
        self.repository.delete(employee_id)
        return Result(None, 204)
