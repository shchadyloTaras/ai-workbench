#!/usr/bin/env bash
# PreToolUse hook on Bash(git config*): block git config --global / --system.
# Generalized from the GitWarden DX track.
#
# Why: a repo's tooling should only ever touch its OWN (--local) git config.
# Changing --global / --system config silently reaches across every repo on the
# machine — exactly the kind of irreversible, out-of-scope side effect a guarded
# workflow must refuse.
#
# Fail-open: any internal error exits 0 so a broken hook never blocks real work.

INPUT=$(cat 2>/dev/null) || exit 0

CMD=$(python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" <<< "$INPUT" 2>/dev/null) || exit 0

if printf '%s' "$CMD" | grep -qE 'git[[:space:]].*config.*--(global|system)'; then
    printf 'BLOCKED — only --local config is allowed: git config --global / --system are forbidden.\n' >&2
    printf 'Use repo-scoped config only: git config --local <key> <value>\n' >&2
    exit 2
fi

exit 0
