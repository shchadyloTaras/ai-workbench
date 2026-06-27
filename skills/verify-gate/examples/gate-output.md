# Example: verify-gate output

## Before — a red gate (stops at tests)

```
── step 1: npx tsc -p tsconfig.node.json --noEmit
✅ step 1 ok
── step 2: npx tsc -p tsconfig.web.json --noEmit
✅ step 2 ok
── step 3: npm test
  FAIL  tests/unit/policy.test.ts > evaluatePolicy > blocks protected branch
  AssertionError: expected 'allow' to be 'block'
  Tests  1 failed | 536 passed (537)
❌ GATE FAIL — step 3 failed (exit 1): npm test
```

The gate stopped at step 3. Lint (step 4) never ran — no point linting code whose tests fail.

## After — the fix, then a green gate

```
── step 1: npx tsc -p tsconfig.node.json --noEmit
✅ step 1 ok
── step 2: npx tsc -p tsconfig.web.json --noEmit
✅ step 2 ok
── step 3: npm test
  Tests  537 passed (537)
✅ step 3 ok
── step 4: npm run lint
✅ step 4 ok
GATE PASS — all 4 checks green.
```

## Takeaway

Same ordered list both times. The only difference is the code. The gate is a pure reporter: it
tells you the earliest thing that's broken and gets out of the way once everything is green.
