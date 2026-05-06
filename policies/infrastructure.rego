package infrastructure

default decision = {
    "allow": false,
    "reason": "Policy evaluation not completed"
}

min_disk := data.infrastructure.min_disk_gb
max_cpu := data.infrastructure.max_cpu_load

# Disk too low
decision = {
    "allow": false,
    "reason": "Disk space below required minimum"
} if {
    input.disk_free_gb < min_disk
}

# CPU too high (only if disk is OK)
decision = {
    "allow": false,
    "reason": "CPU load above allowed maximum"
} if {
    input.disk_free_gb >= min_disk
    input.cpu_load > max_cpu
}

# Successful decision (only if both are OK)
decision = {
    "allow": true,
    "reason": "All checks passed"
} if {
    input.disk_free_gb >= min_disk
    input.cpu_load <= max_cpu
}
