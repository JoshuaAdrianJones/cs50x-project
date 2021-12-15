import os
import logging
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from functools import wraps
import sqlite3
import helpers
from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


UPLOAD_FOLDER = "../uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = sqlite3.connect("file_share_app.db", check_same_thread=False)
# start logger
logger = logging.getLogger("werkzeug")  # grabs underlying WSGI logger


@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    uid = session["user_id"]
    user = list(db.execute(f"SELECT * FROM users WHERE id = {uid}"))
    username = user[0][1]
    return render_template("index.html", username=username)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and helpers.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect("/")
    return render_template("upload.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/login")

        # Query database for username
        username = request.form.get("username")
        rows = list(db.execute(f"SELECT * FROM users WHERE name = '{username}'"))
        print(rows)

        # Ensure username exists and password is correct
        pass_string = request.form.get("password")
        if len(rows) != 1 or not check_password_hash(rows[0][2], pass_string):
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return helpers.apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return helpers.apology("must provide password", 400)

        # check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return helpers.apology("passwords do not match", 400)

        # Query database for username
        username = request.form.get("username")
        rows = list(db.execute(f"SELECT * FROM users WHERE name = '{username}'"))

        # check if username exists
        if len(rows) == 1:
            return helpers.apology("User already exists", 400)

        username = request.form.get("username")
        p_hash = generate_password_hash(request.form.get("password"))
        # dev_only
        user_type = "admin"
        helpers.add_record_to_db(db, username, p_hash, user_type)
        return redirect("/login")

    else:

        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return helpers.apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
