from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from models import users, db
from helpers import login_required

# Configure application
app = Flask(__name__)
app.secret_key = "abcdefg"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
db.init_app(app)

with app.app_context():
    db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user = request.form["username"]
        session["user"] = user
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            flash(f"hello again, {user}")
            return redirect("/")
        else:
            user_entry = users(user)
            db.session.add(user_entry)
            db.session.commit()
            flash(f"welcome, {user}")
            return redirect("/")

