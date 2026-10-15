#!/usr/bin/env bash
# Runs when a Superset workspace is created. Idempotent.
set -euo pipefail
source "$(dirname "$0")/lib.sh"
cd "$WORKSPACE_DIR"

# No package dependencies; just make sure the tools we use are present.
for tool in pandoc python3; do
  command -v "$tool" >/dev/null || { echo "setup: $tool not found on PATH" >&2; exit 1; }
done

# Copy untracked env files from the main checkout (none today, but kept for
# when they appear). Build outputs and editor backups are deliberately skipped.
if [ -n "${SUPERSET_ROOT_PATH:-}" ] && [ "$SUPERSET_ROOT_PATH" != "$WORKSPACE_DIR" ]; then
  for f in "$SUPERSET_ROOT_PATH"/.env*; do
    [ -f "$f" ] || continue
    case "$f" in *~) continue ;; esac
    cp -n "$f" "$WORKSPACE_DIR/" && echo "setup: copied $(basename "$f")"
  done
fi

# Reserve a preview port for this workspace and render the book once.
mkdir -p "$STATE_DIR"
if [ ! -s "$PORT_FILE" ]; then
  pick_port > "$PORT_FILE"
fi
build_site
echo "setup: done (preview port $(cat "$PORT_FILE"))"
