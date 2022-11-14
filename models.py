from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Table containing information about users"""
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    tables = db.relationship('Table', backref='creator', lazy=True)

    def __init__(self, name, password_hash):
        self.name = name
        self.password_hash = password_hash


# Auxiliary table for tracking the many-to-many relationship between tables and
# word pairs.
words_in_tables = db.Table('words_in_tables',
        db.Column('word_pair_id', db.Integer, db.ForeignKey('word_pair.id')),
        db.Column('table_id', db.Integer, db.ForeignKey('table.id')))
        


class Table(db.Model):
    """Table to track tables (!) of word-translation pairs to learn"""
    id = db.Column("id", db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), unique=True)
    words = db.relationship('WordPair', secondary=words_in_tables,
            backref='contained_in')

    def __init__(self, name):
        self.name = name
    

class WordPair(db.Model):
    """Table containing word-translation pairs to learn"""
    td = db.Column("id", db.Integer, primary_key=True)
    #table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    foreignWord = db.Column(db.String(100))
    translation = db.Column(db.String(100))

    def __init__(self, foreignWord, translation):
        self.foreignWord = foreignWord
        self.translation = translation


