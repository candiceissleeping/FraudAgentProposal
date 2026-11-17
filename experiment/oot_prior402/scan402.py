import json, sys, time, urllib.request, os
S = sys.argv[1]
UA = {"User-Agent": "academic-research-script research@example.org"}
def get(url):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e:
            time.sleep(2 ** i)
    raise RuntimeError(url)
pairs = json.load(open(f"{S}/pairs.json"))
out = []
for idx, p in enumerate(pairs, 1):
    c = p["case"]; cik = int(c["cik"])
    sub = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    blocks = [sub["filings"]["recent"]] + [get("https://data.sec.gov/submissions/" + f["name"]) for f in sub["filings"].get("files", [])]
    rows = []
    for b in blocks:
        for i, form in enumerate(b["form"]):
            if form.startswith("8-K") and "4.02" in (b.get("items", [""] * len(b["form"]))[i] or ""):
                rows.append(dict(form=form, filed=b["filingDate"][i], acc=b["accessionNumber"][i], items=b["items"][i], doc=b["primaryDocument"][i]))
    rows.sort(key=lambda r: r["filed"])
    out.append(dict(pid=f"O{idx:02d}T", name=c["name"], cik=cik, event_date=c["event_date"], event_acc=c["event_acc"],
                    former=[f["name"] for f in sub.get("formerNames", [])], filings_402=rows,
                    first_filing=min(min(b["filingDate"]) for b in blocks if b["filingDate"])))
    time.sleep(0.2)
json.dump(out, open(f"{S}/scan402.json", "w"), indent=1)
for o in out:
    print(o["pid"], o["name"], o["event_date"], "| first filing", o["first_filing"], "| former:", o["former"])
    for r in o["filings_402"]:
        print("    ", r["filed"], r["form"], r["acc"], r["items"])
