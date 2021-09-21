from flask import Response, json, current_app
from sqlalchemy.exc import DBAPIError
from werkzeug.exceptions import HTTPException


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context):
        current_app.logger.error(context)
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code = {self.status_code} - context = {self.context}"
        )


def app_exception_handler(exc):
    if isinstance(exc, DBAPIError):
        return Response(
            json.dumps(
                {"app_exception": "Database Error", "errorMessage": exc.orig.pgerror}
            ),
            status=400,
        )
    if isinstance(exc, HTTPException):
        return Response(
            json.dumps({"app_exception": "HTTP Error", "errorMessage": exc.description}),
            status=exc.code,
        )
    return Response(
        json.dumps({"app_exception": exc.exception_case, "errorMessage": exc.context}),
        status=exc.status_code,
        mimetype="application/json",
    )


class AppException:
    class OperationError(AppExceptionCase):
        """
        Generic Exception to catch failed operations
        """

        def __init__(self, context):

            status_code = 500
            AppExceptionCase.__init__(self, status_code, context)

    class InternalServerError(AppExceptionCase):
        """
        Generic Exception to catch failed operations
        """

        def __init__(self, context):

            status_code = 500
            AppExceptionCase.__init__(self, status_code, context)

    class ResourceExists(AppExceptionCase):
        """
        Resource Creation Failed Exception
        """

        def __init__(self, context):

            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class NotFoundException(AppExceptionCase):
        def __init__(self, context="Resource not found"):
            """
            Resource does not exist
            """
            status_code = 404
            AppExceptionCase.__init__(self, status_code, context)

    class Unauthorized(AppExceptionCase):
        def __init__(self, context="Unauthorized", status_code=401):
            """
            Unauthorized
            :param context: extra dictionary object to give the error more context
            """
            AppExceptionCase.__init__(self, status_code, context)

    class ValidationException(AppExceptionCase):
        """
        Resource Creation Failed Exception
        """

        def __init__(self, context):

            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class KeyCloakAdminException(AppExceptionCase):
        def __init__(self, context=None, status_code=400):
            """
            Key Cloak Error. Error with regards to Keycloak authentication
            :param context: extra data to give the error more context
            """

            AppExceptionCase.__init__(self, status_code, context)

    class BadRequest(AppExceptionCase):
        def __init__(self, context=None):
            """
            Bad Request

            :param context:
            """
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class ExpiredTokenException(AppExceptionCase):
        def __init__(self, context=None):
            """
            Expired Token
            :param context:
            """

            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)
