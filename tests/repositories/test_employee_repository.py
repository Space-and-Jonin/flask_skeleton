import secrets
from tests.utils.base_test_case import BaseTestCase


class TestEmployeeRepository(BaseTestCase):
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

    def test_get_employee_distributor_details(self):
        distributor = self.distributor_repository.create(self.distributor_data)

        employee_data = dict(self.employee_data)
        employee_data["distributor_id"] = distributor.id
        employee = self.employee_repository.create(employee_data)
        self.assertEqual(employee.distributor.name, self.distributor_data.get("name"))
