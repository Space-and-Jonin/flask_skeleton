import datetime
import uuid
from dataclasses import dataclass

from sqlalchemy.sql import func

from core.extensions import db


@dataclass
class Employee(db.Model):
    id: str
    first_name: str
    last_name: str
    phone_number: str
    email_address: str
    distributor_id: str
    create_secondary_user: bool
    create_retailer: bool
    created: datetime.datetime
    modified: datetime.datetime

    id = db.Column(db.GUID(), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone_number = db.Column(db.String, unique=True)
    email_address = db.Column(db.String, unique=True)
    distributor_id = db.Column(db.GUID, db.ForeignKey("distributor.id"), nullable=False)
    create_secondary_user = db.Column(db.Boolean, default=False)
    create_retailer = db.Column(db.Boolean, default=False)
    auth_service_id = db.Column(db.GUID())
    tokens = db.relationship(
        "Token", lazy="select", backref=db.backref("employee", lazy="select")
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
