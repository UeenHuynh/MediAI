#!/bin/bash
#
# Render.com Start Command
# Runs startup tasks then starts the API server
#

set -e

# Run startup script (migrations + seed users)
bash api/scripts/startup.sh

# Start API server with uvicorn
cd api
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
