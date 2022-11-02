from flask import Flask, render_template, request, session
from flask_session import Session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

Session(app)

@app.route("/")
def index():
    return render_template("index.html")
