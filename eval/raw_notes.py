"""
LLM-generated doctor's notes (kept in the repo) and their controlled variations.

Each eval/cases/raw_note*.json file is one realistic doctor's note with
gold answers stored next to it. A note may also list "variations": small line edits
to the note, each with the gold change it causes. Because the edit and its gold
change are written together, every variation's gold is known by construction.

Variation kinds
  drop          remove a fact             -> its gold becomes empty
  drop_section  remove a whole section    -> every field in it becomes empty
  flip          change a stated value     -> its gold changes
  negate        state that something is absent ("no medication") -> gold "no"
  distractor    add facts about someone else -> gold unchanged

Edits work on whole lines of the note:
  {"replace": [lines...], "with": [lines...]}   consecutive lines, must match once
  {"after": line, "insert": [lines...]}         insert after a line that matches once
Gold patches: a value sets the field, null makes it empty, and "<prefix>*": null
clears every field starting with <prefix>.

  python eval/raw_notes.py                  # coverage summary
  python eval/raw_notes.py --write-cases    # save eval/cases/raw_note_variants.jsonl
  python eval/run.py --cases eval/cases/raw_note_variants.jsonl --run raw_notes ...
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES_DIR = ROOT / "cases"
OUT = CASES_DIR / "raw_note_variants.jsonl"
KINDS = {"drop", "drop_section", "flip", "negate", "distractor"}


def load_raw_notes(cases_dir: Path = CASES_DIR) -> list[dict]:
    """Raw note files as stored: notes is a list of lines."""
    out = []
    for p in sorted(cases_dir.glob("raw_note*.json")):
        d = json.loads(p.read_text())
        if isinstance(d["notes"], str):
            d["notes"] = d["notes"].split("\n")
        out.append(d)
    return out


def _find_block(lines: list[str], block: list[str]) -> int:
    hits = [i for i in range(len(lines) - len(block) + 1) if lines[i:i + len(block)] == block]
    if len(hits) != 1:
        raise ValueError(f"expected exactly one match, found {len(hits)}: {block[0]!r}")
    return hits[0]


def apply_edits(lines: list[str], edits: list[dict]) -> list[str]:
    lines = list(lines)
    for e in edits:
        if "replace" in e:
            i = _find_block(lines, e["replace"])
            lines[i:i + len(e["replace"])] = e["with"]
        elif "after" in e:
            i = _find_block(lines, [e["after"]])
            lines[i + 1:i + 1] = e["insert"]
        else:
            raise ValueError(f"unknown edit: {e}")
    return lines


def apply_gold(gold: dict, patch: dict) -> dict:
    gold = dict(gold)
    for k, v in patch.items():           # wildcards first, then specific keys
        if k.endswith("*"):
            gold = {g: x for g, x in gold.items() if not g.startswith(k[:-1])}
    for k, v in patch.items():
        if k.endswith("*"):
            continue
        if v is None:
            gold.pop(k, None)
        else:
            gold[k] = v
    return gold


def _base_fields(note: dict) -> dict:
    return {"source": "raw_note", "style": note.get("style"), "split": note.get("split", "dev"),
            "verified": note.get("verified", False)}


def make_cases(notes: list[dict]) -> list[dict]:
    cases = []
    for n in notes:
        cases.append({"id": n["id"], **_base_fields(n), "note": n["id"], "kind": "base", "target": [],
                      "sections": n["sections"], "notes": "\n".join(n["notes"]), "gold": dict(n["gold"])})
        for v in n.get("variations", []):
            gold = apply_gold(n["gold"], v["gold"])
            changed = sorted(k for k in set(gold) | set(n["gold"]) if gold.get(k) != n["gold"].get(k))
            cases.append({"id": f"{n['id']}--{v['id']}", **_base_fields(n), "note": n["id"], "kind": v["kind"],
                          "target": changed, "tests": v.get("tests"), "sections": v.get("sections", n["sections"]),
                          "notes": "\n".join(apply_edits(n["notes"], v["edits"])), "gold": gold})
    return cases


def validate(form, notes: list[dict]) -> list[str]:
    """Problems with the raw notes: unknown keys, bad enum values, edits that don't apply."""
    errs = []
    section_ids = {s.id for s in form.sections}

    def check_gold(where: str, gold: dict, sections: list[str]):
        for k, v in gold.items():
            if v == "*":
                continue
            f = form.fields.get(k)
            if f is None:
                errs.append(f"{where}: unknown field {k}")
                continue
            if f.kind == "enum" and v not in {o.value for o in f.options}:
                errs.append(f"{where}: {k}={v!r} is not one of {[o.value for o in f.options]}")
            if f.kind == "bool" and v is not True:
                errs.append(f"{where}: {k} must be true (leave false out)")
            if f.section not in sections:
                errs.append(f"{where}: {k} is in section {f.section}, not listed in sections {sections}")

    for n in notes:
        bad = set(n["sections"]) - section_ids
        if bad:
            errs.append(f"{n['id']}: unknown sections {bad}")
        check_gold(n["id"], n["gold"], n["sections"])
        ids = [v["id"] for v in n.get("variations", [])]
        if len(ids) != len(set(ids)):
            errs.append(f"{n['id']}: duplicate variation ids")
        for v in n.get("variations", []):
            where = f"{n['id']}--{v['id']}"
            if v["kind"] not in KINDS:
                errs.append(f"{where}: unknown kind {v['kind']!r}")
            try:
                new = apply_edits(n["notes"], v["edits"])
            except ValueError as e:
                errs.append(f"{where}: {e}")
                continue
            if new == n["notes"]:
                errs.append(f"{where}: edits do not change the note")
            gold = apply_gold(n["gold"], v["gold"])
            check_gold(where, gold, v.get("sections", n["sections"]))
            if v["kind"] == "distractor" and gold != n["gold"]:
                errs.append(f"{where}: a distractor must not change the gold")
            if v["kind"] != "distractor" and gold == n["gold"]:
                errs.append(f"{where}: gold patch changes nothing")
    return errs


def summary(form, notes: list[dict], cases: list[dict]) -> str:
    secs = [s.id for s in form.sections]
    w = max(len(n["id"]) for n in notes)
    lines = ["Sections covered (x = in gold)", "", " " * w + "  " + " ".join(s[:5].ljust(5) for s in secs)]
    for n in notes:
        filled = {form.fields[k].section for k, v in n["gold"].items() if v != "*"}
        lines.append(n["id"].ljust(w) + "  " + " ".join(("x" if s in filled else ".").ljust(5) for s in secs))
    kinds = Counter(c["kind"] for c in cases)
    lines += ["", f"{len(cases)} cases from {len(notes)} notes: " + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items()))]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-cases", action="store_true", help=f"write {OUT.relative_to(ROOT.parent)}")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT.parent / "backend"))
    from formfiller.forms import get_form

    form = get_form("t2201")
    notes = load_raw_notes()
    errs = validate(form, notes)
    if errs:
        sys.exit("Invalid raw notes:\n  " + "\n  ".join(errs))
    cases = make_cases(notes)
    print(summary(form, notes, cases))
    if args.write_cases:
        OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases))
        print(f"\nwrote {len(cases)} cases to {OUT.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
