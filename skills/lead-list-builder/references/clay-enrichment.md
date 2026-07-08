# Enrichment hand-off (Clay) — the one human step

Companies without a website in the source data need a **verified domain** before their site can be
read. That is the only thing enrichment is for here. Everything else (reading sites, classifying,
sizing) the skill does for free. Enrichment is touched **once**, on de-duplicated companies.

The skill prints this block at the pause, filled in with the real count and estimate.

## The money rule (state it every time)

**Domain lookup only. Do NOT enable AI columns, email finding, or full "company enrichment".**
Those multiply credit burn 2–5×. One credit ≈ one company for a plain domain lookup.

## Steps for the operator

1. Upload `enrichment_input.csv` to Clay as a new table (Import CSV).
2. Add **one** enrichment column: *"Find company website/domain from name"* (a domain-lookup /
   waterfall). Input = the `company_name` column; use `best_lead_country` as a disambiguator when
   the name is generic. ≈ 1 credit per row.
3. *(Optional fallback, only for rows that came back empty)* enrich the person from
   `best_lead_linkedin` → take the domain off their current company. Run this **only** on the empty
   rows, never the whole table.
4. Do not add any other column. If Clay suggests description / headcount / email — skip. The skill
   pulls description from the site itself and only sources size later, pointwise, where it changes a
   decision.
5. Export the table as CSV **with all original columns plus** the resolved domain (and
   `domain_source` if Clay provides it). Keep `company_key` untouched — it is the join key back.
6. Save that file next to the input as **`clay_output.csv`** and re-run the skill. It resumes
   automatically.

## Sizing / cost (the skill fills these in)

- Companies going to enrichment: **{N}** (unique, de-duplicated).
- Rough cost at ~1 credit/company: **{N} credits ≈ {price}**.
- If the batch is capped (budget), the rest waits in `enrichment_remaining.csv` for a later run.

## What to watch after the run

- **Match rate** — % of rows that got a domain (a good target for the "grey" bucket is >85%; the
  blank bucket is the unknown you're measuring).
- **Burn** — credits actually spent per row (should be ~1.0–1.2; higher means an extra column crept
  in — turn it off).
