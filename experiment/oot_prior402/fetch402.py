import json, sys, time, urllib.request, re, html
S = sys.argv[1]
UA = {"User-Agent": "academic-research-script research@example.org"}
d = json.load(open(f"{S}/scan402.json"))
for o in d:
    for r in o["filings_402"]:
        if r["filed"] >= "2026-06-01": continue
        url = f"https://www.sec.gov/Archives/edgar/data/{o['cik']}/{r['acc'].replace('-','')}/{r['doc']}"
        try:
            t = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")
        except Exception as e:
            t = f"ERR {e}"
        t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"\s+", " ", t)
        m = re.search(r"Item\s*4\.02", t, re.I)
        seg = t[m.start(): m.start() + 1500] if m else t[:800]
        r["text"] = seg
        print(f"### {o['pid']} {o['name']} {r['filed']} {r['form']}\n{seg}\n")
        time.sleep(0.3)
json.dump(d, open(f"{S}/scan402_text.json", "w"), indent=1)
