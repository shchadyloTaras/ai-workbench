#!/usr/bin/env bash
# PostToolUse hook on Edit|Write|MultiEdit: warn/block when subprocess-spawning APIs
# appear outside their one allowed directory.
# Generalized from the GitWarden DX track (rule: "all git execution goes through one runner").
#
# Funnelling every subprocess spawn through a single module keeps env control,
# cancellation, and argument-array safety in exactly one auditable place.
#
# Configure:
#   SPAWN_ALLOWED_DIR — the one directory allowed to spawn   (default: src/main/git/)
#   SPAWN_BANNED      — extended-regex of spawn APIs          (default: execFile|child_process|[^A-Za-z]spawn\()
#
# Scope: only TS/JS source files; test files are exempt (they spawn to build fixtures).
# Fail-open: any internal error exits 0 so a broken hook never blocks real work.

INPUT=$(cat 2>/dev/null) || exit 0

SPAWN_ALLOWED_DIR="${SPAWN_ALLOWED_DIR:-src/main/git/}"
SPAWN_BANNED="${SPAWN_BANNED:-execFile|child_process|[^A-Za-z]spawn\\(}"

FILE=$(python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" <<< "$INPUT" 2>/dev/null) || exit 0

[ -z "$FILE" ] && exit 0

# Allow: the designated spawn home.
case "$FILE" in
    *"$SPAWN_ALLOWED_DIR"*) exit 0 ;;
esac

# Only scan TypeScript/JavaScript source; docs/markdown/JSON are never source.
case "$FILE" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) ;;
    *) exit 0 ;;
esac

# Allow: test files (they may spawn to set up real fixtures).
case "$FILE" in
    *.test.ts|*.test.js|*.spec.ts|*.spec.js) exit 0 ;;
    */tests/*|*/test/*|*/__tests__/*) exit 0 ;;
esac

if grep -qE "$SPAWN_BANNED" "$FILE" 2>/dev/null; then
    printf 'BLOCKED — single-runner rule: subprocess-spawn API found outside %s:\n  %s\n' "$SPAWN_ALLOWED_DIR" "$FILE" >&2
    printf 'All process spawning must go through the one runner in %s.\n' "$SPAWN_ALLOWED_DIR" >&2
    exit 2
fi

exit 0
