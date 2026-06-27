# GitWarden — a real progress-log entry

A real entry from GitWarden's `docs/progress-log.md`, showing the format `progress-log` produces and
the checklist + derived-status discipline it follows.

## The log entry (appended newest-last)

```
### 2026-06-27 — DX-2: Slash commands

- Built: Four slash commands under `.claude/commands/`: `/verify-phase` (both tsc projects + vitest
  + lint + optional e2e), `/commit-phase` (gate check + exact subject/trailer + refuse on red
  tests/missing log entry), `/new-phase` (previous-phase gate + plan/prompt lookup + Goal/Tasks/Exit
  brief), `/log-phase` (append log entry + tick checklist + re-derive status table row, no commit).
- Files added: `.claude/commands/{verify-phase,commit-phase,new-phase,log-phase}.md`.
- Tests: `npm run test:tooling` → 26/26 passed. `npm run lint` clean. No `src/` changes.
- Exit criteria: ✅ met — all four command files exist with valid frontmatter; each behaves per spec.
- Notes / follow-ups: Next: DX-3 — Subagent reviewers.
```

## The checklist box (the source of truth)

```
- [x] DX-2 — Slash commands
- [ ] DX-3 — Subagent reviewers
```

## The derived status row (re-derived in the same edit)

```
| Agentic DX | DX-0–DX-6 | 🟡 DX-0–DX-2 done, DX-3–DX-6 open |
```

## What it demonstrates

- **Exact test counts** (`26/26`), not "tests pass".
- The **checklist box** is what flips "done"; the **status table row** is re-derived from it in the
  same change so the two can never disagree.
- The entry is **appended** — earlier entries are never rewritten.
