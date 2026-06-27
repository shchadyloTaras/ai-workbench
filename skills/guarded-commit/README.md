# guarded-commit

> **One task:** commit a finished unit of work on a strict convention — or refuse, with a reason.

## What it does

Makes exactly one commit, but only after the work earns it:

1. **Refuses on red tests** — runs the test command first; stops if anything fails.
2. **Refuses on a missing log** — confirms the progress-log entry + checklist box exist and are
   staged.
3. **Stages, then commits in separate steps** — so a "log-must-be-staged" hook that scans the whole
   command string can't block a combined `git add && git commit`.
4. **Commits** on the exact subject convention with the agent trailer.
5. **Never pushes.**

## The main file

[`SKILL.md`](SKILL.md) — the five steps and the separate-call mechanic.

## How to run it

- **As an agent skill:** copy to `.claude/skills/guarded-commit/`; ask _"commit phase N"_.
- **As a slash command:** copy `SKILL.md`'s body into `.claude/commands/commit-phase.md` with
  `argument-hint: "<id> <name...>"`; invoke `/commit-phase`.
- **Install the guards (recommended):** wire the two hooks in `.claude/settings.json` so the gates
  hold for *every* commit path, not just this skill:

  ```jsonc
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [
      { "type": "command", "command": ".claude/hooks/no-global-git-config.sh", "if": "Bash(git config*)" },
      { "type": "command", "command": ".claude/hooks/commit-needs-log.sh",     "if": "Bash(git commit*)" }
    ]
  }]
  ```

  Set `COMMIT_REQUIRES_STAGED` to your progress-log path if it isn't `docs/progress-log.md`.

## The rules it enforces

- [`references/commit-convention.md`](references/commit-convention.md) — subject formats and the
  always-on rules (one commit per unit, exact subject, agent trailer, never push).

## The scripts (automatic checking)

- [`scripts/commit-needs-log.sh`](scripts/commit-needs-log.sh) — blocks a commit unless the
  progress-log file is staged. Fail-open. Configurable path.
- [`scripts/no-global-git-config.sh`](scripts/no-global-git-config.sh) — blocks `git config
  --global/--system`. Fail-open.

## Example

[`examples/refused-then-passed.md`](examples/refused-then-passed.md) — a refusal (no log staged),
then the same commit succeeding once the log is written and staged.

## Why it's in this shape

The two refusals make "I committed but forgot the log / committed over red tests" impossible by
construction. The separate stage/commit calls are not a style choice — they're required when a
PreToolUse hook inspects the command string, because that hook runs *before* the command and would
otherwise see `git commit` with nothing staged yet.
