import requests
import yaml
import os
import sys
import time

from cli.utils.loader import load_manifest
from cli.utils.policy import generate_policy_data_files
from cli.utils.opa_client import evaluate_policy
from cli.commands.promote import parse_prometheus_metrics


def run_status():
    print("\n=== SwiftDeploy Status ===\n")

    # 1. Load manifest
    manifest = load_manifest()
    mode = manifest.get("mode", "unknown")
    nginx_port = manifest["nginx"]["port"]

    print(f"Mode: {mode}")

    # 2. Scrape metrics
    metrics_url = f"http://localhost:{nginx_port}/metrics"
    try:
        resp = requests.get(metrics_url, timeout=3)
        text = resp.text
        error_rate, p99_latency_ms = parse_prometheus_metrics(text)
    except Exception:
        print("Metrics: unavailable")
        error_rate = None
        p99_latency_ms = None

    if error_rate is not None:
        print(f"Error Rate: {error_rate:.4f}")
        print(f"P99 Latency: {p99_latency_ms:.2f} ms")

    # 3. Infrastructure metrics
    infra_url = f"http://localhost:{nginx_port}/infra"
    try:
        infra = requests.get(infra_url, timeout=3).json()
        disk_free = infra.get("disk_free_gb")
        cpu_load = infra.get("cpu_load")
        print(f"Disk Free: {disk_free} GB")
        print(f"CPU Load: {cpu_load}")
    except Exception:
        print("Infrastructure metrics: unavailable")

    # 4. Chaos mode
    chaos_url = f"http://localhost:{nginx_port}/chaos/status"
    try:
        chaos = requests.get(chaos_url, timeout=3).json()
        print(f"Chaos Mode: {chaos.get('mode')}")
    except Exception:
        print("Chaos Mode: unavailable")

    # 5. Health
    health_url = f"http://localhost:{nginx_port}/healthz"
    try:
        health = requests.get(health_url, timeout=3).json()
        print(f"Health: {health.get('status')}")
        print(f"Uptime: {health.get('uptime_seconds')} seconds")
    except Exception:
        print("Health: unavailable")

    # 6. Policy evaluations
    print("\n--- Policy Evaluations ---")

    # Canary policy
    if error_rate is not None:
        allowed, reason = evaluate_policy("canary", {
            "error_rate": error_rate,
            "p99_latency_ms": p99_latency_ms
        })
        print(f"Canary Policy: {'ALLOW' if allowed else 'DENY'} ({reason})")

    # Infrastructure policy
    try:
        allowed, reason = evaluate_policy("infrastructure", {
            "disk_free_gb": disk_free,
            "cpu_load": cpu_load
        })
        print(f"Infrastructure Policy: {'ALLOW' if allowed else 'DENY'} ({reason})")
    except Exception:
        print("Infrastructure Policy: unavailable")

    print("\n===========================\n")
