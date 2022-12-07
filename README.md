# MENSABLE 

*This web app was created as a project for the [Harvard
CS50x](https://cs50.harvard.edu/x/2022/) course. To try it out, visit
[mensable.com](TODO: add hosted web app url here) A video demonstration of the
app is available [here](TODO: add video demo url here).*


## Introduction

Mensable - from the Latin *mens, mentis: mind, plan, intention* - is a web app
for learning lists (in mensable, 'tables') of foreign language vocabulary, IT
acronym definitions, historical dates or any other information that can be put
on a flashcard. 

Tables are organized into 'languages' and contain 'word pairs'. Users can
browse, subscribe to and take quizzes on existing word tables as well as
creating and editing their own. Tables can be edited via a built-in edit portal
on the site or by uploading a .csv file containing the word pairs.

When a user takes quizzes on a table, mensable uses the [Leitner
system](https://en.wikipedia.org/wiki/Leitner_system) to keep track of the
user's progress. This is a simple 'spaced-repetition' algorithm for
flashcard-based learning software where word pairs are sorted into an array of
'boxes' for each user. All word pairs start in the 'lowest' box (box 0) and are
moved along to a higher box when answered correctly in a quiz. Quizzes always
cover the words in the lowest-ranked boxes, and an incorrect answer for a word
pair demotes it back to box 0. This system ensures that the maximum time is
spent on the hardest word pairs.


## Implementation

Mensable is implemented as a **flask** web app written in Python 3. The front end
consists only of a set of fairly simple HTML files
([mensable/templates](mensable/templates)) using the Jinja templating engine and relying
on the Bootstrap framework for styling.

However, the standout feature of the app is definitely not the front end but the
system used to model the users, languages, tables, word pairs and table
subscriptions. I originally intended to use a conventional SQL engine such as
psycopg or the CS50 SQL module to interact with the database, but decided after
some experimentation that the best solution was to use the **SQLAlchemy** Object
Relational Mapper (ORM) system. This relates the database tables to python
classes (defined in [mensable/models.py](mensable/models.py)) which greatly simplified
many database operations once I had learned the details of the framework.
(Although admittedly this comes at the cost of an opportunity to learn more
about basic SQL.)

TODO: State underlying database type and hosting platform once hosted.

The app is tested using the **pytest** framework, using the scripts contained in
[tests](/tests). These simulate every operation that user could carry out, and
(as of the time of writing and project submission) give 100% coverage for the
main application code.


## Code structure

The project is divided into the main directory `\mensable` and the `\tests`
directory, with some configuration files here along with this readme. This
structure - borrowed from [the flask
tutorial](https://flask.palletsprojects.com/en/2.2.x/tutorial/) allows the app
to be run as a python package, which is useful for testing. Below I have
outlined the contents of the most important files in the project.

### [`mensable/__init__.py`](mensable/__init__.py)

This is the 'factory' file which identifies the `/mensable` directory as a
python package, and includes the `create_app` function for creating and
configuring the flask app.

### [`mensable/auth.py`](mensable/auth.py)

Contains everything necessary for managing user authorisation: the route
functions `login`, `logout`, `register` and the `login_required`
decorator.

### [`mensable/api.py`](mensable/api.py)

The API file contains route functions for all of mensable's core functionality:
creating, viewing, editing and deleting languages, tables and word pairs, along
with running quizzes, displaying and saving their results.

### [`mensable/models.py`](mensable/models.py)

Here the model classes `User`, `Language`, `Subscription`, `Table` and
`WordPair` are defined, along with an auxiliary database table `table_word_pair`
which tracks the many-to-many relationship between Tables and WordPairs.

### [`mensable/templates/`](mensable/templates/)

This directory contains all the HTML template files used for the front end of
the app. There are too many to describe each in detail here, but the most
important is `base.html` which encodes the basic features of the site and which
all the other files extend. The purpose of each of the files can be inferred
from the filename and from how they are rendered in the python files.

### [`tests/conftest.py`](tests/conftest.py)

Here we define several pytest *fixtures* which are special functions used to
configure and simplify testing, by e.g. setting up a 'dummy' flask app and
logging in a test user.

### [`tests/test_table.csv`](tests/test_table.csv)

This is an example CSV file used to test the adding of words to a table via CSV
upload. It contains two valid word pairs and a line of nonsense characters which
should be rejected by the application.

### [`tests/test_factory.py`](tests/test_factory.py), [`tests/test_auth.py`](tests/test_auth.py), [`tests/test_api.py`](tests/test_api.py)

These files test the code in `mensable/__init__.py`, `mensable/auth.py`,
`mensable/api.py` respectively, thereby proving test coverage for the entire
application (including, implicitly `mensable/models.py`.)

TODO: requirements.txt, setup.py

