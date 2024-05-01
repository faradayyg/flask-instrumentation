from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client.core import CollectorRegistry
from prometheus_client import multiprocess
import os

app = Flask(__name__)
registry = CollectorRegistry()
multiprocess.MultiProcessCollector(
    registry, path=os.getenv("PROMETHEUS_MULTIPROC_DIR", "data")
)
metrics = PrometheusMetrics(app, registry=registry)

# static information as metric
metrics.info("app_info", "Application info", version="1.0.3")


@app.route("/")
def main():
    return "main homepage"


@app.route("/skip")
@metrics.do_not_track()
def skip():
    return "Skip"  # default metrics are not collected   pass


@app.route("/long-running")
@metrics.gauge("in_progress", "Long running requests in progress")
def long_running():
    return "Long running"


@app.route("/stat/<int:status>")
def default_tracked(status):
    return "Status: %s" % status, status


@app.route("/status/<int:status>")
@metrics.do_not_track()
@metrics.summary(
    "requests_by_status",
    "Request latencies by status",
    labels={"status": lambda r: r.status_code},
)
@metrics.histogram(
    "requests_by_status_and_path",
    "Request latencies by status and path",
    labels={"status": lambda r: r.status_code, "path": lambda: request.path},
)
def echo_status(status):
    return "Status: %s" % status, status


@app.route("/new-path")
def new_path():
    return "yaaay"
