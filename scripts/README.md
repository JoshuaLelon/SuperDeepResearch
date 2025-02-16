# Scripts

This folder contains various shell scripts for the Deep Research MCP project.

## Contents

- **`local_test.sh`**  
  Creates/activates a virtual environment, installs dependencies, and runs tests with coverage.  
  Example usage:
  ```
  ./scripts/local_test.sh
  ```

- **`deploy.sh`**  
  Builds and pushes a Docker image to your specified container registry (e.g., Google Container Registry), then optionally applies a Kubernetes deployment or another orchestrator step.  
  Example usage:
  ```
  ./scripts/deploy.sh
  ```

## Adding New Scripts

1. Create the shell script in this folder (e.g., `myscript.sh`).  
2. Update this `README.md` with a brief description of the script’s purpose and usage.

## Related Docs

- [../README.md](../README.md) for the overall project overview.