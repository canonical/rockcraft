"""gunicorn configuration."""  # noqa: INP001 (implicit namespace package)

bind = ["0.0.0.0:8000"]
chdir = "/flask/app"
statsd_host = "localhost:9125"
