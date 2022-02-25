#!/bin/bash

# Enable strict mode:
set -euo pipefail

# Create local user:
cat > /slate_portal_user <<EOF
User_A95B266B-2327-4363-BEE0-A61DCF192DA6
WebPortal
slate@slateci.io
555-5555
SLATE
5B121807-7D5D-407A-8E22-5F001EF594D4
EOF

# Run portal:
cd /etc/slate
source venv/bin/activate
cd slate-website-python
./run_portal_docker.py
