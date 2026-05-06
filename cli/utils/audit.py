import json
import time

AUDIT_LOG = "audit.log"

def write_audit_entry(action, decision, reason, details=None):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "decision": decision,
        "reason": reason,
        "details": details or {}
    }

    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
