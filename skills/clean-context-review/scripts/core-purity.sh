#!/usr/bin/env bash
# PostToolUse hook on Edit|Write|MultiEdit: keep a "pure" layer free of forbidden imports.
# Generalized from the GitWarden DX track (rule: "src/core/ is pure").
#
# A pure layer (domain logic, parsers, decision engines) must not reach for I/O,
# platform, or DOM APIs — so it stays unit-testable in isolation and portable.
#
# Configure:
#   PURE_DIR    — path fragment that marks the pure layer   (default: src/core/)
#   PURE_BANNED — extended-regex of forbidden tokens
#                 (default: child_process|node:fs|'fs'|"fs"|electron|window\.|document\.)
#
# Fail-open: any internal error exits 0 so a broken hook never blocks real work.

INPUT=$(cat 2>/dev/null) || exit 0

PURE_DIR="${PURE_DIR:-src/core/}"
PURE_BANNED="${PURE_BANNED:-child_process|node:child_process|node:fs|\'fs\'|\"fs\"|electron|window\\.|document\\.}"

FILE=$(python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" <<< "$INPUT" 2>/dev/null) || exit 0

# Only enforce inside the pure layer.
case "$FILE" in
    *"$PURE_DIR"*) ;;
    *) exit 0 ;;
esac

if grep -qE "$PURE_BANNED" "$FILE" 2>/dev/null; then
    printf 'BLOCKED — pure layer: forbidden import/usage detected in:\n  %s\n' "$FILE" >&2
    printf 'The pure layer (%s) must not import I/O, platform, or DOM APIs.\n' "$PURE_DIR" >&2
    printf 'Move the impure logic out and inject it via an interface.\n' >&2
    exit 2
fi

exit 0
