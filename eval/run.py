"""
Run extraction configs over eval cases and score them.

  python eval/run.py --cases eval/cases/raw_note.json --models qwen2.5:7b --variants v1_schema v3_select

Raw per-case results are cached under eval/results/raw/<run>/ so an interrupted
run resumes where it stopped. The summary goes to eval/results/<run>.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from formfiller.core.extract import VARIANTS, PipelineConfig, extract  # noqa: E402
from formfiller.forms import get_form  # noqa: E402
from formfiller.llm.ollama import Ollama  # noqa: E402
from formfiller.core.cases import load_cases as read_cases  # noqa: E402
from metrics import aggregate, score_case  # noqa: E402


def load_cases(paths: list[str], limit: int | None, split: str | None) -> list[dict]:
    cases = []
    for p in paths:
        for c in read_cases(p):
            if split is None or c.get("split", "dev") == split:
                cases.append(c)
    return cases[:limit] if limit else cases


def slug(s: str) -> str:
    return s.replace(":", "-").replace("|", "__").replace("/", "-")


async def run_config(form, cfg: PipelineConfig, cases: list[dict], raw_dir: Path, llm: Ollama) -> list[dict]:
    d = raw_dir / slug(cfg.name)
    d.mkdir(parents=True, exist_ok=True)
    scores = []
    for i, case in enumerate(cases, 1):
        f = d / f"{case['id']}.json"
        if f.exists():
            result = json.loads(f.read_text())
        else:
            t = time.monotonic()
            result = await extract(form, case["notes"], cfg, llm)
            f.write_text(json.dumps(result))
            print(f"  [{cfg.name}] {i}/{len(cases)} {case['id']} {time.monotonic() - t:.0f}s", flush=True)
        s = score_case(form, case["gold"], result)
        s["case_id"] = case["id"]
        s["style"] = case.get("style")
        scores.append(s)
    return scores


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="+", default=[str(ROOT / "cases" / "raw_note.json")])
    ap.add_argument("--split", default=None, help="dev | test (default: all)")
    ap.add_argument("--models", nargs="+", default=["qwen2.5:7b"])
    ap.add_argument("--variants", nargs="+", default=["v3_select"], choices=VARIANTS)
    ap.add_argument("--no-route", action="store_true")
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--drop-ungrounded", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--run", default="dev", help="run name (output file)")
    args = ap.parse_args()

    form = get_form("t2201")
    cases = load_cases(args.cases, args.limit, args.split)
    raw_dir = ROOT / "results" / "raw" / args.run
    out_path = ROOT / "results" / f"{args.run}.json"
    summary = json.loads(out_path.read_text()) if out_path.exists() else {"run": args.run, "configs": {}}

    async with Ollama() as llm:
        for model in args.models:
            for variant in args.variants:
                cfg = PipelineConfig(model=model, variant=variant, route=not args.no_route,
                                     think=args.think, drop_ungrounded=args.drop_ungrounded)
                print(f"\n== {cfg.name} on {len(cases)} cases", flush=True)
                scores = await run_config(form, cfg, cases, raw_dir, llm)
                agg = aggregate(scores)
                summary["configs"][cfg.name] = {"config": {"model": model, "variant": variant, "route": cfg.route,
                                                           "think": cfg.think, "drop_ungrounded": cfg.drop_ungrounded},
                                                "aggregate": agg, "cases": scores}
                out_path.write_text(json.dumps(summary, indent=1))
                o = agg["overall"]
                print(f"   accuracy {o['accuracy']:.1%}  precision {o['precision']:.1%}  "
                      f"halluc/case {o['hallucinations_per_case']:.1f}  "
                      f"latency p50 {agg['latency_ms']['p50'] / 1000:.0f}s", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
