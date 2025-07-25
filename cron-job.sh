#!/bin/bash

set -euxo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_CMD=$(which python)

JOB1="0 2 * * * cd $DIR && $PYTHON_CMD server/youtube.py"
JOB2="0 3 * * * cd $DIR && $PYTHON_CMD server/newsletter.py"

if ! crontab -l 2>/dev/null | grep -qF "$JOB1"; then
  echo "Adding cron job for youtube.py..."
  (crontab -l 2>/dev/null; echo "$JOB1") | crontab -
fi

if ! crontab -l 2>/dev/null | grep -qF "$JOB2"; then
  echo "Adding cron job for newsletter.py..."
  (crontab -l 2>/dev/null; echo "$JOB2") | crontab -
fi

echo "Script finished."
