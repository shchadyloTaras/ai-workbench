# progress-log

> **One task:** record a finished phase/task — append the entry, tick the box, re-derive the status.

## What it does

Keeps a project's progress doc honest and append-only. For one completed unit of work it makes
exactly three edits — append a dated entry (newest last), tick the checklist box, and re-derive any
status roll-up that depends on the checklist — then reports what changed. **It does not commit.**

Its core principle is reusable on its own: **one source of truth (the checklist), everything else
is a derived view that must be re-derived in the same edit.** That's what stops a status table from
quietly lying about what's done.

## The main file

[`SKILL.md`](SKILL.md) — the single-source-of-truth rule and the six steps.

## How to run it

- **As an agent skill:** copy to `.claude/skills/progress-log/`; ask _"log phase N — <summary>"_.
- **As a slash command:** copy `SKILL.md`'s body into `.claude/commands/log-phase.md` with
  `argument-hint: "<id> <name> — <summary>"`; invoke `/log-phase`.

## The rules it enforces

- [`references/log-format.md`](references/log-format.md) — the entry format, the newest-last rule,
  and the checklist → derived-view discipline.

## Example

[`examples/sample-entry.md`](examples/sample-entry.md) — a checklist box flipping `[ ]`→`[x]`, a new
log entry, and the status row re-derived from 🟡 to ✅.

## Why it's in this shape

State that survives across sessions is what lets a fresh agent (or a teammate) pick up a project
cold. Append-only + newest-last keeps history intact; re-deriving views in the same edit keeps the
"what's done" answer from ever disagreeing with itself. Separating log from commit means the log
entry is always part of the commit that ships the work — never an afterthought.
