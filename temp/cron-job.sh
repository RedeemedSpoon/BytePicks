#!/bin/bash

set -euxo pipefail

# --- Configuration ---
SERVER="root@bytepicks.com"
REMOTE_DIR="/root/Bytepicks"
FILE_LIST="credentials.json token.json channels.csv newsletter.db"

echo "--- Starting Sync Script ---"

# 1. Download the latest database
scp "$SERVER:$REMOTE_DIR/newsletter.db" .

# 2. Run the Python scripts in sequence
python youtube.py
python newsletter.py

# 3. Upload updated files and data
echo "Uploading results..."
scp $FILE_LIST "$SERVER:$REMOTE_DIR/"

# Safely upload 'data' directory contents if it exists and is not empty
if [ -d "data" ] && [ -n "$(ls -A data)" ]; then
  scp -r data/* "$SERVER:$REMOTE_DIR/data/"
fi

echo "--- Script Finished Successfully ---"
