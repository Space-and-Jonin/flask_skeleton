from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from app.core.utils import GUID


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
db.__setattr__("GUID", GUID)
