import click
from flask import Flask


def init_app(app: Flask):
    @app.cli.command("map_roles")
    def map_roles():
        view_function_set = set()
        with app.test_request_context():
            for fn_name in app.view_functions:
                if fn_name == "static":
                    continue
                else:
                    view_function_set.add(fn_name)

        click.echo(view_function_set)
