from time import sleep

from flask import Flask  # pyright: ignore[reportMissingImports]

def create_app():
    app = Flask(__name__)
    @app.route("/")
    def ok():
        return "ok"


    @app.route("/io")
    def pseudo_io():
        sleep(2)
        return "ok"

    return app
