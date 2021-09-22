import os

from flask import Flask, jsonify

from .exceptions.setup_exceptions import DBConnectionException
from .formatter import default_handler
from flask_mongoengine import MongoEngine
from sqlalchemy.exc import DBAPIError
from .extensions import db, migrate, ma

from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import HTTPException
from .generators import init_generators

from .api_spec import spec
from .exceptions import (
    app_exception_handler,
    AppExceptionCase,
)

# SWAGGER
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Python-Flask-REST-Boilerplate"}
)


def initialize_instance(app: Flask):
    if not app or not isinstance(app, Flask):
        raise TypeError("Invalid Flask application instance")

    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "../app/instance")
    app.instance_path = path
    app.logger.addHandler(default_handler)
    # add extensions
    register_extensions(app)
    register_blueprints(app)
    register_swagger_definitions(app)


def register_extensions(flask_app):
    """Register Flask extensions."""
    from .factory import factory

    initialize_databases(flask_app)
    factory.init_app(flask_app, db)
    init_generators(flask_app)
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


def initialize_databases(flask_app):
    app = flask_app

    db_host = app.config.get("DB_HOST")
    db_name = app.config.get("DB_NAME")
    db_user = app.config.get("DB_USER")
    db_password = app.config.get("DB_PASSWORD")
    db_port = app.config.get("DB_PORT")
    db_engine = app.config.get("DB_ENGINE")

    assert db_engine, "DB_ENGINE not specified"

    db_engine = db_engine.lower()

    if db_engine == "mongodb":
        mongo_db_params = {
            "MONGODB_DB": db_name,
            "MONGODB_PORT": int(db_port) if db_port else 27017,
            "MONGODB_USERNAME": db_user,
            "MONGODB_PASSWORD": db_password,
            "MONGODB_CONNECT": False,
        }
        app.config.from_mapping(**mongo_db_params)
        me = MongoEngine()
        me.init_app(flask_app)
    else:
        db_engine_port_map = {
            "postgres": ("postgresql+psycopg2", int(db_port) if db_port else 5432),
            "mysql": ("mysql+pymysql", int(db_port) if db_port else 3306),
            "oracle": ("oracle+cx_oracle", int(db_port) if db_port else 1521),
            "mssql": ("mssql+pymssql", int(db_port) if db_port else 1433),
            "sqlite": ("sqlite", None),
        }

        if db_engine not in db_engine_port_map:
            raise DBConnectionException(f"{db_engine} connection is not supported")

        db_details = db_engine_port_map.get(db_engine)

        engine_url_prefix = db_details[0]
        db_port = db_details[1]
        db_url = generate_db_url(
            engine_url_prefix, db_host, db_user, db_password, db_port, db_name
        )

        app.config.from_mapping(SQLALCHEMY_DATABASE_URI=db_url)
        db.init_app(flask_app)
        migrate.init_app(flask_app, db)
        with flask_app.app_context():
            db.create_all()


def generate_db_url(
    engine_prefix, db_host, db_user, db_password, db_port, db_name
):  # noqa
    if engine_prefix == "sqlite":
        return f"sqlite:///{db_name}"

    return (
        "{engine_prefix}://{db_user}:{password}@{host}:{port}/{db_name}".format(  # noqa
            engine_prefix=engine_prefix,
            db_user=db_user,
            host=db_host,
            password=db_password,
            port=db_port,
            db_name=db_name,
        )
    )


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
