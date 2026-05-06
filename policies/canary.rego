package canary

default decision = {
    "allow": false,
    "reason": "Policy evaluation not completed"
}

max_error := data.canary.max_error_rate
max_p99 := data.canary.max_p99_latency_ms

# Error rate too high
decision = {
    "allow": false,
    "reason": "Error rate above allowed maximum"
} if {
    input.error_rate > max_error
}

# Latency too high (only if error rate is OK)
decision = {
    "allow": false,
    "reason": "P99 latency above allowed maximum"
} if {
    input.error_rate <= max_error
    input.p99_latency_ms > max_p99
}

# Successful decision (only if both are OK)
decision = {
    "allow": true,
    "reason": "All checks passed"
} if {
    input.error_rate <= max_error
    input.p99_latency_ms <= max_p99
}
