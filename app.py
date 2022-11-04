from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


# Configure application
app = Flask(__name__)
app.secret_key = "abcdefg"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
db = SQLAlchemy(app)


class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

with app.app_context():
    db.create_all()

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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

