from flask import Flask

application = Flask(__name__)

@application.route("/")
def ok():
    return "ok"
