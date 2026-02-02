from flask import Flask

def make_app():
    app = Flask(__name__)

    @app.route("/")
    def ok():
        return "ok"

    return app
