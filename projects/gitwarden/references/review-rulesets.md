# GitWarden — review rule-sets (verbatim)

The two clean-context reviewers GitWarden runs. These are the concrete instances of the generalized
rule-sets in `skills/clean-context-review/references/`.

## core-purity-reviewer — scope: `src/core/**`

Enforces AGENTS.md rule #1 (pure core) and rule #4 (injected services):

- **No forbidden imports:** `child_process` (any variant), `fs` (`node:fs`, `fs/promises`),
  `electron`, DOM globals (`window`, `document`, `navigator`, `localStorage`, `HTMLElement`).
- **Injected services:** every I/O service is an interface, injected — no direct
  `new ConcreteFileService()` / `new ConcreteNetworkClient()` in `src/core/`. Consumers reference
  the interface type.
- **Does not** flag interface definitions themselves — only concrete instantiation of I/O services.

Output: `FINDING: <file>:<line> — <what> violates AGENTS.md rule #N`, or
`CLEAN — src/core/ purity confirmed`.

## safety-reviewer — scope: `src/main/git`, `src/main/security`, `src/main/ai`, IPC/preload

Enforces:

- **Never log secrets** — no logging call includes a token/password/key/device-code identifier or a
  `*SECRET*`/`*TOKEN*`/`*KEY*`/`*PASS*` env var.
- **Git args as arrays** — no template-literal/concatenated git command strings, no `exec`/`spawn`
  with a shell string; path args after `--`.
- **Destructive/remote behind confirmation** — `clean`, `reset --hard`, force-push, `push`/`fetch`/
  `pull` require confirmation; irreversible ones get a stronger warning.
- **execFile only** — only `GitRunner` calls `execFile`; no `exec`/`spawn` with a shell string.
- **AI advisory-only** — AI never calls `GitRunner`, triggers git mutations, sets a `SafetyCode`
  outcome, or bypasses a confirmation gate. Advisory text is fine; only autonomous actions violate.

Output: `FINDING: <file>:<line> — <what> violates <rule source>`, or
`CLEAN — safety rules confirmed`.
