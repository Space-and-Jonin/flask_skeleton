from sqlalchemy.exc import IntegrityError, DBAPIError
from app import db

from app.core.exceptions.app_exceptions import AppException
from app.core.repository.base.crud_repository_interface import (
    CRUDRepositoryInterface,
)


class SQLBaseRepository(CRUDRepositoryInterface):
    model: db.Model

    def __init__(self):
        """
        Base class to be inherited by all repositories. This class comes with
        base crud functionalities attached

        :param model: base model of the class to be used for queries
        """

        self.db = db

    def index(self) -> [db.Model]:
        """

        :return: {list} returns a list of objects of type model
        """
        try:
            data = self.model.query.all()
            return data

        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])

    def create(self, obj_in) -> db.Model:
        """

        :param obj_in: the data you want to use to create the model
        :return: {object} - Returns an instance object of the model passed
        """
        assert obj_in, "Missing data to be saved"

        try:
            obj_data = dict(obj_in)
            db_obj = self.model(**obj_data)
            self.db.session.add(db_obj)
            self.db.session.commit()
            return db_obj
        except IntegrityError as e:
            raise AppException.OperationError(e.orig.args[0])

    def update_by_id(self, obj_id, obj_in) -> db.Model:
        """
        :param obj_id: {int} id of object to update
        :param obj_in: {dict} update data. This data will be used to update
        any object that matches the id specified
        :return: model_object - Returns an instance object of the model passed
        """
        assert obj_id, "Missing id of object to update"
        assert obj_in, "Missing update data"
        assert isinstance(obj_in, dict), "Update data should be a dictionary"

        db_obj = self.find_by_id(obj_id)
        if not db_obj:
            raise AppException.NotFoundException(
                f"Resource of id {obj_id} does not exist"
            )
        try:
            for field in obj_in:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_in[field])
            self.db.session.add(db_obj)
            self.db.session.commit()
            return db_obj
        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])

    def find_by_id(self, obj_id) -> db.Model:
        """
        returns an object matching the specified id if it exists in the database
        :param obj_id: id of object to query
        :return: model_object - Returns an instance object of the model passed
        """
        assert obj_id, "Missing id of object for querying"

        try:
            db_obj = self.model.query.get(obj_id)
            if db_obj is None:
                raise AppException.NotFoundException()
            return db_obj

        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])

    def find(self, filter_param: dict) -> db.Model:
        """
        This method returns the first object that matches the query parameters specified
        :param filter_param {dict}. Parameters to be filtered by
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        try:
            db_obj = self.model.query.filter_by(**filter_param).first()
            return db_obj
        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])

    def find_all(self, filter_param) -> db.Model:
        """
        This method returns all objects that matches the query
        parameters specified
        """
        assert filter_param, "Missing filter parameters"
        assert isinstance(
            filter_param, dict
        ), "Filter parameters should be of type dictionary"

        try:
            db_obj = self.model.query.filter_by(**filter_param).all()
            return db_obj

        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])

    def delete(self, obj_id):

        """
        :param obj_id:
        :return:
        """

        db_obj = self.find_by_id(obj_id)
        try:
            if not db_obj:
                raise AppException.NotFoundException()
            db.session.delete(db_obj)
            db.session.commit()

        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])
