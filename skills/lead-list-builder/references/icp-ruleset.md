# ICP ruleset (default: B2B SaaS product companies + decision-maker titles)

This is the **swappable** definition of "a good company" and "a good contact". The pipeline
mechanics in `SKILL.md` and `scripts/` are project-agnostic; this file is where the target profile
lives. To retarget the skill (different vertical, different titles), edit this file and the matching
constants in `scripts/filter_and_bucket.py` (title regexes + industry buckets) and
`scripts/classify_heuristic.py` (SaaS vs services signals).

The default profile below was generalized from a real engagement: a B2B SaaS product-design agency
building an outreach list of decision-makers at SaaS product companies.

## 1. What counts as an in-profile company ("SaaS")

KEEP (`saas`):
- Owns a **software product sold as a subscription / as-a-service**. B2B or B2C both qualify as
  "SaaS" for classification, but B2C is flagged (`is_b2c`) and excluded when **B2B-only** is on.
- Fintech **with its own product** (a platform/app it sells), not a fund or brokerage.
- A hardware company that **also sells a substantial software platform** as a core offering.

DROP (`not_saas`):
- Agency / consultancy / IT-outsourcing / dev-shop — builds software **for clients**, no own product.
- Pure hardware / device maker with no significant software product.
- Holding / investment group with no single product of its own.
- Offline or services business (utility, logistics operator, event, nonprofit, lab-run diagnostic).

HARD CASES (this is where cheap heuristics fail — resolve by reading, not by a single signal):
- Product **and** services (hybrid) → `saas` only if the product is a standalone SaaS; if mainly a
  services shop, `not_saas`.
- "Has a login / pricing page" alone does **not** prove SaaS (a battery or hardware firm can have
  both). Read what the company actually sells.

## 2. Title tiers (who is worth contacting)

Applied per lead, first match wins (see `classify_title` in `filter_and_bucket.py`):

| Tier | Bucket | Examples | Action |
| --- | --- | --- | --- |
| Pre-drop | `drop` | executive/personal assistant, intern, trainee, fractional, "ex-CEO" | always drop |
| Advisory | `drop` | advisor, consultant, coach, mentor, investor, board member — **unless also founder/owner** | drop |
| Decision-maker core | `keep_t1` | Founder, Co-founder, Owner, CEO, Managing Director, Chairman (many languages) | keep always |
| Function drop | `drop` | Finance/CFO, HR/CHRO, recruiting, legal, SDR/BDR, customer success/support, office manager, community manager | drop (beats seniority: "VP Finance" drops) |
| Decision-maker seniority | `keep_t1` | C-level, President, VP/SVP/EVP, Head of, Director, GM | keep always |
| Senior | `keep_t2` | Principal, Team/Tech/Eng/Product/Design Lead, Senior Manager, Staff Engineer | keep always |
| Specialist (conditional) | `ic_conditional` | rank-and-file Product Manager, Designer, Engineer/Developer | keep **only if company is small** (see §3) |
| No rule matched | `review` | ambiguous / non-standard | needs a look |

"Founder-speak" exact titles (`building`, `stealth`, …) are treated as `keep_t1` (stealth founders).
Marketing leaders (CMO / Head of Growth) are kept when they land in t1/t2 by seniority.

## 3. Toggles (the operator's two-decision surface)

- **B2B-only** — default **on**. B2C products flagged and dropped. Turn off to keep B2C.
- **Giant-company ceiling** — default **on**: companies over **~1,000 employees** are dropped
  (reason `giant`) even if genuinely SaaS — outreach from a small vendor won't land at a
  Mastercard-class enterprise. Size is mostly missing from raw exports, so enforce it twice:
  strip *famous* giants by name before the enrichment hand-off (don't pay for domains you'll
  discard), and flag obvious global-enterprise sites at classification time.
- **Small-company threshold** — default **≤ 200 employees**. `ic_conditional` specialists are kept
  only for companies at/under this size. Company size is usually unknown at classification time, so
  specialists always land in a separate `2_ic_conditional_leads.csv` for a size check rather than
  the ready list.
- **Strictness** — default **strict**: a company still `uncertain` after all classification tiers is
  left OUT of the ready list. **Broad** puts uncertain companies' leads into a review file instead.
- **Geography** — **India and Africa are hard-excluded by default** (operator rule from the source
  engagement, 22.07.2026: these geos never convert for this ICP). Word-boundary match on the
  free-text country field ("Indiana" ≠ "India"); excluded leads stay in the spine tagged
  `drop / geo_excluded(India/Africa)` for audit. Disable with `--no-geo-filter` (stage-1 script)
  when targeting a different market. All other geos are carried through for the operator to slice.

## 4. Industry buckets (free fast-path, before any site read)

From the lead's industry field (see `industry_bucket` in `filter_and_bucket.py`):

- `clear_saas` (Computer Software, Internet, …) → keep for free, no site read needed.
- `clear_drop` (Real Estate, Health Care, Transport, Construction, Retail, Manufacturing,
  Insurance, Government, Nonprofit, Telecom, Logistics, …) → drop for free.
- `grey_ITfin` (IT Services, Consulting, Financial Services, Banking, Staffing, Advertising) →
  ambiguous, must read the site.
- `software_dev` (Software Development) → often outsourcing; must read the site.
- `longtail` (everything else) → must read the site.
- `blank` (no industry) → must read the site.

Only `grey`, `software_dev`, `longtail`, and `blank` companies **without a website in the data**
need paid enrichment. Everything with a website is read for free.
