# Progress-log format & discipline

## Entry format

One entry per completed unit of work, appended at the bottom (newest last):

```
### YYYY-MM-DD — <id>: <name>

- Built: <what was built>
- Files: <key files added/changed>
- Tests: <exact counts — e.g. "Vitest 537/537 passed; Playwright 25/25 passed">
- Exit criteria: ✅ met / ⚠️ partial (why)
- Notes / follow-ups: <anything worth capturing for the next session>
```

`<id>` is the project's unit label: `Phase 56`, `DX-3`, or a `type(scope)` for ad-hoc changes
(`feat(tooling)`, `docs`, `Fix`).

## Rules

1. **Newest last. Never rewrite or reorder past entries.** The log is append-only history.
2. **Exact counts in `Tests:`.** "tests pass" is not good enough — record the numbers so a later
   reader can spot a regression.
3. **Be honest in `Exit criteria:`.** If something is partial, say ⚠️ and why. A green log entry
   over a partial result is how state rots.
4. **The checklist is the source of truth.** The log explains; the checklist box decides "done".

## The derived-view discipline

Anything that restates completion outside the checklist is a **derived view**:

- a Feature/Track status table,
- a "current level" or "current phase" line,
- a build-order summary.

When you tick a checklist box, re-derive **every** affected view in the **same** edit:

| Group state          | Derived status      |
| -------------------- | ------------------- |
| all boxes `[x]`      | ✅ complete         |
| no boxes `[x]`       | ⬜ not started      |
| some boxes `[x]`     | 🟡 (note done/open) |

If a derived view ever disagrees with the checklist, the checklist wins — fix the view.
