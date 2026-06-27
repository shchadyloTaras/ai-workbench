# GitWarden — the quality gate

The exact commands `verify-gate` runs for GitWarden, in order. All must be green; commit only on
green; never push automatically.

```bash
npx tsc -p tsconfig.node.json --noEmit   # 1. typecheck (node) — the one most often forgotten
npx tsc -p tsconfig.web.json  --noEmit   # 2. typecheck (web)
npm test                                 # 3. Vitest — unit + integration
npm run lint                             # 4. ESLint + Prettier
npm run e2e                              # 5. Playwright (UI tier only — the --ui step)
```

Wired into `verify-gate`'s runner:

```bash
scripts/verify-gate.sh \
  "npx tsc -p tsconfig.node.json --noEmit" \
  "npx tsc -p tsconfig.web.json --noEmit" \
  "npm test" \
  "npm run lint"
# append "npm run e2e" for the --ui tier
```

## Why both tsc projects

GitWarden has split TypeScript configs (`tsconfig.node.json` for main/preload, `tsconfig.web.json`
for the renderer). The node project has historically hidden a batch of errors the web project alone
did not surface — so the gate runs **both**, always. This is the concrete reason behind
`verify-gate`'s "run all typecheck projects" rule.

## Extra check for AI phases

Phases that touch `src/core/ai` or `src/main/ai` also run `npm run eval` (offline, deterministic
golden-set) before commit — the `track-runner` "extra check" step.
