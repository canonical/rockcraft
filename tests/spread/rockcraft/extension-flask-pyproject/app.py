from flask import Flask
from pathlib import Path

application = Flask(__name__)

APP_DATA_TEST_FILE = Path("/app-data/flask-write-test.txt")

@application.route("/")
def ok():
    return "ok"

@application.route("/write-data")
def write_app_data():
    APP_DATA_TEST_FILE.write_text("written by Flask\n", encoding="utf-8")
    return "written"
