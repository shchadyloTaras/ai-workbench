#!/usr/bin/env bash
# PreToolUse hook on Bash(git commit*): block a commit unless the required
# progress-log file is staged. Generalized from the GitWarden DX track.
#
# Why: enforces "do not commit until the progress-log entry is written and staged"
# across ALL commit paths, regardless of which command or agent runs the commit.
#
# Configure the required staged path (substring match against staged file names):
#   COMMIT_REQUIRES_STAGED=docs/progress-log.md   (default)
# Bypass for WIP/fixup commits (set in the real shell, not inline — see note):
#   SKIP_LOG_GATE=1
#
# Fail-open: any internal error exits 0 so a broken hook never blocks real work.
#
# NOTE on bypass: when this runs as a Claude Code PreToolUse hook, it executes as
# a separate process BEFORE the Bash command, so an inline `SKIP_LOG_GATE=1 git commit`
# does NOT reach it. The bypass only works from a shell that has `export`ed the var.

INPUT=$(cat 2>/dev/null) || exit 0

[ "${SKIP_LOG_GATE:-0}" = "1" ] && exit 0

REQUIRED="${COMMIT_REQUIRES_STAGED:-docs/progress-log.md}"

CMD=$(python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" <<< "$INPUT" 2>/dev/null) || exit 0

# Defence in depth — only act on git commit commands.
case "$CMD" in
    *"git commit"*) ;;
    *) exit 0 ;;
esac

STAGED=$(git diff --cached --name-only 2>/dev/null) || exit 0

if printf '%s' "$STAGED" | grep -q "$REQUIRED"; then
    exit 0
fi

printf 'BLOCKED — phase workflow: %s is not staged.\n' "$REQUIRED" >&2
printf 'Write the progress-log entry, tick the checklist box, and stage the file before committing.\n' >&2
printf 'To bypass for WIP/fixup commits: export SKIP_LOG_GATE=1 (in your shell), then commit.\n' >&2
exit 2
