from flask import Flask  # pyright: ignore[reportMissingImports]

app = Flask(__name__)


@app.route("/")
def ok():
    return "ok"
