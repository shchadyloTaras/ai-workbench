# The per-phase ritual

`track-runner` repeats this ritual for every pending phase. Each step delegates to a focused skill
where one exists; the orchestrator's job is to run them in order and enforce the gates between them.

| Step | Name        | What happens                                                                 | Delegates to            |
| ---- | ----------- | ---------------------------------------------------------------------------- | ----------------------- |
| a    | Brief       | Gate-check the previous phase; read the plan section + prompt; emit Goal / Tasks / Exit | (this skill)            |
| b    | Implement   | Write the code per plan + prompt + project rules; STOP & ask on ambiguity    | (this skill)            |
| c    | Review      | If the diff touches covered paths, run an independent reviewer per rule-set  | `clean-context-review`  |
| d    | Verify      | Run the full quality gate; stop on first failure                             | `verify-gate`           |
| e    | Extra check | Run any phase-type-specific check (e.g. AI eval) the project defines         | project-defined         |
| f    | Log         | Append the progress entry, tick the checklist, re-derive the status roll-up  | `progress-log`          |
| g    | Commit      | One commit, exact subject convention; stage and commit in separate calls     | `guarded-commit`        |
| h    | Checkpoint  | Print one status line                                                        | (this skill)            |
| i    | Stop-point  | If the plan flags this phase as a stop-point, stop after the commit          | (this skill)            |
| j    | Step mode   | If requested, pause for `continue` before the next phase                     | (this skill)            |

## The brief (step a) in detail

The brief is what lets a fresh context start a phase without re-reading the whole plan:

```
### Phase <N> — <name>

Gate:           previous phase ✅ (confirmed from the checklist + log)
Plan section:   <plan file> §<heading>
Prompt:         <prompt file or "inline">

Goal:           <one sentence from the plan>
Tasks:          <bulleted list from the plan>
Exit criteria:  <bulleted list from the plan>
Invariants:     <the project rules that apply to this phase's scope>
```

## The brief gate

Step **a** also re-confirms the gate for *this* phase (the previous phase must be done and its exit
criteria met). This is deliberately redundant with RESOLVE's entry-gate check: RESOLVE gates the
*track*, step **a** gates each *phase*. If a phase's gate is not met, STOP — do not improvise.
