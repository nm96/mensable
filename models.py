from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Table containing information about users"""
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tables = db.relationship('Table', backref='creator', lazy=True)

    def __init__(self, name):
        self.name = name


class Table(db.Model):
    """Table to track tables (!) of word-translation pairs to learn"""
    id = db.Column("id", db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    words = db.relationship('WordPair', backref='table', lazy=True)

    def __init__(self, name):
        self.name = name
    

class WordPair(db.Model):
    """Table containing word-translation pairs to learn"""
    id = db.Column("id", db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    foreignWord = db.Column(db.String(100))
    translation = db.Column(db.String(100))

    def __init__(self, foreignWord, translation):
        self.foreignWord = foreignWord
        self.translation = translation


