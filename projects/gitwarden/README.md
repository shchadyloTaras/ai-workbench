# Project: GitWarden

The worked example the `skills/` were generalized from. GitWarden is a cross-platform desktop Git
GUI focused on **safe multi-account GitHub usage** (prevent committing/pushing with the wrong
profile, identity, key, or repo). Stack: Electron + TypeScript (strict) + React (Vite); logic in a
pure `src/core/`; Vitest + Playwright.

Its developer-experience (DX) track produced the tooling these skills come from:

| GitWarden artifact (`.claude/…`)                          | Generalized into skill   |
| --------------------------------------------------------- | ------------------------ |
| `commands/run-track.md` + `commands/new-phase.md`         | `track-runner`           |
| `commands/verify-phase.md`                                | `verify-gate`            |
| `commands/commit-phase.md`                                | `guarded-commit`         |
| `commands/log-phase.md`                                   | `progress-log`           |
| `agents/core-purity-reviewer.md` + `agents/safety-reviewer.md` | `clean-context-review` |
| `hooks/commit-needs-log.sh`, `no-global-git-config.sh`    | `guarded-commit/scripts` |
| `hooks/core-purity.sh`, `execfile-guard.sh`               | `clean-context-review/scripts` |

This folder holds the **project-specific** values the skills plug into — the concrete rules,
gate commands, and review rule-sets — plus real examples. To run the skills against GitWarden, point
them here.

## References

- [`references/invariants.md`](references/invariants.md) — the 7 non-negotiable invariants.
- [`references/architecture-rules.md`](references/architecture-rules.md) — the architecture rules
  (pure core, single runner, array args, `--local` only, …).
- [`references/review-rulesets.md`](references/review-rulesets.md) — the exact purity + safety
  rule-sets the two reviewers enforce.
- [`references/gate-commands.md`](references/gate-commands.md) — GitWarden's five-command quality gate.

## Examples

- [`examples/progress-log-entry.md`](examples/progress-log-entry.md) — a real phase entry + checklist
  + derived status row.
- [`examples/wiring.md`](examples/wiring.md) — how GitWarden wired these as commands, agents, and
  hooks in `.claude/`.
