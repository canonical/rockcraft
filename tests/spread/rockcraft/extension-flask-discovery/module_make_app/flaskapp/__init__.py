from flask import Flask  # pyright: ignore[reportMissingImports]

def make_app():
    app = Flask(__name__)

    @app.route("/")
    def ok():
        return "ok"

    return app
