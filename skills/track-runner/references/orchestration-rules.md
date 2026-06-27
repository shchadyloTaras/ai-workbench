# Orchestration rules (track-runner)

These are non-negotiable. They hold regardless of the project the skill is configured for.

1. **One commit per phase.** Never batch two phases into a single commit. Each pending phase
   produces exactly one progress-log entry and one commit.

2. **Stop on red — never advance past a failing phase.** Do not start phase N+1 while phase N has:
   - a failing verify gate, or
   - an open blocking review finding you cannot confidently fix, or
   - any required project-specific check still failing.
   STOP and report which gate failed and the relevant output.

3. **Never guess on ambiguity; never make a destructive/irreversible choice silently.** STOP and
   ask the user when you hit:
   - a genuine design decision the plan does not settle,
   - an ambiguity with more than one reasonable reading, or
   - any destructive/irreversible action (data loss, force-push, history rewrite, file deletion).

4. **Never `git push`.** Not even if asked mid-run. Pushing is always a separate, explicit, manual
   step performed by the user.

5. **Respect the project's invariants.** Read them before writing code. If the project enforces
   them with hooks, treat a firing hook as a real violation — fix the code, not the hook.

## Conflict rule

If a hard rule and a plan instruction appear to conflict, STOP and ask. Do not resolve the
conflict on your own authority.

## Stop-points

A plan may declare certain phases as stop-points ("safe stop point", "feature-complete stop point",
"recommended MVP stop point"). When a phase is a stop-point, finish its commit and then STOP —
even if later phases remain pending. Continuing past a stop-point is the user's call.
