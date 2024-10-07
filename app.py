#app.py
#import mysql as mysql
import json
from flask import Flask, render_template, request
from classify_inputs import Btn_MakePredictions
app = Flask(__name__)

# Notes
# http://localhost:5000/
# Flask Quickstart - https://flask.palletsprojects.com/en/3.0.x/quickstart/
# Flask Template - https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/
# Bootstrap docs - https://getbootstrap.com/docs/5.3/getting-started/introduction/
# Jinja docs - https://jinja.palletsprojects.com/en/3.1.x/templates/

# TODO FUTURE:
#       - Figure out a URL
#       - Request HTTPS cert
#       - Figure out hosting (openstack?)
#       - Logo/favicon

@app.route("/")
def loadpage_home():
    return render_template('home.html')


@app.route("/input/", methods=['GET', 'POST'])
def loadpage_input():
    if request.method == 'POST':
        # Decode JSON, send it to function
        result = Btn_MakePredictions(json.loads(request.form['targets_list']))
        # Return result as JSON
        return json.dumps(result)
    return render_template('input.html')


@app.route("/help/")
def loadpage_help():
    return render_template('help.html')


@app.route("/about/")
def loadpage_about():
    return render_template('about.html')


@app.route("/data/")
def loadpage_data():
    return render_template('data.html')