from app.core.repository import SQLBaseRepository
from app.models import Employee


class EmployeeRepository(SQLBaseRepository):
    model = Employee
