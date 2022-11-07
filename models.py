
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Table containing information about users"""
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name


class WordPair(db.model):
    """Table containing word-translation pairs to learn"""
    _id = db.Column("id", db.Integer, primary_key=True)
    foreign = db.Column(db.String(100))
    translation = db.Column(db.String(100))

    def __init__(self, foreign, translation):
        self.foreign = foreign
        self.translation = translation
