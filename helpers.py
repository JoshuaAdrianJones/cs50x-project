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

    new_uid = latest_UID[0][0] + 1

    db.execute(
        f"INSERT INTO users (id, name, hash, user_type ) VALUES({new_uid}, '{username}', '{p_hash}', '{user_type}');"
    )
    db.commit()


def add_file_to_db(db, file_name, file_path, uploader_id):
    latest_UID = list(db.execute("SELECT count(file_id) FROM files;"))

    new_uid = latest_UID[0][0] + 1
    # record file data and location for later retrieval
    db.execute(
        f"INSERT INTO files (file_id, file_name, file_path, uploader_id ) VALUES({new_uid}, '{file_name}', '{file_path}', '{uploader_id}');"
    )
    #  record file to access list with user ID
    db.execute(
        f"INSERT INTO file_access (file_id, user_id) VALUES({new_uid}, {uploader_id});"
    )
    db.commit()


def load_user_files(db, uid):
    allowed_file_ids = list(
        db.execute(f"SELECT file_id FROM file_access WHERE user_id={uid}")
    )
    allowed_file_ids = tuple([row[0] for row in allowed_file_ids])

    if len(allowed_file_ids) > 1:
        user_files = list(
            db.execute(f"SELECT * FROM files WHERE file_id IN {allowed_file_ids}")
        )
    else:
        user_files = list(
            db.execute(f"SELECT * FROM files WHERE file_id={allowed_file_ids[0]}")
        )

    return user_files
