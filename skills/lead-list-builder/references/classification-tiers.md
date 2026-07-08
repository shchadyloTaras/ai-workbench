# Classification tiers (cheap → expensive, never stop at tier 1)

A company is classified `saas` / `not_saas` / `uncertain` by escalating only as far as needed.
The rule that makes this trustworthy: **a cheap signal proposes, a read decides.** Tier 1 is a
fast filter that also *captures* the site text so tiers 2/3 cost almost nothing.

## Tier 1 — heuristic (deterministic, `scripts/classify_heuristic.py`)

Fetches the homepage (+ `/pricing`, `/product`) and scores SaaS signals (pricing page, free trial,
login, `app.` subdomain, demo, API docs, `SoftwareApplication` JSON-LD, subscription language)
against services-agency signals (agency/studio, outsourcing, "we build for you", portfolio, "get a
quote") and ecommerce. Emits `verdict` (`saas`/`not_saas`/`unclear`/`blocked`/`unreachable`), a
confidence, and the captured `title` / `meta` / `snip`.

**Tier 1 is a filter, not a verdict.** A high-confidence tier-1 `saas` still goes through tier 2.
Why: the signals are shallow — a battery-hardware company with a customer login and a pricing page
scores as "SaaS" on signals alone. Only reading the text ("battery cell **simulation & data
platform**" vs "we manufacture cells") settles it.

## Tier 2 — LLM read of captured text (free re-read, no re-fetch)

For **every** company (not only the unclear ones), read the tier-1 `title` + `meta` + `snip` and
decide against [`icp-ruleset.md`](icp-ruleset.md) §1. Because tier 1 already captured the text,
this costs no new fetches. Prompt shape:

> You classify a company as **saas**, **not_saas**, or **uncertain** for a target list of
> [target profile]. Here is its site text: TITLE=«…» META=«…» SNIPPET=«…».
> saas = its OWN software product sold as a subscription/service (flag is_b2c for consumer apps).
> not_saas = agency/consulting/outsourcing (builds for clients), pure hardware, holding/fund, or
> offline/services business. uncertain = text too thin to tell.
> Hybrids: saas only if the product is standalone; a services-led shop is not_saas.
> Return {verdict, confidence 0-100, is_b2c, one-line reason with the evidence}.

Run these in batches (many companies per call, or parallel subagents for large sets).

## Tier 3 — web search (for the uncertain tail only)

Whatever is still `uncertain` / `blocked` / `unreachable` (dead site, JS-only page, URL-shortener
like bit.ly, "coming soon", thin text) goes to a web search: query the company name (+ industry or
domain as a disambiguator), read what it actually sells, classify with the same prompt. This is the
pass that resolves fetch failures — which are the bulk of the "uncertain" pile, not genuine
ambiguity. Dead/parked/"coming soon" sites with no live product → `not_saas` by rule.

For large tails, dispatch parallel subagents (~10–15 companies each) that web-search and write
structured verdicts, then merge.

## Merge into the final verdict

Combine tiers into one `final_verdict` per company with `final_conf`, `final_reason`,
`final_source` (`site-heuristic+read` / `web-search` / `dead-site-rule`), and `is_b2c`. Then
`scripts/finalize.py` applies the toggles and joins to the leads. Anything still `uncertain` under
strict mode is left out of the ready list and surfaced, never silently shipped.
