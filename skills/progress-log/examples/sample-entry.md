# Example: logging one completed phase

## Before

Checklist (the source of truth) — phase 56 still open:

```
- [ ] Phase 56 — Push Policy Foundations & Pure Helpers
- [ ] Phase 57 — Safety Engine: Branch Access Checks
```

Derived status table row — track not started:

```
| Client Branch Access | 56–59 | ⬜ not started |
```

## After — three edits

**1. Append the entry** (newest last):

```
### 2026-06-28 — Phase 56: Push Policy Foundations & Pure Helpers

- Built: pure push-policy helpers + the PushPolicy type.
- Files: added src/core/policy/PushPolicy.ts, tests/unit/push-policy.test.ts.
- Tests: Vitest 537/537 passed (12 new).
- Exit criteria: ✅ met — full policy matrix covered; logic is pure; lint clean.
- Notes / follow-ups: persistence + IPC wiring lands in Phase 58.
```

**2. Tick the box:**

```
- [x] Phase 56 — Push Policy Foundations & Pure Helpers
- [ ] Phase 57 — Safety Engine: Branch Access Checks
```

**3. Re-derive the status row** (now mixed → 🟡):

```
| Client Branch Access | 56–59 | 🟡 56 done; 57–59 open |
```

## Report

```
Appended: 2026-06-28 — Phase 56 entry (shown above).
Ticked:   Phase 56 box [ ] → [x].
Re-derived: Client Branch Access row  ⬜ not started  →  🟡 56 done; 57–59 open.
No commit (run guarded-commit next).
```

## Takeaway

One ticked box forced one re-derived row — in the same edit. The status table can never silently
disagree with the checklist, because deriving it is part of ticking the box.
