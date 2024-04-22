from flask import Flask, render_template

app = Flask(__name__)

# Notes
# http://localhost:5000/
# Flask Quickstart - https://flask.palletsprojects.com/en/3.0.x/quickstart/
# Flask Template - https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/
# Bootstrap docs - https://getbootstrap.com/docs/5.3/getting-started/introduction/

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
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/inputcompound")
def input():

    return "<b>input command</b>"

@app.route("/showcompound/<int:compid>")
def showcompound(compid):
    compid = compid * 2
    return render_template('compound.html', compid=compid)
# commit test