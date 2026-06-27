#!/usr/bin/env bash
# verify-gate — run a project's quality gate in order, stop on the FIRST failure.
#
# Usage:
#   verify-gate.sh "<cmd1>" "<cmd2>" ...
# Each argument is one gate step, run in order. The script stops at the first
# non-zero exit, prints the last 5 lines of that step's output, and exits 1.
# On all-green it prints "GATE PASS" and exits 0.
#
# Example:
#   verify-gate.sh "npx tsc -p tsconfig.node.json --noEmit" \
#                  "npx tsc -p tsconfig.web.json --noEmit" \
#                  "npm test" "npm run lint"
#
# This script is project-agnostic: it knows nothing about your stack, only the
# ordered list of commands you hand it.

set -u

if [ "$#" -eq 0 ]; then
    printf 'verify-gate: no gate steps given.\n' >&2
    printf 'Usage: verify-gate.sh "<cmd1>" "<cmd2>" ...\n' >&2
    exit 2
fi

step=0
for cmd in "$@"; do
    step=$((step + 1))
    printf '── step %d: %s\n' "$step" "$cmd"
    # Capture combined output so we can show the tail on failure.
    out=$(eval "$cmd" 2>&1)
    code=$?
    if [ "$code" -ne 0 ]; then
        printf '%s\n' "$out" | tail -n 5
        printf '❌ GATE FAIL — step %d failed (exit %d): %s\n' "$step" "$code" "$cmd" >&2
        exit 1
    fi
    printf '✅ step %d ok\n' "$step"
done

printf 'GATE PASS — all %d checks green.\n' "$step"
exit 0
