from flask import flash, render_template, request, session, redirect, Blueprint

from mensable.models import *
from mensable.auth import login_required

bp = Blueprint("api", __name__)


@bp.route("/create_language", methods=["GET", "POST"])
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


@bp.route("/create_table/<language_name>", methods=["GET", "POST"])
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


@bp.route("/edit_table/<language_name>/<table_name>", methods=["GET", "POST"])
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



@bp.route("/delete_word/<language_name>/<table_name>", methods=["POST"])
@login_required
def delete_word(language_name, table_name):
    """Delete a word."""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()
    word_pair_id = request.form["word_pair_id"]
    WordPair.query.filter_by(id=word_pair_id).delete()
    db.session.commit()
    return redirect(f"/edit_table/{language_name}/{table_name}")



@bp.route("/view_table/<language_name>/<table_name>", methods=["GET"])
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


@bp.route("/tables")
@bp.route("/tables/<language_name>")
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

#@bp.after_request
#def after_request(response):
#    """Ensure responses aren't cached"""
#    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    response.headers["Expires"] = 0
#    response.headers["Pragma"] = "no-cache"
#    return response


