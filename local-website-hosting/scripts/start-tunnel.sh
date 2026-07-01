#!/usr/bin/env bash
# Starts a Cloudflare Quick Tunnel to a local port and prints the public URL.
# No account/signup required. Requires: curl. Downloads cloudflared on first
# use if it isn't already installed.
#
# Usage: ./start-tunnel.sh <port> [log-file]

set -euo pipefail

PORT="${1:-}"
LOG_FILE="${2:-cloudflared.log}"

if [ -z "$PORT" ]; then
  echo "Usage: $0 <port> [log-file]" >&2
  exit 1
fi

echo "Checking local server on port $PORT..." >&2
if ! curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/" | grep -q "^2\|^3"; then
  echo "WARNING: http://localhost:$PORT/ did not respond with a 2xx/3xx status." >&2
  echo "Make sure your local server is running before sharing the tunnel URL." >&2
fi

CLOUDFLARED=""
if command -v cloudflared >/dev/null 2>&1; then
  CLOUDFLARED="cloudflared"
else
  echo "cloudflared not found — downloading..." >&2
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      DEST="${LOCALAPPDATA:-$HOME}/cloudflared/cloudflared.exe"
      mkdir -p "$(dirname "$DEST")"
      curl -sSL -o "$DEST" "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
      CLOUDFLARED="$DEST"
      ;;
    Darwin*)
      DEST="$HOME/.local/bin/cloudflared"
      mkdir -p "$(dirname "$DEST")"
      curl -sSL -o "/tmp/cloudflared.tgz" "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
      tar -xzf /tmp/cloudflared.tgz -C "$(dirname "$DEST")"
      chmod +x "$DEST"
      CLOUDFLARED="$DEST"
      ;;
    Linux*)
      DEST="$HOME/.local/bin/cloudflared"
      mkdir -p "$(dirname "$DEST")"
      curl -sSL -o "$DEST" "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
      chmod +x "$DEST"
      CLOUDFLARED="$DEST"
      ;;
    *)
      echo "Unsupported OS for auto-download. Install cloudflared manually: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" >&2
      exit 1
      ;;
  esac
fi

echo "Starting tunnel to http://localhost:$PORT ..." >&2
nohup "$CLOUDFLARED" tunnel --url "http://localhost:$PORT" > "$LOG_FILE" 2>&1 &
disown

# Poll the log for the assigned URL (quick tunnels take a few seconds).
for i in $(seq 1 15); do
  sleep 1
  URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOG_FILE" 2>/dev/null | head -1 || true)
  if [ -n "$URL" ]; then
    echo "$URL"
    exit 0
  fi
done

echo "Timed out waiting for tunnel URL. Check $LOG_FILE for details." >&2
exit 1
