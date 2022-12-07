from datetime import date

from mensable import db


class User(db.Model):
    """Basic information about user accounts"""
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    tables = db.relationship('Table', backref='creator', lazy=True)
    subscriptions = db.relationship('Subscription', backref='learner',
            lazy=True)

    def __init__(self, name, password_hash):
        self.name = name
        self.password_hash = password_hash

    def check_name(self):
        # Allow usernames to contain only letters, numbers and underscores.
        for c in self.name:
            if not (c.isalnum() or c == "_"):
                return False
        return True


class Language(db.Model):
    """Top-level category for word tables. Could be an actual language or
    something like 'IT acronyms' or 'Tree species'."""
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    tables = db.relationship('Table', backref='language', lazy=True)
    words = db.relationship('WordPair', backref='language', lazy=True)

    def __init__(self, name):
        self.name = name

    def check_name(self):
        # Allow language names to contain only letters and spaces.
        for c in self.name:
            if not (c.isalpha() or c == " "):
                return False
        return True


class Subscription(db.Model):
    """Tracks which Tables a User is learning and what the current state of
    their knowledge is via the Leitner system."""
    id = db.Column("id", db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    leitner_boxes = db.Column(db.PickleType)
    last_quiz_results = db.Column(db.PickleType)
    quiz_attempts = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    total_right = db.Column(db.Integer)
    average_percentage_score = db.Column(db.Integer)
    last_quiz_date = db.Column(db.String)
    subscription_date = db.Column(db.String, default=date.today)

    def __init__(self, learner, table):
        self.learner_id = learner.id
        self.table_id = table.id
        self.leitner_boxes = {}
        self.last_quiz_results = {}
        self.quiz_attempts = 0
        self.total_questions = 0
        self.total_right = 0
        self.last_quiz_date = date.today()


# Helper table for keeping track of which WordPairs are in which Tables
table_word_pair = db.Table('table_word_pair',
        db.Column('word_pair_id', db.Integer, db.ForeignKey('word_pair.id')),
        db.Column('table_id', db.Integer, db.ForeignKey('table.id')))
        

class Table(db.Model):
    """The fundamental objects in mensABLE - basically they are lists of
    word-translation pairs to learn."""
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    words = db.relationship('WordPair', secondary=table_word_pair,
            backref='contained_in')
    subscriptions = db.relationship('Subscription', backref='table')
    created = db.Column(db.String(20), default=date.today)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))

    def __init__(self, name):
        self.name = name

    def check_name(self):
        # Allow table names to contain only letters, numbers and spaces.
        for c in self.name:
            if not (c.isalnum() or c == " "):
                return False
        return True
    

class WordPair(db.Model):
    """A word in a foreign language/category and its translation/english
    definition."""
    id = db.Column("id", db.Integer, primary_key=True)
    foreignWord = db.Column(db.String(100))
    translation = db.Column(db.String(100))
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))

    def __init__(self, foreignWord, translation):
        self.foreignWord = foreignWord
        self.translation = translation


