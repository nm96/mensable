from flask import flash, render_template, request, session, redirect, Blueprint
import os
import csv
import Levenshtein
import sys
from datetime import date
from random import shuffle

from mensable.models import *
from mensable.auth import login_required

bp = Blueprint("api", __name__)


@bp.route("/")
@login_required
def home():
    """Render homepage - including lists of languages and tables a user is
    subscribed to."""
    user = User.query.filter_by(id=session["user_id"]).first()
    subs = user.subscriptions
    subs.sort(key=lambda sub: sub.last_quiz_date)
    languages = set(sub.table.language for sub in subs)
    today = date.today()
    return render_template("home.html", user=user, subs=subs,
            languages=languages, date=today)


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
    """List all languages"""
    languages = Language.query.all()
    return render_template("languages.html", languages=languages)


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
    user = User.query.filter_by(id=session["user_id"]).first()
    
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

        table.creator_id = user.id
        table.language_id = language.id
        db.session.add(table)
        db.session.commit()

        # Now create a subscription to this table.
        sub = Subscription(user, table)
        db.session.add(sub)
        db.session.commit()
        return redirect(f"/edit_table/{language_name}/{table_name}")


@bp.route("/edit_table/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def edit_table(language_name, table_name):
    """Edit an existing word table"""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()

    if table.creator_id != session["user_id"]:
        flash("Cannot edit another user's table")
        return redirect("/tables")

    if request.method == "GET":
        return render_template("edit_table.html", language=language, table=table)

    elif request.method == "POST":
        # Get word and translation from input form.
        foreignWord = request.form["foreignWord"]
        translation = request.form["translation"]
        add_word_pair(foreignWord, translation, table, language)
        return redirect(f"/edit_table/{language.name}/{table.name}")


def add_word_pair(foreignWord, translation, table, language):
    """Add a word pair to a table"""
    # Strip whitespace
    foreignWord = foreignWord.strip()
    translation = translation.strip()

    # Check that words are non-empty.
    if not foreignWord or not translation:
        flash("Please enter both a word and a translation.")
        return

    # Check if word is already in database.
    existing = WordPair.query.filter_by(foreignWord=foreignWord).first()
    if existing and existing.language_id == language.id:
        flash(f"{foreignWord} is already in the database.")
        table.words.insert(0, existing)
        db.session.commit()
        return

    # Enter word pair into database.
    word_pair = WordPair(foreignWord, translation)
    word_pair.language_id = language.id
    db.session.add(word_pair)
    table.words.insert(0, word_pair)   # Maintain many-to-many relationship.
    db.session.commit()
    return


@bp.route("/upload_csv/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def upload_csv(language_name, table_name):
    """Edit an existing word table by adding words from a csv file"""
    table = Table.query.filter_by(name=table_name).first()
    language = Language.query.filter_by(name=language_name).first()

    if request.method == "GET":
        return render_template("upload_csv.html", language=language, table=table)

    elif request.method == "POST":
        uploaded_file = request.files["csv_file"]
        filename = os.path.join(uploaded_file.filename)
        uploaded_file.save(filename)
        with open(filename) as csv_file:
            for row in csv.reader(csv_file):
                if len(row) == 2:
                    foreignWord, translation = row
                    add_word_pair(foreignWord, translation, table, language)
        return redirect(f"/edit_table/{language.name}/{table.name}")


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


@bp.route("/delete_table/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def delete_table(language_name, table_name):
    """Delete a table."""
    table = Table.query.filter_by(name=table_name).first()
    if request.method == "GET":
        return render_template("delete_table.html", table=table)
    elif request.method == "POST":
        for sub in table.subscriptions:
            db.session.delete(sub)
        db.session.delete(table)
        db.session.commit()
        return redirect(f"/tables/{language_name}")


@bp.route("/view_table/<language_name>/<table_name>", methods=["GET"])
@login_required
def view_table(language_name, table_name):
    """View an existing word table"""
    user = User.query.filter_by(id=session["user_id"]).first()
    table = Table.query.filter_by(name=table_name).first()

    if not table:
        flash(f"Table {table_name} does not exist")
        return redirect("/")

    if not table.words:
        flash(f"Table {table_name} is empty, try editing it here")
        return redirect(f"/edit_table/{language_name}/{table_name}")

    sub = Subscription.query.filter_by(learner_id=user.id, table_id=table.id).first()
    return render_template("view_table.html", table=table, user=user, sub=sub)


@bp.route("/quiz/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def quiz(language_name, table_name):
    """Test a user's knowledge of the words in a table with a randomized quiz"""

    QUIZ_LENGTH = 6
    table = Table.query.filter_by(name=table_name).first()

    if request.method == "GET":
        user = User.query.filter_by(id=session["user_id"]).first()

        if "quiz" not in session or session["quiz"]["table_id"] != table.id:
            # Create quiz dictionary session variable.
            session["quiz"] = {}
            quiz = session["quiz"] # (alias)

            # Check if user is subscribed to table yet.
            sub = Subscription.query.filter_by(learner_id=user.id, table_id=table.id).first()

            # Create subscription if not.
            if not sub:
                sub = Subscription(user, table)

            # Update leitner boxes, checking for new and deleted words in list
            lboxes = sub.leitner_boxes.copy()
            database_word_ids = [word_pair.id for word_pair in table.words] 
            for word_id in database_word_ids:
                if word_id not in lboxes:
                    lboxes[word_id] = 0
            for word_id in list(lboxes.keys()):
                if word_id not in database_word_ids:
                    del lboxes[word_id]
            sub.leitner_boxes = lboxes
            db.session.add(sub)
            db.session.commit()

            # Load list of "QUIZ_LENGTH" highest-prioirity word pair IDs to learn from
            # Leitner boxes. 
            word_ids = list(lboxes.keys())
            word_ids.sort(key=lambda id: lboxes[id])
            word_ids = word_ids[:QUIZ_LENGTH]
            shuffle(word_ids)
            quiz["total_count"] = len(word_ids)
            quiz["word_ids"] = word_ids
            quiz["to_test"] = word_ids.copy()
            quiz["right_list"] = []
            quiz["wrong_list"] = []
            quiz["right_count"] = 0
            quiz["table_id"] = table.id 
            
            # Start quiz by redirecting back to the route.
            return redirect(f"/quiz/{language_name}/{table_name}")

        else:
            quiz = session["quiz"]

            if len(quiz["to_test"]) == 0:
                return redirect(f"/results/{language_name}/{table_name}")

            # Otherwise ask user to translate current first word in the list.
            word_id = quiz["to_test"][0]
            word_pair = WordPair.query.filter_by(id=word_id).first()
            return render_template("quiz.html", table=table,
                    word_pair=word_pair)

    elif request.method == "POST":
        print("\n\n QUIZ = ", session["quiz"], file=sys.stderr)
        word_id = session["quiz"]["to_test"][0]
        session["quiz"]["to_test"] = session["quiz"]["to_test"][1:]
        print("\n\n QUIZ = ", session["quiz"], file=sys.stderr)
        word_pair = WordPair.query.filter_by(id=word_id).first()
        answer = request.form["answer"]

        # Compare answer to translation from database and record results.
        if compare_strings(answer, word_pair.translation):
            flash(f"Correct: {word_pair.foreignWord} translates to {word_pair.translation}.")
            session["quiz"]["right_list"].append(word_id)
            session["quiz"]["right_count"] += 1
            print("\n\n QUIZ = ", session["quiz"], file=sys.stderr)
            session.modified = True
            return redirect(f"/quiz/{language_name}/{table_name}")
        else:
            session["quiz"]["wrong_list"].append(word_id)
            print("\n\n QUIZ = ", session["quiz"], file=sys.stderr)
            session.modified = True
            return render_template("wrong.html", table=table,
                    word_pair=word_pair, answer=answer)


def compare_strings(s1, s2):
    """Soft string comparison, converts to lower case and removes whitespace,
    allows for typos up to a Levenshtein distance of 2"""
    s1 = s1.lower()
    s2 = s2.lower()
    s1 = s1.replace(" ", "")
    s2 = s2.replace(" ", "")
    if Levenshtein.distance(s1, s2) <= 2:
        return True
    return False


@bp.route("/results/<language_name>/<table_name>", methods=["GET"])
@login_required
def results(language_name, table_name):
    # Load relevant objects
    user = User.query.filter_by(id=session["user_id"]).first()
    table = Table.query.filter_by(name=table_name).first()
    sub = Subscription.query.filter_by(learner_id=user.id, table_id=table.id).first()

    if "quiz" not in session:
        results = sub.last_quiz_results

    else:
        quiz = session["quiz"]

        # Upate Leitner boxes
        lboxes = sub.leitner_boxes.copy()
        for word_id in quiz["right_list"]:
            # Move to next box along
            lboxes[word_id] += 1
        for word_id in quiz["wrong_list"]:
            # Move back to first box
            lboxes[word_id] = 0
        sub.leitner_boxes = lboxes 

        # Tidy up
        db.session.commit()
        del session["quiz"]

        # Convert quiz data into more detailed results dictionary
        results = quiz.copy()
        results["wrong_list"] = [WordPair.query.filter_by(id=id).first() for id in
                quiz["wrong_list"]]
        results["right_list"] = [WordPair.query.filter_by(id=id).first() for id in
                quiz["right_list"]]
        results["percentage_score"] = int(results["right_count"] /
                results["total_count"] * 100)
        if results["percentage_score"] > 90:
            headline = "Congrats! "
        elif results["percentage_score"] > 60:
            headline = "Not bad! "
        else:
            headline = "Better luck next time - "
        
        headline += f"""
                   you scored {results['right_count']}/{results['total_count']}
                   ({results['percentage_score']}%)
                   """
        results["headline"] = headline

        # Save full details of most recent results to the subscription
        sub.last_quiz_results = results
        sub.quiz_attempts += 1
        sub.total_questions += results["total_count"]
        sub.total_right += results["right_count"]
        sub.average_percentage_score = int(sub.total_right /
                sub.total_questions * 100)
        sub.last_quiz_date = date.today()
        db.session.commit()

    # Display results
    return render_template("results.html", results=results, sub=sub)


@bp.route("/unsubscribe/<language_name>/<table_name>", methods=["GET", "POST"])
@login_required
def unsubscribe(language_name, table_name):
    """Unsubscribe from a table and delete learning data."""
    user = User.query.filter_by(id=session["user_id"]).first()
    table = Table.query.filter_by(name=table_name).first()
    sub = Subscription.query.filter_by(learner_id=user.id, table_id=table.id).first()

    if request.method == "GET":
        return render_template("unsubscribe.html", user=user, table=table)

    elif request.method == "POST":
        db.session.delete(sub)
        db.session.commit()
        return redirect(f"/tables/{language_name}")

