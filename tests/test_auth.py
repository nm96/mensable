import pytest
from flask import session

from mensable.models import User

def test_register(client, app):
    # Check that page appears on GET.
    assert client.get('/register').status_code == 200
    # Check that POST redirects appropriately.
    response = client.post('/register', data={'username': 'a', 'password': 'b',
        'confirmation': 'b'})
    assert response.headers['Location'] == '/'
    # Check that the user just registered can be found in the database.
    with app.app_context():
        user = User.query.filter_by(name='a').first()
    assert user is not None


def test_login(client, auth):
    # Check that page appears on GET.
    assert client.get('/login').status_code == 200
    # Check that POST redirects appropriately given valid login details.
    response = auth.login()
    assert response.headers['Location'] == '/'
    # Check that user is registered in session as logged in.
    with client:
        client.get('/')
        assert session['user_id'] == 1
    # Check that POST redirects appropriately given INVALID login details.
    invalid_logins = [('','test_pwd'),
                      ('test_user', ''), 
                      ('not_user', 'not_pwd'),
                      ('test_user', 'wrong_pwd')]
    for login in invalid_logins:
        response = auth.login(*login)
        assert response.headers['Location'] == '/login'




def test_logout(client, auth):
    # First log in
    auth.login()
    # Then log out and check that no user is registered in the session.
    with client:
        auth.logout()
        assert 'user_id' not in session
