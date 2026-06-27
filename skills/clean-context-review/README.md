# clean-context-review

> **One task:** independently review a diff against a named rule-set, and report `file:line` findings.

## What it does

Runs a **read-only** reviewer that starts with a **clean context** (no authoring history) over a
diff, checked against a specific rule-set. It reports each violation as
`FINDING: file:line — <what> violates <rule>`, or `CLEAN`. It never edits code.

The principle is **maker ≠ checker**: the context that wrote the code can't be trusted to catch its
own blind spots, so the reviewer is deliberately a different one.

It ships two reusable rule-sets (a "pure layer" rule-set and a "safety" rule-set) and two
edit-time hook scripts that mechanize the narrowest of those checks.

## The main file

[`SKILL.md`](SKILL.md) — how to pick rule-sets, dispatch fresh reviewers, and act on findings.

## How to run it

- **As Claude Code subagents:** drop the rule-sets into agent definitions under `.claude/agents/`
  (one agent per rule-set, `tools: Read, Grep, Glob, Bash`) and invoke them on a diff.
- **As a skill:** copy this folder to `.claude/skills/clean-context-review/`; ask
  _"review this diff for purity"_ / _"…for safety"_.
- **As edit-time hooks:** wire the scripts as PostToolUse hooks (see below) so the mechanical checks
  fire the instant a violation is written.

```jsonc
"PostToolUse": [{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    { "type": "command", "command": ".claude/hooks/core-purity.sh" },
    { "type": "command", "command": ".claude/hooks/execfile-guard.sh" }
  ]
}]
```

## The rules it enforces

- [`references/reviewer-pattern.md`](references/reviewer-pattern.md) — the maker≠checker contract and
  finding format.
- [`references/ruleset-purity.md`](references/ruleset-purity.md) — pure-layer rule-set (no forbidden
  imports, injected deps).
- [`references/ruleset-safety.md`](references/ruleset-safety.md) — secrets, arg-arrays, destructive
  confirmation, advisory-AI boundary.

## The scripts (automatic checking)

- [`scripts/core-purity.sh`](scripts/core-purity.sh) — blocks a forbidden import in the pure layer.
  Configure `PURE_DIR` / `PURE_BANNED`.
- [`scripts/execfile-guard.sh`](scripts/execfile-guard.sh) — flags subprocess spawns outside the one
  allowed dir. Configure `SPAWN_ALLOWED_DIR` / `SPAWN_BANNED`.

## Example

[`examples/finding-example.md`](examples/finding-example.md) — a reviewer catching a real purity
violation, the fix, and the re-review coming back `CLEAN`.

## Why it's in this shape

A hook is a fast tripwire on one grep-able pattern; a clean-context reviewer is a broader read that
understands intent and scope. Neither replaces the other. Running the reviewer fresh is what keeps
it honest — it has no stake in the code being right.
