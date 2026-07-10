#!/usr/bin/env python3
"""
filter_and_bucket.py — stage 1 of lead-list-builder (FREE, no paid tools).

Reads a raw lead export (any column layout — you pass a column mapping),
then:
  1. Classifies every lead's job title into a tier
     (keep_t1 / keep_t2 / ic_conditional / drop / review) using the ICP
     title rules in references/icp-ruleset.md.
  2. Sets aside leads with no / placeholder company name (Stealth, Self-employed,
     Freelance, …) into a separate "manual" file — never auto-processed.
  3. Dedups leads to UNIQUE COMPANIES; a company is "in-play" if it has at
     least one kept-title lead.
  4. Buckets each in-play company by industry
     (clear_saas / software_dev / grey_ITfin / clear_drop / longtail / blank).
  5. Splits companies into:
       - clear_saas          -> keep for free (industry alone is decisive)
       - clear_drop          -> drop for free
       - have_website        -> classify now, no enrichment needed
                                (includes companies whose NAME embeds the domain,
                                 e.g. "Checkout.com", "boost.ai" — no credits wasted)
       - need_enrichment     -> go to the enrichment tool (Clay) to find a domain
     and writes a ready-to-upload enrichment-input file.

The title rules, company-key normalization, and industry buckets are the
PROJECT-AGNOSTIC core. What changes per file is only the column mapping.

Deterministic: fixed random seed for any sampling.

Usage:
  python3 filter_and_bucket.py \
      --input leads.csv --outdir out/ \
      --col-company Company --col-title Title \
      [--col-website Website] [--col-linkedin "LinkedIn URL"] \
      [--col-country Country] [--col-industry Industry] \
      [--col-description Description] [--col-id id] \
      [--col-name "Full Name" | --col-firstname First --col-lastname Last] \
      [--enrich-cap N]   # cap the enrichment batch to N companies (0 = all that need it)

Outputs (UTF-8-BOM so Excel opens them cleanly) -> --outdir:
  leads_master_tagged.csv            one row per lead, with its tier tag (join spine)
  leads_no_company_manual.csv        leads with no/placeholder company
  companies_clear_saas_keep.csv      keep, free (industry)
  companies_clear_nonsaas_drop.csv   drop, free (industry)
  companies_have_website.csv         classify now (stage 2), no enrichment
  enrichment_input.csv               -> upload to Clay (domain lookup only)
  enrichment_remaining.csv           companies over the cap, for a later batch
"""

import argparse
import csv
import os
import random
import re
import sys
from collections import Counter, defaultdict

RANDOM_SEED = 42

# ===========================================================================
# ICP title classification — PROJECT-AGNOSTIC CORE (see references/icp-ruleset.md)
# Order of checks matters. Keep in sync with the ruleset doc.
# ===========================================================================

RX = lambda p: re.compile(p, re.I)

PRE_DROP = RX(
    r"executive assistant|personal assistant|assistant to|office of the|"
    r"\b(intern|internship|trainee|student|aspiring)\b|"
    r"\b(fractional)\b|"
    r"\b(former|ex)[- ](ceo|cto|cpo|coo|founder|co-?founder)"
)
ADVISORY = RX(r"\b(advisor|adviser|advisory|consultant|consulting|coach|mentor|investor|board member|venture partner)\b")
FOUNDER_OWNER = RX(
    r"\b(founder|co-?founder|cofounder|founding|fondateur|fondatrice|gr[üu]nder(in)?|medgrundare|grundare|"
    r"oprichter|fundador|fundadora)\b|(?<!product )(?<!process )\bowner\b|\beigenaar\b|\binhaber(in)?\b|\bpropietario\b"
)
T1_CORE = RX(
    r"\b(founder|co-?founder|cofounder|founding partner|entrepreneur|fondateur|fondatrice|gr[üu]nder(in)?|medgrundare|grundare|"
    r"oprichter|fundador|fundadora)\b|"
    r"(?<!product )(?<!process )\bowner\b|\beigenaar\b|\binhaber(in)?\b|\bpropietario\b|"
    r"\bceo\b|chief executive|\bpdg\b|gesch[äa]ftsf[üu]hrer|directeur g[ée]n[ée]ral|directrice g[ée]n[ée]rale|"
    r"managing director|general director|director general|amministratore delegato|gerente general|"
    r"\bchairman\b"
)
FOUNDER_SPEAK = {"building", "building something new", "building something", "stealth", "stealth founder", "stealth mode"}
FUNC_DROP = RX(
    r"\b(cfo|chief financial|chro|chief people|chief human resources)\b|"
    r"\b(finance|financial|accounting|accountant|bookkeep\w*|controller|treasurer|payroll|tax|audit\w*)\b|"
    r"\bhr\b|human resources|people operations|people ops|"
    r"\b(recruit\w*|sourcer|talent acquisition|headhunter|staffing)\b|"
    r"\b(legal|counsel|paralegal|compliance)\b|"
    r"\b(sdr|bdr)\b|sales development|lead generation|leadgen|"
    r"customer (success|support|care|service)|help ?desk|"
    r"office manager|administrative|admin assistant|"
    r"community manager"
)
T1_SENIOR = RX(
    r"\bchief\b|\b(cto|cpo|cpto|coo|cio|ciso|cmo|cro|cco|cdo)\b|"
    r"\bpresident\b|\b(vp|svp|evp|avp)\b|vice president|"
    r"\bhead of\b|\bhead,\b|\bdirector\b|\bdirecteur\b|\bdirectrice\b|\bleiter(in)?\b|\bhoofd\b|"
    r"managing partner|general manager"
)
T2_SENIOR = RX(
    r"\bprincipal\b|\b(team|tech|engineering|product|design|group) lead\b|\blead (product|engineer|developer|designer|architect)\b|"
    r"senior (product )?manager|engineering manager|product management|"
    r"senior product manager|\bstaff (engineer|developer)\b|\blead\b|"
    r"\b(product|design|engineering|technology) leader\b"
)
IC_COND = RX(
    r"product owner|product manager|produktmanager|chef de produit|product designer|"
    r"product operations|\bproduct\b|"
    r"\b(ux|ui)\b|\bdesigner\b|ux research\w*|"
    r"\b(engineer|engineering|developer|programmer|architect|devops)\b|software develop\w*"
)


def classify_title(title: str):
    """Return (bucket, reason). Buckets: keep_t1 | keep_t2 | ic_conditional | drop | review."""
    t = (title or "").strip()
    if not t:
        return "review", "empty title"
    if t.lower().strip(".!") in FOUNDER_SPEAK:
        return "keep_t1", "founder-speak (stealth)"
    if PRE_DROP.search(t):
        return "drop", "assistant/intern/fractional/former"
    if ADVISORY.search(t) and not FOUNDER_OWNER.search(t):
        return "drop", "advisor/consultant/investor"
    if T1_CORE.search(t):
        return "keep_t1", "founder/owner/CEO-level"
    if FUNC_DROP.search(t):
        return "drop", "finance/HR/recruiting/legal/support/sales-dev"
    if T1_SENIOR.search(t):
        return "keep_t1", "C-level/VP/Head/Director"
    if T2_SENIOR.search(t):
        return "keep_t2", "Lead/Principal/Senior Manager"
    if IC_COND.search(t):
        return "ic_conditional", "product/design/eng IC (keep if small company)"
    return "review", "no rule matched"


# ===========================================================================
# Company-key normalization (conservative — don't over-merge distinct firms)
# ===========================================================================

LEGAL_SUFFIX = re.compile(
    r"[\s,.]+(inc|llc|ltd|limited|gmbh|bv|b\.v|ab|aps|oy|srl|sarl|sas|pty|co|corp|corporation|s\.a|sa)\.?$", re.I
)
PLACEHOLDER = {
    "self-employed", "self employed", "freelance", "freelancer", "independent",
    "confidential", "personal", "private", "n/a", "na", "none", "-", "--", ".",
}
PLACEHOLDER_RX = re.compile(r"\bstealth\b|self[- ]employed|sole proprietor", re.I)


def is_placeholder(key: str) -> bool:
    return (not key) or key in PLACEHOLDER or bool(PLACEHOLDER_RX.search(key))


def company_key(name: str) -> str:
    s = (name or "").strip().strip('"').strip()
    s = re.sub(r"\s+", " ", s).lower()
    s = LEGAL_SUFFIX.sub("", s).strip(" ,.")
    return s


NAME_DOMAIN_RX = re.compile(
    r"\b([a-z0-9][a-z0-9-]{1,62}\.(?:com|io|ai|co|net|org|app|dev|tech|cloud|digital|"
    r"agency|studio|us|uk|de|fr|ca|in|me|ly|gg|so|xyz))\b", re.I)


def domain_from_name(name: str) -> str:
    """A name like 'Checkout.com' or 'boost.ai' already carries the domain —
    treat it as the website so the company never reaches paid enrichment."""
    m = NAME_DOMAIN_RX.search(name or "")
    return m.group(1).lower() if m else ""


# ===========================================================================
# Industry bucketing (see references/icp-ruleset.md)
# ===========================================================================

def industry_bucket(ind: str) -> str:
    s = (ind or "").lower().strip().strip('"')
    if not s:
        return "blank"
    if any(k in s for k in ("computer software", "internet", "technology, information",
                            "information technology and internet")):
        return "clear_saas"
    if "software development" in s:
        return "software_dev"
    if any(k in s for k in ("it services", "information technology & services",
                            "information technology and services", "consult",
                            "financial services", "banking", "investment", "venture capital",
                            "marketing & advert", "marketing and advert", "advertising",
                            "staffing", "recruit")):
        return "grey_ITfin"
    if any(k in s for k in ("real estate", "hospital", "health care", "transport", "trucking",
                            "railroad", "construction", "retail", "restaurant", "hospitality",
                            "education management", "primary/secondary", "higher education",
                            "manufactur", "automotive", "oil", "mining", "farming", "food",
                            "apparel", "wholesale", "insurance", "law practice", "government",
                            "non-profit", "nonprofit", "civic", "religious", "sports",
                            "broadcast", "publishing", "telecommunication", "logistics",
                            "wine", "leisure", "travel", "airlines", "maritime", "utilities")):
        return "clear_drop"
    return "longtail"


TIER_RANK = {"keep_t1": 0, "keep_t2": 1, "ic_conditional": 2, "review": 3, "drop": 4}
IN_PLAY = {"keep_t1", "keep_t2", "ic_conditional"}


# ===========================================================================
# Runner
# ===========================================================================

def get(row, col):
    return (row.get(col) or "").strip() if col else ""


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description="Filter + dedup + bucket a raw lead export (stage 1).")
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--col-company", required=True, help="column holding the company name")
    ap.add_argument("--col-title", required=True, help="column holding the person's job title")
    ap.add_argument("--col-website", default="")
    ap.add_argument("--col-linkedin", default="")
    ap.add_argument("--col-country", default="")
    ap.add_argument("--col-industry", default="")
    ap.add_argument("--col-description", default="")
    ap.add_argument("--col-id", default="")
    ap.add_argument("--col-name", default="", help="single full-name column")
    ap.add_argument("--col-firstname", default="")
    ap.add_argument("--col-lastname", default="")
    ap.add_argument("--enrich-cap", type=int, default=0, help="max companies in the enrichment batch (0 = all that need it)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    leads_total = 0
    title_counts = Counter()
    review_titles = Counter()
    noname_rows = []
    lead_tags = []

    companies = defaultdict(lambda: {
        "display": Counter(), "industries": Counter(), "buckets": Counter(),
        "n_leads": 0, "n_inplay": 0, "website": "", "description": "", "best": None,
    })

    with open(args.input, newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        if args.col_company not in (reader.fieldnames or []):
            sys.exit(f"ERROR: company column {args.col_company!r} not found. Columns: {reader.fieldnames}")
        for row in reader:
            leads_total += 1
            title = get(row, args.col_title)
            bucket, reason = classify_title(title)
            title_counts[bucket] += 1
            if bucket == "review":
                review_titles[title] += 1

            raw_name = get(row, args.col_company)
            key = company_key(raw_name)
            placeholder = is_placeholder(key)
            linkedin = get(row, args.col_linkedin)
            country = get(row, args.col_country)
            if args.col_name:
                full_name = get(row, args.col_name)
            else:
                full_name = f"{get(row, args.col_firstname)} {get(row, args.col_lastname)}".strip()

            lead_tags.append({
                "lid": get(row, args.col_id),
                "linkedin_url": linkedin,
                "full_name": full_name,
                "job_title": title,
                "title_bucket": bucket,
                "title_reason": reason,
                "company_name": raw_name,
                "company_key": "" if placeholder else key,
                "country": country,
            })

            if placeholder:
                noname_rows.append({
                    "full_name": full_name, "job_title": title, "title_bucket": bucket,
                    "linkedin_url": linkedin, "country": country, "company_name_raw": raw_name,
                })
                continue

            c = companies[key]
            c["n_leads"] += 1
            c["display"][raw_name] += 1
            ind = get(row, args.col_industry)
            if ind:
                c["industries"][ind] += 1
            if bucket in IN_PLAY:
                c["n_inplay"] += 1
            web = get(row, args.col_website)
            if web and not c["website"]:
                c["website"] = web
            desc = get(row, args.col_description)
            if desc and not c["description"]:
                c["description"] = desc
            cand = (TIER_RANK[bucket], 0 if country else 1, linkedin, full_name, title, country)
            if c["best"] is None or cand < c["best"]:
                c["best"] = cand

    # ---- company-level bucketing ----
    comp_rows = []
    bucket_counts = Counter()
    for key, c in companies.items():
        if c["n_inplay"] == 0:
            continue
        top_ind = c["industries"].most_common(1)[0][0] if c["industries"] else ""
        b = industry_bucket(top_ind)
        bucket_counts[b] += 1
        rank, _, li, name, title, country = c["best"]
        display_name = c["display"].most_common(1)[0][0]
        comp_rows.append({
            "company_key": key,
            "company_name": display_name,
            "industry": top_ind,
            "industry_bucket": b,
            "n_leads": c["n_leads"],
            "n_icp_leads": c["n_inplay"],
            "existing_website": c["website"] or domain_from_name(display_name),
            "has_description": "yes" if c["description"] else "",
            "best_lead_name": name,
            "best_lead_title": title,
            "best_lead_linkedin": li,
            "best_lead_country": country,
        })
    comp_rows.sort(key=lambda r: (-r["n_icp_leads"], r["company_key"]))
    COMP_FIELDS = list(comp_rows[0].keys()) if comp_rows else []

    by_bucket = defaultdict(list)
    for r in comp_rows:
        by_bucket[r["industry_bucket"]].append(r)

    # companies that already have a website -> classify now (skip enrichment)
    have_site = [r for r in comp_rows if r["existing_website"] and r["industry_bucket"] != "clear_drop"]
    need_site = lambda rows: [r for r in rows if not r["existing_website"]]

    grey_need = need_site(by_bucket["grey_ITfin"])
    long_need = need_site(by_bucket["longtail"])
    blank_need = need_site(by_bucket["blank"])
    swdev_need = need_site(by_bucket["software_dev"])

    # enrichment batch: grey + longtail + software_dev first, then blank sample to the cap
    core = grey_need + long_need + swdev_need
    random.seed(RANDOM_SEED)
    if args.enrich_cap and args.enrich_cap > 0:
        fill_n = max(0, args.enrich_cap - len(core))
        blank_sample = random.sample(blank_need, min(fill_n, len(blank_need)))
        batch = (core + blank_sample)[:args.enrich_cap]
    else:
        batch = core + blank_need
    picked = {r["company_key"] for r in batch}
    remaining = [r for r in (core + blank_need) if r["company_key"] not in picked]

    O = args.outdir
    n_master = write_csv(os.path.join(O, "leads_master_tagged.csv"), lead_tags, list(lead_tags[0].keys()) if lead_tags else [])
    n_noname = write_csv(os.path.join(O, "leads_no_company_manual.csv"), noname_rows, list(noname_rows[0].keys()) if noname_rows else [])
    n_saas = write_csv(os.path.join(O, "companies_clear_saas_keep.csv"), by_bucket["clear_saas"], COMP_FIELDS)
    n_drop = write_csv(os.path.join(O, "companies_clear_nonsaas_drop.csv"), by_bucket["clear_drop"], COMP_FIELDS)
    n_site = write_csv(os.path.join(O, "companies_have_website.csv"), have_site, COMP_FIELDS)
    n_enr = write_csv(os.path.join(O, "enrichment_input.csv"), batch, COMP_FIELDS)
    n_rem = write_csv(os.path.join(O, "enrichment_remaining.csv"), remaining, COMP_FIELDS)

    pct = lambda n, d: f"{100*n/d:.1f}%" if d else "-"
    inplay = sum(bucket_counts.values())
    print(f"LEADS: {leads_total:,}")
    for b in ("keep_t1", "keep_t2", "ic_conditional", "review", "drop"):
        print(f"  {b:15s} {title_counts[b]:>8,} ({pct(title_counts[b], leads_total)})")
    print(f"  no/placeholder company -> manual: {len(noname_rows):,}")
    print(f"\nIN-PLAY COMPANIES: {inplay:,}")
    for b in ("clear_saas", "software_dev", "grey_ITfin", "clear_drop", "longtail", "blank"):
        print(f"  {b:14s} {bucket_counts[b]:>8,} ({pct(bucket_counts[b], inplay)})")
    print(f"\nhave website (classify now): {n_site:,}")
    print(f"need enrichment (-> Clay)  : {n_enr:,}" + (f"  [capped; {n_rem:,} deferred]" if args.enrich_cap else ""))
    print(f"clear keep (free): {n_saas:,} | clear drop (free): {n_drop:,}")
    print(f"\nfiles -> {O}")
    for name, n in [("leads_master_tagged.csv", n_master), ("leads_no_company_manual.csv", n_noname),
                    ("companies_clear_saas_keep.csv", n_saas), ("companies_clear_nonsaas_drop.csv", n_drop),
                    ("companies_have_website.csv", n_site), ("enrichment_input.csv", n_enr),
                    ("enrichment_remaining.csv", n_rem)]:
        print(f"  {name:38s} {n:>8,}")


if __name__ == "__main__":
    main()
