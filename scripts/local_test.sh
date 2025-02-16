#!/usr/bin/env bash
# local_test.sh
# Runs local tests, including linting & coverage.

set -e

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running tests..."
pytest --cov=.

echo "Tests completed successfully." 