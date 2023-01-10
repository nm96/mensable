import os    

from mensable import create_app

def test_config():
    # Artificially set database url environment variable.
    uri = "sqlite:///:memory:"
    os.environ["DATABASE_URL"] = uri
    # Create app in normal mode.
    assert not create_app().testing
    # Create app in testing mode.
    assert create_app({"TESTING": True, 
        "SQLALCHEMY_DATABASE_URI": uri}).testing
