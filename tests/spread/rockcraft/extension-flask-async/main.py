from time import sleep

from flask import Flask
from pathlib import Path

APP_DATA_TEST_FILE = Path("/app-data/flask-write-test.txt")

def create_app():
    app = Flask(__name__)
    @app.route("/")
    def ok():
        return "ok"


    @app.route("/io")
    def pseudo_io():
        sleep(2)
        return "ok"

    @app.route("/write-data")
    def write_app_data():
        APP_DATA_TEST_FILE.write_text("written by Flask\n", encoding="utf-8")
        return "written"

    return app
