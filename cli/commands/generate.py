from cli.utils.loader import load_manifest
from cli.utils.renderer import render_template
from cli.utils.policy import generate_policy_data_files
import os
import sys

def run_generate():
    # Notify user that the generation process has started
    print("Generating configuration files... please hold on.........")

    # Import data from the manifest file
    manifest = load_manifest()

    # Generate policy JSON files
    try:
        generate_policy_data_files(manifest)
    except Exception as e:
        print(f"Error generating policy data files: {e}")
        sys.exit(1)

    # Map manifest data to the template context object
    context = {
        "services": manifest["services"],
        "nginx": manifest["nginx"],
        "network": manifest["network"],
        "mode": manifest.get("mode", "stable"),
        "app_version": manifest.get("version", "1.0.0"),
        "app_port": manifest["services"]["port"],
        "replicas": manifest["services"].get("replicas", 1),
        "env": manifest["services"].get("env", {}),
        "volumes": manifest["services"].get("volumes", []),
        "routes": manifest["nginx"].get("routes", [])
    }

    # Process and write the Docker Compose configuration file
    try:
        compose_output = render_template("docker-compose.yml.j2", context)
        with open("docker-compose.yml", "w") as f:
            f.write(compose_output)
    except Exception as e:
        print(f"Error generating docker-compose.yml: {e}")
        sys.exit(1)

    # Process and write the Nginx server configuration file
    try:
        nginx_output = render_template("nginx.conf.j2", context)
        with open("nginx.conf", "w") as f:
            f.write(nginx_output)
    except Exception as e:
        print(f"Error generating nginx.conf: {e}")
        sys.exit(1)

    print("congratulations! docker-compose.yml, nginx.conf, and policy files generated successfully, you're good to go!")
