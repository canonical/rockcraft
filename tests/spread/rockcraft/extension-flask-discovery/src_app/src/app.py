from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def ok():
        return "ok"

    return app
