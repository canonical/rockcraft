"""gunicorn configuration."""

bind = ["0.0.0.0:8000"]
chdir = "/app"
statsd_host = "localhost:9125"
