---
name: guarded-commit
description: Commit a unit of work on a strict subject convention, but REFUSE first if tests are red or the required progress-log entry is missing/unstaged. Stages and commits in separate steps so a "log-must-be-staged" hook can't block a combined call. Never pushes. Use when committing a completed phase/task in a project that gates commits on green tests + a written log.
---

# guarded-commit

You produce **one** commit with an exact subject convention — but only after the work has earned
it. You refuse on red tests or a missing progress-log entry, and you **never push**.

## Step 1 — Refuse on red tests

Run the project's test command. If it fails (exit ≠ 0), STOP and report:

```
REFUSED: tests are red. Fix tests first.
```

Do not stage or commit.

## Step 2 — Refuse on a missing log entry

If the project gates commits on a written progress-log entry (most do — see `progress-log`),
confirm both exist for this unit of work:

- a progress-log entry whose heading names this phase/task, and
- a ticked checklist box for it.

If either is missing, STOP and report:

```
REFUSED: no progress-log entry for <id>. Run the progress-log step first.
```

Do not stage. (A project may also enforce this with a PreToolUse hook — see
`scripts/commit-needs-log.sh`. Treat a firing hook as a real miss: write the log entry, don't
bypass the hook.)

## Step 3 — Stage, then commit — in SEPARATE calls

This is the load-bearing mechanic. If the project's "log must be staged" hook inspects the **whole**
shell command string, a combined `git add … && git commit …` is blocked because the string
contains `git commit` *before* the stage has been observed. So:

1. **One shell call with no `git commit` in it** — stage everything, including the progress-log
   file (e.g. `git add -A`).
2. **A separate shell call** — `git commit` with the message below.

## Step 4 — The message

- **Subject:** the project's exact convention (e.g. `Phase N: <name>` or `<type>(<scope>): <summary>`).
  Read it from the project's commit-convention reference.
- **Body:** one line summarizing what was built.
- **Trailer:** the agent's identity, e.g. `Co-Authored-By: <Agent> <noreply@anthropic.com>`.

```bash
git commit -m "$(cat <<'EOF'
<subject>

<one-line body>

Co-Authored-By: <Agent> <noreply@anthropic.com>
EOF
)"
```

## Step 5 — Report, and never push

Print the commit hash and subject (`git log -1 --format="%H %s"`). Do **not** run `git push` under
any circumstance, even if asked within this skill — pushing is a separate, explicit, manual step.

## Bundled guards (optional, project-installable)

- `scripts/commit-needs-log.sh` — PreToolUse hook on `git commit`: blocks the commit unless the
  required progress-log file is staged. Fail-open (any internal error exits 0). Configure the
  required path via `$COMMIT_REQUIRES_STAGED`.
- `scripts/no-global-git-config.sh` — PreToolUse hook on `git config`: blocks `--global` /
  `--system` config changes so a repo can only touch its `--local` config. Fail-open.
