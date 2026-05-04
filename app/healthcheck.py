import urllib.request
import sys
import time

# Allow time for service startup
time.sleep(2)

try:
    # Check health endpoint with a 1s timeout
    with urllib.request.urlopen("http://localhost:3000/healthz", timeout=1) as response:
        # Exit with success if status is 200 OK
        if response.status == 200:
            sys.exit(0)
        else:
            # Fail for any other status code
            sys.exit(1)
except Exception:
    # Fail on connection error or timeout
    sys.exit(1)