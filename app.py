#app.py
#import mysql as mysql
import json
from flask import Flask, render_template, request
from classify_inputs import Btn_MakeTargetPredictions
from chemical_pred import Btn_MakeChemPredictions
from classify_inputs import Btn_Autofill_Targets
app = Flask(__name__)

# Notes
# http://localhost:5000/
# Flask Quickstart - https://flask.palletsprojects.com/en/3.0.x/quickstart/
# Flask Template - https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/
# Bootstrap docs - https://getbootstrap.com/docs/5.3/getting-started/introduction/
# Jinja docs - https://jinja.palletsprojects.com/en/3.1.x/templates/

# TODO:
#       - URL and project name
#       - Logo/favicon?
#       - Warning messages printing
#       - TSV export formatting (include warnings?)

@app.route("/")
def loadpage_home():
    return render_template('home.html')


@app.route("/autocomplete/", methods=['POST'])
def targetsautofill_function():
    # Decode JSON, send it to function
    result = Btn_Autofill_Targets(json.loads(request.form['empty_targets_list']))
    # Return result as JSON
    return json.dumps(result)


@app.route("/target_pred/", methods=['GET', 'POST'])
def loadpage_input():
    if request.method == 'POST':
        # Decode JSON, send it to function
        result = Btn_MakeTargetPredictions(json.loads(request.form['targets_list']))
        # Return result as JSON
        return json.dumps(result)
    return render_template('target_pred.html')


@app.route("/chemical_pred/", methods=['GET', 'POST'])
def loadpage_chemical_pred():
    if request.method == 'POST':
        # Decode JSON, send it to function
        result = Btn_MakeChemPredictions(json.loads(request.form['targets_list']))
        print(result)
        # Return result as JSON
        return json.dumps(result)
    return render_template('chemical_pred.html')

@app.route("/help/")
def loadpage_help():
    return render_template('help.html')


@app.route("/about/")
def loadpage_about():
    return render_template('about.html')


@app.route("/data/")
def loadpage_data():
    return render_template('data.html')