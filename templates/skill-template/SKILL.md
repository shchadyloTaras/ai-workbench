---
name: <skill-slug>
description: <One sentence: what the skill does + WHEN to use it. This is the trigger — write it so an agent can tell from a user's request whether this skill applies. Start with the task verb. Mention the concrete situation, not just the capability.>
---

# <skill-slug>

<One paragraph: the single task this skill performs, and the principle that makes it safe/correct.
One skill = one task. If you're describing two tasks, split into two skills.>

## How to run

<Numbered steps the AI follows. Be concrete and ordered. If there are gates, state what STOPs the
skill and what it reports when it stops. Prefer explicit "STOP and report: …" over soft guidance.>

1. …
2. …
3. …

## Rules

<The non-negotiables. If the skill must never do something (push, guess, delete), say so here in
imperative form. Link to a references/ file if the rule-set is long.>

- …

## Output

<Exactly what the skill prints / produces. Give the literal format if it matters (e.g. a finding
line, a verdict string, a commit subject).>
