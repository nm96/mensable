import pytest
from werkzeug.security import generate_password_hash

from mensable import create_app, db
from mensable.models import *

@pytest.fixture
def app():
    app = create_app({'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': "sqlite:///:memory:"})

    with app.app_context():
        # Add dummy user to database
        user = User('test', generate_password_hash('test'))
        db.session.add(user)
        db.session.commit()

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
