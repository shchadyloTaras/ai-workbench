# ai-workbench

A personal workbench of **reusable AI-agent skills** — small, self-contained capabilities
that help an AI coding agent (Claude Code, Codex, etc.) do real engineering work safely and
repeatably across projects.

Each skill is one task, packaged so a **human** and an **AI** can both pick it up cold:
human-readable instructions, machine-readable instructions, the rules it enforces, an optional
automatic checker, and a before/after example.

The first batch of skills was extracted and **generalized** from the developer-experience (DX)
tooling of a real project ([GitWarden](projects/gitwarden/README.md)) — a phase-driven delivery
workflow with executable guardrails and clean-context code review. The project-specific rules
that those skills were originally built against live under [`projects/`](projects/) as a worked
example; the skills themselves are project-agnostic.

---

## The idea

A skill is a folder you can drop into any project (or read on its own). Every skill answers:

- **what it does** — one task, stated in one line
- **the main file** — `SKILL.md`, the instructions the AI follows
- **how to run it** — install into a project or invoke it directly
- **the README** — the human-facing version of the same thing
- **an example** — before → after, so you can see the effect

## The approach

| Convention                  | Meaning                                                    |
| --------------------------- | ---------------------------------------------------------- |
| **one skill = one task**    | a skill does a single, nameable job — nothing more         |
| `README.md`                 | instructions **for humans** — what, why, how to install    |
| `SKILL.md`                  | instructions **for the AI** — the steps it actually runs   |
| `references/`               | the **rules** the skill enforces (conventions, rule-sets)  |
| `scripts/`                  | **automatic checking** — runnable guards, where useful     |
| `examples/`                 | **before / after** — a concrete demonstration              |

Not every skill needs every folder — `scripts/` and `references/` appear only where they earn
their place.

## Layout

```
ai-workbench/
├── README.md                  ← you are here
├── skills/                    ← the reusable skills (project-agnostic)
│   ├── track-runner/          ← drive a multi-phase plan, one commit per phase
│   ├── verify-gate/           ← run the full quality gate, stop on first failure
│   ├── guarded-commit/        ← commit on a strict convention; refuse on red / missing log
│   ├── progress-log/          ← keep an append-only progress log + checklist + status
│   └── clean-context-review/  ← independent read-only review of a diff (maker ≠ checker)
├── projects/                  ← project-specific rules + examples the skills plug into
│   └── gitwarden/             ← the worked example these skills were generalized from
└── templates/
    └── skill-template/        ← copy this to start a new skill
```

## The skills

| Skill                                                            | One-line task                                                                 |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [`track-runner`](skills/track-runner/README.md)                 | Run a whole feature track phase-by-phase, stopping on any failure or stop-point. |
| [`verify-gate`](skills/verify-gate/README.md)                   | Run typecheck + tests + lint (+ e2e) in order, stop on the first failure.      |
| [`guarded-commit`](skills/guarded-commit/README.md)             | Commit with an exact subject convention; refuse on red tests or a missing log. |
| [`progress-log`](skills/progress-log/README.md)                 | Append a progress entry, tick the checklist, re-derive the status roll-up.     |
| [`clean-context-review`](skills/clean-context-review/README.md) | Dispatch a read-only reviewer against a named rule-set; report `file:line` findings. |

`track-runner` is the orchestrator — it calls the other four (plus `clean-context-review`) once
per phase. Each of the four also stands alone.

## How to use a skill

A skill is plain Markdown + the occasional shell script, so you can use it three ways:

1. **As a Claude Code / agent skill** — copy `skills/<name>/SKILL.md` (and its `references/`,
   `scripts/`) into your project's `.claude/skills/<name>/`, or into `~/.claude/skills/<name>/`
   for all projects. The `SKILL.md` frontmatter (`name` + `description`) lets the agent discover
   and trigger it.
2. **As a slash command** — drop the body of `SKILL.md` into `.claude/commands/<name>.md`; invoke
   it with `/<name>`. (This is how these started life — see `projects/gitwarden`.)
3. **As a human checklist** — just read the `README.md`. Every step is something a person can do
   by hand.

To wire a skill to a specific project, point it at that project's rule files under
`projects/<name>/references/`. See [`projects/gitwarden`](projects/gitwarden/README.md) for a
complete, working set.

## Starting a new skill

Copy [`templates/skill-template/`](templates/skill-template/) to `skills/<your-skill>/`, fill in
`SKILL.md` and `README.md`, and add `references/` / `scripts/` / `examples/` only if the skill
needs them. Keep it to **one task**.

---

_Provenance: the initial skills were generalized from the GitWarden project's Agentic DX track
(slash commands, subagent reviewers, and PreToolUse/PostToolUse hook guardrails). See
[`projects/gitwarden`](projects/gitwarden/README.md) for the original rules and examples._
