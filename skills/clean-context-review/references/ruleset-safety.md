# Rule-set: safety

For code that handles subprocess execution, credentials, remote/destructive actions, or AI
integration. Adapt to your project.

## RULE S1 — never log secrets

No logging call (`console.*`, `logger.*`) may include a credential value: identifiers containing
`token`, `password`/`pass`, `apiKey`/`secret`/`key` (as a credential), device codes, or env vars
named `*SECRET*`/`*TOKEN*`/`*KEY*`/`*PASS*`.

## RULE S2 — subprocess args are an array, never a string

Commands pass arguments as an **array** to `execFile` (or equivalent). Forbidden:

- template-literal command strings — `` `git ${args}` ``,
- string concatenation — `'git ' + args`,
- shell-string invocations — `exec('git …')`, `spawn('sh', ['-c', '…'])`.

Path arguments come **after `--`** to prevent option injection.

## RULE S3 — destructive/remote actions behind confirmation

Any destructive (`reset --hard`, `clean`, force-push) or remote (`push`, `fetch`, `pull`) action
requires explicit user confirmation. Irreversible actions get a distinct, stronger warning.

## RULE S4 — one runner for subprocesses

Process spawning lives in exactly one module; nothing else calls `execFile`/`exec`/`spawn`.
(Mechanical counterpart: `scripts/execfile-guard.sh`.)

## RULE S5 — AI is advisory-only

No blocker, gate, or mutation may depend on model output. AI must never: call the subprocess runner
directly, trigger a commit/push/destructive action, set a safety-check result, or bypass a
user-confirmation gate. Advisory text (suggestions, draft messages, explanations) is fine — only
**autonomous actions** are violations.

## Reviewer output for this rule-set

```
FINDING: <file>:<line> — logs a token variable violates safety rule S1
FINDING: <file>:<line> — builds a command string violates safety rule S2
CLEAN — safety rule-set confirmed
```
