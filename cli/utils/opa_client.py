import requests

OPA_URL = "http://localhost:8181/v1/data"

def evaluate_policy(package: str, input_data: dict):
    """
    Sends input data to OPA and retrieves the combined decision object
    containing both allow and reason.
    """
    url = f"{OPA_URL}/{package}/decision"
    response = requests.post(url, json={"input": input_data})

    result = response.json().get("result", {})

    # FIX: read from result["decision"]
    decision = result.get("decision", result)
    allow = decision.get("allow", False)
    reason = decision.get("reason", "No reason provided")

    return allow, reason
