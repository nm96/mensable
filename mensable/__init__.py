from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['SECRET_KEY'] = "dev"

    if not test_config:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db"
    else:
        app.config.from_mapping(test_config)

    from mensable import auth, api

    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
