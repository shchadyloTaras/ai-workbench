# GitWarden — how the skills are wired

These skills started life as GitWarden's `.claude/` tooling. This is the original wiring, as a
reference for installing the generalized skills into any project.

## Slash commands — `.claude/commands/`

Each workflow skill was a slash command (its `SKILL.md` body + a small frontmatter):

```
.claude/commands/
├── run-track.md      → skills/track-runner       (argument-hint: "<feature-slug> [--step]")
├── new-phase.md      → folded into track-runner   (argument-hint: "<phase-number-or-DX-N>")
├── verify-phase.md   → skills/verify-gate         (argument-hint: "[--ui]")
├── commit-phase.md   → skills/guarded-commit      (argument-hint: "<N> <phase name...>")
└── log-phase.md      → skills/progress-log        (argument-hint: "<N> <name> — <summary>")
```

`allowed-tools` examples — `verify-phase`: `Bash(npx tsc*), Bash(npm run lint), Bash(npm test),
Bash(npm run e2e)`; `commit-phase`: `Bash(npm test), Bash(git add*), Bash(git commit*),
Bash(git status), Read, Bash(grep*)`.

## Subagents — `.claude/agents/`

The two review rule-sets were read-only subagents (`tools: Read, Grep, Glob, Bash`):

```
.claude/agents/
├── core-purity-reviewer.md  → clean-context-review + ruleset-purity
└── safety-reviewer.md       → clean-context-review + ruleset-safety
```

## Hooks — `.claude/hooks/` + `.claude/settings.json`

The four guards, wired as PreToolUse (Bash) and PostToolUse (Edit/Write):

```jsonc
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [
        { "type": "command", "command": ".claude/hooks/no-global-git-config.sh", "if": "Bash(git config*)" },
        { "type": "command", "command": ".claude/hooks/commit-needs-log.sh",     "if": "Bash(git commit*)" }
      ]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [
        { "type": "command", "command": ".claude/hooks/core-purity.sh" },
        { "type": "command", "command": ".claude/hooks/execfile-guard.sh" }
      ]
    }]
  }
}
```

All four hooks **fail open**: on any internal error they exit 0, so a broken hook never blocks
legitimate work.

## The order it was built in

GitWarden's DX track built these in dependency order: docs reconciliation → executable guardrails
(hooks) → slash commands → subagent reviewers → AI evals → shareability. Guardrails first, because
the commands and the orchestrator rely on them holding.
