from flask import Flask, jsonify, request
import os
import time
from datetime import datetime
import random

app = Flask(__name__)

# Record application start time
start_time = time.time()

# Global tracking for fault injection settings
chaos_state = {
    "mode": None,
    "duration": 0,
    "rate": 0
}


@app.route("/")
def home():
    # Load environment configuration
    mode = os.getenv("MODE", "stable")
    version = os.getenv("APP_VERSION", "1.0.0")
    timestamp = datetime.now().isoformat()

    # Simulate latency if slow mode is active
    if chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])

    # Randomly trigger failures if error mode is active
    if chaos_state["mode"] == "error":
        if random.random() < chaos_state["rate"]:
            return jsonify({"error": "chaos error occurred"}), 500

    response = jsonify({
        "message": f"Welcome to SwiftDeploy ({mode} mode)",
        "version": version,
        "timestamp": timestamp
    })

    # Add identifying header for canary deployments
    if mode == "canary":
        response.headers["X-Mode"] = "canary"

    return response


@app.route("/healthz")
def healthz():
    mode = os.getenv("MODE", "stable")
    uptime = int(time.time() - start_time)

    # Health check reflects current chaos latency
    if chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])

    # Health check reflects current chaos error rate
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


@app.route("/chaos", methods=["POST"])
def chaos():
    mode = os.getenv("MODE", "stable")

    # Restrict chaos controls to canary environment only
    if mode != "canary":
        return jsonify({"error": "Chaos mode is only available in canary"}), 403

    data = request.get_json()

    if not data or "mode" not in data:
        return jsonify({"error": "Missing 'mode' in request body"}), 400

    global chaos_state
    chaos_mode = data["mode"]

    # Configure latency injection
    if chaos_mode == "slow":
        chaos_state["mode"] = "slow"
        chaos_state["duration"] = int(data.get("duration", 1))
        return jsonify({"status": "slow mode activated"})

    # Configure error rate injection
    elif chaos_mode == "error":
        chaos_state["mode"] = "error"
        chaos_state["rate"] = float(data.get("rate", 0.5))
        return jsonify({"status": "error mode activated"})

    # Reset to normal operation
    elif chaos_mode == "recover":
        chaos_state["mode"] = None
        chaos_state["duration"] = 0
        chaos_state["rate"] = 0
        return jsonify({"status": "recovered"})

    else:
        return jsonify({"error": "invalid chaos mode"}), 400


if __name__ == "__main__":
    # Start server on configurable port
    port = int(os.getenv("APP_PORT", 3000))
    app.run(host="0.0.0.0", port=port)