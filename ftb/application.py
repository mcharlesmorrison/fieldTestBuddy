#! /usr/bin/env python3

import os
import json
import argon2 as ag

from flask import (
    Flask,
    make_response,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request,
    jsonify,
)

from typing import Dict, List, Any

from forms import form_from_defn, LoginForm, CreateFieldTestForm, SelectFieldTestForm

from cassutils.dbUtils import userDB


"""
this file is SO messsy must be refactored
"""


application = Flask(__name__)

# NOTE need to enforce https

# TODO obviously change this!
# do something like python -c 'import secrets; print(secrets.token_hex())'
application.secret_key = os.environ["ftb_flask_secret"]

User = Dict[str, Any]

mock_field_test_defn_db: Dict[str, List[Any]] = dict()
mock_field_test_db: Dict[str, List[Any]] = dict()

mock_field_test_defn_db["casslabs"] = [("test", "integer", None, True)]


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
        user_data = userDB.getUser(username, "ftb_admin")

        if user_data is None:
            flash("Login Unsuccessful. Please check username and password", "danger")
            return redirect(url_for("login"))

        user_hash = user_data["password"]

        print(user_hash, form.password.data)
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
            # TODO Update password w/ new hash sometimes
            # do somethign like `db.set_password_hash_for_user(user, new_hash)`

        # set user session (keeps them logged in etc)
        # handles cryptography so the user can't modify their session :O
        session["username"] = username
        session["user_type"] = user_data["userType"]

        flash(f"Logged in as {username}!", "success")
        user_data["userType"] == "ftb_admin"
        application.logger.info(
            f"{username} logged in with {user_data['userType']} privileges"
        )

        return redirect(url_for("home"))

    return render_template("login.html", form=form)


@application.route("/logout")
def logout():
    maybe_username = session.pop("username", None)
    session.pop("user_type", None)
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
    is_admin = session["user_type"] == "ftb_admin"
    if not is_admin:
        flash("You must be logged in as an admin to create a field test", "danger")
        return redirect(url_for("home"))

    form = CreateFieldTestForm()
    if form.validate_on_submit():
        # TODO do i have to escape here?
        field_names = request.form.getlist("field_name[]")
        field_types = request.form.getlist("field_type[]")
        default_values = request.form.getlist("default_value[]")
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

    return render_template("field_test/create_field_test.html", form=form)


@application.route("/field_test/select_field_test", methods=["GET", "POST"])
def select_field_test():
    """
    this is "U1" in the wireframes
    """

    if "username" not in session:
        flash("You must be logged in to upload a field test", "danger")
        return redirect(url_for("login"))

    application.logger.info(f"{session['username']} is selecting a field test")

    field_test_form = SelectFieldTestForm()

    field_test_types = list(mock_field_test_defn_db.keys())
    field_test_form.field_test_type.choices = field_test_types

    if field_test_form.validate_on_submit():
        # TODO do i have to escape here?
        field_test_type = field_test_form.field_test_type.data
        # TODO check that field_test_type is actually in db, though it should always since this is fm dropdown
        mock_field_test_defn_db[field_test_type]
        # TODO add field test to db, etc
        flash("Field Test Selected!", "success")
        # TODO confirm field_test_type is valid unicode, or even better, choose
        # a different identifier for this (uuid?)
        return redirect(f"/field_test/upload_field_test/{field_test_type}")

    # log form errors
    return render_template("field_test/select_field_test.html", form=field_test_form)


@application.route(
    "/field_test/upload_field_test/<field_test_type>", methods=["GET", "POST"]
)
def upload_field_test(field_test_type):
    if "username" not in session:
        flash("You must be logged in to upload a field test", "danger")
        return redirect(url_for("login"))

    application.logger.info(
        f"{session['username']} is uploading a field test of type {field_test_type}"
    )

    try:
        field_test_defn = mock_field_test_defn_db[field_test_type]
    except KeyError:
        flash("Invalid field test type", "danger")
        return redirect(url_for("select_field_test"))

    upload_form = form_from_defn(field_test_type, field_test_defn)

    if request.method == "POST" and upload_form.validate():
        # TODO add field test to db, etc
        form_data = {}
        for field_name, *rest in field_test_defn:
            form_data[field_name] = upload_form[field_name].data

        # TODO upload files to amazon s3

        mock_field_test_db[field_test_type + "random_string"] = form_data

        flash("Field Test Uploaded!", "success")
        return redirect(url_for("home"))

    application.logger.info(f"form errors: {upload_form.errors}")
    field_test_types = list(mock_field_test_defn_db.keys())
    application.logger.info(f"field tests: {field_test_types}")
    return render_template(
        "field_test/upload_field_test.html",
        form=upload_form,
        field_test_type=field_test_type,
    )


@application.route("/field_test/query", methods=["GET", "POST"])
def query():
    if "username" not in session:
        flash("You must be logged in to search for field tests", "danger")
        return redirect(url_for("login"))

    return render_template("field_test/query_field_test.html")


@application.route("/search")
def search():
    request.args.get("query")
    # TODO HOW do you filter by query
    #     results = Item.query.filter(Item.name.like(f'%{query}%')).all()?
    return jsonify([{"field_test_name": k, **v} for k, v in mock_field_test_db.items()])


@application.route("/download")
def download():
    request.args.get("query")
    # TODO HOW do you filter by query
    #     results = Item.query.filter(Item.name.like(f'%{query}%')).all()?
    results = mock_field_test_db
    results_json = json.dumps(results)

    response = make_response(results_json)
    response.headers["Content-Disposition"] = "attachment; filename=results.json"
    response.headers["Content-Type"] = "application/json"

    # # Sending the zip file for download
    # return send_file(zip_filename,
    #              mimetype='application/zip',
    #              as_attachment=True,
    #              download_name=zip_filename)

    return response


if __name__ == "__main__":
    application.run(debug=True)
