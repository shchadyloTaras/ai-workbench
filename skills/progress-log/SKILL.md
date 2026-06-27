---
name: progress-log
description: Record a completed phase/task in an append-only progress log — append a dated entry (newest last, fixed format), tick its checklist box, and re-derive any status roll-up that depends on the checklist. Does NOT commit. Use when a unit of work is done and verified and needs to be logged before committing.
---

# progress-log

You record a finished unit of work so project state survives across sessions and agents. Three
edits, then a report. **You do not commit** — that's the next step (`guarded-commit`).

## The single-source-of-truth rule

A project's progress doc usually has three parts:

- a **Checklist** — the **authoritative** record of what's done (one box per phase/task),
- a **status roll-up** (a table, a "current level" line) — a **derived view** of the checklist,
- an append-only **log** of dated entries.

The checklist is the source of truth. Every other place that restates completion is derived. When
you tick a box you MUST re-derive every affected view in the same change. If a view ever disagrees
with the checklist, the checklist wins.

## Step 1 — Read the current state

Read the progress doc in full. Note: the exact format of the most recent entries, today's date,
the current state of this item's checklist box, and the current state of the status roll-up.

## Step 2 — Append the entry

Append a new entry at the **bottom** (newest last), matching the existing format exactly. A typical
entry:

```
### YYYY-MM-DD — <Phase N / type(scope)>: <name>

- Built: <what was built>
- Files: <key files added/changed>
- Tests: <exact counts, e.g. "537/537 passed">
- Exit criteria: ✅ met / ⚠️ partial (why)
- Notes / follow-ups: <anything worth capturing>
```

Do **not** rewrite or reorder past entries.

## Step 3 — Tick the checklist box

Change this item's `- [ ] …` to `- [x] …`. (For a non-checklist item — e.g. an ad-hoc tooling or
docs change — there may be no box; in that case the log entry alone is the record.)

## Step 4 — Re-derive the status roll-up

Recompute every derived view the ticked box affects:

- a status table row: all boxes in a group `[x]` → ✅ complete; none → ⬜ not started; mixed → 🟡
  (note which are done vs open),
- any "current level" / "current phase" line.

Update them in the **same** edit so they never drift from the checklist.

## Step 5 — Do NOT commit

Do not run `git add` or `git commit`. Leave that to `guarded-commit`.

## Step 6 — Report

Report: the full new entry, which box you ticked, and the status row you re-derived (before → after).
