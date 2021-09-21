import os

from flask import Flask
from core import init_app
from werkzeug.utils import import_string

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, ".env")


def create_app(config="config.DevelopmentConfig"):
    """Construct the core application"""

    app = Flask(__name__, instance_relative_config=False)
    with app.app_context():
        environment = os.getenv("FLASK_ENV")
        cfg = import_string(config)()
        if environment == "production":
            cfg = import_string("config.ProductionConfig")()
        app.config.from_object(cfg)

        init_app(app)
        return app
