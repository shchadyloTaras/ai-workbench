---
name: verify-gate
description: Run a project's full quality gate — typecheck, tests, lint, and optionally e2e — in a fixed order, stopping on the FIRST failure and reporting ✅/❌ per step. Use before any commit, or when the user asks to "verify", "run the gate", or "check everything is green".
---

# verify-gate

You run the project's quality gate **in order** and **stop on the first failure**. Report each step
as ✅ or ❌ with the last few lines of its output, then a single final verdict.

## The gate

Run these steps in this exact order. The specific commands come from the project (read them from
the project's rule file, e.g. `projects/<name>/references/gate-commands.md`). A typical gate:

1. **Typecheck** — every typecheck project the repo defines. Run **all** of them; do not assume one
   covers another. (Projects with split configs often hide errors in the config you skipped.)
2. **Tests** — the unit/integration suite.
3. **Lint** — linter + formatter check.
4. **E2E** — only when the change is UI-facing, or the user asks for the full gate (the `--ui` tier).

## How to run

For each step, in order:

1. Run the command, capturing combined stdout+stderr (`2>&1`).
2. If its exit code ≠ 0 → mark the step ❌, print the **last 5 lines** of output, and **STOP**.
   Do not run any later step.
3. If exit code = 0 → mark the step ✅ and continue.

You may use the bundled `scripts/verify-gate.sh`, which takes the gate commands as arguments and
implements exactly this stop-on-first-failure behaviour.

## Final verdict

After all steps pass, or on the first failure, print one of:

```
GATE PASS — all checks green.
```

```
GATE FAIL — <step that failed>.
```

Never run a later step after an earlier one fails. Never report PASS unless every step in scope
actually returned exit 0.

## Notes

- This skill **only reports** — it does not fix failures. Hand the failing output back to the caller
  (or, inside `track-runner`, stop the loop).
- "Run all typecheck projects" is load-bearing: a repo with separate `tsconfig.node.json` /
  `tsconfig.web.json` (or equivalent) can have errors that only one of them surfaces.
