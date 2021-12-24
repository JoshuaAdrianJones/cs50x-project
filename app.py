import logging
import os
import re
import sqlite3
from functools import wraps
from tempfile import mkdtemp

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    safe_join,
    send_file,
    send_from_directory,
    session,
)
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError, default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import helpers
from helpers import add_file_to_db, load_user_files, login_required

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


UPLOAD_FOLDER = f"{os.getcwd()}/uploads/"
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
    if request.method == "GET":
        uid = session["user_id"]
        user = list(db.execute(f"SELECT * FROM users WHERE id = {uid}"))
        user_name = user[0][1]
        users_files = load_user_files(db=db, uid=uid)
        return render_template(
            "index.html", user_name=user_name, users_files=users_files
        )
    else:
        print(request.method)
        print(request.values)
        print(request.form.get("file_name"))
        get_file(request.form.get("file_name"))
        uid = session["user_id"]
        user = list(db.execute(f"SELECT * FROM users WHERE id = {uid}"))
        user_name = user[0][1]
        users_files = load_user_files(db=db, uid=uid)
        return render_template(
            "index.html", user_name=user_name, users_files=users_files
        )


def get_file(file_name):

    try:
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], file_name, as_attachment=True
        )
    except FileNotFoundError:
        abort(404)


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
            file_name = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
            file.save(file_path)
            print(file_name)
            uid = session["user_id"]
            print(uid)
            add_file_to_db(
                db=db,
                file_name=file_name,
                uploader_id=session["user_id"],
                file_path=file_path,
            )
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
