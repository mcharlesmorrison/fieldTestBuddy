#! /usr/bin/env python3

import argon2 as ag

from flask import Flask, render_template, redirect, url_for, flash

from forms import LoginForm

application = Flask(__name__)
application.secret_key = "i am a secret key"


# Note need to enforce https


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # TODO Update this lol
        ph = ag.PasswordHasher()
        # get hash from db for form.username.data
        username = form.username.data
        user_hash = "test"  # ph.hash(form.password.data)

        ph.verify(user_hash, form.password.data)
        try:
            ph.verify(user_hash, form.password.data)
            pass
        except (
            ag.exceptions.VerifyMismatchError,
            ag.exceptions.VerificationError,
        ):
            flash("Login Unsuccessful. Please check username and password", "danger")
            return redirect(url_for("home"))
        except ag.exceptions.InvalidHash:
            flash("something has gone wrong; please try again!", "danger")
            return redirect(url_for("home"))
        else:
            if ph.check_needs_rehash(hash):
                # do somethign like `db.set_password_hash_for_user(user, ph.hash(password))`
                pass
            flash(f"Logged in as {username}!", "success")
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


if __name__ == "__main__":
    application.run(debug=True)
