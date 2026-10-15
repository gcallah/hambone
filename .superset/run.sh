#!/usr/bin/env bash
# Superset Run command: live HTML preview of the book on a per-workspace port.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
cd "$WORKSPACE_DIR"
mkdir -p "$STATE_DIR"

# Reuse the reserved port if it's still free, otherwise pick (and save) another.
port=$(cat "$PORT_FILE" 2>/dev/null || true)
if [ -z "$port" ] || ! port_is_free "$port"; then
  port=$(pick_port "$port")
  echo "$port" > "$PORT_FILE"
fi

build_site

# Rebuild whenever a chapter changes.
(
  stamp="$SITE_DIR/index.html"
  while sleep 2; do
    if [ -n "$(find chaps -name '*.md' -newer "$stamp" 2>/dev/null)" ]; then
      build_site && echo "preview: rebuilt"
    fi
  done
) &
watcher=$!

python3 -I -m http.server "$port" --bind 127.0.0.1 --directory "$SITE_DIR" &
server=$!

echo "$watcher $server" > "$PID_FILE"
cleanup() {
  kill "$watcher" "$server" 2>/dev/null || true
  rm -f "$PID_FILE"
}
trap cleanup EXIT INT TERM HUP

echo "Preview: http://127.0.0.1:$port/"
wait "$server"
