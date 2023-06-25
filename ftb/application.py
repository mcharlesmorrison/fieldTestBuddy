#! /usr/bin/env python3

import argon2 as ag

from flask import Flask, render_template, redirect, url_for, flash, session, request

from typing import Dict, List, Any

from forms import LoginForm, CreateFieldTestForm, FieldTestForm


"""
this file is SO messsy must be refactored
"""


application = Flask(__name__)

# NOTE need to enforce https

# TODO obviously change this!
# do something like python -c 'import secrets; print(secrets.token_hex())'
application.secret_key = "i am a secret key"

User = Dict[str, Any]

mock_field_test_defn_db: Dict[str, List[Any]] = dict()
mock_field_test_db: Dict[str, List[Any]] = dict()
mock_user_db: Dict[str, User] = dict()

mock_field_test_defn_db["casslabs"] = ["test", "integer", None, True]
mock_user_db["admin"] = {"username": "admin", "is_admin": True, "corp": "casslabs"}


def is_user_admin(username: str) -> bool:
    user_info = mock_user_db[username]
    return user_info["is_admin"]


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))

    form = LoginForm()
    # form.validate_on_submit() checks if it's a POST request
    # and if the form is valid
    if form.validate_on_submit():
        # TODO Update this lol
        ph = ag.PasswordHasher()
        # get hash from db for form.username.data
        username = form.username.data
        user_hash = ph.hash(form.password.data)

        try:
            ph.verify(user_hash, form.password.data)
        except (
            ag.exceptions.VerifyMismatchError,
            ag.exceptions.VerificationError,
        ):
            flash("Login Unsuccessful. Please check username and password", "danger")
            return redirect(url_for("home"))
        except ag.exceptions.InvalidHash:
            flash("something has gone wrong; please try again!", "danger")
            return redirect(url_for("home"))

        if ph.check_needs_rehash(user_hash):
            ph.hash(form.password.data)
            # do somethign like `db.set_password_hash_for_user(user, new_hash)`

        # set user session (keeps them logged in etc)
        # handles cryptography so the user can't modify their session :O
        session["username"] = username

        flash(f"Logged in as {username}!", "success")
        is_admin = is_user_admin(username)
        application.logger.info(
            f"{username} logged in with {'admin' if is_admin else 'user'} privileges"
        )

        return redirect(url_for("home"))

    return render_template("login.html", form=form)


@application.route("/logout")
def logout():
    maybe_username = session.pop("username", None)
    if maybe_username is not None:
        flash("logged out", "success")
    else:
        flash("you were not logged in", "warning")
    return redirect(url_for("home"))


@application.route("/field_test/create", methods=["GET", "POST"])
def create_field_test():
    """
    How do we prevent user from creating a field test with a name that already exists?
    Divided by user org ofc
    """
    if "username" not in session:
        flash("You must be logged in and an admin to create a field test", "danger")
        return redirect(url_for("login"))

    application.logger.info(f"{session['username']} is creating a field test")

    # need to check that username can access admin for org
    # this is probably not how we want to do this, but this
    # gives an idea of what we have to do here
    # is_admin, org = db.get_info_for(username)
    is_admin = is_user_admin(session["username"])
    if not is_admin:
        flash("You must be logged in as an admin to create a field test", "danger")
        return redirect(url_for("home"))

    form = CreateFieldTestForm()
    if form.validate_on_submit():
        # TODO do i have to escape here?
        field_names = request.form.getlist("field_name[]")
        field_types = request.form.getlist("field_type[]")
        default_values = [
            None if val == "" else [v.strip() for v in val.split(",")]
            for val in request.form.getlist("default_value[]")
        ]
        required = [
            is_required == "true" for is_required in request.form.getlist("required[]")
        ]
        # these fields here are the ones that the admin sets for the field test
        field_test_defn = list(zip(field_names, field_types, default_values, required))
        application.logger.info(
            f"field test defn created by {session['username']}: {field_test_defn}"
        )
        flash("Field Test Created!", "success")
        # TODO add field test to db, etc
        mock_field_test_defn_db[form.field_test_type.data] = field_test_defn
        print(mock_field_test_defn_db)
        return redirect(url_for("home"))

    return render_template("field_tester_pages/create_field_test.html", form=form)


@application.route("/field_test/upload_field_test", methods=["GET", "POST"])
def upload_field_test():
    """
    this is "U1" in the wireframes
    """

    if "username" not in session:
        flash("You must be logged in and an admin to upload a field test", "danger")
        return redirect(url_for("login"))

    application.logger.info(f"{session['username']} is uploading a field test")

    field_test_form = FieldTestForm()

    field_test_types = list(mock_field_test_defn_db.keys())

    field_test_form.field_test_type.choices = field_test_types

    if field_test_form.validate_on_submit():
        # TODO do i have to escape here?
        field_test_type = field_test_form.field_test_type.data
        # TODO check that field_test_type is actually in db, though it should always since this is fm dropdown
        mock_field_test_defn_db[field_test_type]
        # TODO add field test to db, etc
        flash("Field Test Selected!", "success")
        return redirect(url_for("home"))
    else:
        # log form errors
        application.logger.error(f"form errors: {field_test_form.errors}")
        field_test_types = list(mock_field_test_defn_db.keys())
        application.logger.info(f"field tests: {field_test_types}")
        return render_template(
            "field_tester_pages/field_test_selector.html", form=field_test_form
        )


if __name__ == "__main__":
    application.run(debug=True)
