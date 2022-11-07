from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db
from helpers import login_required

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
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
        # Check if username exists in database
        found_user = User.query.filter_by(name=username).first()
        if found_user:
            session["user_id"] = found_user.id
            flash(f"hello again, {username}")
            return redirect("/")
        else:
            # If username is not in database, raise error and redirect
            flash(f"Error: user {username} not in database, please register.")
            return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        # Check if username exists in database
        found_user = User.query.filter_by(name=username).first()
        if found_user:
            flash(f"User {username} already registered!")
            return redirect("/login")
        else:
            # If username is not in database, create new entry in users table
            # i.e. new 'User' object
            user_entry = User(username)
            db.session.add(user_entry)
            db.session.commit()
            flash(f"welcome to mensable, {username}")
            return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/create_table")
@login_required
def create_table():
    """Create a new word table to learn"""
    if request.method == "GET":
        return render_template("create_table.html")
    elif request.method == "POST":
        table_name = request.form["table_name"]
        table = Table(table_name)
        table.creator_id = session["user_id"]
        return redirect("/edit_table", table)


@app.route("/edit_table")
@login_required
def edit_table():
    """Edit an existing word table"""
    if request.method == "GET":
        return render_template("edit_table.html")
    elif request.method == "POST":
        pass
    


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


