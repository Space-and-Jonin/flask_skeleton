from flask import current_app as app
from app.core.exceptions import AppException
from app.core.result import Result
from app.repositories.distributor_repository import DistributorRepository


class DistributorController:
    def __init__(self, distributor_repository: DistributorRepository):
        self.repository = distributor_repository

    def create(self, data):
        name = data.get("name")

        existing_distributor = self.repository.find({"name": name})
        if existing_distributor:
            app.logger.info(f"Distributor with name {name} exists")
            raise AppException.ResourceExists(f"Distributor with name {name} exists")
        distributor = self.repository.create(data)
        return Result(distributor, 201)

    def update(self, distributor_id, data):
        distributor = self.repository.update_by_id(distributor_id, data)
        return Result(distributor, 200)

    def show(self, distributor_id):
        distributor = self.repository.find_by_id(distributor_id)
        return Result(distributor, 200)

    def index(self):
        distributors = self.repository.index()
        return Result(distributors, 200)

    def delete(self, distributor_id):
        self.repository.delete(distributor_id)
        return Result(None, 204)
