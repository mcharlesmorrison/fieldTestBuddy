#! /usr/bin/env python3

import json
import bcrypt
import os 

from pathlib import Path
from contextlib import contextmanager

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
    send_file
)

from werkzeug.utils import secure_filename

from typing import Dict, List, Any

from ftb.forms import (
    form_from_defn,
    LoginForm,
    CreateFieldTestForm,
    SelectFieldTestForm,
)

import ftb.dbUtilities as dbUtils


application = Flask(__name__)

# TODO need to enforce https
# TODO need server-side sessions

# TODO obviously change this!
# do something like python -c 'import secrets; print(secrets.token_hex())'
application.secret_key = "jas;ldkjvhaskjdhff"  # os.environ["ftb_flask_secret"]
application.config["UPLOAD_FOLDER"] = "/tmp/cass"

User = Dict[str, Any]


@application.route("/")
def home():
    return render_template("index.html", username=session.get("username", None))


@application.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        flash("You are already logged in", "warning")
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user_data = dbUtils.getUser(username, "ftb_admin")
        if user_data is None:
            flash("Login Unsuccessful. Please check username and password", "danger")
            return redirect(url_for("login"))

        user_hash = user_data["password"]

        if not bcrypt.checkpw(str.encode(form.password.data), str.encode(user_hash)):
            flash("Login Unsuccessful. Please check username and password", "danger")
            return redirect(url_for("home"))

        # set user session (keeps them logged in etc)
        # handles cryptography so the user can't modify their session :O
        session["username"] = username
        session["userType"] = user_data["userType"]

        flash(f"Logged in as {username}!", "success")

        application.logger.info(
            f"{username} logged in with {user_data['userType']} privileges"
        )

        return redirect(url_for("home"))

    return render_template("login.html", form=form)


@application.route("/logout")
def logout():
    session.pop("userType", None)

    maybe_username = session.pop("username", None)
    if maybe_username is not None:
        flash("logged out", "success")

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
    is_admin = session["userType"] in ("ftb_admin", "casslabsadmin")
    if not is_admin:
        flash("You must be logged in as an admin to create a field test", "danger")
        return redirect(url_for("home"))

    form = CreateFieldTestForm()

    if form.errors:
        flash(form.errors, "danger")

    if form.validate_on_submit():
        # TODO do i have to escape here?
        field_names = request.form.getlist("field_name[]")
        field_types = request.form.getlist("field_type[]")
        default_values = request.form.getlist("default_value[]")
        required = request.form.getlist("required[]")

        field_test_defn = {
            "fieldTestType": form.field_test_type.data,
            "fields": {
                field_name: {
                    "type": field_type,
                    "default": default_value,
                    "required": is_required,
                }
                for field_name, field_type, default_value, is_required in zip(
                    field_names, field_types, default_values, required
                )
            },
        }

        dbUtils.metadataDefUpload(field_test_defn, session["userType"])

        application.logger.info(
            f"field test defn created by {session['username']}: {field_test_defn}"
        )
        flash("Field Test Created!", "success")

        return redirect(url_for("home"))

    return render_template("field_test/create_field_test.html", form=form)


@application.route("/field_test/select_field_test", methods=["GET", "POST"])
def select_field_test():
    if "username" not in session:
        flash("You must be logged in to upload a field test", "danger")
        return redirect(url_for("login"))

    application.logger.info(f"{session['username']} is selecting a field test")

    field_test_form = SelectFieldTestForm()

    field_test_types = dbUtils.getFieldTestTypes(session["userType"])
    field_test_form.field_test_type.choices = field_test_types

    if field_test_form.validate_on_submit():
        # TODO do i have to escape here?
        field_test_type = field_test_form.field_test_type.data
        # NOTE should we check that field_test_type is actually in db?
        #      though it should always since this is fm dropdown
        # TODO add field test to db, etc
        flash("Field Test Selected!", "success")
        # TODO confirm field_test_type is valid unicode, or even better, choose
        # a different identifier for this (uuid?)
        return redirect(f"/field_test/upload_field_test/{field_test_type}")

    # log form errors
    return render_template("field_test/select_field_test.html", form=field_test_form)


ALLOWED_EXTENSIONS = {"csv", "xls", "bin", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
        field_test_defn = dbUtils.getMetadataDef(field_test_type, session["userType"])
    except KeyError:
        flash("Invalid field test type", "danger")
        return redirect(url_for("select_field_test"))

    upload_form = form_from_defn(field_test_type, field_test_defn["fields"])

    if request.method == "POST" and upload_form.validate():
        # TODO add field test to db, etc
        form_data = {}
        for field_name, *rest in field_test_defn["fields"].items():
            try:
                form_data[field_name] = upload_form[field_name].data
            except KeyError as e:
                raise KeyError(f"cant find form value for key {field_name}") from e

        filenames = []
        for file in request.files.getlist("folderupload"):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(str(Path(application.config["UPLOAD_FOLDER"]) / filename))
                filenames.append(Path(application.config["UPLOAD_FOLDER"]) / filename)

        metadata = [form_data for _ in range(len(filenames))]

        # TODO upload files to amazon s3
        dbUtils.ftbDbUploadBulk(
            application.config["UPLOAD_FOLDER"], metadata, session["userType"]
        )

        flash("Field Test Uploaded!", "success")
        return redirect(url_for("home"))

    field_test_types = dbUtils.getFieldTestTypes(session["userType"])

    application.logger.info(f"field tests: {field_test_types}")

    return render_template(
        "field_test/upload_field_test.html",
        form=upload_form,
        field_test_type=field_test_type,
    )

@application.route("/field_test/query", methods=["GET", "POST"])
def query():
    print("in query!")
    if "username" not in session:
        flash("You must be logged in to search for field tests", "danger")
        return redirect(url_for("login"))
    
    user_type = session["userType"]
    is_admin = user_type in ("ftb_admin", "casslabsadmin")
    
    if not is_admin:
        flash("You must be logged in as an admin to create a field test", "danger")
        return redirect(url_for("home"))

    field_names = dbUtils.getUniqueFieldNames(user_type)
    if len(field_names) == 0:
        flash("No field tests found", "danger")
        return redirect(url_for("home"))

    print("Request Method: ", request.method)
    results_fieldTests = []
    test_downloaded = []
    # Handle the search query
    print(request.form)
    if request.method == "POST":
        if "search" in request.form:
            selected_field = request.form.get("field_name")
            search_value = request.form.get("search_value")
            # store these in user session YAAHHH!!!
            session["field_value_stored"] = selected_field
            session["search_value_stored"] = search_value
            results = dbUtils.ftbPartialMatchQuery(selected_field, search_value, user_type)
            results_fieldTests = list({result["fieldTestName"] for result in results})
        elif "download_tests" in request.form:
            print("download starts here!")
            test_downloaded = True
            zip_name = dbUtils.ftbQuery(session.get("field_value_stored"), session.get("search_value_stored"), user_type, application.root_path)
            print(os.path.basename(zip_name))
            return send_file(os.path.basename(zip_name), as_attachment=True)

    return render_template("field_test/query_field_test.html", 
                           field_names=field_names, results_fieldTests=results_fieldTests, test_downloaded=test_downloaded) 


@application.route("/search")
def search():
    filter_ = request.args.get("filter")
    field = request.args.get("field")
    print(field, filter)
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
