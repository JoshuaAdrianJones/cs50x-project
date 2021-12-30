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
    latest_UID_access = list(
        db.execute("SELECT count(access_record_id) FROM file_access;")
    )

    new_uid_access = latest_UID_access[0][0] + 1
    db.execute(
        f"INSERT INTO file_access (access_record_id, file_id, user_id) VALUES({new_uid_access},{new_uid}, {uploader_id});"
    )
    db.commit()


def load_user_files(db, uid):
    allowed_file_ids = list(
        db.execute(f"SELECT file_id FROM file_access WHERE user_id={uid}")
    )
    if allowed_file_ids:
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
    else:
        return []


def add_user_file_association(db, file_to_add_user_to, user_id_to_add):
    latest_UID = list(db.execute("SELECT count(access_record_id) FROM file_access"))
    file_id = list(
        db.execute(
            f"SELECT file_id from files where file_name='{file_to_add_user_to}' "
        )
    )[0][0]
    new_uid = latest_UID[0][0] + 1
    db.execute(
        f"INSERT INTO file_access (access_record_id, file_id, user_id) VALUES({new_uid}, {file_id},{user_id_to_add});"
    )
    db.commit()
