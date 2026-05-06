import yaml
import subprocess
import sys
import time
import requests
import os
import re

from cli.utils.loader import load_manifest
from cli.commands.generate import run_generate
from cli.utils.policy import generate_policy_data_files
from cli.utils.opa_client import evaluate_policy
from cli.utils.audit import write_audit_entry


def parse_prometheus_metrics(text):
    """
    Extracts:
      - error_rate
      - p99 latency (ms)
    from Prometheus text format.
    """

    status_counts = {}
    buckets = []

    for line in text.splitlines():

        # -------------------------------
        # Parse http_requests_total
        # -------------------------------
        if line.startswith("http_requests_total"):
            m = re.match(r'.*status_code="(\d+)"}\s+([\d\.]+)', line)
            if m:
                code = m.group(1)
                value = float(m.group(2))
                status_counts[code] = value

        # -------------------------------
        # Parse histogram buckets
        # -------------------------------
        if line.startswith("http_request_duration_seconds_bucket"):
            m = re.match(r'.*le="([\d\.]+)".*}\s+([\d\.]+)', line)
            if m:
                boundary = float(m.group(1))   # seconds
                count = float(m.group(2))      # cumulative count
                buckets.append((boundary, count))

    # Compute error rate
    total = sum(status_counts.values())
    errors = status_counts.get("500", 0)
    error_rate = errors / total if total > 0 else 0

    # Compute p99 latency (ms)
    p99_latency_ms = 0

    if buckets:
        buckets.sort(key=lambda x: x[0])
        total_reqs = buckets[-1][1]

        if total_reqs > 0:
            target = total_reqs * 0.99

            for boundary, count in buckets:
                if count >= target:
                    p99_latency_ms = boundary * 1000  # convert seconds → ms
                    break

    return error_rate, p99_latency_ms



def run_promote():
    print("Promoting deployment mode... hold on.........")

    # 1. Load manifest
    manifest = load_manifest()

    # 2. Generate JSON policy files
    generate_policy_data_files(manifest)

    # 3. Scrape canary metrics
    nginx_port = manifest["nginx"]["port"]
    metrics_url = f"http://localhost:{nginx_port}/metrics"

    try:
        resp = requests.get(metrics_url, timeout=3)
        text = resp.text
    except Exception:
        print("Failed to scrape metrics — cannot evaluate canary policy.")
        sys.exit(1)

    # Parse Prometheus text
    error_rate, p99_latency_ms = parse_prometheus_metrics(text)

    canary_metrics = {
        "error_rate": error_rate,
        "p99_latency_ms": p99_latency_ms
    }

    # 4. Ask OPA if promotion is allowed
    allowed, reason = evaluate_policy("canary", canary_metrics)

    write_audit_entry(
    action="promote",
    decision="allow" if allowed else "deny",
    reason=reason,
    details=canary_metrics
    )

    if not allowed:
        print(f"Promotion blocked by policy: {reason}")
        sys.exit(1)

    print("Policy check passed — proceeding with promotion.")

    # 5. Toggle mode
    current_mode = manifest.get("mode", "stable")
    new_mode = "canary" if current_mode == "stable" else "stable"
    manifest["mode"] = new_mode

    with open("manifest.yml", "w") as f:
        yaml.dump(manifest, f)

    print(f"Mode switched from {current_mode} → {new_mode}")

    # 6. Regenerate config files
    run_generate()

    # 7. Restart only the app container
    service_name = "app"
    project_dir = os.getcwd()
    compose_file = os.path.join(project_dir, "docker-compose.yml")

    try:
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "up", "-d", "--no-deps", "--force-recreate", service_name],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart service container: {e}")
        sys.exit(1)

    # 8. Health check for new mode
    health_url = f"http://localhost:{nginx_port}/healthz"
    print(f"Waiting for new mode to become healthy at {health_url}...")

    start = time.time()
    while time.time() - start < 30:
        try:
            r = requests.get(health_url, timeout=2)
            if r.status_code == 200 and r.json().get("mode") == new_mode:
                print(f"Promotion successful! Service is now running in {new_mode} mode.")
                sys.exit(0)
        except Exception:
            pass

        time.sleep(2)

    print("Promotion failed: service did not switch modes within 30 seconds.")
    sys.exit(1)
