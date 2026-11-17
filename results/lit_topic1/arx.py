import sys, time, urllib.request, urllib.parse, re, json, xml.etree.ElementTree as ET
NS={"a":"http://www.w3.org/2005/Atom"}
def q(query, n=25):
    url="https://export.arxiv.org/api/query?"+urllib.parse.urlencode({"search_query":query,"max_results":n,"sortBy":"relevance"})
    for i in range(4):
        try:
            x=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"lit-search/0.1"}),timeout=40).read(); break
        except Exception as e: time.sleep(4*(i+1)); x=None
    out=[]
    if not x: return out
    for e in ET.fromstring(x).findall("a:entry",NS):
        out.append(dict(id=e.find("a:id",NS).text.split("/abs/")[-1], date=e.find("a:published",NS).text[:10],
            title=re.sub(r"\s+"," ",e.find("a:title",NS).text).strip(), abs=re.sub(r"\s+"," ",e.find("a:summary",NS).text).strip(),
            authors=[a.find("a:name",NS).text for a in e.findall("a:author",NS)][:4]))
    return out
if __name__=="__main__":
    store=json.load(open("arx_store.json")) if __import__("os").path.exists("arx_store.json") else {}
    for query in open(sys.argv[1]).read().strip().split("\n"):
        res=q(query); print("\n###",query,len(res))
        for r in res:
            if r["date"]<"2023-06": continue
            base=re.sub(r"v\d+$","",r["id"]); new=base not in store; store[base]=r
            print(("* " if new else "  ")+base, r["date"], "|", r["title"][:120])
        time.sleep(3.2)
    json.dump(store,open("arx_store.json","w"))
