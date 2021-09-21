from unittest import mock

from app.core.exceptions import AppException
from tests.utils.base_test_case import BaseTestCase


class TestDistributorViews(BaseTestCase):
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

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_create_distributor(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        with self.client:
            response = self.client.post(
                "/api/v1/distributor/", json=self.distributor_data, headers=self.headers
            )
            self.assertStatus(response, 201)

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_distributor_permissions(self, mock_jwt):
        mock_jwt.side_effect = self.no_role_side_effect
        with self.client:
            response = self.client.post(
                "/api/v1/distributor/", json=self.distributor_data, headers=self.headers
            )
            self.assertStatus(response, 403)

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_show_distributor(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect

        distributor = self.distributor_repository.create(self.distributor_data)
        employee_data = self.employee_data.copy()
        employee_data["distributor_id"] = distributor.id

        self.employee_repository.create(employee_data)
        with self.client:
            response = self.client.get(
                f"/api/v1/distributor/{distributor.id}", headers=self.headers
            )
            self.assertStatus(response, 200)
            data = response.json

            self.assertEqual(
                data.get("employees")[0].get("first_name"),
                self.employee_data.get("first_name"),
            )

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_get_all_distributors(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        self.distributor_repository.create(self.distributor_data)

        with self.client:
            response = self.client.get("/api/v1/distributor/", headers=self.headers)
            self.assert_200(response)
            data = response.json
            self.assertIsInstance(data, list)
            self.assertEqual(data[0].get("name"), self.distributor_data.get("name"))

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_update_distributor(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        distributor_name = "sage distribution"
        distributor = self.distributor_repository.create(self.distributor_data)

        with self.client:
            response = self.client.patch(
                f"/api/v1/distributor/{distributor.id}",
                json={"name": distributor_name},
                headers=self.headers,
            )

            self.assert_200(response)
            data = response.json
            self.assertEqual(data.get("name"), distributor_name)

        updated_distributor = self.distributor_repository.find_by_id(distributor.id)

        self.assertEqual(updated_distributor.name, distributor_name)

    @mock.patch("app.core.utils.auth.jwt.decode")
    def test_delete_distributor(self, mock_jwt):
        mock_jwt.side_effect = self.required_roles_side_effect
        distributor = self.distributor_repository.create(self.distributor_data)

        distributor_search = self.distributor_repository.find_by_id(distributor.id)
        self.assertEqual(distributor_search.name, self.distributor_data.get("name"))

        with self.client:
            response = self.client.delete(
                f"/api/v1/distributor/{distributor.id}", headers=self.headers
            )

            self.assertStatus(response, 204)

        with self.assertRaises(AppException.NotFoundException):
            self.distributor_repository.find_by_id(distributor.id)
