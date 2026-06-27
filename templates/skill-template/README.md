# <skill-name>

> **One task:** <one line — the single job this skill does>

## What it does

<2–4 sentences for a human. What problem it solves, what it produces, and one line on what it will
NOT do (so the boundary is clear).>

## The main file

[`SKILL.md`](SKILL.md) — the instructions the AI follows.

## How to run it

- **As an agent skill:** copy this folder to `.claude/skills/<skill-name>/`; ask _"…"_.
- **As a slash command:** copy `SKILL.md`'s body into `.claude/commands/<skill-name>.md` with the
  right `argument-hint` and `allowed-tools`; invoke `/<skill-name>`.
- **As a human checklist:** just follow the steps in this README.

## The rules it enforces

- [`references/…`](references/) — <the rule-set, if any. Delete this section if the skill has no
  references/.>

## The scripts (automatic checking)

- [`scripts/…`](scripts/) — <runnable guard(s), if any. Delete if none.>

## Example

- [`examples/…`](examples/) — before → after. <Delete if none, but a before/after is strongly
  recommended.>

## Why it's in this shape

<1–3 sentences on the design choice that matters most — why this skill works the way it does, not
some other way. This is where you justify the constraint that makes it safe/correct.>

---

## Using this template

1. Copy `templates/skill-template/` to `skills/<your-skill>/`.
2. Fill in `SKILL.md` (AI instructions) and this `README.md` (human instructions).
3. Keep `references/` (rules), `scripts/` (checks), `examples/` (before/after) **only if needed** —
   delete the empty ones.
4. Keep it to **one task**. If it's two tasks, make two skills.
5. Add a row for it to the table in the root [`README.md`](../../README.md).
