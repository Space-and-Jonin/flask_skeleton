import datetime
import uuid

from sqlalchemy import func

from app import db
from dataclasses import dataclass


@dataclass
class Token(db.Model):
    id: uuid.UUID
    token: str
    expiration: datetime.datetime
    employee_id: uuid.UUID
    created: datetime.datetime

    id = db.Column(db.GUID, primary_key=True, default=uuid.uuid4)
    token = db.Column(db.String(6), nullable=False)
    expiration = db.Column(db.DateTime(timezone=True), nullable=False)
    employee_id = db.Column(db.GUID, db.ForeignKey("employee.id"), nullable=False)
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
