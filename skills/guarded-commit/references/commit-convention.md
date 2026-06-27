# Commit convention (configure per project)

`guarded-commit` writes one commit with an exact subject. Pick the convention your project uses and
record it here (or in `projects/<name>/references/`). Two common shapes:

## A. Phase/task subjects

For a phase-driven plan where each phase is one commit:

```
Phase <N>: <name>

<one-line body — what this phase built>

Co-Authored-By: <Agent> <noreply@anthropic.com>
```

Variant for a non-numbered tooling/docs change: `<type>(<scope>): <summary>`, e.g.
`feat(tooling): add the track-runner skill`.

## B. Conventional Commits

```
<type>(<scope>): <summary>

<body>

Co-Authored-By: <Agent> <noreply@anthropic.com>
```

`type` ∈ feat | fix | docs | refactor | test | chore | build | ci.

## Rules that hold for any convention

- **Subject is exact.** No trailing period, imperative mood, under ~72 chars.
- **One commit per unit of work.** Don't batch two phases/tasks into one commit.
- **Always include the agent trailer** so authorship of AI-assisted commits is traceable.
- **The body is one line** unless the project asks for more.
- **Never push** as part of the commit step.

## The pre-commit gates

Before the commit is even built, two refusals apply (see `SKILL.md`):

1. tests must be green, and
2. the required progress-log entry must exist **and be staged**.

Both are enforceable mechanically by the bundled `scripts/commit-needs-log.sh` hook.
