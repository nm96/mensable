from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from models import users, db
from helpers import login_required

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = "dummy_secret_key"

# Set up database
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
@login_required
def home():
    """Render homepage"""
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        # Record username from login form
        username = request.form["username"]
        # Log current username in session
        session["user"] = username
        # Check if username exists in database
        found_user = users.query.filter_by(name=username).first()
        if found_user:
            flash(f"hello again, {user}")
            return redirect("/")
        else:
            # If username is not in database, create new entry in users table
            # i.e. new 'users' object
            user_entry = users(user)
            db.session.add(user_entry)
            db.session.commit()
            flash(f"welcome to mensable, {session['user']}")
            return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


