#! /usr/bin/env python3

from flask import Flask, render_template

application = Flask(__name__)

@application.route('/')
@application.route('/<rest>')
def home(rest=""):
    return render_template('index.html', rest=rest)

if __name__ == '__main__':
    application.run(debug=False)
