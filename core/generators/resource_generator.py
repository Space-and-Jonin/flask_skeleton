import os
import pathlib
import click
from flask import Flask
from flask.cli import AppGroup
from jinja2 import Template


def init_generators(app: Flask):
    gen_cli = AppGroup("generate")

    @gen_cli.command("repository")
    @click.argument("name")
    def generate_repository(name: str):
        create_repository(name)

    @gen_cli.command("model")
    @click.argument("name")
    def generate_model(name: str):
        create_model(name)

    @gen_cli.command("controller")
    @click.argument("name")
    def generate_controller(name: str):
        create_controller(name)

    def create_controller(name):
        file_dir = os.path.join(app.root_path, "controllers")
        root_dir_name = os.path.basename(app.root_path)
        if not os.path.exists(file_dir):
            pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
        file_name = f"{name}_controller.py"
        model_name = name.capitalize()
        repository_file_name = f"{name}_repository"
        repository_class_name = f"{model_name}Repository"

        template_details = {
            "repository_file_name": repository_file_name,
            "repository_class_name": repository_class_name,
            "root_dir_name": root_dir_name,
            "model_name": model_name,
        }
        template_string = """from {{root_dir_name}}.repositories.{{repository_file_name}} import {{repository_class_name}}
from core import Result

class {{model_name}}Controller:

    def index(self):
        pass

    def create(self, data):
        pass

    def show(item_id):
        pass

    def update(item_id, data):
        pass

    def delete(item_id):
        pass

        """

        template = Template(template_string)
        data = template.render(**template_details)
        file = os.path.join(file_dir, file_name)
        if not os.path.exists(file):
            with open(file, "w") as w:
                w.write(data)
            add_to_init(file_dir, f"{name}_controller", f"{name.capitalize()}Controller")

    def create_model(name):
        file_dir = os.path.join(app.root_path, "models")
        if not os.path.exists(file_dir):
            pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
        file_name = f"{name}_model.py"
        model_name = name.capitalize()

        template_string = """from core.extensions import db
from dataclasses import dataclass


@dataclass
class {{model_name}}(db.Model):
    pass

"""
        template = Template(template_string)
        data = template.render(model_name=model_name)
        file = os.path.join(file_dir, file_name)
        if not os.path.exists(file):
            with open(file, "w") as w:
                w.write(data)

            add_to_init(file_dir, f"{name}_model", model_name)
        else:
            click.echo(f"{name}_model.py exits")

    def create_repository(name):
        file_dir = os.path.join(app.root_path, "repositories")
        if not os.path.exists(file_dir):
            pathlib.Path(file_dir).mkdir(parents=True, exist_ok=True)
        file_name = f"{name}_repository.py"
        model_name = name.capitalize()
        template_string = """from core.repository import SQLBaseRepository
from app.models import {{model_name}}

class {{model_name}}Repository(SQLBaseRepository):
    model = {{model_name}}

"""
        template = Template(template_string)
        data = template.render(model_name=model_name)
        file = os.path.join(file_dir, file_name)
        if not os.path.exists(file):
            with open(file, "w") as w:
                w.write(data)
            add_to_init(file_dir, f"{name}_repository", f"{name.capitalize()}Repository")
        else:
            click.echo(f"{name}_repository.py exists")

        click.echo(f"{name.capitalize()}Repository created successfully")

    def add_to_init(dir_path, file_name, class_name):
        with open(os.path.join(dir_path, "__init__.py"), "a") as w:
            w.write(f"from .{file_name} import {class_name}")

    app.cli.add_command(gen_cli)
