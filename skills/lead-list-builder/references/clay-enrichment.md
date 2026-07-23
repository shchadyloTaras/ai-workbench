# Enrichment hand-off (Clay) — the one human step

Companies without a website in the source data need a **verified domain** before their site can be
read. That is the only thing enrichment is for here. Everything else (reading sites, classifying,
sizing) the skill does for free. Enrichment is touched **once**, on de-duplicated companies.

The skill prints this block at the pause, filled in with the real count and estimate.

`enrichment_input.csv` is already thinned before it gets here: name-embedded domains
("Checkout.com", "boost.ai") were extracted at stage 1, and famous giants (>~1,000 employees) were
stripped to `companies_giants_dropped.csv`. If you still spot a household-name enterprise in the
file, delete the row instead of enriching it.

## The money rule (state it every time)

**Domain lookup only. Do NOT enable AI columns, email finding, or full "company enrichment".**
Those multiply credit burn 2–5×.

Clay has **two separate meters — never conflate them**: **actions** (cheap, included in the plan,
self-renew monthly, do NOT roll over) and **data credits** (the expensive meter). A Clearbit domain
lookup spends only actions (≈ $0); person enrichment spends both. Price any step by which meter it
burns, not by "rows in the table".

## Steps for the operator

1. Upload `enrichment_input.csv` to Clay as a new table (Import CSV).
2. Add **one** enrichment column — and prefer the FREE one: the **Clearbit "Find Company Domain"**
   integration, input = the `company_name` column (use `best_lead_country` as a disambiguator when
   the name is generic). Measured on a real 14,429-company run: ~1 **action** per company,
   **0 data credits** ≈ $0 — actions are the plan's included, self-renewing meter. Only if Clearbit
   is unavailable fall back to a paid domain waterfall (≈ 1 credit per row — the expensive meter;
   never start there).
3. *(Optional fallback, only for rows that came back empty)* enrich the person from
   `best_lead_linkedin` → take the domain off their current company ("Enrich person"). Run this
   **only** on the empty rows, never the whole table — this one burns BOTH meters (~1 action +
   0.5 credits per row).
4. Do not add any other column. If Clay suggests description / headcount / email — skip. The skill
   pulls description from the site itself and only sources size later, pointwise, where it changes a
   decision.
5. Export the table as CSV **with all original columns plus** the resolved domain (and
   `domain_source` if Clay provides it). Clay usually lands the domain in its own column named
   `Domain` — leave it as is, don't rename anything; the skill finds it by content on resume.
   Keep `company_key` untouched — it is the join key back.
6. Save that file next to the input as **`clay_output.csv`** and re-run the skill. It resumes
   automatically.

## Sizing / cost (the skill fills these in)

- Companies going to enrichment: **{N}** (unique, de-duplicated).
- With the free Clearbit column: **{N} actions, 0 credits ≈ $0** — fits the plan's included
  actions. If {N} exceeds the monthly action pool, either stretch across months ($0) or bump the
  plan's action slider for one month and downgrade after.
- If the batch is capped (budget), the rest waits in `enrichment_remaining.csv` for a later run.

## What to watch after the run

- **Match rate** — % of rows whose cleaned domain column holds a REAL domain. The trap: "the
  action ran" ≠ "a domain was found" — Clay writes literal text like **"No Result Found"** into
  the column, and on a real 14,429-row run the ran-rate read 98.8% while the true found-rate was
  **67.2%**. Count only values that parse as domains. (Good target for the "grey" bucket is >85%;
  the blank bucket is the unknown you're measuring.)
- **Burn** — meter units actually spent per row (~1 action, 0 credits with Clearbit; credits
  ticking up means a paid column crept in — turn it off).
