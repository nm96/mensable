import pytest
from flask import session
from werkzeug.datastructures import FileStorage

from mensable.models import *


def test_home(client, auth):
    # Log in and check that home page can be got
    auth.login()
    assert client.get('/').status_code == 200


def test_create_language(app, client, auth, api):
    auth.login()
    route = '/create_language'
    assert client.get(route).status_code == 200

    # Try a valid new language
    language_name = 'Newese'
    response = api.create_language(language_name)
    assert response.headers['Location'] == '/create_table/' + language_name
    with app.app_context():
        language = Language.query.filter_by(name=language_name).first()
        assert language is not None

    # Try an existing langauge
    response = api.create_language(language_name)
    assert response.headers['Location'] == route

    # Try an invalid language name
    language_name = "   *(&(& 9879 (&(&*(&*&*& "
    response = api.create_language(language_name)
    assert response.headers['Location'] == route
    with app.app_context():
        language = Language.query.filter_by(name=language_name).first()
        assert language is None


def test_create_table(app, client, auth, api):
    auth.login()
    route = f"/create_table/{api.language_name}"

    api.create_language()
    assert client.get(route).status_code == 200


    # Try a valid new table
    table_name = "Newtable"
    response = api.create_table(table_name)
    assert response.headers['Location'] == f"/edit_table/{api.language_name}/{table_name}"
    with app.app_context():
        table = Table.query.filter_by(name=table_name).first()
        assert table is not None

    # Try an existing table, check for redirect
    response = api.create_table(table_name)
    assert response.headers['Location'] == route

    # Try an invalid table name, check for redirect
    table_name = " &**(&(& 9*&(& "
    response = api.create_table(table_name)
    assert response.headers['Location'] == route
    with app.app_context():
        table = Table.query.filter_by(name=table_name).first()
        assert table is None


def test_edit_table(app, client, auth, api):
    route = f"/edit_table/{api.language_name}/{api.table_name}"
    auth.login()
    api.create_language()
    api.create_table()
    assert client.get(route).status_code == 200

    # Try adding a valid new word
    foreignWord, translation = "foo", "bar"
    response = api.add_word_pair(foreignWord, translation)
    assert response.headers['Location'] == route
    with app.app_context():
        word_pair = WordPair.query.filter_by(foreignWord=foreignWord,
                translation=translation).first()
        assert word_pair is not None

    invalid_word_pairs = [("", "Nothing"),
                          ("Nada", ""), 
                          (foreignWord, "baz")]

    for foreignWord, translation in invalid_word_pairs:
        api.add_word_pair(foreignWord, translation)
        assert response.headers['Location'] == route
        with app.app_context():
            word_pair = WordPair.query.filter_by(foreignWord=foreignWord,
                    translation=translation).first()
            assert word_pair is None


    # Register and log in as a different user, confirm that attempts to edit
    # redirect to "/tables".
    auth.logout()
    auth.register("new_user", "123", "123")
    response = client.get(route)
    assert response.headers['Location'] == "/tables"


def test_upload_csv(app, client, auth, api):
    route = f"/upload_csv/{api.language_name}/{api.table_name}"
    auth.login()
    api.create_language()
    api.create_table()
    assert client.get(route).status_code == 200
    csv_file = FileStorage(stream=open("tests/test_table.csv", "rb"))
    response = client.post(route, data={"csv_file": csv_file})
    assert response.headers['Location'] == f"/edit_table/{api.language_name}/{api.table_name}"
    with app.app_context():
        table = Table.query.filter_by(name=api.table_name).first()
        assert len(table.words) == 2
        # TODO: More thorough / clear testing of csv upload here.


def test_delete_word(app, client, auth, api):
    auth.login()
    route = f"/delete_word/{api.language_name}/{api.table_name}"

    # Create default word pair
    api.add_full_stack()
    with app.app_context():
        word_pair = WordPair.query.filter_by(foreignWord=api.foreignWord).first()

    # Now delete it
    response = client.post(route, data={'word_pair_id': word_pair.id})
    assert response.headers['Location'] == f"/edit_table/{api.language_name}/{api.table_name}"

    # Confirm it is no longer in database
    with app.app_context():
        word_pair = WordPair.query.filter_by(foreignWord=api.foreignWord).first()
        assert word_pair is None


def test_delete_table(app, client, auth, api):
    auth.login()
    route = f"/delete_table/{api.language_name}/{api.table_name}"
    api.add_full_stack()
    assert client.get(route).status_code == 200
    response = client.post(route)
    assert response.headers['Location'] == '/tables/Testese'
    with app.app_context():
        table = Table.query.filter_by(name=api.table_name).first()
        assert table is None


def test_view_table(client, auth, api):
    auth.login()
    route = f"/view_table/{api.language_name}/{api.table_name}"
    api.create_language()

    # First check nonexistent table redirects to home
    response = client.get('/view_table/{api.language_name}/Notatable')
    assert response.headers['Location'] == '/' 

    # Then check empty table redirects to edit
    api.create_table()
    response = client.get(route) 
    assert response.headers['Location'] == f"/edit_table/{api.language_name}/{api.table_name}"

    # Now populate table and check that page can be viewed
    api.add_word_pair()
    assert client.get(route).status_code == 200


def test_languages_and_tables(client, auth, api):
    auth.login()
    assert client.get('/languages').status_code == 200
    assert client.get('/tables').status_code == 200
    api.create_language()
    assert client.get(f"/tables/{api.language_name}").status_code == 200


def test_quiz(client, auth, api):
    auth.login()
    route = f"/quiz/{api.language_name}/{api.table_name}"
    api.add_full_stack()
    # Quiz should start with a redirect.
    assert client.get(route).status_code == 302
    # Get again to start the quiz.
    assert client.get(route).status_code == 200
