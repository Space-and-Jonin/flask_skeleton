from faker import Faker
from flask_sqlalchemy import SQLAlchemy


class Seeder:
    db: SQLAlchemy().Model
    fake: Faker

    @classmethod
    def run(cls):
        print("Seeding complete")
