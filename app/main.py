from flask import Flask, jsonify, request
import os
import time
from datetime import datetime
import random
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import g
import shutil 

# Counter: total requests
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"]
)

# Histogram: request latency
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "path"]
)

# Gauges: uptime, mode, chaos
APP_UPTIME = Gauge("app_uptime_seconds", "Application uptime in seconds")
APP_MODE = Gauge("app_mode", "0=stable, 1=canary")
CHAOS_ACTIVE = Gauge("chaos_active", "0=none, 1=slow, 2=error")

app = Flask(__name__)

# Record application start time
start_time = time.time()

# Global tracking for fault injection settings
chaos_state = {
    "mode": None,
    "duration": 0,
    "rate": 0
}

current_mode = os.getenv("MODE", "stable")
APP_MODE.set(1 if current_mode == "canary" else 0)

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - g.start_time

    REQUEST_LATENCY.labels(
        request.method,
        request.path
    ).observe(latency)

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.path,
        status_code=response.status_code
    ).inc()

    APP_UPTIME.set(int(time.time() - start_time))
    APP_MODE.set(1 if os.getenv("MODE") == "canary" else 0)

    chaos_map = {"none": 0, None: 0, "slow": 1, "error": 2}
    CHAOS_ACTIVE.set(chaos_map.get(chaos_state["mode"], 0))

    return response


@app.route("/")
def home():
    mode = os.getenv("MODE", "stable")
    version = os.getenv("APP_VERSION", "1.0.0")
    timestamp = datetime.now().isoformat()

    if chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])

    if chaos_state["mode"] == "error":
        if random.random() < chaos_state["rate"]:
            return jsonify({"error": "chaos error occurred"}), 500

    response = jsonify({
        "message": f"Welcome to SwiftDeploy ({mode} mode)",
        "version": version,
        "timestamp": timestamp
    })

    if mode == "canary":
        response.headers["X-Mode"] = "canary"

    return response


@app.route("/healthz")
def healthz():
    mode = os.getenv("MODE", "stable")
    uptime = int(time.time() - start_time)

    if chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])

    if chaos_state["mode"] == "error":
        if random.random() < chaos_state["rate"]:
            return jsonify({"error": "chaos error occurred"}), 500

    response = jsonify({
        "status": "healthy",
        "uptime_seconds": uptime,
        "mode": mode
    })

    if mode == "canary":
        response.headers["X-Mode"] = "canary"

    return response


@app.route("/metrics")
def metrics():
    data = generate_latest()
    return app.response_class(data, mimetype=CONTENT_TYPE_LATEST)



# Infrastructure metrics endpoint

@app.route("/infra")
def infra():
    disk_free = shutil.disk_usage("/").free / (1024**3)
    cpu_load = os.getloadavg()[0]

    return jsonify({
        "disk_free_gb": round(disk_free, 2),
        "cpu_load": round(cpu_load, 2)
    })


# Chaos status endpoint

@app.route("/chaos/status")
def chaos_status():
    return jsonify({
        "mode": chaos_state["mode"] or "off"
    })


# Chaos control endpoint (canary only)
@app.route("/chaos", methods=["POST"])
def chaos():
    mode = os.getenv("MODE", "stable")

    if mode != "canary":
        return jsonify({"error": "Chaos mode is only available in canary"}), 403

    data = request.get_json()

    if not data or "mode" not in data:
        return jsonify({"error": "Missing 'mode' in request body"}), 400

    global chaos_state
    chaos_mode = data["mode"]

    if chaos_mode == "slow":
        chaos_state["mode"] = "slow"
        chaos_state["duration"] = int(data.get("duration", 1))
        return jsonify({"status": "slow mode activated"})

    elif chaos_mode == "error":
        chaos_state["mode"] = "error"
        chaos_state["rate"] = float(data.get("rate", 0.5))
        return jsonify({"status": "error mode activated"})

    elif chaos_mode == "recover":
        chaos_state["mode"] = None
        chaos_state["duration"] = 0
        chaos_state["rate"] = 0
        return jsonify({"status": "recovered"})

    else:
        return jsonify({"error": "invalid chaos mode"}), 400


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 3000))
    app.run(host="0.0.0.0", port=port)
