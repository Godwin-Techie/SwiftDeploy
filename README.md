# SwiftDeploy – Lightweight Deployment & Canary Release Tool

SwiftDeploy is a simple DevOps automation tool that manages application deployment, canary releases, configuration generation, and chaos testing.

# It uses:

- Docker Compose for container orchestration
- Nginx as a reverse proxy
- A Python CLI for deployment automation
- A Flask API that supports stable, canary, and chaos modes
  -SWIFTDEPLOY IS DESIGNED FOR FAST, LOCAL, REPRODUCIBLE DEPLOYMENTS WITH ZERO DOWNTIME DURING MODE PROMOTION.

# Features

- Automatic config generation (docker-compose.yml, nginx.conf)
- Stable to Canary(and vice-versa) promotion with health verification
- Chaos testing (slow, error, recover)
- Zero downtime container restart
- Nginx reverse proxy with custom headers
- Health endpoint with uptime + mode reporting

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

# 5. Generate Config Files

- SwiftDeploy generates docker-compose.yml and nginx.conf automatically.
  - swiftdeploy generate
  - This reads manifest.yml
  - Produces docker-compose.yml
  - Produces nginx.conf

# 6. Deploy the Application

- Start the containers and wait for health checks.
  - swiftdeploy deploy
  - Builds and starts containers
  - Waits for /healthz to return healthy
  - Confirms mode is active

# CLI Subcommands Walkthrough

- SwiftDeploy includes several CLI commands.

1.  # swiftdeploy init
    - Generates:
    - docker-compose.yml
    - nginx.conf
    - Based on manifest.yml.

2.  # swiftdeploy validate
    - validates:
    - docker-compose.yml
    - nginx.conf
    - Based on manifest.yml.

3.  # swiftdeploy deploy
    - Builds and starts the entire stack.
    - Starts Nginx + App
    - Waits for /healthz
    - Confirms mode (stable/canary)

4.  # swiftdeploy promote
    Switches between:
    - from stable mode to canary mode
    - from stable mode to canary mode
    - Then:
    - Saves manifest
    - Regenerates configs
    - Restarts ONLY the app container
    - Waits for health
    - Confirms new mode

# Testing Canary Mode

- curl -I http://localhost:8080/
  - you should see:
  - X-Mode: canary
  - X-Deployed-By: swiftdeploy

# Chaos Testing

Chaos mode is only active in canary.

- Enable slow mode run:
- curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d '{"mode":"slow","duration":5}'

- Enable error mode run:
  curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d '{"mode":"error","rate":0.5}'

- Recover mode run:
  curl -X POST http://localhost:8080/chaos \ -H "Content-Type: application/json" \ -d '{"mode":"recover"}'

# Health Endpoint

- Run:
  http://localhost:8080/healthz

- Return:
  {
  "status": "healthy",
  "uptime_seconds": 123,
  "mode": "canary"
  }
