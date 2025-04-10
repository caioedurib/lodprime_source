#app.py
#import mysql as mysql
import json
from flask import Flask, render_template, request, Blueprint
from classify_inputs import Btn_MakeTargetPredictions
from chemical_pred import Btn_MakeChemPredictions
from classify_inputs import Btn_Autofill_Targets
from os import environ
from util import auth_required

app = Flask(__name__)

# Notes
# http://localhost:5000/
# Flask Quickstart - https://flask.palletsprojects.com/en/3.0.x/quickstart/
# Flask Template - https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/
# Bootstrap docs - https://getbootstrap.com/docs/5.3/getting-started/introduction/
# Jinja docs - https://jinja.palletsprojects.com/en/3.1.x/templates/

prefix = environ.get('prefix', '')

@app.route("/")
def loadpage_home():
    return render_template('home.html', prefix=prefix)

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
    return render_template('target_pred.html', prefix=prefix)


@app.route("/chemical_pred/", methods=['GET', 'POST'])
def loadpage_chemical_pred():
    if request.method == 'POST':
        # Decode JSON, send it to function
        result = Btn_MakeChemPredictions(json.loads(request.form['targets_list']))
        # Return result as JSON
        return json.dumps(result)
    return render_template('chemical_pred.html', prefix=prefix)

@app.route("/help/")
def loadpage_help():
    return render_template('help.html', prefix=prefix)


@app.route("/about/")
def loadpage_about():
    return render_template('about.html', prefix=prefix)


@app.route("/data/")
def loadpage_data():
    return render_template('data.html', prefix=prefix)

@app.route("/log/")
@auth_required
def loadpage_log():
    with open('internal_files/log.json', 'r') as log_file:
        press_counter = 0
        success_counter = 0
        failure_counter = 0

        # Actually tab delimited, but whatever
        target_csv = "timestamp\tcompound_name\tvalid_targets\tmale_prediction\tfemale_prediction\n"
        chem_csv = "timestamp\tcompound_name\tcid\tmale_prediction\tfemale_prediction\n"
        for line in log_file:
            press_counter = press_counter + 1
            json_line = json.loads(line)

            for prediction in json_line["output"]:
                if prediction["result_status"] == "Success":
                    success_counter = success_counter + 1
                elif prediction["result_status"] == "Failed":
                    failure_counter = failure_counter + 1
                else:
                    print(f"Error: Unexpected result status: {prediction['result_status']}")

            if json_line["pred_type"] == 'target_pred':
                for prediction in json_line["output"]:
                    if prediction["result_status"] == "Success":
                        target_csv = target_csv + json_line["timestamp"] + '\t' + prediction["compound"] + '\t' + str(prediction["target_number"]) + '\t' + str(prediction["m_prediction"]) + '\t' + str(prediction["f_prediction"]) + '\n'
                print(target_csv)

            if json_line["pred_type"] == 'chemical_pred':
                for prediction in json_line["output"]:
                    if prediction["result_status"] == "Success":
                        chem_csv = chem_csv + json_line["timestamp"] + '\t' + prediction["compound"] + '\t' + str(prediction["cid"]) + '\t' + str(prediction["m_prediction"]) + '\t' + str(prediction["f_prediction"]) + '\n'
                print(chem_csv)
            elif json_line["pred_type"] == 'chemical_pred':
                continue

    return render_template('log.html', prefix=prefix,
                           press_counter=press_counter,
                           success_counter=success_counter,
                           failure_counter=failure_counter,
                           target_csv=target_csv,
                           chem_csv=chem_csv)
