#! /usr/bin/env python3

import argon2 as ag

from flask import Flask, render_template, redirect, url_for, flash, session, abort

from forms import LoginForm, FieldTestForm


application = Flask(__name__)

# NOTE need to enforce https

# TODO obviously change this!
# do something like python -c 'import secrets; print(secrets.token_hex())'
application.secret_key = "i am a secret key"


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    # form.validate_on_submit() checks if it's a POST request
    # and if the form is valid
    if form.validate_on_submit():
        # TODO Update this lol
        ph = ag.PasswordHasher()
        # get hash from db for form.username.data
        username = form.username.data
        user_hash = "test"  # ph.hash(form.password.data)

        ph.verify(user_hash, form.password.data)
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

        if ph.check_needs_rehash(hash):
            new_hash = ph.hash(password)
            # do somethign like `db.set_password_hash_for_user(user, new_hash)`

        # set user session (keeps them logged in etc)
        # handles cryptography so the user can't modify their session :O
        session["username"] = username

        flash(f"Logged in as {username}!", "success")

        return redirect(url_for("home"))

    return render_template("login.html", form=form)


@application.route("/logout")
def logout():
    session.pop("username", None)
    flash("logged out", "success")
    return redirect(url_for("home"))


@application.route("/field_test", methods=["GET", "POST"])
def create_field_test():
    if "username" not in session:
        flash("You must be logged in and an admin to create a field test", "danger")
        return redirect(url_for("login"))

    # need to check that username can access admin for org
    is_admin, org = True, "Fox"  # db.get_info_for(username)
    if not is_admin:
        flash("You must be logged in and an admin to create a field test", "danger")
        return redirect(url_for("login"))

    form = CreateFieldTestForm()
    if form.validate_on_submit():
        flash("Field Test Created!", "success")
        return redirect(url_for("home"))

    return render_template("field_test.html", form=form)


if __name__ == "__main__":
    application.run(debug=True)
