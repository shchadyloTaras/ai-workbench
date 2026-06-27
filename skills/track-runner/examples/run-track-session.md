# Example: a track-runner session

A real resolve-and-loop run, using the GitWarden project's "Client Branch Access" track as the
worked example. Shows the RESOLVE output, one phase of the LOOP, and a clean stop at a stop-point.

## Before

```
$ run-track client-branch-access
```

The checklist shows four pending phases and the plan flags the last one:

```
- [ ] Phase 56 — Push Policy Foundations & Pure Helpers
- [ ] Phase 57 — Safety Engine: Branch Access Checks
- [ ] Phase 58 — Policy Persistence, IPC & Push-Path Wiring
- [ ] Phase 59 — Push Policy UI   (feature-complete stop point)
```

## After — RESOLVE

```
Track:          client-branch-access
Plan:           docs/plans/client-branch-access-plan.md
Pending phases: 56, 57, 58, 59
Entry gate:     Phase 55a ✅  (last phase of the AI Chat Redesign track — done, exit criteria met)
Stop points:    Phase 59 — "feature-complete stop point"
```

The entry gate is the phase *immediately before* the first pending phase — here that's `55a`,
which lives in a **different** track. track-runner gates on it correctly anyway.

## After — LOOP (phase 56)

```
### Phase 56 — Push Policy Foundations & Pure Helpers
Gate:          Phase 55a ✅
Goal:          pure push-policy helpers + the policy type
Tasks:         add PushPolicy type; pure evaluatePolicy(); unit tests
Exit criteria: 12+ unit tests green; logic lives in the pure core; lint clean
Invariants:    #1 pure core (this phase is logic-only)

[implement…]
[review]  diff touches the pure core → clean-context-review with the "pure-core" rule-set
          → CLEAN
[verify]  verify-gate → GATE PASS (tsc ×2, tests 537/537, lint)
[log]     progress-log → entry appended, checklist box 56 ticked, status row re-derived
[commit]  guarded-commit → staged (incl. the log), then committed in a separate call

✅ Phase 56 Push Policy Foundations committed a1b2c3d. Next: 57.
```

…phases 57 and 58 run the same way…

## After — STOP at the stop-point

```
✅ Phase 59 Push Policy UI committed e4f5a6b. Next: done.

Phase 59 is flagged "feature-complete stop point" — stopping here.
Track client-branch-access: 4/4 pending phases committed. Next track is yours to choose.
```

## What this demonstrates

- The **entry gate can cross track boundaries** (56's gate is 55a).
- **One commit per phase** — four phases, four commits.
- A **stop-point halts the loop cleanly** even though no phases remained anyway; had phases 60+
  belonged to this track, they would *not* have been auto-started.
- **Nothing was pushed.**
