#!/bin/bash

# Enable strict mode:
set -euo pipefail

# Run portal:
cd /etc/slate
source venv/bin/activate
cd slate-website-python
./run_portal_docker.py
