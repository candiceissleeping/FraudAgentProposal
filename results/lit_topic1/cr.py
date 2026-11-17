import sys, time, urllib.request, urllib.parse, json, re, os
store=json.load(open("cr_store.json")) if os.path.exists("cr_store.json") else {}
def q(query, ssrn):
    p={"query.bibliographic":query,"rows":20,"filter":"from-pub-date:2023-06"+(",prefix:10.2139" if ssrn else ""),"select":"DOI,title,author,issued,container-title,abstract,type"}
    url="https://api.crossref.org/works?"+urllib.parse.urlencode(p)
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"lit-search/0.1"}),timeout=40))["message"]["items"]
        except Exception as e: time.sleep(3*(i+1))
    return []
for line in open(sys.argv[1]).read().strip().split("\n"):
    for ssrn in (True, False):
        res=q(line, ssrn); print("\n###",("SSRN " if ssrn else "ALL  ")+line,len(res))
        for r in res:
            t=(r.get("title") or [""])[0]; y=(r.get("issued",{}).get("date-parts") or [[0]])[0][0]
            new=r["DOI"] not in store; store[r["DOI"]]=r
            print(("* " if new else "  ")+str(y), r["DOI"][:28].ljust(28), "|", re.sub(r"\s+"," ",t)[:110], "|", ((r.get("container-title") or [""])[0])[:30])
        time.sleep(1)
json.dump(store,open("cr_store.json","w"))
