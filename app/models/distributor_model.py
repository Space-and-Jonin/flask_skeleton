import uuid
import datetime
from dataclasses import dataclass

from sqlalchemy.sql import func

from app import db


@dataclass
class Distributor(db.Model):
    id: str
    name: str
    location: str
    tin_number: str
    employees: list
    created: datetime.datetime
    modified: datetime.datetime

    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(), nullable=False, unique=True)
    location = db.Column(db.String(), nullable=False)
    tin_number = db.Column(db.String(), nullable=False)
    employees = db.relationship(
        "Employee", lazy=True, backref=db.backref("distributor", lazy="joined")
    )
    created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
