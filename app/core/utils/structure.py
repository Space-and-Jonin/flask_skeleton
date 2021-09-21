from functools import wraps
from flask import request

from app.core.exceptions import AppException


def docs(**other_args):
    def struct(func):
        method = request.method
        input_schema = (
            other_args.get("input_schema").__name__
            if other_args.get("input_schema")
            else None
        )
        output_schema = (
            other_args.get("output_schema").__name__
            if other_args.get("output_schema")
            else None
        )

        responses = other_args.get("responses", default=[{200: "OK"}])
        output_description = other_args.get("output_description")
        input_description = other_args.get("input_description")
        tag = other_args.get("tag")

        # parameters = None

        # request_args = request.args.keys()
        #
        # for argument in request_args:
        #     if not parameters:
        #         parameters = argument
        #     else:
        #         parameters += ("\n" + argument)

        responses = None
        print(responses)

        func.__doc__ = f"""
        ---
        {method}:
          description: {input_description}
          requestBody:
            required: true
            content:
              application/json:
                schema: {input_schema}
          responses:
              200:
              description: {output_description}
              content:
                application/json:
                  schema: {output_schema}
          tags:
              - {tag}
        """

        @wraps(func)
        def view_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        def validator(input_schema):
            errors = input_schema().validate(request.json)
            if errors:
                raise AppException.ValidationException(context=errors)

        return view_wrapper

    return struct
