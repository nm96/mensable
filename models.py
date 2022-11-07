
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name


class Words(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
