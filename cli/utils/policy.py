import os
import json

def generate_policy_data_files(manifest):
    # Ensure policies directory exists
    os.makedirs("policies", exist_ok=True)

    # Extract policy sections
    infra = manifest.get("policy", {}).get("infrastructure", {})
    canary = manifest.get("policy", {}).get("canary", {})

    # Prepare JSON data in the correct structure
    infra_data = {
        "infrastructure": {
            "min_disk_gb": infra.get("min_disk_gb"),
            "max_cpu_load": infra.get("max_cpu_load")
        }
    }

    canary_data = {
        "canary": {
            "max_error_rate": canary.get("max_error_rate"),
            "max_p99_latency_ms": canary.get("max_p99_latency_ms")
        }
    }

    # Write JSON files
    with open("policies/infrastructure.json", "w") as f:
        json.dump(infra_data, f, indent=2)

    with open("policies/canary.json", "w") as f:
        json.dump(canary_data, f, indent=2)

    print("Policy data files generated successfully.")
