from unittest import mock

from core import AppException
from app.constants import EMPLOYEE_ENDPOINT
from tests.utils.base_test_case import BaseTestCase
from tests.utils.mock_auth_service import MockAuthService


class TestEmployeeViews(BaseTestCase):
    distributor_data = {
        "location": "second rangoon close, cantonments, accra",
        "name": "sage",
        "tin_number": "abc_iad",
    }

    employee_data = {
        "first_name": "john",
        "last_name": "doe",
        "email_address": "john@example.com",
        "create_secondary_user": True,
        "create_retailer": True,
        "phone_number": "0244444449",
    }

    def create_employee(self):
        distributor = self.create_distributor()
        employee_data = dict(self.employee_data)
        employee_data["distributor_id"] = distributor.id
        return self.employee_repository.create(employee_data)

    def create_distributor(self):
        return self.distributor_repository.create(self.distributor_data)

    @mock.patch("core.utils.auth.jwt.decode")
    @mock.patch(
        "app.services.keycloak_service.AuthService.get_keycloak_access_token"
    )  # noqa
    @mock.patch("app.services.keycloak_service.AuthService.create_user")
    def test_create(self, mock_create_user, mock_admin_access_token, mock_jwt):
        mock_create_user.side_effect = MockAuthService().create_user
        mock_jwt.side_effect = self.required_roles_side_effect
        distributor = self.create_distributor()

        employee_data = dict(self.employee_data)
        employee_data["distributor_id"] = distributor.id
        employee_data["password"] = "p@$$w0rd"

        with self.client:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.client.post(
                EMPLOYEE_ENDPOINT, headers=headers, json=employee_data
            )
            token_data = response.json
            self.assertStatus(response, 201)
            self.assertIn("access_token", token_data)
            self.assertIn("refresh_token", token_data)

    def test_no_authentication_header_error(self):
        employee_data = {}

        with self.client:
            response = self.client.post(EMPLOYEE_ENDPOINT, json=employee_data)
            self.assert401(response)

    @mock.patch("core.utils.auth.jwt.decode")
    def test_create_required_fields(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        employee_data = {}

        with self.client:
            response = self.client.post(
                EMPLOYEE_ENDPOINT, json=employee_data, headers=self.headers
            )
            errors = response.json.get("errorMessage")
            self.assertStatus(response, 400)
            self.assertIn("first_name", errors)
            self.assertIn("last_name", errors)
            self.assertIn("password", errors)
            self.assertIn("phone_number", errors)

    @mock.patch("core.utils.auth.jwt.decode")
    def test_required_roles(self, mock_jwt):
        mock_jwt.side_effect = self.no_role_side_effect
        employee_data = {}
        with self.client:
            response = self.client.post(
                EMPLOYEE_ENDPOINT, json=employee_data, headers=self.headers
            )
            self.assert403(response)

    @mock.patch("core.utils.auth.jwt.decode")
    def test_update_employee(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        employee = self.create_employee()

        with self.client:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.client.patch(
                f"/api/v1/employee/accounts/{str(employee.id)}",
                headers=headers,
                json={"first_name": "jane"},
            )

            response_data = response.json
            self.assertTrue(mock_jwt.is_called)
            self.assertEqual(response_data.get("first_name"), "jane")
            self.assert_200(response)
        # Test if record in database reflects the new changes
        employee_search = self.employee_repository.find_by_id(employee.id)
        self.assertEqual(employee_search.first_name, "jane")

    @mock.patch("core.utils.auth.jwt.decode")
    def test_show_employee(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        employee = self.create_employee()
        with self.client:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.client.get(
                f"/api/v1/employee/accounts/{str(employee.id)}", headers=headers
            )

            response_data = response.json

            self.assert_200(response)
            self.assertEqual(response_data.get("first_name"), "john")

    @mock.patch("core.utils.auth.jwt.decode")
    def test_delete_employee(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        employee = self.create_employee()

        with self.client:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.client.delete(
                f"/api/v1/employee/accounts/{str(employee.id)}", headers=headers
            )

            self.assert_status(response, 204)

        with self.assertRaises(AppException.NotFoundException):
            self.employee_repository.find_by_id(employee.id)
