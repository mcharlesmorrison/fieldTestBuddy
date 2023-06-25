#! /usr/bin/env python3

# import boto3

from flask import Flask, render_template
from flask import Flask, render_template, request, redirect, url_for, flash

application = Flask(__name__)
application.secret_key = "i am a secret key"


@application.route("/")
def home():
    return render_template("index.html")


@application.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Here, you would usually store the user data in a database
        # For simplicity, we'll use flash messages
        flash(f"Account created for {username}!", "success")

        return redirect(url_for("signup"))

    return render_template("signup.html")


if __name__ == "__main__":
    application.run(debug=False)
