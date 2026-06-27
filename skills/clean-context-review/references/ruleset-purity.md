# Rule-set: pure layer

For a layer that must stay free of side effects so it's unit-testable in isolation and portable
across runtimes (domain types, parsers, decision/safety engines). Adapt the paths/tokens to your
project.

## RULE P1 — no forbidden imports

The pure layer (default `src/core/`) must not import:

- subprocess APIs — `child_process` (any variant: `node:child_process`, `require('child_process')`),
- filesystem — `fs` (any variant: `node:fs`, `fs/promises`),
- platform/runtime — `electron` (or your platform shell),
- DOM/browser globals — `window`, `document`, `navigator`, `localStorage`, `HTMLElement`, used as a
  browser-context dependency.

## RULE P2 — dependencies are injected

Any service in the pure layer with I/O side effects must be an **interface**, injected — never a
direct `new ConcreteThing()` that performs I/O. Consumers reference the interface type, not the
concrete class.

## What is NOT a violation

- An **interface or type** that merely *describes* an impure dependency (it has no implementation).
- Pure data transforms, even if named like I/O (`serialize`, `parseFoo`) as long as they touch no
  real I/O.
- Files outside the pure layer — out of scope for this rule-set.

## Reviewer output for this rule-set

```
FINDING: <file>:<line> — <forbidden import/usage> violates pure-layer rule P1
FINDING: <file>:<line> — direct instantiation of an I/O service violates pure-layer rule P2
CLEAN — pure-layer rule-set confirmed
```

Mechanical counterpart: `scripts/core-purity.sh` catches P1 at edit time.
