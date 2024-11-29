from time import sleep

from flask import Flask  # pyright: ignore[reportMissingImports]

app = Flask(__name__)


@app.route("/")
def ok():
    return "ok"

@app.route("/io")
def psudo_io():
    sleep(2)
    return "ok"
