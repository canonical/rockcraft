import flask

app = flask.Flask(__name__)


@app.route("/")
def index():
    return "Hello, world!\n"


# [docs:time-endpoint-start]
import datetime


@app.route("/time")
def time():
    return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
# [docs:time-endpoint-end]


if __name__ == "__main__":
    app.run()
