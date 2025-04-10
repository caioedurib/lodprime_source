import json
from functools import wraps
from flask import make_response, request, current_app
from os import environ
from datetime import datetime

# prefix = environ.get('prefix', '')
user = environ.get('lodprime_user', '')
password = environ.get('lodprime_password', '')
if user == '':
    print("NO USERNAME SET! Set lodprime_user environment variable. Quitting.")
    exit()
if user == 'REPLACEME':
    print("DEFAULT USERNAME SET! Set new lodprime_user environment variable. Quitting.")
    exit()

if password == '':
    print("NO PASSWORD SET! Set lodprime_password environment variable. Quitting.")
    exit()
if password == 'REPLACEME':
    print("DEFAULT PASSWORD SET! Set new lodprime_password environment variable. Quitting.")
    exit()


def writelog(pred_type, output):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = {'timestamp': timestamp, 'pred_type': pred_type, 'output': output}
    print(json.dumps(log_line))
    with open('internal_files/log.json', 'a+') as log_file:
        log_file.write(json.dumps(log_line))
        log_file.write('\n')


def writelog_targetpred(targets_list):
    result = []
    for row in targets_list:
        if row["target_number"] != 0:
            result_status = "Success"
        else:
            result_status = "Failed"
        compound = row["compound"]
        target_number = row["target_number"]
        m_prediction = row["m_prediction"]
        f_prediction = row["f_prediction"]

        result.append({
            'compound': compound,
            'target_number': int(target_number),
            'm_prediction': int(m_prediction),
            'f_prediction': int(f_prediction),
            'result_status': result_status
        })
    if len(result) != 0:
        writelog('target_pred', result)


def writelog_chempred(targets_list):
    result = []
    for row in targets_list:
        if row["cid"] != -1:
            result_status = "Success"
        else:
            result_status = "Failed"
        compound = row["compound"]
        cid = row["cid"]
        m_prediction = row["m_prediction"]
        f_prediction = row["f_prediction"]
        result.append({
            'compound': compound,
            'cid': int(cid),
            'm_prediction': int(m_prediction),
            'f_prediction': int(f_prediction),
            'result_status': result_status
        })
    if len(result) != 0:
        writelog('chemical_pred', result)


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == user and auth.password == password:
            return f(*args, **kwargs)
        return make_response("<h1>Access denied!</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    return decorated
