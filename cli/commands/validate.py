import os
import sys
import subprocess
import socket
import requests
import shutil

from cli.utils.loader import load_manifest
from cli.utils.opa_client import evaluate_policy
from cli.utils.audit import write_audit_entry


def run_validate():
    print("Validating manifest, hold on.........")

    # 1. Load manifest
    try:
        manifest = load_manifest()
    except Exception as e:
        print(f"manifest.yaml is missing or invalid YAML: {e}")
        sys.exit(1)

    # 2. Schema validation
    errors = validate_manifest(manifest)
    if errors:
        print("Manifest validation failed:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)

    # 3. Check Docker image exists
    image = manifest["services"]["image"]
    if not docker_image_exists(image):
        print(f"Docker image not found locally: {image}")
        sys.exit(1)

    # 4. Check port availability
    nginx_port = manifest["nginx"]["port"]
    if port_in_use(nginx_port):
        print(f"Nginx port {nginx_port} is already in use on the host.")
        sys.exit(1)

    # 5. Validate nginx.conf syntax
    if os.path.exists("nginx.conf"):
        nginx_image = manifest["nginx"]["image"]
        if not validate_nginx_config_docker(nginx_image):
            print("nginx.conf syntax is invalid.")
            sys.exit(1)
    else:
        print("nginx.conf not found — run `swiftdeploy init` first.")
        sys.exit(1)

   # 6. Collect host metrics (app is not running yet)
    host_metrics = {
    "disk_free_gb": shutil.disk_usage("/").free / (1024**3),
    "cpu_load": os.getloadavg()[0]
    }
    infra_metrics = host_metrics

    # 7. Evaluate OPA policy
    print("Infrastructure metrics collected:")
    print(f" - Disk Free: {infra_metrics['disk_free_gb']:.2f} GB")
    print(f" - CPU Load: {infra_metrics['cpu_load']:.2f}")

    print("Manifest validation successful! You're good to go.")
    sys.exit(0)


def docker_image_exists(image_name):
    result = subprocess.run(
        ["docker", "image", "inspect", image_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def validate_nginx_config_docker(nginx_image):
    nginx_conf_path = os.path.abspath("nginx.conf")

    cmd = [
        "docker", "run", "--rm",
        "--add-host", "app:127.0.0.1",
        "-v", f"{nginx_conf_path}:/etc/nginx/nginx.conf:ro",
        nginx_image,
        "nginx", "-t"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def validate_manifest(manifest):
    errors = []

    # Validate application service
    services = manifest.get("services")
    if not services:
        errors.append("Missing required section: services")
    else:
        image = services.get("image")
        if not image or not isinstance(image, str) or not image.strip():
            errors.append("Missing required field: services.image")

        port = services.get("port")
        if port is None:
            errors.append("Missing required field: services.port")
        else:
            if not isinstance(port, int):
                errors.append("Invalid type for field: services.port must be an integer")
            elif port < 1 or port > 65535:
                errors.append("Invalid value for field: services.port must be between 1 and 65535")

    # Validate nginx
    nginx = manifest.get("nginx")
    if not nginx:
        errors.append("Missing required section: nginx")
    else:
        image = nginx.get("image")
        if not image or not isinstance(image, str) or not image.strip():
            errors.append("Missing required field: nginx.image")

        port = nginx.get("port")
        if port is None:
            errors.append("Missing required field: nginx.port")
        else:
            if not isinstance(port, int):
                errors.append("Invalid type for field: nginx.port must be an integer")
            elif port < 1 or port > 65535:
                errors.append("Invalid value for field: nginx.port must be between 1 and 65535")

    # Validate network
    network = manifest.get("network")
    if not network:
        errors.append("Missing required section: network")
    else:
        name = network.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            errors.append("Missing required field: network.name")

        driver = network.get("driver_type")
        if not driver or not isinstance(driver, str) or not driver.strip():
            errors.append("Missing required field: network.driver_type")

    return errors
