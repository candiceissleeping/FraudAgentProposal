"""Remove narrative sentences cited as red flags in stage 1 (same phrase list for U and M)."""
import re, sys, json
PHRASES = [
    # restructuring write-off of customer accounts / footnotes hiding it
    "discontinued customer accounts", "adjustments related to restructuring activity",
    # revenue timing / policy
    "delay in a number of", "upon shipment or delivery", "Revenues in excess of amounts billed",
    "directly from our vendors",
    # liquidity, covenants, borrowing base
    "support of our principal stockholder", "eligible receivables and inventory", "fixed charge",
    # related-party control, guarantee, management agreement, distributor share sales
    "affiliated with our Chairman", "guaranteed", "management services agreement", "Management Agreement",
    "of our outstanding shares", "one of our distributors", "have not been formalized",
    # earn-out reversals, goodwill test, control premium
    "assumptions utilized in the calculation of purchase price obligations",
    "exceeded carrying value", "exceeded its carrying value", "control premium",
    # inconsistent restructuring completion date
    "substantially completed by the end of the first quarter",
]
SENT = re.compile(r"(?<=[.;])\s+(?=[A-Z(“\[])")

def ablate(text):
    hits = {p: 0 for p in PHRASES}
    out = []
    for line in text.split("\n"):
        sents = SENT.split(line)
        keep = []
        for s in sents:
            hit = [p for p in PHRASES if p.lower() in s.lower()]
            for p in hit: hits[p] += 1
            if not hit: keep.append(s)
        if keep or not line.strip():
            out.append(" ".join(keep))
    return "\n".join(out), hits

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    t = open(src).read()
    a, hits = ablate(t)
    open(dst, "w").write(a)
    print(json.dumps({"chars_before": len(t), "chars_after": len(a), "hits": hits}, indent=0))
