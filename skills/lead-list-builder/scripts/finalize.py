#!/usr/bin/env python3
"""
finalize.py — stage 3 (deterministic): turn company verdicts + the tagged
lead spine into the final, ready-to-use contact lists.

Takes:
  --companies  a CSV of companies each carrying a FINAL verdict column
               (default `final_verdict` in {saas, not_saas, uncertain}); may
               also carry final_conf, final_reason, final_source, is_b2c,
               a website column, industry, n_icp_leads. This file is produced
               by merging the tier-1 heuristic with the tier-2 LLM / tier-3
               web-search reads (the SKILL orchestrates that merge).
  --leads      leads_master_tagged.csv from stage 1 (company_key + title_bucket
               + person fields).

Applies the ICP toggles:
  --b2b-only            (flag) companies flagged is_b2c are excluded from SaaS.
  --strict / --broad    strict (default): uncertain companies are left OUT of
                        the ready list. broad: their leads go to a review file.
  --ic-size-threshold N informational only (we usually lack company size here),
                        so rank-and-file (ic_conditional) leads always land in
                        their own "only if company is small" file, never the
                        ready list.

Writes -> --outdir:
  1_ready_leads.csv            decision-makers + seniors at SaaS companies (USE THIS)
  2_ic_conditional_leads.csv   specialists — only if the company is small
  3_company_classification.csv audit: every company, verdict, confidence, reason, method
  _SUMMARY.txt                 plain-language recap (counts in / out, what needs attention)
"""

import argparse
import csv
import os
from collections import Counter, defaultdict

TRUEY = {"true", "yes", "1", "y", "так", "b2c", "saas_b2c"}
LEVEL = {"keep_t1": "decision-maker", "keep_t2": "senior", "ic_conditional": "specialist"}


def first_present(row, names):
    for n in names:
        if n in row and (row.get(n) or "").strip():
            return row[n].strip()
    return ""


def main():
    ap = argparse.ArgumentParser(description="Join company verdicts to leads and emit final contact lists.")
    ap.add_argument("--companies", required=True)
    ap.add_argument("--leads", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--col-verdict", default="final_verdict")
    ap.add_argument("--b2b-only", action="store_true")
    ap.add_argument("--broad", action="store_true", help="include uncertain companies' leads in a review file")
    ap.add_argument("--ic-size-threshold", type=int, default=200)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # ---- load company verdicts, keyed by company_key ----
    comp = {}
    b2b_excluded = 0
    for r in csv.DictReader(open(args.companies, encoding="utf-8-sig", errors="replace")):
        key = (r.get("company_key") or "").strip()
        if not key:
            continue
        verdict = (r.get(args.col_verdict) or r.get("verdict") or "").strip().lower()
        is_b2c = (r.get("is_b2c") or "").strip().lower() in TRUEY or \
                 (r.get("category") or "").strip().lower() in TRUEY
        reason = r.get("final_reason") or r.get("reason") or ""
        if args.b2b_only and is_b2c and verdict == "saas":
            verdict = "not_saas"
            reason = "B2C excluded (B2B-only) | " + reason
            b2b_excluded += 1
        comp[key] = {
            "company_name": r.get("company_name") or "",
            "verdict": verdict,
            "conf": r.get("final_conf") or r.get("conf") or "",
            "reason": reason,
            "source": r.get("final_source") or "",
            "website": first_present(r, ["existing_website", "resolved_domain", "website", "domain"]),
            "industry": r.get("industry") or "",
            "is_b2c": "yes" if is_b2c else "",
        }

    # ---- stream leads, attach verdicts ----
    ready, ic_cond, review = [], [], []
    seen_saas_companies = set()
    for l in csv.DictReader(open(args.leads, encoding="utf-8-sig", errors="replace")):
        key = (l.get("company_key") or "").strip()
        if not key or key not in comp:
            continue
        c = comp[key]
        v = c["verdict"]
        bucket = (l.get("title_bucket") or "").strip()
        rec = {
            "Company": c["company_name"] or l.get("company_name", ""),
            "Website": c["website"],
            "SaaS confidence %": c["conf"],
            "Name": l.get("full_name", ""),
            "Title": l.get("job_title", ""),
            "Level": LEVEL.get(bucket, bucket),
            "Country": l.get("country", ""),
            "LinkedIn": l.get("linkedin_url", ""),
        }
        if v == "saas":
            if bucket in ("keep_t1", "keep_t2"):
                ready.append(rec)
                seen_saas_companies.add(key)
            elif bucket == "ic_conditional":
                ic_cond.append(rec)
        elif v == "uncertain" and args.broad and bucket in ("keep_t1", "keep_t2"):
            review.append(rec)

    order = {"decision-maker": 0, "senior": 1, "specialist": 2}
    for lst in (ready, ic_cond, review):
        lst.sort(key=lambda r: (r["Company"].lower(), order.get(r["Level"], 9), r["Name"].lower()))

    HEAD = ["Company", "Website", "SaaS confidence %", "Name", "Title", "Level", "Country", "LinkedIn"]

    def write(path, rows):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=HEAD, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

    O = args.outdir
    write(os.path.join(O, "1_ready_leads.csv"), ready)
    write(os.path.join(O, "2_ic_conditional_leads.csv"), ic_cond)
    if args.broad:
        write(os.path.join(O, "2b_uncertain_review_leads.csv"), review)

    # audit
    vcount = Counter(c["verdict"] for c in comp.values())
    with open(os.path.join(O, "3_company_classification.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Company", "Website", "Verdict", "Confidence %", "B2C?", "Reason", "Method"])
        for c in sorted(comp.values(), key=lambda c: (c["verdict"] != "saas", c["company_name"].lower())):
            w.writerow([c["company_name"], c["website"], c["verdict"], c["conf"], c["is_b2c"], c["reason"][:160], c["source"]])

    # summary
    lines = [
        "LEAD-LIST-BUILDER — SUMMARY",
        "",
        f"Companies classified : {len(comp):,}",
        f"  SaaS               : {vcount.get('saas', 0):,}",
        f"  not SaaS           : {vcount.get('not_saas', 0):,}",
        f"  uncertain          : {vcount.get('uncertain', 0):,}",
        f"  (B2C excluded by B2B-only: {b2b_excluded:,})" if args.b2b_only else "  (B2B-only: off — B2C kept)",
        "",
        f"READY leads (decision-makers + seniors at SaaS): {len(ready):,}  in {len(seen_saas_companies):,} companies",
        f"  -> 1_ready_leads.csv   ← use this for outreach",
        f"Specialist leads (only if company is small, <= {args.ic_size_threshold}): {len(ic_cond):,}",
        f"  -> 2_ic_conditional_leads.csv",
    ]
    if args.broad:
        lines.append(f"Uncertain-company leads for review: {len(review):,} -> 2b_uncertain_review_leads.csv")
    lines += ["", "Audit of every company + why: 3_company_classification.csv"]
    txt = "\n".join(lines) + "\n"
    open(os.path.join(O, "_SUMMARY.txt"), "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
