from flask import Flask  # pyright: ignore[reportMissingImports]

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"
