from flask import flash, render_template, request, session, redirect, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from mensable.models import *

bp = Blueprint("auth", __name__)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        # Record username from login form
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            flash("Please enter a username.")
            return redirect("/login")
            
        if not password:
            flash("Please enter a password.")
            return redirect("/login")

        user = User.query.filter_by(name=username).first()
        if not user:
            flash("Username not recognized - try again or register for an account.")
            return redirect("/login")
        
        if not check_password_hash(user.password_hash, password):
            flash(f"Incorrect password for user {username}.")
            return redirect("/login")

        # NOTE the use of f-strings in lines like the above is probably a bit
        # of a security risk.

        session["user_id"] = user.id
        return redirect("/")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":

        username = request.form["username"]

        if not username.isalnum():
            flash("Please enter a valid alphanumeric username.")
            return redirect("/register")

        user_exists = User.query.filter_by(name=username).first()
        if user_exists:
            flash(f"Username taken.")
            return redirect("/register")

        password = request.form["password"]
        if not password:
            flash("Please enter a password.")
            return redirect("/register")

        if password != request.form["confirmation"]:
            flash("Password and confirmation must match.")
            return redirect("/register")

        password_hash = generate_password_hash(password)
        user = User(username, password_hash)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        flash(f"User {username} registered and logged in - welcome to Mensable.")
        return redirect("/")


@bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

