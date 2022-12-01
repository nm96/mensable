from flask import flash, render_template, request, session, redirect, Blueprint
from random import sample
from time import sleep

from mensable.models import *
from mensable.auth import login_required

bp = Blueprint("api", __name__)


@bp.route("/")
@login_required
def home():
    """Render homepage"""
    user = User.query.filter_by(id=session["user_id"]).first()
    return render_template("home.html", username=user.name)


@bp.route("/create_language", methods=["GET", "POST"])
@login_required
def create_language():
    """Create a new language."""
    
    if request.method == "GET":
        return render_template("create_language.html")

    elif request.method == "POST":
        language_name = request.form["language_name"].strip()

        existing_language = Language.query.filter_by(name=language_name).first()
        if existing_language:
            flash(f"The language {language_name} already exists.")
            return redirect("/create_language")

        language = Language(language_name)

        if not language.check_name():
            flash("Language name can contain only letters and spaces.")
            return redirect("/create_language")

        db.session.add(language)
        db.session.commit()
        flash("Now create a first table in the new language.")
        return redirect("/create_table/" + language_name)


@bp.route("/create_table/<language_name>", methods=["GET", "POST"])
@login_required
def create_table(language_name):
    """Create a new word table to learn"""

    language = Language.query.filter_by(name=language_name).first()
    
    if request.method == "GET":
        return render_template("create_table.html", language=language)

    elif request.method == "POST":
        table_name = request.form["table_name"].strip()

        existing_table = Table.query.filter_by(name=table_name).first()
        if existing_table:
            flash(f"Table {table_name} already exists.")
            return redirect(f"/create_table/{language_name}")

        table = Table(table_name)

        if not table.check_name():
            flash("Table name can contain only letters and spaces.")
            return redirect(f"/create_table/{language_name}")

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
        foreignWord = request.form["foreignWord"].strip()
        translation = request.form["translation"].strip()

        # Check if words are non-empty.
        if not foreignWord or not translation:
            flash("Please enter both a word and a translation.")
            return redirect(f"/edit_table/{language_name}/{table_name}")

        # Enter word pair into database.
        word_pair = WordPair(foreignWord, translation)
        word_pair.language_id = language.id
        db.session.add(word_pair)
        table.words.append(word_pair)   # Maintain many-to-many relationship.
        db.session.commit()
        return redirect(f"/edit_table/{language_name}/{table_name}")



@bp.route("/delete_word/<language_name>/<table_name>", methods=["POST"])
@login_required
def delete_word(language_name, table_name):
    """Delete a word."""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()
    word_pair_id = request.form["word_pair_id"]
    word_pair = WordPair.query.filter_by(id=word_pair_id).first()
    db.session.delete(word_pair)
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
        return render_template("all_tables.html", tables=tables)
    else:
        language = Language.query.filter_by(name=language_name).first()
        tables = Table.query.filter_by(language_id=language.id)
        return render_template("tables_in_language.html", tables=tables,
                language=language)


@bp.route("/languages")
@login_required
def languages():
    languages = Language.query.all()
    return render_template("languages.html", languages=languages)


@bp.route("/quiz/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def quiz(language_name, table_name):
    """Test a user's knowledge of the words in a table with a randomized quiz"""

    if request.method == "GET":

        table = Table.query.filter_by(name=table_name).first()

        if not table:
            flash(f"Table {table_name} not found")
            return redirect("/")

        if "to_test" not in session:
            # Load list of word pairs IDs to learn as session variable
            all_word_pair_ids = [word_pair.id for word_pair in table.words]
            session["to_test"] = sample(all_word_pair_ids, 
                                        min(5, len(all_word_pair_ids)))
            # Set up dictionary to record test score
            session["test_score"] = {"correct": 0, "total": 0}
            return redirect(f"/quiz/{language_name}/{table_name}")

        else:
            # If list of words to test is empty, clear the relevant session
            # variables and display the results.
            if len(session["to_test"]) == 0:
                correct = session["test_score"]["correct"]
                total = session["test_score"]["total"]
                del session["to_test"]
                del session["test_score"]
                return render_template("results.html", correct=correct,
                        total=total)

            # Otherwise ask user to translate current first word in the list.
            word_pair_id = session["to_test"][0]
            word_pair = WordPair.query.filter_by(id=word_pair_id).first()
            return render_template("quiz.html", table=table,
                    word_pair=word_pair)


    elif request.method == "POST":
        word_pair_id = session["to_test"][0]
        word_pair = WordPair.query.filter_by(id=word_pair_id).first()
        answer = request.form["answer"]

        # TODO: Use fuzzywuzzy to allow for typos
        # TODO: Allow alternative translations
        # TODO: Decide capitalization policy
        if word_pair.translation.lower() == answer.lower():
            flash("Correct!")
            session["test_score"]["correct"] += 1
            session["test_score"]["total"] += 1
        else:
            flash(f"Wrong! The correct translation is {word_pair.translation}.")
            session["test_score"]["total"] += 1

        session["to_test"] = session["to_test"][1:]
        return redirect(f"/quiz/{language_name}/{table_name}")




