from flask import Flask  # pyright: ignore[reportMissingImports]

application = Flask(__name__)


@application.route("/")
def ok():
    return "ok"
