import pytest
from flask import session

from mensable.models import *


def test_home(client, auth):
    # Log in and check that home page can be got
    auth.login()
    assert client.get('/').status_code == 200


def test_create_language(client, auth):
    route = '/create_language'
    auth.login()
    assert client.get(route).status_code == 200

    # Try a valid new language
    new_language_name = 'Newese'
    response = client.post(route, data={'language_name': new_language_name})
    assert response.headers['Location'] == '/create_table/' + new_language_name

    # Try an existing langauge
    response = client.post(route, data={'language_name': 'Testese'})
    assert response.headers['Location'] == route

    # Try an invalid language name
    response = client.post(route, data={'language_name': '  &^%%^% '})
    assert response.headers['Location'] == route


