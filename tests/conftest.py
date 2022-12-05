import pytest
from werkzeug.security import generate_password_hash

from mensable import create_app, db
from mensable.models import *

@pytest.fixture
def app():
    app = create_app({'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': "sqlite:///:memory:"})

    with app.app_context():
        # Add dummy user to temporary test database
        user = User('testuser', generate_password_hash('testpwd'))
        db.session.add(user)
        # Add dummy language
        language = Language('Testese')
        db.session.add(language)
        # Add a dummy table
        # TODO: Use the actual API route here rather than trying to reproduce
        # the functionality!
        table = Table('Testtable')
        table.creator_id = 1
        table.language_id = 1
        db.session.add(table)
        db.session.commit()

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions(object):
    # Define default username and password
    username = "testuser"
    password = "testpwd"

    def __init__(self, client):
        self._client = client

    def register(self, username=username, password=password,
            confirmation=password):
        return self._client.post( "/register", data={"username": username,
            "password": password, "confirmation": confirmation})

    def login(self, username=username, password=password):
        return self._client.post( '/login', data={'username': username,
            'password': password})

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
