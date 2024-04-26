from flask import Flask, render_template, request

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
        compound_name = request.form['Compound_Name']
        drugage_id = request.form['DrugAge_ID']
        print(compound_name)
        print(drugage_id)
    return render_template('input.html')


@app.route("/help/")
def loadpage_help():
    return render_template('help.html')

@app.route("/datasets/")
def loadpage_datasets():
    return render_template('datasets.html')