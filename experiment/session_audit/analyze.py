"""analyze.py <tag> [since_iso] [until_iso]: run the websearch_check detector over a stored session log."""
import collections, json, os, re, sys
sys.path.insert(0, os.getcwd())
from experiment.websearch_check import classify
tag = sys.argv[1]; since = sys.argv[2] if len(sys.argv) > 2 else ''; until = sys.argv[3] if len(sys.argv) > 3 else '9'
here = os.environ.get('AUDIT_DIR', 'audit_store')
evs = [json.loads(l) for l in open(f'{here}/store/{tag}.jsonl', encoding='utf-8')]
evs.sort(key=lambda e: e.get('created_at', ''))
calls, agents, tools_all = [], {}, collections.Counter()
for e in evs:
    ts = e.get('created_at', '')
    if not (since <= ts <= until) or 'assistant' not in e:
        continue
    inner = e['assistant'].get('internal_anthropic_catchall') or e['assistant']
    pid = inner.get('parent_tool_use_id')
    for b in (inner.get('message') or {}).get('content') or []:
        if b.get('type') not in ('tool_use', 'server_tool_use'):
            continue
        calls.append((ts, pid, b))
        tools_all[(b['name'], 'sub' if pid else 'main')] += 1
        if b['name'] in ('Agent', 'Task'):
            agents[b['id']] = (ts, b.get('input') or {})
print(f'window {since or "start"} .. {until}: {len(calls)} tool calls, {len(agents)} subagents launched')
print('tool counts:', dict(tools_all))
# detector over everything (main + sub)
fake = [{'type': 'assistant', 'parent_tool_use_id': pid, 'message': {'content': [b]}} for ts, pid, b in calls]
res = classify(fake)
for k in ('web_tool', 'shell_net', 'mcp', 'delegate'):
    hits = res['hits'][k]
    print(f'{k}: {len(hits)}')
    if k != 'delegate':
        for h in hits[:20]:
            print('   ', h['tool'], '(sub)' if h['subagent'] else '(main)', h['input'][:160])
# per-subagent: what it touched
per = collections.defaultdict(list)
for ts, pid, b in calls:
    if pid:
        per[pid].append(b)
print('\nper subagent (description | n calls | tools | files read outside its own input):')
for aid, (ts, inp) in agents.items():
    bs = per.get(aid, [])
    names = collections.Counter(b['name'] for b in bs)
    paths = sorted({(b.get('input') or {}).get('file_path') or (b.get('input') or {}).get('path') or (b.get('input') or {}).get('pattern') or '' for b in bs if b['name'] in ('Read', 'Grep', 'Glob')})
    ban = bool(re.search(r'web|internet|search|上網|搜尋', inp.get('prompt', ''), re.I))
    print(f"{ts[:19]} | {inp.get('subagent_type','')} | {inp.get('description','')[:40]} | {len(bs)} | {dict(names)} | prompt_mentions_web={ban} | {[p[-60:] for p in paths][:4]}")
