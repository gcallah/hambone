# Shared helpers for the Superset lifecycle scripts. Sourced, not executed.

WORKSPACE_DIR="${SUPERSET_WORKSPACE_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STATE_DIR="$WORKSPACE_DIR/.superset/.local"
SITE_DIR="$STATE_DIR/site"
PORT_FILE="$STATE_DIR/port"
PID_FILE="$STATE_DIR/pids"

PORT_MIN=4100
PORT_MAX=4999

# Exit 0 if nothing is listening on 127.0.0.1:$1.
port_is_free() {
  python3 -I -c '
import socket, sys
s = socket.socket()
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
except OSError:
    sys.exit(1)
finally:
    s.close()
' "$1"
}

# Echo a free port, starting from a per-workspace hash (or $1 if given) so
# parallel workspaces land on different ports.
pick_port() {
  local span=$((PORT_MAX - PORT_MIN + 1))
  local start="${1:-}"
  if [ -z "$start" ]; then
    local hash
    hash=$(printf '%s' "$WORKSPACE_DIR" | cksum | cut -d' ' -f1)
    start=$((PORT_MIN + hash % span))
  fi
  local i p
  for ((i = 0; i < span; i++)); do
    p=$((PORT_MIN + (start - PORT_MIN + i) % span))
    if port_is_free "$p"; then
      echo "$p"
      return 0
    fi
  done
  echo "No free port in $PORT_MIN-$PORT_MAX" >&2
  return 1
}

# Build the public site (bin/site) into the preview directory.
build_site() {
  "$WORKSPACE_DIR/bin/site" -o "$SITE_DIR" >/dev/null
}
