"""
Regression probe for the mental-functions grid bug: the model rates grid items
the notes never mention, copying the rating of a rated item in the same category
(e.g. notes rate "Judgment — understand consequences: some", model also rates
the three other Judgment items "some").

Cases are made from the hand-labelled case by editing the rating lines in code,
so gold labels are known by construction (no LLM writes notes):

  base           unchanged notes
  drop:<key>     one rated line removed       -> that item's gold becomes empty
  flip:<key>     one rating some <-> severe   -> that item's gold flips

Only the grid chunk (mental_b, 28 items) is sent to the model, through the same
extract_chunk() the app uses. Per pipeline it reports:

  rated accuracy   rated items filled correctly (the control: a fix must not
                   lose these)
  halluc / case    unrated items filled anyway, split into
                     copied      value equals a rating stated for a same-category item
                     other       category has a rated item, value differs
                     fabricated  category has no rated item at all
  flip-follow      unrated siblings of a flipped item whose prediction changed to
                   track the edit. This is the causal test: only the edited line
                   differs between the two prompts.
  dropped filled   items whose line was removed but were filled anyway

  python eval/grid_copy.py --variants v1_schema v2_evidence v3_select
  python eval/grid_copy.py --write-cases     # also save eval/cases/grid_copy.jsonl
  make grid-check                            # regression gate for the default pipeline
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRID_CHUNK = "mental_b"
GRID_PREFIX = "mental_q5_"

# Rating lines in the hand-labelled notes -> logical field.
LINE_KEYS = {
    "Adaptive functioning — performing everyday tasks": "mental_q5_adaptive_everyday_tasks",
    "Adaptive functioning — go into community": "mental_q5_adaptive_go_into_community",
    "Attention — impulse control": "mental_q5_attention_impulse_control",
    "Concentration — focus on simple tasks": "mental_q5_concentration_focus",
    "Goal-setting — make and carry out plans": "mental_q5_goal_make_plans",
    "Goal-setting — self-direct to begin tasks": "mental_q5_goal_self_direct",
    "Judgment — understand consequences": "mental_q5_judgment_consequences",
    "Memory — remember simple instructions": "mental_q5_memory_simple_instructions",
    "Regulation of behaviour": "mental_q5_regulation_behaviour",
    "Regulation of emotions": "mental_q5_regulation_emotions",
}
LINE_RE = re.compile(r"^- (?P<label>.+?): (?P<rating>no|some|severe) limitations[ \t]*$", re.MULTILINE)
FLIP = {"some": "severe", "severe": "some"}
EMPTY = (None, "", False, "not_mentioned")


def category(key: str) -> str:
    return key[len(GRID_PREFIX):].split("_")[0]


def parse_ratings(notes: str) -> dict[str, str]:
    """{field key: enum value} for every grid rating line in the notes."""
    out = {}
    for m in LINE_RE.finditer(notes):
        key = LINE_KEYS.get(m["label"].strip())
        if key is None:
            raise ValueError(f"unmapped rating line: {m.group(0)!r}")
        out[key] = f"{m['rating']}_limitations"
    return out


# ── Cases ────────────────────────────────────────────────────────────────────

def make_cases(hand: dict) -> list[dict]:
    notes, gold = hand["notes"], hand["gold"]
    rated = parse_ratings(notes)
    grid_gold = {k: v for k, v in gold.items() if k.startswith(GRID_PREFIX)}
    if rated != grid_gold:
        raise ValueError(f"notes and gold disagree on the grid: {rated} vs {grid_gold}")

    lines = {m["label"].strip(): m for m in LINE_RE.finditer(notes)}

    def case(cid, kind, target, new_notes, new_gold):
        return {"id": f"grid-{cid}", "source": "grid_copy", "style": hand.get("style"), "split": "dev",
                "kind": kind, "target": target, "notes": new_notes, "gold": new_gold,
                "sections": hand.get("sections")}

    cases = [case("base", "base", None, notes, dict(gold))]
    for label, m in lines.items():
        key = LINE_KEYS[label]
        line = m.group(0)
        short = key[len(GRID_PREFIX):]

        g = {k: v for k, v in gold.items() if k != key}
        cases.append(case(f"drop-{short}", "drop", key, notes.replace(line + "\n", "", 1), g))

        new_rating = FLIP[m["rating"]]
        new_line = line.replace(f": {m['rating']} limitations", f": {new_rating} limitations")
        g = dict(gold) | {key: f"{new_rating}_limitations"}
        cases.append(case(f"flip-{short}", "flip", key, notes.replace(line, new_line, 1), g))
    return cases


# ── Scoring ──────────────────────────────────────────────────────────────────

def score_grid(grid_keys: list[str], gold: dict, pred: dict) -> dict:
    """Bucket every grid item. gold/pred map key -> value; missing means empty."""
    g = {k: gold.get(k) for k in grid_keys if gold.get(k) not in EMPTY}
    by_cat: dict[str, set] = {}
    for k, v in g.items():
        by_cat.setdefault(category(k), set()).add(v)

    counts, items = Counter(), {}
    for k in grid_keys:
        p = pred.get(k)
        if k in g:
            b = "omitted" if p in EMPTY else ("correct" if p == g[k] else "wrong")
        elif p in EMPTY:
            b = "true_empty"
        else:
            sib = by_cat.get(category(k))
            b = "fabricated" if not sib else ("copied" if p in sib else "other")
        counts[b] += 1
        items[k] = b
    return {"counts": dict(counts), "items": items}


def flip_follow(grid_keys: list[str], target: str, base_gold: dict, base_pred: dict,
                flip_gold: dict, flip_pred: dict) -> list[dict]:
    """For each unrated sibling of the flipped item: did its prediction track the edit?"""
    rows = []
    for s in grid_keys:
        if s == target or category(s) != category(target):
            continue
        if base_gold.get(s) not in EMPTY or flip_gold.get(s) not in EMPTY:
            continue  # rated sibling: not a copy target
        b, f = base_pred.get(s), flip_pred.get(s)
        rows.append({"item": s, "base": b, "flip": f, "changed": b != f,
                     "followed": b == base_gold[target] and f == flip_gold[target]})
    return rows


def summarize(grid_keys: list[str], cases: list[dict], preds: dict[str, dict]) -> dict:
    tot = Counter()
    for c in cases:
        if c["id"] in preds:
            tot.update(score_grid(grid_keys, c["gold"], preds[c["id"]])["counts"])
    n = sum(1 for c in cases if c["id"] in preds)
    rated = tot["correct"] + tot["wrong"] + tot["omitted"]
    halluc = tot["copied"] + tot["other"] + tot["fabricated"]

    base = next(c for c in cases if c["kind"] == "base")
    follow = []
    for c in cases:
        if c["kind"] == "flip" and c["id"] in preds and base["id"] in preds:
            follow += flip_follow(grid_keys, c["target"], base["gold"], preds[base["id"]], c["gold"], preds[c["id"]])

    dropped = [(c["target"], preds[c["id"]].get(c["target"])) for c in cases if c["kind"] == "drop" and c["id"] in preds]
    return {
        "n_cases": n,
        "counts": dict(tot),
        "rated_accuracy": tot["correct"] / rated if rated else None,
        "halluc_per_case": halluc / n if n else None,
        "copied_per_case": tot["copied"] / n if n else None,
        "copy_share": tot["copied"] / halluc if halluc else None,
        "flip_pairs": len(follow),
        "flip_changed": sum(r["changed"] for r in follow),
        "flip_followed": sum(r["followed"] for r in follow),
        "dropped": len(dropped),
        "dropped_filled": sum(v not in EMPTY for _, v in dropped),
        "follow_detail": follow,
    }


# ── Runner ───────────────────────────────────────────────────────────────────

async def predict(form, chunk, notes: str, variant: str, model: str, llm) -> dict:
    from formfiller.core import codec, evidence
    from formfiller.core.extract import PipelineConfig, extract_chunk

    cfg = PipelineConfig(model=model, variant=variant)

    async def call(messages, schema_=None):
        return await llm.chat(cfg.model, messages, schema=schema_, think=cfg.think, num_ctx=cfg.num_ctx)

    t = time.monotonic()
    values, meta, errors = await extract_chunk(form, chunk, notes, variant, call)
    clean = codec.coerce(form, values)
    values = {k: clean[k] for k in chunk.keys}
    fields = {k: {"evidence": m["evidence"], **evidence.ground(m["evidence"], notes)} for k, m in meta.items()}
    return {"values": values, "fields": fields, "errors": errors, "ms": int((time.monotonic() - t) * 1000)}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-note", default=str(ROOT / "cases" / "raw_note.json"))
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--variants", nargs="+", default=["v1_schema", "v2_evidence", "v3_select"],
                    choices=["v1_schema", "v2_evidence", "v3_select"])
    ap.add_argument("--limit", type=int, help="only the first N cases (base is always first)")
    ap.add_argument("--write-cases", action="store_true", help="save cases to eval/cases/grid_copy.jsonl")
    ap.add_argument("--max-copied", type=float, help="exit 1 if any variant exceeds this many copied items per case")
    ap.add_argument("--no-cache", action="store_true",
                    help="ignore cached raw results (use after changing prompts or the model)")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT.parent / "backend"))
    from formfiller.core.cases import load_cases
    from formfiller.forms import get_form
    from formfiller.llm.ollama import Ollama

    form = get_form("t2201")
    chunk = next(c for c in form.chunks if c.id == GRID_CHUNK)
    grid_keys = list(chunk.keys)
    hand = load_cases(args.raw_note)[0]
    cases = make_cases(hand)[: args.limit] if args.limit else make_cases(hand)

    if args.write_cases:
        out = ROOT / "cases" / "grid_copy.jsonl"
        out.write_text("".join(json.dumps(c) + "\n" for c in cases))
        print(f"wrote {len(cases)} cases to {out}")

    summary_path = ROOT / "results" / "grid_copy.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    failed = []
    async with Ollama() as llm:
        for variant in args.variants:
            name = f"{args.model}|{variant}"
            raw = ROOT / "results" / "raw" / "grid_copy" / name.replace(":", "-").replace("|", "__")
            raw.mkdir(parents=True, exist_ok=True)
            preds = {}
            print(f"\n== {name} on {len(cases)} cases", flush=True)
            for i, c in enumerate(cases, 1):
                f = raw / f"{c['id']}.json"
                if f.exists() and not args.no_cache:
                    r = json.loads(f.read_text())
                else:
                    r = await predict(form, chunk, c["notes"], variant, args.model, llm)
                    f.write_text(json.dumps(r))
                    print(f"  {i}/{len(cases)} {c['id']} {r['ms'] / 1000:.0f}s"
                          f"{'  ERR ' + '; '.join(r['errors']) if r['errors'] else ''}", flush=True)
                preds[c["id"]] = r["values"]
            s = summarize(grid_keys, cases, preds)
            summary[name] = s
            summary_path.write_text(json.dumps(summary, indent=1))
            if args.max_copied is not None and (s["copied_per_case"] or 0) > args.max_copied:
                failed.append(name)

    print("\n| Pipeline | Cases | Rated acc. | Halluc/case | Copied/case | Fabricated | Flip followed | Dropped but filled |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, s in summary.items():
        c = s["counts"]
        acc = f"{s['rated_accuracy']:.0%}" if s["rated_accuracy"] is not None else "–"
        print(f"| `{name}` | {s['n_cases']} | {acc} | {s['halluc_per_case']:.1f} | {s['copied_per_case']:.1f} | "
              f"{c.get('fabricated', 0)} | {s['flip_followed']}/{s['flip_pairs']} | {s['dropped_filled']}/{s['dropped']} |")
    if failed:
        print(f"\nFAIL: copied/case above {args.max_copied} for {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
