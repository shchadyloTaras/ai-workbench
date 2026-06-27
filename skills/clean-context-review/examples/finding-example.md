# Example: a purity finding, fixed, re-reviewed

## Before — the diff under review

A new "pure layer" file reaches for the filesystem to load a config:

```ts
// src/core/policy/PushPolicy.ts
import { readFileSync } from 'node:fs';

export function loadPolicy(path: string): PushPolicy {
  return JSON.parse(readFileSync(path, 'utf8'));
}
```

## Reviewer output (pure-layer rule-set)

```
FINDING: src/core/policy/PushPolicy.ts:2 — import { readFileSync } from 'node:fs' violates pure-layer rule P1
FINDING: src/core/policy/PushPolicy.ts:5 — direct filesystem read in the pure layer violates pure-layer rule P1/P2
```

(The edit-time hook `core-purity.sh` would also have blocked this the moment the import was written.)

## After — the fix

The pure layer takes data, not a path; the I/O moves out and is injected:

```ts
// src/core/policy/PushPolicy.ts  (pure: takes parsed data, no I/O)
export function parsePolicy(raw: unknown): PushPolicy {
  return PushPolicySchema.parse(raw);
}
```

```ts
// src/main/policy/PolicyLoader.ts  (impure: allowed here, injected into callers)
import { readFileSync } from 'node:fs';
import { parsePolicy } from '../../core/policy/PushPolicy';

export const loadPolicy = (path: string) =>
  parsePolicy(JSON.parse(readFileSync(path, 'utf8')));
```

## Re-review

```
CLEAN — pure-layer rule-set confirmed
```

## Takeaway

The reviewer didn't rewrite the code — it pointed at `file:line` and named the rule. The fix
(parse-don't-load + inject the I/O) is the maker's job; the re-review confirms it landed. The
authoring context might have shipped the original happily; a clean reviewer did not.
