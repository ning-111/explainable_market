#!/usr/bin/env bash
# Start the Explainable Market demo app with the project venv.
set -e
cd "$(dirname "$0")"
source ../venv/bin/activate
exec python app.py
