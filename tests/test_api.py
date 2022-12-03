import pytest
from flask import session

from mensable.models import *


def test_home(client, auth):
    # Log in and check that home page can be got
    auth.login()
    assert client.get('/').status_code == 200


def test_create_language(app, auth, client):
    route = '/create_language'
    auth.login()
    assert client.get(route).status_code == 200

    # Try a valid new language
    new_language_name = 'Newese'
    response = client.post(route, data={'language_name': new_language_name})
    assert response.headers['Location'] == '/create_table/' + new_language_name
    with app.app_context():
        language = Language.query.filter_by(name=new_language_name).first()
        assert language is not None

    # Try an existing langauge
    response = client.post(route, data={'language_name': 'Testese'})
    assert response.headers['Location'] == route

    # Try an invalid language name
    response = client.post(route, data={'language_name': '  &^%%^% '})
    assert response.headers['Location'] == route


def test_create_table(app, auth, client):
    auth.login()

    # Now use a route where we specify the language
    route = '/create_table/Testese'
    assert client.get(route).status_code == 200

    # Try a valid new table
    response = client.post(route, data={'table_name': 'Newtable'})
    assert response.headers['Location'] == '/edit_table/Testese/Newtable'
    with app.app_context():
        table = Table.query.filter_by(name='Newtable').first()
        assert table is not None

    # Try an existing table, check for redirect
    response = client.post(route, data={'table_name': 'Testtable'})
    assert response.headers['Location'] == route

    # Try an invalid table name, check for redirect
    response = client.post(route, data={'table_name': '%&^&%&%'})
    assert response.headers['Location'] == route


def test_edit_table(app, auth, client):
    route = '/edit_table/Testese/Testtable'
    auth.login()
    assert client.get(route).status_code == 200

    # Try adding a valid new word
    response = client.post(route, data={'foreignWord': 'testo', 'translation':
        'test'})
    assert response.headers['Location'] == route
    with app.app_context():
        word_pair = WordPair.query.filter_by(foreignWord='testo').first()
        assert word_pair is not None

    # Try adding invalid word pairs
    response = client.post(route, data={'foreignWord': '', 'translation':
        'test_translation'})
    assert response.headers['Location'] == route
    response = client.post(route, data={'foreignWord': 'wordo', 'translation': ''})
    assert response.headers['Location'] == route


def test_delete_word(app, auth, client):
    auth.login()
    route = '/delete_word/Testese/Testtable'

    # First create a word to delete using /edit_table (TODO - put this in
    # conftest for consistency?)
    client.post('/edit_table/Testese/Testtable', data={'foreignWord': 'testo', 'translation':
        'test'})

    # Now delete it
    response = client.post(route, data={'word_pair_id': 1})
    assert response.headers['Location'] == '/edit_table/Testese/Testtable'
    with app.app_context():
        word_pair = WordPair.query.filter_by(foreignWord='testo').first()
        assert word_pair is None



def test_view_table(auth, client):
    auth.login()
    route = '/view_table/Testese/Testtable'

    # First check nonexistent table redirects to home
    response = client.get('/view_table/Testese/Notatable')
    assert response.headers['Location'] == '/' 

    # Then check empty table redirects to edit
    response = client.get(route) 
    assert response.headers['Location'] == '/edit_table/Testese/Testtable'

    # Now populate table and check that page can be viewed
    client.post('/edit_table/Testese/Testtable', data={'foreignWord': 'testo', 'translation':
        'test'})
    assert client.get(route).status_code == 200


def test_tables(auth, client):
    auth.login()
    assert client.get('/tables').status_code == 200
    assert client.get('/tables/Testese').status_code == 200


def test_languages(auth, client):
    auth.login()
    assert client.get('/languages').status_code == 200


def test_quiz(auth, client):
    auth.login()
    route = '/quiz/Testese/Testtable'
    client.post('/edit_table/Testese/Testtable', data={'foreignWord': 'testo', 'translation':
        'test'})
    # Quiz should start with a redirect.
    assert client.get(route).status_code == 302
    # Get again to start the quiz.
    assert client.get(route).status_code == 200
