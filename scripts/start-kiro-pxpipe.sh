#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  Loop Engineering — pxpipe launch wrapper
#  Cuts input token cost ~59-70% by rendering dense context as images.
#  Dashboard: http://127.0.0.1:47821
#  Research:  ../pxpipe-research.md
# ─────────────────────────────────────────────────────────────

PORT=47821

# ── Kill any stale proxy on the port ─────────────────────────
if lsof -ti tcp:$PORT &>/dev/null; then
  echo "→ Killing stale proxy on :$PORT"
  kill $(lsof -ti tcp:$PORT) 2>/dev/null || true
  sleep 1
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
npx --yes pxpipe-proxy
