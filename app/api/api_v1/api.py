from .endpoints.distributor_view import distributor
from .endpoints.employee_view import employee


def init_app(app):
    """
    Register app blueprints over here
    eg: # app.register_blueprint(user, url_prefix="/api/users")
    :param app:
    :return:
    """

    app.register_blueprint(distributor, url_prefix="/api/v1/distributor")
    app.register_blueprint(employee, url_prefix="/api/v1/employee")
