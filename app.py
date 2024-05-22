#import mysql as mysql
import json
from flask import Flask, render_template, request
from classify_inputs import Input_Make_Predictions, input_placeholder
app = Flask(__name__)

# Notes
# http://localhost:5000/
# Flask Quickstart - https://flask.palletsprojects.com/en/3.0.x/quickstart/
# Flask Template - https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/
# Bootstrap docs - https://getbootstrap.com/docs/5.3/getting-started/introduction/
# Jinja docs - https://jinja.palletsprojects.com/en/3.1.x/templates/

# TODO:
#       - Get functions for each action a user can take
#       - List the variables in
#       - Define what is displayed
#       - Figure out how the input is gathered (GET/POST/Form?)

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
        # TODO: Might be good to do JSON validation here, maybe with "marshmallow" library
        targets_list = json.loads(request.form['targets_list'])
        return input_placeholder(targets_list)

        # classification_result = Input_Make_Predictions(targets_list)
    return render_template('input.html')
    # GET TABLE, CONVERT TO JSON, SEND TO CLASSIFY INPUTS


@app.route("/help/")
def loadpage_help():
    return render_template('help.html')


@app.route("/about/")
def loadpage_about():
    return render_template('about.html')


@app.route("/datasets/")
def loadpage_datasets():
    return render_template('datasets.html')