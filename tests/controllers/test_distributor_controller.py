from app.core.exceptions import AppException
from tests.utils.base_test_case import BaseTestCase


class TestDistributorController(BaseTestCase):
    def test_create(self):
        distributor = self.distributor_controller.create(self.distributor_data)
        self.assertEqual(self.distributor_data.get("name"), distributor.value.name)

    def test_throw_create_error(self):
        with self.assertRaises(AssertionError):
            self.distributor_controller.create({})

        with self.assertRaises(AppException.OperationError):
            self.distributor_controller.create({"tin_number": "abc_iad"})

    def test_throw_exists_exception(self):
        self.distributor_controller.create(self.distributor_data)

        with self.assertRaises(AppException.ResourceExists):
            self.distributor_controller.create(self.distributor_data)

    def test_update(self):
        distributor = self.distributor_repository.create(self.distributor_data)
        new_tin = "adsk493"
        updated_distributor = self.distributor_controller.update(
            distributor.id, {"tin_number": new_tin}
        )

        self.assertEqual(new_tin, updated_distributor.value.tin_number)

    def test_get(self):
        """
        Encapsulates both find one and find all
        """
        self.distributor_repository.create(self.distributor_data)
        distributor = self.distributor_repository.create(
            {
                "location": "second rangoon close, cantonments, accra",
                "name": "sage",
                "tin_number": "abc_iad",
            }
        )
        distributors = self.distributor_controller.index()
        self.assertIsInstance(distributors.value, list)
        self.assertEqual(len(distributors.value), 2)

        distributor_search = self.distributor_controller.show(distributor.id)
        self.assertEqual(distributor_search.value.name, "sage")

    def test_delete(self):
        distributor = self.distributor_repository.create(self.distributor_data)
        self.distributor_controller.delete(distributor.id)

        with self.assertRaises(AppException.NotFoundException):
            self.distributor_controller.show(distributor.id)
