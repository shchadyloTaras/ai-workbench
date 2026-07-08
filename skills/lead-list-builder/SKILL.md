---
name: lead-list-builder
description: Turn a raw, messy lead/company export (LinkedIn dump, CRM export, purchased list) into a clean, ready-to-use outreach list — only companies that fit a target profile (default: SaaS product companies) and only decision-maker/senior contacts — as cheaply as possible, pausing once for a domain-enrichment step (Clay) that needs a human. Use when someone hands you a big lead file and asks "filter this down to the right companies and people", "clean my leads", "who here is actually SaaS", or "build me a target list". Non-technical-friendly: the operator makes at most two decisions; everything else has a safe default.
---

# lead-list-builder

You turn a raw lead export into a clean target list in three stages, with one human pause in the
middle. The single principle that keeps it correct **and** cheap: **spend effort in order of
price, and never treat a cheap signal as a final answer.** Free rules first (titles, industry),
then read the sites you already have, then pay for enrichment only on what's left, and re-read
anything a cheap heuristic guessed. Paid enrichment (Clay) is touched **once**, on de-duplicated
companies only.

The pipeline mechanics are project-agnostic. The *definition* of a good company and a good title
lives in [`references/icp-ruleset.md`](references/icp-ruleset.md) — swap that file to retarget the
skill; the default ruleset is "B2B SaaS product companies + decision-maker titles".

## How to run

### Stage 0 — Intake (get exactly two confirmations, then nothing else)

1. **Find the file.** Ask for / locate the export. Make a per-run working folder next to it,
   e.g. `leads_run_<YYYY-MM-DD>/`, and copy the input in. **Never write over the operator's file.**
2. **Detect the columns.** Read the header + ~30 sample rows and map these roles (support English
   and other languages, and messy names): **company** (required), **title** (required), **website /
   domain**, **person LinkedIn URL**, **country**, **industry**, **company description**, **person
   name** (single, or first+last), **row id**. Then show the operator your mapping in one plain
   block and ask **"is this right?"** — e.g. *"company = `Company`, title = `Job Title`, website =
   `Website` (filled in 4% of rows), country = `Location`. Correct?"* If the **company** column
   can't be found, STOP and say so — the skill can't run without it.
3. **Confirm the ICP toggles in one screen, with defaults** (from `references/icp-ruleset.md`):
   *"I'll keep SaaS companies, **B2B only** (B2C dropped), titles = decision-makers + seniors
   (rank-and-file specialists only at small companies ≤200). Strict mode: anything still uncertain
   is left out. Press enter to accept, or tell me what to change."* Record the answers.

### Stage 1 — Free filter (no cost)

4. Run `scripts/filter_and_bucket.py` with the confirmed column mapping (see its `--help`). It
   writes `leads_master_tagged.csv` (the join spine), the clear keep/drop company files, the
   `companies_have_website.csv` set, and `enrichment_input.csv`. Report the funnel in plain terms.

### Stage 2 — Classify the companies that already have a website (still no cost)

5. **Tier 1 (cheap):** run `scripts/classify_heuristic.py --input companies_have_website.csv
   --col-website existing_website`. It fetches each site and captures its title/description.
6. **Tier 2 (free re-read):** for **every** company — not just the unclear ones — do a real read of
   the captured `title`/`meta`/`snip` and decide SaaS vs not per the ruleset. A lone tier-1 signal
   (e.g. "has a login") is **never** final on its own — read the text. See
   [`references/classification-tiers.md`](references/classification-tiers.md).
7. **Tier 3 (still free-ish):** for whatever is still `uncertain` / `blocked` / `unreachable`
   (dead site, JS-only page, bit.ly, thin text), do a web search for the company and classify from
   what you find. This is the pass that clears the "uncertain tail". Merge all tiers into a
   `final_verdict` column (`saas` / `not_saas` / `uncertain`) with `final_conf`, `final_reason`,
   `final_source`, and `is_b2c`.

### Enrichment pause (the one human step) — STOP and hand off

8. If `enrichment_input.csv` is non-empty and no `clay_output.csv` exists yet, **STOP** and print
   the exact Clay instructions from [`references/clay-enrichment.md`](references/clay-enrichment.md),
   including the estimated size and cost, and the money rule: **domain lookup only — no AI / email /
   company-enrichment columns.** Tell the operator to drop the result back as `clay_output.csv` and
   re-run the skill. Do not proceed past this point in the same run.

### Resume — after Clay (detected automatically)

9. On re-invocation, if `clay_output.csv` is present, continue from here. Detect its resolved-domain
   column, then run Stage 2's three tiers on the enriched companies exactly as above.

### Stage 3 — Finalize (deterministic)

10. Merge the have-website verdicts and the enriched verdicts into one companies-with-`final_verdict`
    file, then run `scripts/finalize.py --companies <that> --leads leads_master_tagged.csv`
    with `--b2b-only` (unless the operator turned it off) and `--broad` only if they chose the wide
    list. It writes `1_ready_leads.csv`, `2_ic_conditional_leads.csv`, `3_company_classification.csv`,
    `_SUMMARY.txt`.
11. Give a short plain-language recap: how many companies in / out, how many ready leads, what (if
    anything) needs a human eye, and the file names.

## Rules

- **Two decisions max** from the operator (column mapping, ICP toggles). Everything else has a
  default — never make them configure the rules.
- **Never overwrite the input.** All work goes in the per-run folder.
- **De-dup to companies before enrichment.** Never send raw leads to Clay — half the credits would
  burn on duplicates. One credit ≈ one company.
- **Clay = domain lookup only.** Never enable AI columns, email finding, or full company enrichment.
  State this in the pause message every time.
- **A lone tier-1 heuristic verdict is never final** — always do the tier-2 read of the captured
  text before shipping a company as SaaS. (This is the guardrail against false "SaaS" like a battery
  company that merely has a login page.)
- **No-company / placeholder rows** (Stealth, Self-employed, blank) are set aside to a manual file,
  never auto-classified.
- **Strict by default:** a company that is still `uncertain` after all three tiers is left OUT of
  the ready list (surface it, don't ship it). Only `--broad` puts it in a review file.
- **B2B-only by default.** B2C products are flagged and excluded unless the operator opts them in.
- **Announce cost before spending it.** Before the pause, state ~how many companies go to Clay and
  the rough price.

## Output

Files in the per-run folder:

- `1_ready_leads.csv` — the deliverable: decision-makers + seniors at in-profile companies
  (`Company, Website, SaaS confidence %, Name, Title, Level, Country, LinkedIn`), sorted by company.
- `2_ic_conditional_leads.csv` — specialists to include only if the company is small.
- `3_company_classification.csv` — audit: every company, verdict, confidence, reason, method.
- `_SUMMARY.txt` — plain-language counts and next steps.

And, at the pause, a printed Clay hand-off block (file to upload, the domain-only rule, est. cost).
