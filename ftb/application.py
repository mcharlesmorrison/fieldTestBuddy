#! /usr/bin/env python3

from argon2 import PasswordHasher

from flask import Flask, render_template
from flask import Flask, render_template, request, redirect, url_for, flash

application = Flask(__name__)
application.secret_key = "i am a secret key"


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/signup", methods=["GET", "POST"])
def signup():
    """
    TODO
        - impl db
    """
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        ph = PasswordHasher()
        hashed_password = ph.hash(request.form["password"])

        # Here, you would usually store the user data in a database
        # For simplicity, we'll use flash messages
        flash(f"Account created for {username}!", "success")

        return redirect(url_for("signup"))

    return render_template("signup.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    """
    TODO
        - impl db
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        ph = PasswordHasher()
        hash = "1234"  # get hash from db
        ph.verify(hash, password)

        # Here, you would usually check the user's password against
        # the hashed password in your database
        # For simplicity, we'll use flash messages
        flash(f"Logged in as {username}!", "success")

        return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    application.run(debug=True)
