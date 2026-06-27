# track-runner

> **One task:** run a whole feature track phase-by-phase, to completion or to a stop-point.

## What it does

Given a project with a multi-phase **plan** and a **phase checklist**, `track-runner` walks every
still-pending phase in order and, for each one, runs the full ritual:

```
brief → implement → review → verify → log → commit   (one commit per phase)
```

It stops the moment anything goes wrong — a failed gate, a blocking review finding, an ambiguity
it shouldn't guess on, or a phase the plan marks as a stop-point. **It never pushes.**

It's the orchestrator: it delegates the actual per-phase steps to the other workbench skills
([`verify-gate`](../verify-gate/README.md), [`progress-log`](../progress-log/README.md),
[`guarded-commit`](../guarded-commit/README.md),
[`clean-context-review`](../clean-context-review/README.md)).

## The main file

[`SKILL.md`](SKILL.md) — the instructions the AI follows (RESOLVE → LOOP → FINISH).

## How to run it

- **As an agent skill:** copy this folder to `.claude/skills/track-runner/` in your project.
  Then ask: _"run the track for `<track-name>`"_ (optionally "step through it").
- **As a slash command:** copy the body of `SKILL.md` into `.claude/commands/run-track.md` with
  frontmatter `argument-hint: "<track-name> [--step]"` and
  `allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git*), Bash(npm*), Task`; invoke `/run-track`.
- **Configure it for your project:** point it at your project's rule files — plan file, checklist,
  gate commands, commit convention, review rule-sets. A complete worked set is in
  [`projects/gitwarden/references/`](../../projects/gitwarden/references/).

## The rules it enforces

- [`references/orchestration-rules.md`](references/orchestration-rules.md) — the five hard rules
  (one commit per phase, stop-on-red, no-guessing, no-push, respect invariants).
- [`references/phase-workflow.md`](references/phase-workflow.md) — the per-phase ritual in detail.

## Example

[`examples/run-track-session.md`](examples/run-track-session.md) — a resolve-and-loop session,
including a clean stop at a feature-complete stop-point.

## Why it's safe

Every gate between phases is a hard stop, not a warning. The only way the loop advances is green
tests + a clean review + a written log entry + a successful single-phase commit. If it can't get
there, it stops and tells you why — it never pushes and never papers over a red gate.
