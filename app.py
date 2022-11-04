from flask import Flask, flash, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"

# Set up database
db = SQLAlchemy(app)

Session(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=true)
    name = db.Coumn(db.String(100))
    email = db.Coumn(db.String(100))

    def __init__(name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("home.html")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
