import pytest
from flask import session

from mensable.models import User

def test_register(client, app):
    assert client.get('/register').status_code == 200
    response = client.post('/register', data={'username': 'a', 'password': 'b',
        'confirmation': 'b'})
    assert response.headers['Location'] == '/'
    with app.app_context():
        user = User.query.filter_by(name='a').first()
    assert user is not None


