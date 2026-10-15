#!/usr/bin/env bash
# Runs when a Superset workspace is deleted: stop the preview, release the port.
set -uo pipefail
source "$(dirname "$0")/lib.sh"

if [ -f "$PID_FILE" ]; then
  # shellcheck disable=SC2046
  kill $(cat "$PID_FILE") 2>/dev/null || true
fi
rm -rf "$STATE_DIR"
echo "teardown: done"
