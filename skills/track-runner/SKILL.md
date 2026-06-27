---
name: track-runner
description: Run a whole feature track phase-by-phase — for each pending phase: brief from the plan, implement, review, verify, log, commit (one commit per phase). Stops on any failed gate, blocking review finding, ambiguity, or plan stop-point. Never pushes. Use when a project has a multi-phase plan + a phase checklist and the user wants the next phase(s) driven to completion.
---

# track-runner

You drive an entire **feature track** to completion, one phase at a time, by orchestrating the
project's per-phase skills: brief → implement → review → verify → log → commit. This skill is the
loop and the gates; the per-phase work is delegated to the project's other skills
(`verify-gate`, `progress-log`, `guarded-commit`, `clean-context-review`).

Configure it for a project by reading that project's rule files (see
`projects/<name>/references/` in this workbench, e.g. `projects/gitwarden/`): the **plan file**,
the **phase checklist**, the **gate commands**, the **commit convention**, and the
**review rule-sets**.

## HARD RULES — read first, they govern every step

1. **One commit per phase.** Never batch two phases into one commit. Each pending phase gets its
   own progress-log entry and its own commit.
2. **Stop on red — never advance past a failing phase.** Do not start phase N+1 if phase N's
   verify gate fails, a reviewer returns a blocking finding you cannot confidently fix, or any
   required check fails. STOP and report which gate failed.
3. **Never guess on ambiguity; never make a destructive/irreversible choice silently.** If a
   genuine design decision, an ambiguity the plan does not settle, or any destructive/irreversible
   action (data loss, force-push, history rewrite, deleting files) arises → STOP and ask the user.
   Do not pick a default and proceed.
4. **Never `git push`** — under any circumstance, even if asked mid-run. Pushing is a separate,
   explicit, manual step.
5. **Respect the project's invariants.** Read them from the project's rule files before you write
   code, and do not violate them (a project may also enforce them with hooks — see
   `clean-context-review` and `guarded-commit` scripts).

If a hard rule and a plan instruction appear to conflict, STOP and ask — do not resolve it yourself.

## RESOLVE — find the track, its pending phases, and the entry gate

1. **Map the track to its plan + checklist.** From the track name (or slug) the user gave, locate
   the project's plan file and the section of the phase checklist that owns this track. If the
   project documents its files in an index (e.g. an `AGENTS.md` "Reference docs" section), confirm
   against it. If the track does not resolve to exactly one plan, STOP and report the candidates.
2. **Collect the pending phases.** Read the phase checklist. Collect every phase in the track's
   range whose box is unchecked (`[ ]`), in **ascending order**. Skip phases already done (`[x]`).
   If none are pending, report `Track already complete` and STOP.
3. **Confirm the entry gate.** The phase immediately **before** the first pending phase (it may
   belong to a different track) must be marked done **and** show its exit criteria met in the
   progress log. If not, STOP: `Track gate not met: <gate-phase> must be done first.`

Then print the resolved plan before entering the loop:

```
Track:          <name>
Plan:           <plan file>
Pending phases: <comma-separated list>
Entry gate:     <gate-phase> ✅
Stop points:    <phases the plan flags as stop points — see LOOP step i>
```

## LOOP — for each pending phase N, in ascending order

**a. BRIEF.** Confirm phase N's previous-phase gate. Read the plan section (and any matching prompt)
for phase N. Output a short brief: **Goal**, **Tasks**, **Exit criteria**, and which project
invariants apply to this phase's scope. If the gate is not met, STOP.

**b. IMPLEMENT.** Write the code for phase N following the plan, the prompt, and the project's
architecture rules (build logic-first where the project asks for it). If — and only if — a genuine
design decision, an unsettled ambiguity, or a destructive/irreversible choice arises → **STOP and
ask** (HARD RULE 3). Do not guess.

**c. REVIEW (conditional).** Inspect the diff (`git diff` + `git status`). If it touches paths the
project's review rule-sets cover, invoke `clean-context-review` with the matching rule-set
(e.g. a "pure core" rule-set, a "safety" rule-set). Fix any blocking `FINDING` and re-review; if a
finding cannot be confidently fixed, STOP and report it verbatim.

**d. VERIFY.** Run `verify-gate` (add the UI/e2e tier if this is a UI phase). If the gate fails,
**STOP**, report the failing step with its output, and do **not** proceed to the next phase
(HARD RULE 2).

**e. EXTRA CHECKS (conditional).** Run any phase-type-specific check the project defines for the
paths this phase touched (e.g. an AI-quality eval for AI code). If it fails, STOP.

**f. LOG.** Run `progress-log` for phase N: append the entry, tick the checklist box, re-derive the
status roll-up. Do **not** commit here.

**g. COMMIT.** Run `guarded-commit` for phase N. If the project enforces a "log must be staged"
gate via a hook that inspects the whole command string, you **cannot** combine staging and
committing in one shell call — stage (including the progress-log file) in one call that contains
**no** `git commit`, then run `git commit` in a **separate** call. Never push.

**h. CHECKPOINT.** Print exactly one line:
`✅ Phase N <name> committed <short-hash>. Next: <N+1 or done>.`

**i. STOP-POINT.** When you read phase N's plan section (step a), check whether the plan flags N as
a stop point — phrases like "safe stop point", "feature-complete stop point", or
"recommended MVP stop point". If so, **STOP after its commit** and report, even if later phases
remain. The user decides whether to continue past a stop point.

**j. STEP MODE.** If the user asked for step mode (e.g. a `--step` flag), pause after each phase's
checkpoint and wait for `continue` before starting the next phase.

## FINISH

When every pending phase is committed (or a stop-point was hit), print a summary table — each phase
with its commit hash and test counts — and name the next phase/track. Never push.
