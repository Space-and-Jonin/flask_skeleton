from functools import wraps
from flask import request

from app.core.exceptions.app_exceptions import AppException


def validator(schema):
    def validate_data(func):
        """
        A wrapper to validate data using marshmallow schema
        :param func: {function} the function to wrap around
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            errors = schema().validate(request.json)
            if errors:
                raise AppException.ValidationException(context=errors)

            return func(*args, **kwargs)

        return view_wrapper

    return validate_data
