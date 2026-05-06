import json
import os

def run_audit():
    log_file = "audit.log"

    if not os.path.exists(log_file):
        print("No audit log found.")
        return

    print("\n=== SwiftDeploy Audit Log ===\n")

    with open(log_file, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except:
                continue

            ts = entry["timestamp"]
            action = entry["action"].upper()
            decision = entry["decision"].upper()
            reason = entry["reason"]
            details = entry.get("details", {})

            print(f"[{ts}] {action} → {decision}")
            print(f"Reason: {reason}")

            for k, v in details.items():
                print(f"{k}: {v}")

            print("")

    print("=============================\n")
