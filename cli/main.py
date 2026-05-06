import sys

def main():
    # Check for minimum required command line arguments
    if len(sys.argv) < 2:
        print("swiftDeploy CLI")
        print("usage: swiftDeploy <command>")
        return

    # Extract the primary command argument
    command = sys.argv[1]

    # Route to manifest and environment validation
    if command == "validate":
        from cli.commands.validate import run_validate
        run_validate()

    # Route to initial configuration generation
    elif command == "init":
        from cli.commands.generate import run_generate
        run_generate()

    # Route to stack deployment and health monitoring
    elif command == "deploy":
        from cli.commands.up import run_up
        run_up()

    elif command == "status":
        from cli.commands.status import run_status
        run_status()

    elif command == "audit":
        from cli.commands.audit import run_audit
        run_audit()

    # Route to infrastructure removal and cleanup
    elif command == "teardown":
        from cli.commands.down import run_down
        run_down()

    # Route to deployment mode switching (e.g., stable to canary)
    elif command == "promote":
        from cli.commands.promote import run_promote
        run_promote()

    # Handle unsupported command inputs
    else:
        print(f"unknown command: {command}")
        print("available commands: init, deploy, teardown, promote, validate, chaos")

if __name__ == "__main__":
    # Execute the CLI entry point
    main()