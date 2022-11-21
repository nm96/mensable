from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from models import *
from helpers import login_required


@app.route("/")
@login_required
def home():
    """Render homepage"""
    user = User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return redirect("/login")
    return render_template("home.html", username=user.name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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


@app.route("/register", methods=["GET", "POST"])
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


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/create_language", methods=["GET", "POST"])
@login_required
def create_language():
    
    if request.method == "GET":
        return render_template("create_language.html")

    elif request.method == "POST":
        language_name = request.form["language_name"]

        if not language_name.isalnum():
            flash("Language name can only contain alphanumeric characters.")
            return redirect("/create_language")

        existing_language = Language.query.filter_by(name=language_name).first()
        if existing_language:
            flash(f"Language {language_name} already exists.")
            return redirect("/create_language")

        language = Language(language_name)
        db.session.add(language)
        db.session.commit()
        return redirect("/create_table/" + language_name)


@app.route("/create_table/<language_name>", methods=["GET", "POST"])
@login_required
def create_table(language_name):
    """Create a new word table to learn"""

    language = Language.query.filter_by(name=language_name).first()
    
    if request.method == "GET":
        return render_template("create_table.html", language=language)

    elif request.method == "POST":
        table_name = request.form["table_name"]

        if not table_name.isalnum():
            flash("Table name can only contain alphanumeric characters.")
            return redirect(f"/create_table/{language_name}")

        existing_table = Table.query.filter_by(name=table_name).first()
        if existing_table:
            flash(f"Table {table_name} already exists.")
            return redirect(f"/create_table/{language_name}")

        table = Table(table_name)
        table.creator_id = session["user_id"]
        table.language_id = language.id
        db.session.add(table)
        db.session.commit()
        return redirect(f"/edit_table/{language_name}/{table_name}")


@app.route("/edit_table/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def edit_table(language_name, table_name):
    """Edit an existing word table"""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()

    if request.method == "GET":
        return render_template("edit_table.html", language=language, table=table)

    elif request.method == "POST":
        # Get word and translation from input form.
        foreignWord = request.form["foreignWord"]
        translation = request.form["translation"]
        # Tidy them up by removing spaces at start and end.
        foreignWord = foreignWord.strip()
        translation = translation.strip()
        # Check if words are (still) non-empty
        if not foreignWord or not translation:
            flash("please enter both a word and a translation")
            return redirect(f"/edit_table/{language_name}/{table_name}")
        # Enter word pair into database.
        word_pair = WordPair(foreignWord, translation)
        word_pair.language_id = language.id
        db.session.add(word_pair)
        table.words.append(word_pair)
        db.session.commit()
        return redirect(f"/edit_table/{language_name}/{table_name}")



@app.route("/delete_word/<language_name>/<table_name>", methods=["POST"])
@login_required
def delete_word(language_name, table_name):
    """Delete a word."""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()
    word_pair_id = request.form["word_pair_id"]
    WordPair.query.filter_by(id=word_pair_id).delete()
    db.session.commit()
    return redirect(f"/edit_table/{language_name}/{table_name}")



@app.route("/view_table/<language_name>/<table_name>", methods=["GET"])
@login_required
def view_table(language_name, table_name):
    """View an existing word table"""
    table = Table.query.filter_by(name=table_name).first()

    if not table:
        flash(f"Table {table_name} does not exist")
        return redirect("/")

    if not table.words:
        flash(f"Table {table_name} is empty, try editing it here")
        return redirect(f"/edit_table/{language_name}/{table_name}")

    return render_template("view_table.html", table=table)


@app.route("/tables")
@app.route("/tables/<language_name>")
@login_required
def tables(language_name=None):
    """List all tables, or optionally all tables in a given language"""
    if not language_name:
        tables = Table.query.all()
    else:
        language = Language.query.filter_by(name=language_name).first()
        tables = Table.query.filter_by(language_id=language.id)
    return render_template("tables.html", tables=tables)





# The code below is taken from the CS50 finance exercise - need to figure out
# what it does, have disabled it for now because it seems to interfere with the
# flash message functionality.

#@app.after_request
#def after_request(response):
#    """Ensure responses aren't cached"""
#    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    response.headers["Expires"] = 0
#    response.headers["Pragma"] = "no-cache"
#    return response


