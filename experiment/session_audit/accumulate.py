"""Audit another Claude Code cloud session for web access. Run from the repo root; data goes to $AUDIT_DIR (default audit_store/).
"""accumulate.py <tag> <saved_list_events_file> <cutoff_iso>
Appends the page's events to store/<tag>.jsonl (dedup by uuid) and prints one status line:
NEXT before_id=<first_id> | oldest=<ts> | ...   or   STOP (reached cutoff / no more pages)."""
import json, os, sys
tag, path, cutoff = sys.argv[1], sys.argv[2], sys.argv[3]
here = os.environ.get('AUDIT_DIR', 'audit_store')
os.makedirs(os.path.join(here, 'store'), exist_ok=True)
s = open(path, encoding='utf-8').read()
c = json.loads(s[s.find('{'):s.rfind('}') + 1])['ccr']
store = os.path.join(here, 'store', tag + '.jsonl')
seen = set()
if os.path.exists(store):
    for l in open(store, encoding='utf-8'):
        seen.add(json.loads(l)['_id'])
ts = [e.get('created_at', '') for e in c['data'] if e.get('created_at')]
new = 0
with open(store, 'a', encoding='utf-8') as fh:
    for e in c['data']:
        inner = next((v for k, v in e.items() if isinstance(v, dict)), {})
        uid = inner.get('uuid') or json.dumps(e, sort_keys=True)[:200]
        if uid in seen:
            continue
        seen.add(uid); new += 1
        e['_id'] = uid
        fh.write(json.dumps(e, ensure_ascii=False) + '\n')
oldest = min(ts) if ts else ''
stop = (not c.get('has_more')) or (oldest and oldest < cutoff)
print(('STOP' if stop else 'NEXT'), f"before_id={c.get('first_id')} | oldest={oldest[:19]} | newest={max(ts)[:19] if ts else ''} | new={new} | total={len(seen)}")
