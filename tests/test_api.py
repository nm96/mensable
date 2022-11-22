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


def test_create_table(client, auth):
    route = '/create_table/Testese'
    auth.login()
    assert client.get(route).status_code == 200

    # Try a valid new table
    response = client.post(route, data={'table_name': 'Newtable'})
    assert response.headers['Location'] == '/edit_table/Testese/Newtable'

    # Try an existing table
    response = client.post(route, data={'table_name': 'Testtable'})
    assert response.headers['Location'] == route

    # Try an invalid table name
    response = client.post(route, data={'table_name': '%&^&%&%'})
    assert response.headers['Location'] == route


def test_edit_table(client, auth):
    route = '/edit_table/Testese/Testtable'
    auth.login()
    assert client.get(route).status_code == 200

    # Try adding a valid new word
    response = client.post(route, data={'foreignWord': 'testo', 'translation':
        'test'})
    assert response.headers['Location'] == route
    # TODO: Check if word is actually in database (and do similar queries in
    # other tests)

    # Try adding invalid word pairs
    response = client.post(route, data={'foreignWord': '', 'translation':
        'test_translation'})
    assert response.headers['Location'] == route
    response = client.post(route, data={'foreignWord': 'wordo', 'translation': ''})
    assert response.headers['Location'] == route



