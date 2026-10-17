"""Score the packets with Claude through the Message Batches API (design section 3.4).

  python -m experiment.yoy.run_llm submit --run pilot     # one batch: every arm x repeat, plus identity probes
  python -m experiment.yoy.run_llm collect --run pilot    # wait for it, write results/exp1_<run>/

Every arm is sent with the same system prompt and output schema; only the packet differs.
Opus 5.5 does not accept sampling parameters, so each packet is scored REPEATS times and
the scores are averaged. No refusal fallback model is configured: one model must score
every document, so refusals are recorded and reported instead.

Needs `pip install anthropic` and Anthropic API credentials (ANTHROPIC_API_KEY or `ant auth login`).
"""
import argparse
import json
import os
import time

from experiment.yoy import packets

MODEL = "claude-opus-5-5"
EFFORT = "high"
REPEATS = 3
MAX_TOKENS = 16000
FRAUD_TYPES = ["revenue", "expenses_or_costs", "assets_or_inventory", "reserves_or_liabilities",
               "related_party_or_off_balance_sheet", "disclosure_only", "other"]

SYSTEM = """You are a forensic accountant. You will read excerpts of one company's annual report on Form 10-K and judge whether the financial statements for Year T are intentionally and materially misstated (accounting fraud later sanctioned by the SEC).

About half of the reports you will see were later found to be fraudulently misstated for Year T; the rest come from comparable companies with no known misstatement.

Rules:
- Use only the text provided. Names and calendar years are masked; do not try to identify the company and do not use outside knowledge about any company.
- Some inputs also contain the prior-year (Year T-1) report or a paragraph-level comparison of the two years. Use them if present.
- Quote evidence verbatim from the input. Say for each quote whether it comes from the current-year report, the prior-year report, or the year-over-year comparison.
- fraud_probability is your probability (0-100) that Year T is fraudulently misstated."""

SCHEMA = {
    "type": "object",
    "properties": {
        "evidence": {"type": "array", "items": {
            "type": "object",
            "properties": {"section": {"type": "string"},
                           "source": {"type": "string", "enum": ["current", "prior", "changes"]},
                           "quote": {"type": "string"},
                           "why": {"type": "string"}},
            "required": ["section", "source", "quote", "why"], "additionalProperties": False}},
        "reasoning_summary": {"type": "string"},
        "fraud_types": {"type": "array", "items": {"type": "string", "enum": FRAUD_TYPES}},
        "fraud_probability": {"type": "integer"},
    },
    "required": ["evidence", "reasoning_summary", "fraud_types", "fraud_probability"],
    "additionalProperties": False,
}

PROBE_SYSTEM = """The user will show you masked excerpts of a company's annual report on Form 10-K. Names and calendar years have been masked. Guess which company it is and which fiscal year Year T is. If you cannot tell, give your best guess with low confidence."""
PROBE_SCHEMA = {
    "type": "object",
    "properties": {"company_guess": {"type": "string"},
                   "fiscal_year_guess": {"type": "integer"},
                   "confidence": {"type": "integer"},
                   "clues": {"type": "string"}},
    "required": ["company_guess", "fiscal_year_guess", "confidence", "clues"],
    "additionalProperties": False,
}
PROBE_ARM = "A1"  # current + prior-year raw text: the most identifying input


def client():
    """Pinned to the public API: a shell's ANTHROPIC_BASE_URL may point elsewhere (EXP1_BASE_URL overrides)."""
    import anthropic
    return anthropic.Anthropic(base_url=os.environ.get("EXP1_BASE_URL", "https://api.anthropic.com"))


def run_dir(out, run):
    return os.path.join(out, "runs", run)


def _params(model, effort, system, schema, text):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    return MessageCreateParamsNonStreaming(
        model=model, max_tokens=MAX_TOKENS, system=system,
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": text}])


def requests_for(packet_dir, doc_ids, model, effort, repeats):
    from anthropic.types.messages.batch_create_params import Request

    def read(arm, doc):
        with open(os.path.join(packet_dir, "packets", arm, f"{doc}.txt"), encoding="utf-8") as f:
            return f.read()
    reqs = []
    for doc in doc_ids:
        for arm in packets.ARMS:
            text = read(arm, doc)
            for r in range(1, repeats + 1):
                reqs.append(Request(custom_id=f"{arm}-{doc}-r{r}", params=_params(model, effort, SYSTEM, SCHEMA, text)))
        reqs.append(Request(custom_id=f"PROBE-{doc}",
                            params=_params(model, effort, PROBE_SYSTEM, PROBE_SCHEMA, read(PROBE_ARM, doc))))
    return reqs


def submit(args):
    os.makedirs(run_dir(args.out, args.run), exist_ok=True)
    meta_path = os.path.join(run_dir(args.out, args.run), "batch.json")
    if os.path.exists(meta_path):
        raise SystemExit(f"{meta_path} exists: this run was already submitted")
    with open(os.path.join(args.out, "key.json"), encoding="utf-8") as f:
        doc_ids = sorted(json.load(f))
    reqs = requests_for(args.out, doc_ids, args.model, args.effort, args.repeats)
    batch = client().messages.batches.create(requests=reqs)
    meta = {"batch_id": batch.id, "model": args.model, "effort": args.effort, "repeats": args.repeats,
            "n_docs": len(doc_ids), "n_requests": len(reqs), "submitted": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print(f"submitted {len(reqs)} requests as batch {batch.id}")


def parse_result(result):
    """-> dict with status, stop_reason, usage and the parsed JSON (or None)."""
    r = result.result
    if r.type != "succeeded":
        return {"status": r.type, "stop_reason": None, "data": None, "usage": None}
    msg = r.message
    text = next((b.text for b in msg.content if b.type == "text"), None)
    data = None
    if msg.stop_reason == "end_turn" and text:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
    return {"status": "succeeded", "stop_reason": msg.stop_reason, "data": data,
            "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}}


def collect(args):
    api = client()
    rdir = run_dir(args.out, args.run)
    with open(os.path.join(rdir, "batch.json"), encoding="utf-8") as f:
        meta = json.load(f)
    while True:
        batch = api.messages.batches.retrieve(meta["batch_id"])
        if batch.processing_status == "ended":
            break
        c = batch.request_counts
        print(f"{batch.processing_status}: {c.processing} processing, {c.succeeded} succeeded, {c.errored} errored", flush=True)
        time.sleep(60)
    n = 0
    with open(os.path.join(rdir, "responses.jsonl"), "w", encoding="utf-8") as f:
        for result in api.messages.batches.results(meta["batch_id"]):
            f.write(json.dumps({"custom_id": result.custom_id, **parse_result(result)}, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} results -> {rdir}/responses.jsonl")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["submit", "collect"])
    ap.add_argument("--run", required=True, help="run name, e.g. pilot")
    ap.add_argument("--out", default=packets.DEFAULT_DIR)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--effort", default=EFFORT)
    ap.add_argument("--repeats", type=int, default=REPEATS)
    args = ap.parse_args()
    {"submit": submit, "collect": collect}[args.action](args)


if __name__ == "__main__":
    main()
