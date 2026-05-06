# SwiftDeploy – Lightweight Deployment, Canary & Policy-Gated Release Tool

SSwiftDeploy is a DevOps automation tool that manages application deployment, canary releases, configuration generation, chaos testing, and policy-based safety enforcement.
It is designed for fast, local, reproducible deployments with zero downtime and built-in safety guardrails.

# Core Stack:

- Docker Compose (container orchestration)
- Nginx (reverse proxy)
- Python CLI (deployment automation)
- Flask API (application service)
- Open Policy Agent (OPA) (policy engine)
- Prometheus-style metrics (/metrics endpoint)

# Key Features

# Deployment & Traffic Control

- Automatic config generation (docker-compose.yml, nginx.conf)
- Stable ↔ Canary promotion with health verification
- Zero-downtime container restarts
- Nginx reverse proxy with custom headers

# Chaos Engineering

- Inject slow, error, and recovery states
- Test system resilience in real-time

# Observability ("The Eyes")

- /metrics endpoint (Prometheus format)
  -Tracks:
  - Request throughput & errors
  - Latency (histogram)
  - App state (mode, uptime, chaos)

# Policy Engine ("The Brain")

- Open Policy Agent (OPA) sidecar
- Deployment decisions are NOT made in CLI
- All allow/deny logic lives in Rego policies

# Policy-Gated Deployments

- Pre-deploy checks
  - CPU, Memory, Disk validation
- Pre-promote checks
  - Error rate
  - P99 latency
- Deployments are blocked automatically if unsafe

# Observability CLI

- swiftdeploy status
  - Live metrics dashboard
  - Policy compliance view
  - Tracks req/sec + latency
- Audit System ("The Memory")
- Logs all events to history.jsonl
  - swiftdeploy audit generates:
  - Timeline of deployments & chaos events
  - Policy violations report

# Installation & Setup

Follow these steps to set up SwiftDeploy on your machine.

# 1. Clone the Repository

- Get the project files onto your machine.
  - Run:
  - git clone <https://github.com/Godwin-Techie/SwiftDeploy.git>
  - Enter the folder:
  - cd swiftdeploy

# 2. Install Python Dependencies

The CLI and API require Python packages.

- pip install -r requirements.txt
  - This ensure Python 3.10+ is installed
  - This installs Flask, PyYAML, Requests, etc.

# 3. Install Docker & Docker Compose

- SwiftDeploy uses Docker Compose to orchestrate containers.
  - Install Docker Desktop or Docker Engine
  - Confirm installation with: docker --version

# 4. Create Your Manifest File

- The manifest controls deployment mode and ports.
  - Create manifest.yml
    - •Example:
    - mode: stable
    - nginx:
    - port: 8080
    - app:
    - port: 5000

# 5. Initialize Project

- swiftdeploy init
  - Generates:
    - docker-compose.yml
    - nginx.conf
    - OPA configuration
    - policies/ directory
    - This reads manifest.yml

# 6. Deploy the Application

- swiftdeploy deploy
  - What happens:
    - Collect system metrics (CPU, disk, memory)
    - Send to OPA (pre-deploy)
    - OPA evaluates policies
    - Deploy OR Block with reason

# Decision Model

- CLI → sends input to OPA
- OPA → returns structured decision:
- {
  - "allow": false,
  - "reason": "Disk space below 10GB"
- }
- CLI must NOT override decisions

# Metrics Endpoint

- http://localhost:8080/metrics
  - Tracks:
- Throughput - http_requests_total{method, path, status_code}
- Latency - http_request_duration_seconds (histogram)
- State - app_uptime_seconds - app_mode (0=stable, 1=canary) - chaos_active (0=none, 1=slow, 2=error)

# Promotion (Policy-Gated)

- swiftdeploy promote
  - What happens:
    - Scrape /metrics
    - Compute:
    - Error rate
    - P99 latency
    - Send to OPA (pre-promote)
    - Promote OR Block

# Chaos Testing

- Only active in canary mode.
- Slow Mode:
- curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d {"mode":"slow","duration":5}'
- Error Mode:
- curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d '{"mode":"error","rate":0.5}'
- Recover:
- curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d '{"mode":"recover"}'

# Status Dashboard

- swiftdeploy status
- Displays:
  - Live req/sec
  - P99 latency
  - Current mode
  - Policy compliance (PASS/FAIL)

# Audit Report

- swiftdeploy audit
- Generates:
  - audit_report.md
  - Includes:
  - Deployment timeline
  - Chaos events
  - Policy violations

# Testing Canary Mode

- curl -I http://localhost:8080/
  - Headers:
    - X-Mode: canary
    - X-Deployed-By: swiftdeploy

# Design Philosophy

- Separation of Concerns
  - CLI → execution only
  - OPA → decision making
- Safety First
  - No deployment without validation
  - Canary must prove itself before promotion
- Observability-Driven
  - Metrics power decisions
  - Everything is measurable

# Bring everything down

- swiftdeploy teardown
- Removes all containers
- networks and volumes
- clean deletes generated configs
