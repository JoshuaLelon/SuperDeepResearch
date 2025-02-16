#!/usr/bin/env bash
# deploy.sh
# Handles production deployment.

set -e

echo "Building docker image..."
docker build -t deep-research-mcp .

echo "Tagging image..."
docker tag deep-research-mcp gcr.io/YOUR_PROJECT_ID/deep-research-mcp:latest

echo "Pushing to container registry..."
docker push gcr.io/YOUR_PROJECT_ID/deep-research-mcp:latest

echo "Deploying image via your orchestrator-of-choice..."
# e.g., kubectl apply -f k8s_deployment_manifest.yaml
# (or your favorite deployment solution)

echo "Deployment complete!" 