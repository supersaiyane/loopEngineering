#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  Loop Engineering — pxpipe launch wrapper
#  An optional proxy for rendering context as images; savings vary.
#  Dashboard: http://127.0.0.1:47821
#  Research:  ../pxpipe-research.md
# ─────────────────────────────────────────────────────────────

PORT=47821

if ! command -v pxpipe-proxy >/dev/null 2>&1; then
  echo "pxpipe-proxy is not installed. Review the package before installing it; see the README." >&2
  exit 1
fi

if ! command -v lsof >/dev/null 2>&1; then
  echo "Cannot check whether port $PORT is in use: lsof is not installed." >&2
  exit 1
fi

# ── Refuse to stop another process using the port ────────────
if lsof -ti tcp:$PORT &>/dev/null; then
  echo "Port $PORT is already in use. Stop the existing process before starting pxpipe." >&2
  exit 1
fi

# ── Print instructions — open Kiro in a SEPARATE terminal ────
echo ""
echo "  ┌──────────────────────────────────────────────────────┐"
echo "  │  pxpipe proxy starting on http://127.0.0.1:$PORT    │"
echo "  │                                                      │"
echo "  │  Open Kiro in a NEW terminal tab with:              │"
echo "  │    ANTHROPIC_BASE_URL=http://127.0.0.1:$PORT kiro   │"
echo "  │                                                      │"
echo "  │  Or Claude Code:                                     │"
echo "  │    ANTHROPIC_BASE_URL=http://127.0.0.1:$PORT claude │"
echo "  │                                                      │"
echo "  │  Dashboard: http://127.0.0.1:$PORT/                 │"
echo "  │  Events:    ~/.pxpipe/events.jsonl                   │"
echo "  │                                                      │"
echo "  │  GUARD 3: git SHAs · file:line · camelCase IDs      │"
echo "  │  always re-fetch exact strings — never recall from   │"
echo "  │  memory (old turns may be images, not text)          │"
echo "  │                                                      │"
echo "  │  Ctrl+C to stop the proxy.                           │"
echo "  └──────────────────────────────────────────────────────┘"
echo ""

# ── Run proxy in FOREGROUND — keep this terminal open ────────
# Proxy stays alive as long as this terminal is open.
# Ctrl+C cleanly stops it.
exec pxpipe-proxy
