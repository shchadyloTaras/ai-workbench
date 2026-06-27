# verify-gate

> **One task:** run the full quality gate in order, stop on the first failure, report ✅/❌ per step.

## What it does

Runs your project's checks — typecheck(s) → tests → lint → (optional) e2e — **in a fixed order**,
**stopping at the first red step**. It reports each step's result and a single final verdict
(`GATE PASS` / `GATE FAIL`). It reports; it does not fix.

## The main file

[`SKILL.md`](SKILL.md) — the order, the stop-on-first-failure rule, and the verdict format.

## How to run it

- **As an agent skill:** copy to `.claude/skills/verify-gate/`; ask _"verify"_ / _"run the gate"_.
- **As a slash command:** copy `SKILL.md`'s body into `.claude/commands/verify-gate.md` with
  `argument-hint: "[--ui]"`; invoke `/verify-gate`.
- **As a script:** run the bundled checker directly —

  ```bash
  scripts/verify-gate.sh \
    "npx tsc -p tsconfig.node.json --noEmit" \
    "npx tsc -p tsconfig.web.json --noEmit" \
    "npm test" \
    "npm run lint"
  # add "npm run e2e" as a final argument for the --ui tier
  ```

  It runs each command in order and exits non-zero at the first failure, echoing which step failed.

## Configure it for your project

List your exact gate commands in `projects/<name>/references/gate-commands.md`. See
[`projects/gitwarden/references/gate-commands.md`](../../projects/gitwarden/references/gate-commands.md)
for a real five-command gate.

## Example

[`examples/gate-output.md`](examples/gate-output.md) — a failing run (stops at tests) and the
green run after the fix.

## Why it's in this shape

Stopping on the **first** failure keeps output short and points at the earliest break, which is
usually the cause of the later ones. Running **all** typecheck projects (not just one) is the rule
that most often catches an error a single config would have hidden.
