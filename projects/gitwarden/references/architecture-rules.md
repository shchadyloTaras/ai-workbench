# GitWarden — architecture rules

The rules `track-runner` cites in each phase brief and that the reviewers/hooks enforce. Numbered
to match GitWarden's `AGENTS.md`.

- **Rule #1 — pure core.** `src/core/` (Safety Engine, porcelain parser, types) is pure: no
  `child_process`, `fs`, `electron`, or DOM imports. Runs under plain Vitest.
- **Rule #2 — GitRunner only.** All git execution goes through `GitRunner` (`src/main/git/`), the
  single `execFile` caller, with controlled env, cancellation, and per-repo serialization.
- **Rule #3 — array args.** Git args are always an array, never string-interpolated; path args after
  `--`.
- **Rule #4 — injected services / `--local` only.** Core services are interfaces, injected for
  testability. Git config changes are `--local` only — never `--global`/`--system`.
- **Rule #5 — no secrets logged.** Never log tokens, passwords, keys, or device codes.
- **Rule #6 — destructive behind confirmation.** Destructive/remote actions require confirmation;
  irreversible ones (`git clean`) get a distinct stronger warning.
- **Rule #7 — AI advisory-only.** AI never triggers git actions, sets safety results, or bypasses a
  confirmation gate.

## Build order discipline

GitWarden builds **logic-first**: `src/core/` + git + safety ship with green tests before any UI.
A phase brief notes which of the above rules apply to that phase's scope, so the reviewer step in
`track-runner` knows which rule-set(s) to run.

## Which rule maps to which check

| Rule | Reviewer rule-set entry | Edit-time hook        |
| ---- | ----------------------- | --------------------- |
| #1   | purity P1               | `core-purity.sh`      |
| #2   | safety S4               | `execfile-guard.sh`   |
| #3   | safety S2               | (reviewer)            |
| #4   | purity P2 / `--local`   | `no-global-git-config.sh` |
| #5   | safety S1               | (reviewer)            |
| #6   | safety S3               | (reviewer)            |
| #7   | safety S5               | (reviewer)            |
