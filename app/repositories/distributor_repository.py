from core.repository import SQLBaseRepository
from app.models import Distributor


class DistributorRepository(SQLBaseRepository):
    model = Distributor

    def get_distributor_employees(self, distributor_id):
        return super().find_by_id(distributor_id).employees
