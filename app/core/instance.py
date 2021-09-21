import os
import logging

from flask import Flask, jsonify, has_request_context, request
from flask.logging import default_handler
from flask_mongoengine import MongoEngine
from sqlalchemy.exc import DBAPIError
from .extensions import db, migrate, ma

from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import HTTPException

from .api_spec import spec
from .exceptions.app_exceptions import (
    app_exception_handler,
    AppExceptionCase,
)

# SWAGGER
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Python-Flask-REST-Boilerplate"}
)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
    "%(levelname)s in %(module)s: %(message)s"
)
default_handler.setFormatter(formatter)
default_handler.setLevel(logging.ERROR)
default_handler.setLevel(logging.INFO)


def initialize_instance(app: Flask):
    if not app or not isinstance(app, Flask):
        raise TypeError("Invalid Flask application instance")

    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "../instance")
    app.instance_path = path
    app.logger.addHandler(default_handler)
    # add extensions
    register_extensions(app)
    register_blueprints(app)
    register_swagger_definitions(app)


def register_extensions(flask_app):
    """Register Flask extensions."""
    # from app.core.factory import factory

    if flask_app.config["DB_ENGINE"] == "MONGODB":
        me = MongoEngine()
        me.init_app(flask_app)
    elif flask_app.config["DB_ENGINE"] == "POSTGRES":
        db.init_app(flask_app)
        migrate.init_app(flask_app, db)
        with flask_app.app_context():
            db.create_all()
    # factory.init_app(flask_app, db)
    ma.init_app(flask_app)

    @flask_app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return app_exception_handler(e)

    @flask_app.errorhandler(DBAPIError)
    def handle_db_exception(e):
        return app_exception_handler(e)

    @flask_app.errorhandler(AppExceptionCase)
    def handle_app_exceptions(e):
        return app_exception_handler(e)

    return None


def register_blueprints(app):
    from app.api.api_v1 import api

    """Register Flask blueprints."""
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    api.init_app(app)
    return None


def register_swagger_definitions(app):
    with app.test_request_context():
        for fn_name in app.view_functions:
            if fn_name == "static":
                continue
            print(f"Loading swagger docs for function: {fn_name}")
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    @app.route("/static/swagger.json")
    def create_swagger_spec():
        """
        Swagger API definition.
        """
        return jsonify(spec.to_dict())
