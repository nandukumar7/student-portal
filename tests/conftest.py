import pytest
from app import app
from databases.db import db


@pytest.fixture
def client():

    app.config["TESTING"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():

        db.create_all()

        with app.test_client() as client:
            yield client

        db.drop_all()