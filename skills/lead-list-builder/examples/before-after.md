# Example: 126k raw LinkedIn leads → a clean SaaS target list

A real run of `lead-list-builder` (numbers are from the engagement it was generalized from).

## Before

One CSV: **126,117 leads** exported from a LinkedIn outreach campaign. Typical problems:

- No reliable "is this SaaS?" field — the one that existed was made from company names only and was
  wrong ~half the time.
- Company website present in only **3.5%** of rows; company size in **3.7%**. You can't filter by
  hand.
- Full of noise: interns, HR, recruiters, assistants; agencies and consultancies mixed in with real
  product companies; ~9% of rows have no company name at all.

Naive fix: pay a vendor to enrich all 126k rows ≈ **$10,400**.

## After

Run the skill. It asks two things — "are these the right columns?" and "keep the default rules
(B2B SaaS, decision-makers, strict)?" — then does the work:

| Stage | What happened | Result |
| --- | --- | --- |
| 1. Free filter | title rules + dedup to companies + industry buckets | 126,117 leads → **49,769 unique in-play companies**; 16,503 no-company rows set aside |
| 2. Read the free sites | 2,294 companies already had a website → tier-1 heuristic + tier-2 read + tier-3 web-search on the tail | **1,755 SaaS / 539 not-SaaS / 0 uncertain** |
| — pause — | 34,966 companies without a website → `enrichment_input.csv` to Clay (domain lookup only) | ≈ $500, not $10,400 |
| 3. Finalize | join SaaS companies back to their decision-maker/senior leads, B2B-only | **4,650 ready leads in 1,683 companies** |

Deliverable `1_ready_leads.csv` (decision-makers + seniors at SaaS companies):

```
Company,Website,SaaS confidence %,Name,Title,Level,Country,LinkedIn
AirDNA,https://airdna.co,96,…,CEO,decision-maker,United States,https://linkedin.com/in/…
Crelate,https://crelate.com,97,…,Founder,decision-maker,United States,https://linkedin.com/in/…
…
```

Plus `2_ic_conditional_leads.csv` (specialists, only if the company is small), and
`3_company_classification.csv` — an audit row for every company with the verdict, confidence,
one-line reason, and which tier decided it.

## The lesson baked into the skill

During review, a "battery" company (About:Energy / Voltt) showed up as SaaS. It turned out to be
correct — it sells a battery-cell **simulation & data platform**, i.e. software — but it exposed
that most companies had been accepted on a lone tier-1 signal ("has a login"), not a read. That is
why the skill now **always** runs the tier-2 read before shipping a company as in-profile, and never
treats a heuristic hit as final.
