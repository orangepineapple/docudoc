"""
python -m formfiller extract notes.txt [--model qwen2.5:7b] [--variant v2_evidence] [--json out.json]
python -m formfiller fill notes.txt -o filled.pdf --patient "Jane Doe" [--initials AB]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .core import codec
from .core.extract import VARIANTS, PipelineConfig, extract
from .core.fill import fill_pdf
from .core.form import NOT_MENTIONED
from .forms import get_form


def _print_summary(form, result: dict) -> None:
    v = result["values"]
    print(f"\n{form.title}  ·  {result['config']['name']}  ·  {result['stats']['ms'] / 1000:.1f}s")
    for s in form.sections:
        st = result["sections"].get(s.id, {}).get("status", "?")
        filled = [k for k in form.fields if form.fields[k].section == s.id and v[k] not in ("", False, NOT_MENTIONED)]
        print(f"\n  {'●' if filled else '○'} {s.label} [{st}]")
        for k in filled:
            m = result["fields"].get(k, {})
            flag = "" if not m or m.get("grounded") else "  ⚠ ungrounded"
            print(f"      {k:<46} {str(v[k])[:60]}{flag}")
    if result["issues"]:
        print("\n  Issues:")
        for i in result["issues"]:
            print(f"    [{i['severity']}] {i['field']}: {i['message']}")


async def _main(args) -> None:
    form = get_form(args.form)
    notes = sys.stdin.read() if args.notes == "-" else Path(args.notes).read_text()
    cfg = PipelineConfig(model=args.model, variant=args.variant, route=not args.no_route, think=args.think)
    result = await extract(form, notes, cfg)
    _print_summary(form, result)
    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
    if args.cmd == "fill":
        profile = {"patient_name": args.patient, "practitioner_type": args.practitioner,
                   "practitioner_initials": args.initials}
        raw = codec.to_raw(form, result["values"]) | form.stamp_profile(result["values"], profile)
        Path(args.output).write_bytes(fill_pdf(form.template_path, form.field_map, raw))
        print(f"\n  PDF written to {args.output}. AI-assisted: review every field before signing.")


def main() -> None:
    p = argparse.ArgumentParser(prog="formfiller")
    p.add_argument("cmd", choices=["extract", "fill"])
    p.add_argument("notes", help="notes file, or - for stdin")
    p.add_argument("--form", default="t2201")
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--variant", default="v2_evidence", choices=VARIANTS)
    p.add_argument("--no-route", action="store_true")
    p.add_argument("--think", action="store_true")
    p.add_argument("--json", help="also write the full result as JSON")
    p.add_argument("-o", "--output", default="filled.pdf")
    p.add_argument("--patient", default="")
    p.add_argument("--practitioner", default="medical_doctor")
    p.add_argument("--initials", default="")
    asyncio.run(_main(p.parse_args()))


if __name__ == "__main__":
    main()
