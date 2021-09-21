from sqlalchemy.exc import DBAPIError

from app.core.exceptions import AppException
from app.core.repository import SQLBaseRepository
from app.models import Token


class TokenRepository(SQLBaseRepository):
    model = Token

    def current_token(self, employee_id):
        try:
            self.model.query.filter_by(employee_id=employee_id).order_by(
                "expiration desc"
            ).limit(1)
        except DBAPIError as e:
            raise AppException.OperationError(e.orig.args[0])
