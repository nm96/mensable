import pytest
from flask import session

from mensable.models import *


def test_login_required(client):
    # Check that going to / without logging in redirects to /login.
    response = client.get("/")
    assert response.headers["Location"] == "/login"


def test_login(client, auth):
    # Check that login page appears on GET.
    assert client.get("/login").status_code == 200
    
    # Check that POST redirects appropriately given valid login details.
    response = auth.login()
    assert response.headers["Location"] == "/"

    # Check that user is registered in session as logged in.
    with client:
        client.get("/")
        assert session["user_id"] == 1

    # Check that POST redirects appropriately given INVALID login details.
    invalid_logins = [("","testpwd"),
                      ("testuser", ""), 
                      ("notuser", "notpwd"),
                      (f"{auth.username}", "wrongpwd")]

    for login in invalid_logins:
        response = auth.login(*login)
        assert response.headers["Location"] == "/login"


def test_register(client, app, auth):
    # Check that page appears on GET.
    assert client.get("/register").status_code == 200
    
    # Define credentials to use.
    username, password = "new_user", "new_password"

    # Register using fixture
    response = auth.register(username, password, password)
    assert response.headers["Location"] == "/"

    # Check that the user just registered can be found in the database.
    with app.app_context():
        user = User.query.filter_by(name=username).first()
        assert user is not None

    # Check that POST redirects appropriately for invalid registration details.
    invalid_registrations = [(" *)^ ", "newpwd", "newpwd"),
                             ("testuser", "testpwd", "testpwd"),
                             ("newuser2", "", ""),
                             ("newuser3", "newpwd", "wrongpwd")]

    for registration in invalid_registrations:
        response = auth.register(*registration)
        assert response.headers["Location"] == "/register"

    with app.app_context():
        user = User.query.filter_by(name="newuser2").first()
        assert user is None
        user = User.query.filter_by(name="newuser3").first()
        assert user is None


def test_logout(client, auth):
    # First log in
    auth.login()

    # Then log out and check that no user is registered in the session.
    with client:
        auth.logout()
        assert "user_id" not in session
