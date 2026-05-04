import yaml
import os
import sys

def load_manifest():
    # Define the source file for project configuration
    path = "manifest.yml"

    # Verify the existence of the configuration file
    if not os.path.exists(path):
        raise FileNotFoundError("manifest.yml not found in project root")

    # Parse YAML content using secure loading practices
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"manifest.yml contains invalid YAML: {e}")

    # Ensure the file is not empty
    if data is None:
        raise ValueError("manifest.yml is empty or invalid")

    # Confirm the root structure is a key-value mapping
    if not isinstance(data, dict):
        raise ValueError("manifest.yml must contain a YAML dictionary at the root")

    return data