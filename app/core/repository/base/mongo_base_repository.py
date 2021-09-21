import mongoengine
from app.core.exceptions.app_exceptions import AppException
from app.core.repository.base.crud_repository_interface import (
    CRUDRepositoryInterface,
)


class MongoBaseRepository(CRUDRepositoryInterface):
    """
    Base class to be inherited by all Mongo repositories. This class comes with
    base crud functionalities attached
    """

    model: mongoengine

    def index(self):
        return self.model.objects()

    def create(self, obj_in):
        """

        :param obj_in: the data you want to use to create the model
        :return: {object} - Returns an instance object of the model passed
        """
        assert obj_in, "Missing data to be saved"

        db_obj = self.model(**obj_in)
        db_obj.save()
        return db_obj

    def update_by_id(self, item_id, obj_in):
        """
        :param item_id: {int}
        :param obj_in: {dict}
        :return: model_object - Returns an instance object of the model passed
        """
        assert item_id, "Missing object id to update"
        assert obj_in, "No new data to update with"

        db_obj = self.find_by_id(item_id)
        db_obj.modify(**obj_in)
        return db_obj

    def find_by_id(self, obj_id):
        """
        returns a user if it exists in the database
        :param obj_id: int - id of the user
        :return: model_object - Returns an instance object of the model passed
        """

        assert obj_id, "Missing object id to find"

        try:
            db_obj = self.model.objects.get(pk=obj_id)
            return db_obj
        except mongoengine.DoesNotExist:
            raise AppException.NotFoundException(
                f"Resource of id {obj_id} does not exist"
            )

    def find(self, filter_param):
        """
        returns an item that satisfies the data passed to it if it exists in
        the database

        :param filter_param: {dict}
        :return: model_object - Returns an instance object of the model passed
        """

        assert filter_param, "Missing filter parameters"
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        try:
            db_obj = self.model.objects.get(**filter_param)
            return db_obj
        except mongoengine.DoesNotExist:
            raise AppException.NotFoundException("Resource does not exist")

    def find_all(self, filter_param):
        """
        returns all items that satisfies the filter params passed to it

        :param filter_param: {dict}
        :return: model_object - Returns an instance object of the model passed
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        db_obj = self.model.objects(**filter_param)
        return db_obj

    def delete(self, item_id):

        """

        :param item_id: id of the item that should be deleted
        :return:
        """

        assert item_id, "Missing id of object to be deleted"

        db_obj = self.find_by_id(item_id)
        db_obj.delete()
