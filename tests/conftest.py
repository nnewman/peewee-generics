import os

import pytest

from examples.todo_app import create_app, database
from .provider import faker_instance


@pytest.fixture(scope='session', autouse=True)
def app():
    """
    Create an app for the test scope and up a sample database
    """
    yield create_app()
    os.remove('./todo.db')


@pytest.fixture(scope='function', autouse=True)
def db(app):
    """Rollback database state between individual tests"""
    with database.atomic() as transaction:
        yield database
        transaction.rollback()


@pytest.fixture(scope='session')
def faker():
    """Faker instance"""
    return faker_instance
