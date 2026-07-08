#!/usr/bin/env python3
"""
classify_heuristic.py — stage 2, tier 1 (cheap, deterministic, no LLM).

Fetches each company's website and scores SaaS signals (pricing page / free
trial / login / app-subdomain / demo / API / SoftwareApplication JSON-LD)
against services-agency signals (agency/studio, outsourcing, "we build for
you", portfolio, quote) and ecommerce. Decisive overrides beat weak keyword
noise. This is TIER 1 only — see references/classification-tiers.md.

IMPORTANT: a tier-1 'saas'/'not_saas' verdict is NOT final on its own. Every
company still gets a tier-2 LLM read of the captured title/meta/snippet (the
About:Energy lesson: a lone "has a login" signal is not proof). This script
just does the cheap first pass and CAPTURES the site text so the LLM read
downstream is free (no re-fetch).

Verdicts: saas | not_saas | unclear | blocked | unreachable
  blocked     = live but bot-blocked (403/429/503)
  unclear     = conflicting/thin signals (incl. product+services hybrids)

Env:  LIMIT=N (sample first N)   WORKERS=N (default 24)

Usage:
  python3 classify_heuristic.py --input companies.csv --col-website existing_website \
      --outdir out/ [--out-name companies_classified.csv]

Passes through every input column and appends:
  verdict, conf, http, saas, svc, es(signals), esv(service-signals), title, meta, snip
"""

import argparse
import csv
import os
import re
import ssl
import sys
import html as ihtml
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import HTTPError

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

SAAS = [
    ("pricing_page",  r'href=["\'][^"\']*(pricing|/plans)\b', 4),
    ("pricing_text",  r'\b(pricing|our plans|price plans|per (month|user|seat)|/mo\b|billed (annually|monthly)|choose your plan)\b', 2),
    ("free_trial",    r'\b(free trial|start (for )?free|try (it )?free|get started free|no credit card|start your free trial|14[- ]day)\b', 4),
    ("signup_login",  r'\b(sign ?up|create (an|your) account|log ?in|sign ?in)\b', 1),
    ("app_subdomain", r'href=["\']https?://(app|my|dashboard|login|secure|portal)\.', 3),
    ("demo",          r'\b(book a demo|request a demo|schedule a demo|get a demo|see it in action|product tour|watch (the )?demo)\b', 3),
    ("platform_soft", r'\b(the .{0,25}? platform|our platform|the software|all-in-one platform|\bsaas\b|software as a service)\b', 2),
    ("api_docs",      r'\b(developer(s)? (docs|portal|api)|/docs\b|api reference|webhooks|\bsdk\b|integrations? (with|library|directory))\b', 1),
    ("trust",         r'\b(soc ?2|iso ?27001|gdpr|hipaa|uptime|single sign-on|\bsso\b|enterprise[- ]grade)\b', 1),
    ("reviews",       r'\b(g2\.com|capterra|trustradius|4\.\d/5|leader in [a-z ]+ on g2)\b', 1),
    ("subscription",  r'\b(subscription|subscribe|cancel anytime|upgrade your plan|manage your subscription)\b', 2),
    ("jsonld_soft",   r'"@type"\s*:\s*"(SoftwareApplication|WebApplication)"', 5),
]
SERVICES = [
    ("our_services",  r'\b(our services|services we (offer|provide)|what we do|full[- ]service)\b', 2),
    ("we_help_build", r'\b(we (help|design|build|develop|create) .{0,40}?(for you|for your|for clients|for brands|for businesses|your (brand|product|business)))\b', 3),
    ("agency_studio", r'\b((digital|creative|design|marketing|branding|dev(elopment)?|software) (agency|studio)|we are an? .{0,20}?(agency|studio|consultancy)|consulting firm|design & build)\b', 4),
    ("portfolio",     r'\b(our portfolio|view portfolio|selected work|recent projects|our work\b)\b', 1),
    ("quote_hire",    r'\b(get a quote|request a quote|hire (us|me)|work with us|let\'?s (talk|build)|book a call|schedule a call|start a project)\b', 2),
    ("outsourcing",   r'\b(staff augmentation|dedicated (development )?team|nearshore|offshore|custom software development|software development (company|services)|it (consulting|outsourcing)|managed (it )?services|end-to-end development)\b', 4),
    ("clients_served",r'\b(our clients|clients we|client testimonials|trusted by (leading )?(brands|clients))\b', 1),
]
ECOM = [("ecommerce", r'\b(add to cart|shop now|add to bag|view cart|free shipping|our (store|shop)\b)\b', 4)]

TAG_RE = re.compile(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>")
ANGLE_RE = re.compile(r"(?s)<[^>]+>"); WS_RE = re.compile(r"\s+")


def host_variants(u):
    u = (u or "").strip()
    u = re.sub(r"^https?://", "", u).strip("/").split("/")[0]
    if not u:
        return []
    apex = re.sub(r"^www\.", "", u)
    hosts = [f"www.{apex}", apex] if not u.startswith("www.") else [u, apex]
    return [f"https://{h}" for h in dict.fromkeys(hosts)] + [f"http://{h}" for h in dict.fromkeys(hosts)]


def get(url, timeout=11):
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html"})
        with urlopen(req, timeout=timeout, context=CTX) as r:
            return r.getcode(), r.read(500_000).decode(r.headers.get_content_charset() or "utf-8", "replace"), r.geturl()
    except HTTPError as e:
        try:
            body = e.read(50_000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body, url
    except Exception:
        return None, "", url


def fetch_site(url):
    base = None; blocked = False; home = ""
    for cand in host_variants(url):
        code, body, final = get(cand)
        if code == 200 and len(body) > 200:
            base = final.rstrip("/"); home = body; break
        if code in (403, 429, 503):
            blocked = True
    else:
        return ("blocked" if blocked else None), "", url
    combined = home
    m = re.match(r"(https?://[^/]+)", base)
    root = m.group(1) if m else base
    for path in ("/pricing", "/product"):
        code, body, _ = get(root + path)
        if code == 200 and len(body) > 200:
            combined += "\n" + body
    return 200, combined, base


def extract(doc):
    title = ""; m = re.search(r"(?is)<title[^>]*>(.*?)</title>", doc)
    if m:
        title = WS_RE.sub(" ", ANGLE_RE.sub(" ", m.group(1))).strip()[:200]
    descs = re.findall(r'(?is)<meta[^>]+(?:name=["\']description["\']|property=["\']og:description["\'])[^>]+content=["\'](.*?)["\']', doc)
    desc = ihtml.unescape(" ".join(descs)).strip()[:400]
    text = ihtml.unescape(WS_RE.sub(" ", ANGLE_RE.sub(" ", TAG_RE.sub(" ", doc))))
    return title, desc, text


def score(group, blob):
    hits, total = [], 0
    for name, rx, w in group:
        if re.search(rx, blob, re.I):
            hits.append(name); total += w
    return total, hits


def classify(url):
    status, doc, base = fetch_site(url)
    if status == "blocked":
        return dict(http="blocked", verdict="blocked", conf=0, saas=0, svc=0, es="", esv="", title="", meta="", snip="")
    if status != 200 or not doc:
        return dict(http="unreachable", verdict="unreachable", conf=0, saas=0, svc=0, es="", esv="", title="", meta="", snip="")
    title, desc, text = extract(doc)
    links = doc[:250_000]; tblob = (title + " " + desc + " " + text)[:150_000]
    sl, h1 = score([s for s in SAAS if "href" in s[1] or s[0] in ("app_subdomain", "jsonld_soft")], links)
    st, h2 = score([s for s in SAAS if not ("href" in s[1] or s[0] in ("app_subdomain", "jsonld_soft"))], tblob)
    svc, hsvc = score(SERVICES, tblob); eco, _ = score(ECOM, tblob)
    saas = sl + st; sh = h1 + h2
    strong_saas = any(x in sh for x in ("pricing_page", "app_subdomain", "free_trial", "jsonld_soft"))
    strong_svc = any(x in hsvc for x in ("agency_studio", "outsourcing"))
    margin = saas - svc
    if strong_saas and strong_svc:
        verdict, conf = "unclear", 45
    elif strong_saas:
        verdict, conf = "saas", min(95, 80 + margin)
    elif strong_svc:
        verdict, conf = "not_saas", min(92, 78 + max(0, -margin) * 3)
    elif eco >= 4 and saas < 4:
        verdict, conf = "not_saas", 78; hsvc = ["ecommerce"] + hsvc
    elif saas >= 4 and margin >= 3:
        verdict, conf = "saas", min(90, 55 + margin * 4)
    elif svc >= 4 and margin <= -2:
        verdict, conf = "not_saas", min(88, 55 + (-margin) * 4)
    elif saas >= 3 and svc <= 1:
        verdict, conf = "saas", 55
    elif svc >= 3 and saas <= 1:
        verdict, conf = "not_saas", 55
    else:
        verdict, conf = "unclear", 30
    _san = lambda s: re.sub(r"[\x00-\x1f]", " ", s)
    title, desc = _san(title), _san(desc)
    snip = _san((title + " | " + desc + " | " + text)[:800])
    return dict(http=status, verdict=verdict, conf=conf, saas=saas, svc=svc,
                es=";".join(sh), esv=";".join(hsvc), title=title, meta=desc[:180], snip=snip)


def main():
    ap = argparse.ArgumentParser(description="Tier-1 heuristic SaaS classification by fetching each website.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--col-website", required=True, help="column holding the website / resolved domain")
    ap.add_argument("--out-name", default="companies_classified.csv")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    limit = int(os.environ.get("LIMIT", "0")); workers = int(os.environ.get("WORKERS", "24"))

    rows = list(csv.DictReader(open(args.input, encoding="utf-8-sig", errors="replace")))
    if args.col_website not in (rows[0].keys() if rows else []):
        sys.exit(f"ERROR: website column {args.col_website!r} not found. Columns: {list(rows[0].keys()) if rows else []}")
    if limit:
        rows = rows[:limit]
    print(f"classifying {len(rows)} sites, {workers} workers…", file=sys.stderr)
    res = [None] * len(rows); done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fut = {ex.submit(classify, r[args.col_website]): i for i, r in enumerate(rows)}
        for f in as_completed(fut):
            i = fut[f]
            try:
                res[i] = f.result()
            except Exception as e:
                res[i] = dict(http="err", verdict="unreachable", conf=0, saas=0, svc=0, es="", esv=str(e)[:30], title="", meta="", snip="")
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(rows)}", file=sys.stderr)

    extra = ["verdict", "conf", "http", "saas", "svc", "es", "esv", "title", "meta", "snip"]
    fields = list(rows[0].keys()) + [c for c in extra if c not in rows[0].keys()]
    out = os.path.join(args.outdir, args.out_name)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader()
        for r, x in zip(rows, res):
            w.writerow({**r, **x})
    from collections import Counter
    vc = Counter(x["verdict"] for x in res)
    print("\nVERDICTS (tier-1 heuristic):", file=sys.stderr)
    for k in ("saas", "not_saas", "unclear", "blocked", "unreachable"):
        n = vc.get(k, 0)
        print(f"  {k:12s} {n:>6} ({100*n/len(rows):.1f}%)" if rows else f"  {k}: 0", file=sys.stderr)
    print(f"-> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
