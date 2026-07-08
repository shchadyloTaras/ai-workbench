# lead-list-builder

> **One task:** turn a raw, messy lead/company export into a clean outreach list — only in-profile
> companies (default: B2B SaaS) and only decision-maker/senior contacts — for the lowest cost.

## What it does

You hand it a big, noisy export (a LinkedIn dump, a CRM export, a purchased list) and it returns a
short, trustworthy list of **who to contact where**: decision-makers and seniors at companies that
match your target profile. It filters for free first (job titles, industry), reads the websites it
already has, and only pays for domain enrichment on the companies that still need it — pausing once
so a human runs that enrichment step in Clay. It will **not** invent leads (every contact comes from
your file), and it will **not** ship a company as "SaaS" on a shallow signal alone — it reads the
site before deciding.

The operator makes at most **two decisions** (are the detected columns right? are the default rules
OK?); everything else has a safe default.

## The main file

[`SKILL.md`](SKILL.md) — the instructions the AI follows.

## How to run it

- **As an agent skill:** copy this folder to `.claude/skills/lead-list-builder/` (project) or
  `~/.claude/skills/lead-list-builder/` (all projects); then say _"clean these leads"_ / _"build a
  target list from this file"_ / _"which of these are actually SaaS?"_ and attach the export.
- **As a slash command:** copy `SKILL.md`'s body into `.claude/commands/clean-leads.md`; invoke
  `/clean-leads` with the file.
- **As a human checklist:** follow the stages in `SKILL.md` by hand — run the three scripts in
  order, do the Clay step at the pause.

## The rules it enforces

- [`references/icp-ruleset.md`](references/icp-ruleset.md) — what counts as an in-profile company
  and a worth-contacting title (the default is B2B-SaaS; **swap this file to retarget**).
- [`references/classification-tiers.md`](references/classification-tiers.md) — the cheap→expensive
  classification method and why a heuristic verdict is never final.
- [`references/clay-enrichment.md`](references/clay-enrichment.md) — the domain-lookup hand-off and
  the money rules for the paid step.

## The scripts

- [`scripts/filter_and_bucket.py`](scripts/filter_and_bucket.py) — stage 1: title filter + dedup to
  companies + industry buckets + build the enrichment input. Takes a column mapping (any file shape).
- [`scripts/classify_heuristic.py`](scripts/classify_heuristic.py) — stage 2 tier-1: fetch each site,
  score SaaS vs services signals, and capture the text for the free read.
- [`scripts/finalize.py`](scripts/finalize.py) — stage 3: join verdicts to leads, apply the toggles,
  emit the ready list + audit + summary.

## Example

- [`examples/before-after.md`](examples/before-after.md) — a real run: 126k raw leads → 4,650 ready
  contacts at 1,683 SaaS companies, for ~$500 of enrichment instead of a ~$10k vendor bill.

## Why it's in this shape

The two design choices that matter: **spend in order of price** (free rules, then the sites you
already have, then paid enrichment only on the remainder) is what makes it ~20× cheaper than
enriching everything; and **a cheap signal proposes, a read decides** — the heuristic is only a
filter, every company is read before it's called in-profile — is what stops plausible-but-wrong
verdicts (a hardware firm with a login page reading as "SaaS"). The single human pause exists because
domain enrichment is the one step an AI can't do for you.
