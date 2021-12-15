import os
import logging
from flask import Flask, flash, request, redirect
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp
from functools import wraps
import sqlite3


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


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"txt", "xml"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def add_record_to_db(db, username, p_hash, user_type):
    latest_UID = list(db.execute("SELECT count(id) FROM users;"))
    print(f"latest ID is {latest_UID}")
    new_uid = latest_UID[0][0] + 1
    print(new_uid, username, p_hash, user_type)
    db.execute(
        f"INSERT INTO users (id, name, hash, user_type ) VALUES({new_uid}, '{username}', '{p_hash}', '{user_type}');"
    )
    db.commit()
