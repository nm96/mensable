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
        user = User("testuser", generate_password_hash("testpwd"))
        db.session.add(user)
        db.session.commit()
        # Add dummy language
        #language = Language('Testese')
        #db.session.add(language)
        # Add a dummy table
        # TODO: Use the actual API route here rather than trying to reproduce
        # the functionality!
        #table = Table('Testtable')
        #table.creator_id = 1
        #table.language_id = 1
        #db.session.add(table)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions(object):

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


class APIActions(object):

    language_name = "Testese"
    table_name = "TestTable"
    foreignWord, translation = "Testo", "Test"

    def __init__(self, client):
        self._client = client

    def create_language(self, language_name=language_name):
        return self._client.post("/create_language", data={"language_name":
            language_name})

    def create_table(self, table_name=table_name, language_name=language_name):
        route =  f"/create_table/{language_name}"
        return self._client.post(route, data={"table_name": table_name})

    def add_word_pair(self, 
            foreignWord=foreignWord,
            translation=translation,
            language_name=language_name,
            table_name=table_name): 
        route =  f"/edit_table/{language_name}/{table_name}"
        return self._client.post(route, data={"foreignWord": foreignWord,
            "translation": translation})

    def add_full_stack(self, 
            foreignWord=foreignWord,
            translation=translation,
            language_name=language_name,
            table_name=table_name): 
        """Add a word pair along with a table and language to contain it."""
        self.create_language(language_name=language_name)
        self.create_table(table_name=table_name, 
                          language_name=language_name)
        self.add_word_pair(foreignWord=foreignWord,
                           translation=translation, 
                           table_name=table_name, 
                           language_name=language_name)
        
    def quiz_response(self, answer=translation, table_name=table_name,
            language_name=language_name):
        route =  f"/quiz/{language_name}/{table_name}"
        return self._client.post(route, data={"answer": answer})


@pytest.fixture
def api(client):
    return APIActions(client)

