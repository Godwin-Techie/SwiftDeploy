import os
import sys
import subprocess
import shutil


def run_down():
    print("Tearing down SwiftDeploy stack... hold on.........")

    # Define cleanup paths FIRST (fixes UnboundLocalError)
    generated_files = [
        "docker-compose.yml",
        "nginx.conf",
        "history.jsonl",
        "audit_report.md"
    ]

    logs_dir = "logs"
    policy_data_dir = "policies/data"
    bundles_dir = "bundles"

    # Stop containers if compose file exists
    if os.path.exists("docker-compose.yml"):
        try:
            subprocess.run(
                ["docker", "compose", "down", "--volumes", "--remove-orphans"],
                check=True
            )
            print("Containers, networks, and volumes removed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to tear down stack: {e}")
            sys.exit(1)
    else:
        print("No docker-compose.yml found. Nothing to tear down.")

    # CLEAN MODE
    if "--clean" in sys.argv:
        print("Cleaning all generated SwiftDeploy files...")

        # 1. Remove generated files
        for file in generated_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed {file}")
                except Exception as e:
                    print(f"Failed to remove {file}: {e}")

        # 2. Remove logs directory
        if os.path.exists(logs_dir):
            try:
                shutil.rmtree(logs_dir)
                print("Removed logs directory")
            except Exception as e:
                print(f"Failed to remove logs directory: {e}")

        # 3. Remove OPA policy data directory
        if os.path.exists(policy_data_dir):
            try:
                shutil.rmtree(policy_data_dir)
                print("Removed policy data directory")
            except Exception as e:
                print(f"Failed to remove policy data directory: {e}")

        # 4. Remove bundles directory
        if os.path.exists(bundles_dir):
            try:
                shutil.rmtree(bundles_dir)
                print("Removed bundles directory")
            except Exception as e:
                print(f"Failed to remove bundles directory: {e}")

    print("SwiftDeploy teardown complete. You're good to go!")
    sys.exit(0)
