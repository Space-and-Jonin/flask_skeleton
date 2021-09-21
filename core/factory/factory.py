import click
from flask import Flask
from faker import Faker
from . import Seeder
from app import factory

__all__ = ("factory",)


def init_app(app: Flask, db):
    @app.cli.command("db_seed")
    @click.option("--model", "-m", "model")
    @click.option("--cycle", "-c", "cycle")
    def db_seed(model, cycle):
        count = 1
        if cycle:
            count = int(cycle)

        print("migrating models")
        run_seeder(count, model, db)


def run_seeder(count, model, db):
    for _ in range(count):
        if model is None:
            for subclass in Seeder.__subclasses__():
                migrate(subclass, db)
        else:
            for subclass in Seeder.__subclasses__():
                if model.lower() == subclass.__name__.lower()[:-7]:
                    migrate(subclass, db)
        Seeder.run()


def migrate(factory_class, db):
    fake = Faker()
    factory_class.db = db
    factory_class.fake = fake
    factory_class.run()
