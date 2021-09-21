import os
from flask_testing import TestCase
from app import create_app, db
from app.controllers import DistributorController, EmployeeController
from app.repositories import DistributorRepository, EmployeeRepository, TokenRepository
from config import Config
from tests.utils.mock_auth_service import MockAuthService


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app("config.TestingConfig")
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI="sqlite:///"
            + os.path.join(app.instance_path, "test.db?check_same_thread=False"),
        )
        self.distributor_repository = DistributorRepository()
        self.distributor_controller = DistributorController(
            distributor_repository=self.distributor_repository
        )

        self.employee_repository = EmployeeRepository()
        self.token_repository = TokenRepository()
        self.auth_service = MockAuthService()
        self.employee_controller = EmployeeController(
            employee_repository=self.employee_repository,
            token_repository=self.token_repository,
            auth_service=self.auth_service,
        )
        self.distributor_data = {
            "location": "second rangoon close, cantonments, accra",
            "name": "Quantum Distributor",
            "tin_number": "abc_iad",
        }
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa: E501
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.app_name = Config.APP_NAME
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        return app

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.drop_all()

    def dummy_kafka_method(self, notification, data):  # noqa
        return True

    def required_roles_side_effect(  # noqa
        self, token, key, algorithms, audience, issuer
    ):
        return {
            "realm_access": {
                "roles": [
                    f"{Config.APP_NAME}_create_employee",
                    f"{Config.APP_NAME}_update_employee",
                    f"{Config.APP_NAME}_show_employee",
                    f"{Config.APP_NAME}_delete_employee",
                    f"{Config.APP_NAME}_create_distributor",
                    f"{Config.APP_NAME}_get_distributor",
                    f"{Config.APP_NAME}_get_all_distributors",
                    f"{Config.APP_NAME}_delete_distributor",
                    f"{Config.APP_NAME}_update_distributor",
                ]
            },
        }

    def no_role_side_effect(self, token, key, algorithms, audience, issuer):  # noqa
        return {
            "realm_access": {"roles": []},
        }
