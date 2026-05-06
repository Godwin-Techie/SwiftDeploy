import os
import sys
import time
import subprocess
import requests
import shutil

from cli.utils.loader import load_manifest
from cli.commands.generate import run_generate
from cli.utils.policy import generate_policy_data_files
from cli.utils.opa_client import evaluate_policy
from cli.utils.audit import write_audit_entry

def wait_for_opa():
    """Wait until OPA is reachable on localhost:8181."""
    opa_url = "http://localhost:8181/health?plugins"
    print("Waiting for OPA to become ready...")

    start = time.time()
    while time.time() - start < 20:
        try:
            r = requests.get(opa_url, timeout=2)
            if r.status_code == 200:
                print("OPA is ready.")
                return True
        except Exception:
            pass
        time.sleep(1)

    print("OPA did not become ready in time.")
    return False


def run_up():
    print("Starting SwiftDeploy stack... hold on.........")

    # 1. Load manifest
    manifest = load_manifest()

    # 2. Generate JSON policy files BEFORE starting containers
    generate_policy_data_files(manifest)

    # 3. Refresh configuration files
    run_generate()

    # 4. Start containers (OPA starts here)
    project_dir = os.getcwd()
    compose_file = os.path.join(project_dir, "docker-compose.yml")

    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True)
        print("Containers starting... this may take a few seconds.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start containers: {e}")
        sys.exit(1)

    # 5. Wait for OPA to be ready
    if not wait_for_opa():
        print("Cannot perform policy check because OPA is unavailable.")
        sys.exit(1)

    # 6. Collect host metrics for OPA
    host_metrics = {
        "cpu_load": os.getloadavg()[0],
        "disk_free_gb": shutil.disk_usage("/").free / (1024**3)
    }

    # 7. Ask OPA if deployment is allowed
    allowed, reason = evaluate_policy("infrastructure", host_metrics)

    write_audit_entry(
    action="deploy",
    decision="allow" if allowed else "deny",
    reason=reason,
    details=host_metrics
    )

    if not allowed:
        print(f"Deployment blocked by policy: {reason}")
        sys.exit(1)

    print("Policy check passed — proceeding with deployment.")

    # 8. Health check
    nginx_port = manifest["nginx"]["port"]
    health_url = f"http://localhost:{nginx_port}/healthz"

    print(f"Waiting for service to become healthy at {health_url}...")

    start = time.time()
    while time.time() - start < 60:
        try:
            r = requests.get(health_url, timeout=2)
            if r.status_code == 200:
                print("Service is healthy! SwiftDeploy stack is up and running.")
                sys.exit(0)
        except Exception:
            pass

        time.sleep(2)

    print("ERROR: Service did not become healthy within 60 seconds.")
    sys.exit(1)
