import os
import sys
import subprocess
import shutil


def run_down():
    # Notify user of stack teardown initiation
    print("Tearing down SwiftDeploy stack... hold on.........")

    # Verify presence of the orchestration file before proceeding
    if not os.path.exists("docker-compose.yml"):
        print("No docker-compose.yml found. Nothing to tear down.")
        sys.exit(0)

    # Execute command to stop and remove containers, volumes, and orphans
    try:
        subprocess.run(
            ["docker", "compose", "down", "--volumes", "--remove-orphans"],
            check=True
        )
        print("Containers, networks, and volumes are being removed...")
    except subprocess.CalledProcessError as e:
        print(f"Failed to tear down stack: {e}")
        sys.exit(1)

    # Check for cleanup flag in command line arguments
    if "--clean" in sys.argv:
        print("Cleaning generated configuration files...")

        # Delete specific deployment configuration files
        for file in ["docker-compose.yml", "nginx.conf"]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed {file}")
                except Exception as e:
                    print(f"Failed to remove {file}: {e}")

        # Recursively delete the logs directory
        if os.path.exists("logs"):
            try:
                shutil.rmtree("logs")
                print("Removed logs directory")
            except Exception as e:
                print(f"Failed to remove logs directory: {e}")

    print("SwiftDeploy teardown complete. You're good to go!")
    sys.exit(0)