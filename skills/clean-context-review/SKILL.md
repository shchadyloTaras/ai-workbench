---
name: clean-context-review
description: Review a diff with a fresh, read-only reviewer against a NAMED rule-set (maker ≠ checker) — report each violation as "FINDING: file:line — <what> violates <rule>", or "CLEAN". The reviewer reads the diff and the rule-set only, never the authoring session's history, and never edits code. Use to independently check a change before it ships (e.g. architectural purity, security/safety rules).
---

# clean-context-review

You perform an **independent**, **read-only** review of a diff against a specific rule-set. The
point is **maker ≠ checker**: the reviewer must not be the context that wrote the code, so it can't
rationalize its own work. It reads the diff and the rule-set, reports findings, and edits nothing.

## How to run

1. **Pick the rule-set(s)** that apply to what the diff touched. A project defines its own; this
   skill ships two reusable starting points:
   - [`references/ruleset-purity.md`](references/ruleset-purity.md) — a layer that must stay free of
     forbidden imports / side effects and use injected dependencies.
   - [`references/ruleset-safety.md`](references/ruleset-safety.md) — secrets never logged,
     subprocess args as arrays, destructive/remote actions behind confirmation, advisory-AI boundary.
2. **Dispatch a fresh-context reviewer per rule-set.** Use a subagent / separate invocation that
   starts **without** the authoring session's history. Give it only: the changed files (or the
   diff) and the rule-set. Run multiple rule-sets in parallel when several apply.
3. **The reviewer reports**, for each changed file in scope:
   - `FINDING: <file>:<line> — <what was found> violates <rule>` for each violation, or
   - `CLEAN — <rule-set> confirmed` if there are none.
4. **Act on findings.** A blocking finding must be fixed and the file re-reviewed. If it can't be
   confidently fixed, STOP and surface the finding verbatim (don't ship over it).

## Reviewer contract (what the reviewer must and must not do)

The reviewer:

- reads **only** the provided diff/files and the named rule-set,
- reports `file:line` findings in the exact format above,
- ignores files outside the rule-set's stated scope,
- does **not** edit code, does **not** suggest rewrites unless asked, and does **not** flag the
  rule's own legitimate home (e.g. the one directory where a "forbidden" API is allowed to live).

See [`references/reviewer-pattern.md`](references/reviewer-pattern.md) for the full contract.

## Automated counterparts (scripts)

Two of these checks can run mechanically at edit time as PostToolUse hooks, so a violation is caught
the instant it's written rather than at review time:

- `scripts/core-purity.sh` — blocks an edit that adds a forbidden import to the "pure" layer.
- `scripts/execfile-guard.sh` — warns/blocks when subprocess-spawning APIs appear outside their
  one allowed directory.

The hooks and the reviewer are complementary: the hook is a fast, narrow, always-on tripwire; the
reviewer is a broader read of intent. Use both. Both fail open — a broken hook never blocks work.
