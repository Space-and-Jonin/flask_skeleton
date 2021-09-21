import secrets
from unittest import mock
from core import AppException
from tests.utils.base_test_case import BaseTestCase


class TestEmployeeController(BaseTestCase):
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

    password = secrets.token_hex(8)

    def create_employee(self):
        distributor = self.distributor_repository.create(self.distributor_data)
        employee_data = dict(self.employee_data)
        employee_data["distributor_id"] = distributor.id
        return self.employee_repository.create(employee_data)

    def test_create(self):

        employee_data = dict(self.employee_data)
        employee_data["password"] = self.password

        distributor = self.distributor_repository.create(self.distributor_data)
        employee_data["distributor_id"] = distributor.id
        employee = self.employee_controller.create(employee_data)

        self.assertIn("access_token", employee.value)
        self.assertIn("refresh_token", employee.value)

        # check if object exists in database
        employees = self.employee_repository.index()
        new_employee = employees[0]

        self.assertEqual(new_employee.first_name, "john")

    def test_login(self):
        employee_data = dict(self.employee_data)
        employee_data["password"] = self.password

        distributor = self.distributor_repository.create(self.distributor_data)
        employee_data["distributor_id"] = distributor.id
        employee = self.employee_controller.create(employee_data)

        self.assertIn("access_token", employee.value)

        login_result = self.employee_controller.login(
            {"phone_number": "0244444449", "password": self.password}
        )

        self.assertIn("access_token", login_result.value)
        self.assertIn("refresh_token", login_result.value)

    def test_update(self):
        employee = self.create_employee()
        self.employee_controller.update(
            employee.id,
            {
                "create_secondary_user": False,
            },
        )

        updated_employee = self.employee_repository.find_by_id(employee.id)

        self.assertFalse(updated_employee.create_secondary_user)

    def test_show(self):
        employee = self.create_employee()

        employee_search = self.employee_controller.show(employee.id)

        self.assertEqual(employee_search.value.first_name, "john")

    def test_index(self):
        employee = self.create_employee()

        self.employee_repository.create(
            {
                "first_name": "jane",
                "last_name": "doe",
                "email_address": "jane@example.com",
                "create_secondary_user": True,
                "create_retailer": True,
                "phone_number": "0245585869",
                "distributor_id": employee.distributor_id,
            }
        )

        employees = self.employee_controller.index()
        self.assertIsInstance(employees.value, list)
        self.assertEqual(len(employees.value), 2)

    def test_unique_employee_error(self):
        self.create_employee()
        employee_data = dict(self.employee_data)
        employee_data["password"] = self.password

        # test unique email
        with self.assertRaises(AppException.ResourceExists):
            self.employee_controller.create(employee_data)

        # test unique phone number
        with self.assertRaises(AppException.ResourceExists):
            employee_data["email"] = "meeee@eg.com"
            self.employee_controller.create(employee_data)

    @mock.patch("app.producer.KafkaProducer")
    def test_request_password_reset(self, mock_kafka_producer):
        employee = self.create_employee()

        request_data = {"phone_number": employee.phone_number, "password": self.password}

        response = self.employee_controller.request_password_reset(request_data)

        # check if kafka publisher is fired
        assert mock_kafka_producer.is_called
        self.assertIn("id", response.value)

    @mock.patch("app.notifications.sms_notification_handler.publish_to_kafka")
    @mock.patch("app.controllers.employee_controller.utc.localize")
    def test_reset_password(self, mock_utc, mock_kafka_producer):
        mock_utc.side_effect = self.side_effect
        employee = self.create_employee()

        request_data = {"phone_number": employee.phone_number, "password": self.password}

        response = self.employee_controller.request_password_reset(request_data)

        token_id = response.value.get("id")

        arguments = mock_kafka_producer.call_args_list[0].args
        token = arguments[1].get("details").get("verification_code")

        response = self.employee_controller.reset_password(
            {"token_id": str(token_id), "new_password": "123444", "token": str(token)}
        )

        self.assertEqual(None, response.value)

    def side_effect(self, args):  # noqa
        return args

    @mock.patch("app.producer.KafkaProducer")
    def test_resend_token(self, mock_kafka_producer):
        employee = self.create_employee()

        request_data = {"phone_number": employee.phone_number, "password": self.password}

        response = self.employee_controller.request_password_reset(request_data)

        # check if kafka publisher is fired
        assert mock_kafka_producer.is_called
        token_id = response.value.get("id")
        new_response = self.employee_controller.resend_token(token_id)
        assert mock_kafka_producer.is_called

        self.assertIn("id", new_response.value)
