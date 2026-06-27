# GitWarden — the 7 non-negotiable invariants

These never change regardless of DX level. They are the concrete instances the generalized skills
reference (`track-runner` HARD RULE 5, `clean-context-review` rule-sets, `guarded-commit` guards).

1. **Pure core.** `src/core/` imports no `child_process`, `fs`, `electron`, or DOM globals. It is
   plain-Vitest-testable — the verifiability backbone.
2. **One runner.** All git execution goes through `GitRunner` (`src/main/git/`) — the only
   `execFile` caller; controlled env, cancellable, per-repo serialization.
3. **Array args.** Git arguments are always an array, never string-interpolated. Path args go after
   `--`.
4. **`--local` only.** Only `--local` git config changes — never `--global` or `--system`.
5. **No secrets logged.** Tokens, passwords, keys, device codes never reach a logging call.
6. **Destructive/remote behind confirmation.** `push`/`fetch`/`pull` and `reset --hard`/`clean`/
   force-push require explicit confirmation; irreversible ones get a stronger warning.
7. **AI advisory-only.** AI assistants never trigger git actions autonomously, never set a safety
   result, never bypass a confirmation gate.

## Always-valid

`git push` happens only when the user explicitly asks. No command, hook, or agent pushes
automatically — which is exactly why `track-runner` and `guarded-commit` carry an absolute "never
push" rule.
