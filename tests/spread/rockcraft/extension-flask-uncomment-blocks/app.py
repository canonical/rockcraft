from flask import Flask
import glob

app = Flask(__name__)


@app.route("/")
def ok():
    return "ok"

@app.route("/check_lib")
def check_lib():# glob.glob with recursive=True allows '**' to search all subdirectories
    matches = glob.glob('/usr/lib/**/libpq.so.5*', recursive=True)

    if matches:
        return "ok"
    else:
        return "Library not found", 404
