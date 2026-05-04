import os
import sys
import time
import subprocess
import requests

from cli.utils.loader import load_manifest
from cli.commands.generate import run_generate


def run_up():
    # Notify user of stack initialization
    print("Starting SwiftDeploy stack... hold on.........")

    # Refresh configuration files before deployment
    run_generate()

    # Define path for the orchestration file
    project_dir = os.getcwd()
    compose_file = os.path.join(project_dir, "docker-compose.yml")

    # Launch the container stack in detached mode
    try:
        subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], check=True)
        print("Containers starting... this may take a few seconds.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start containers: {e}")
        sys.exit(1)

    # Load manifest to determine the active health check endpoint
    manifest = load_manifest()
    nginx_port = manifest["nginx"]["port"]
    health_url = f"http://localhost:{nginx_port}/healthz"

    print(f"Waiting for service to become healthy at {health_url}...")

    # Monitor service health with a 60-second timeout
    start = time.time()
    while time.time() - start < 60:
        try:
            r = requests.get(health_url, timeout=2)
            # Successful response indicates stack readiness
            if r.status_code == 200:
                print("Service is healthy! SwiftDeploy stack is up and running. You're good to go!")
                sys.exit(0)
        except Exception:
            pass

        time.sleep(2)

    # Report failure if health threshold is not met
    print("ERROR: Service did not become healthy within 60 seconds.")
    sys.exit(1)