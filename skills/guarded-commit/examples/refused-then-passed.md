# Example: guarded-commit refuses, then passes

## Before — a combined call is blocked by the hook

The agent tries to be clever and do it all in one shell call:

```
$ git add -A && git commit -m "Phase 56: Push Policy Foundations"

BLOCKED — phase workflow: docs/progress-log.md is not staged.
Write the progress-log entry, tick the checklist box, and stage the file before committing.
```

Why: the PreToolUse hook runs **before** the command and scans the whole string. It sees
`git commit`, checks the staged tree, and the progress-log file isn't there yet (the `git add` in
the same string hasn't run from the hook's point of view). Blocked.

## After — write the log, then stage and commit in separate calls

```
# 1. progress-log skill writes the entry + ticks the checklist box

# 2. stage — a call with NO "git commit" in it
$ git add -A

# 3. commit — a SEPARATE call
$ git commit -m "$(cat <<'EOF'
Phase 56: Push Policy Foundations

Pure push-policy helpers + policy type + 12 unit tests.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
[main a1b2c3d] Phase 56: Push Policy Foundations

$ git log -1 --format="%H %s"
a1b2c3d…  Phase 56: Push Policy Foundations
```

The hook is satisfied (the log is staged), tests were green, the subject matches the convention,
and the agent trailer is present. **Nothing was pushed.**

## Also caught: red tests

```
$ commit-phase 56 Push Policy Foundations
REFUSED: tests are red. Fix tests first.
```

No staging, no commit — the refusal happens at step 1, before anything is touched.
