# The clean-context reviewer pattern (maker ≠ checker)

## Why a fresh context

The agent that wrote the code is the worst judge of whether it's correct — it shares every
assumption that produced the bug. A reviewer that starts **clean** (no authoring history) reads the
diff on its own terms and against an explicit rule-set. That independence is the whole value.

In Claude Code this is a **subagent** (its own context window); in another tool it's a separate
invocation seeded only with the diff + the rule-set. Either way: the reviewer must not inherit the
maker's conversation.

## The reviewer contract

A reviewer **does**:

- read only the provided changed files / diff and the named rule-set,
- report each violation as `FINDING: <file>:<line> — <what was found> violates <rule>`,
- report exactly `CLEAN — <rule-set> confirmed` when there are none,
- stay within the rule-set's stated scope (ignore files it doesn't cover).

A reviewer **does not**:

- edit code,
- propose rewrites unless explicitly asked,
- report on files outside scope,
- flag the rule's own legitimate home — e.g. if a rule says "no `spawn` outside `runner/`", the
  reviewer must not flag `spawn` *inside* `runner/`, nor flag the interface/type that defines the
  allowed shape.

## Finding format

```
FINDING: src/core/policy.ts:42 — import { readFile } from 'node:fs' violates pure-layer rule
CLEAN — safety rule-set confirmed
```

One line per finding. `file:line` so the caller can jump straight to it. The `<rule>` names which
rule-set entry was violated, so the fix is unambiguous.

## Running several rule-sets

When a diff touches multiple concerns (say, pure-layer code **and** a subprocess call), dispatch one
reviewer per rule-set, in parallel. Each is blind to the others; together they cover more than one
reviewer trying to hold every rule at once.

## Reviewer vs. hook

| | Hook (script) | Clean-context reviewer |
|---|---|---|
| When | edit time (instant) | review time (before ship) |
| Scope | one narrow mechanical pattern | the full rule-set + intent |
| Output | block the edit | `file:line` findings |
| Misses | anything not a simple grep | nothing it's told to look for, but slower |

Use both: the hook is the tripwire, the reviewer is the read.
