import yaml
import subprocess
import sys
import time
import requests
import os

from cli.utils.loader import load_manifest
from cli.commands.generate import run_generate


def run_promote():
    # Notify user of deployment state transition
    print("Promoting deployment mode... hold on.........")

    # Retrieve current configuration from manifest
    manifest = load_manifest()

    # Toggle between stable and canary deployment modes
    current_mode = manifest.get("mode", "stable")
    new_mode = "canary" if current_mode == "stable" else "stable"
    manifest["mode"] = new_mode

    # Persist the updated mode to the manifest file
    with open("manifest.yml", "w") as f:
        yaml.dump(manifest, f)

    print(f"Mode switched from {current_mode} → {new_mode}")

    # Rebuild configuration files based on the new mode
    run_generate()

    # Define the specific service target for the restart
    service_name = "app"
    print(f"Restarting service container: {service_name}")
    project_dir = os.getcwd()
    compose_file = os.path.join(project_dir, "docker-compose.yml")

    # Hot-reload the specific service without affecting other containers
    try:
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "up", "-d", "--no-deps", "--force-recreate", service_name],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart service container: {e}")
        sys.exit(1)

    # Initialize health check parameters
    nginx_port = manifest["nginx"]["port"]
    health_url = f"http://localhost:{nginx_port}/healthz"
    print(f"Waiting for new mode to become healthy at {health_url}...")

    # Poll the health endpoint for status and mode verification
    start = time.time()
    while time.time() - start < 30:
        try:
            r = requests.get(health_url, timeout=2)
            # Confirm service is healthy and reporting the correct mode
            if r.status_code == 200 and r.json().get("mode") == new_mode:
                print(f"yay!Promotion successful! Service is now running in {new_mode} mode.")
                sys.exit(0)
        except Exception:
            pass

        time.sleep(2)

    # Exit with error if health check fails to validate within timeout
    print("Promotion failed: service did not switch modes within 30 seconds.")
    sys.exit(1)