"""Load eval cases from .jsonl (one case per line) or .json (one case or a list).

Readable .json cases may store "notes" as a list of lines; it is joined back
into a single string so every consumer sees the same shape.
"""
from __future__ import annotations

import json
from pathlib import Path


def _normalize(case: dict) -> dict:
    if isinstance(case.get("notes"), list):
        case = {**case, "notes": "\n".join(case["notes"])}
    return case


def load_cases(path: str | Path) -> list[dict]:
    p = Path(path)
    text = p.read_text()
    if p.suffix == ".json":
        data = json.loads(text)
        cases = data if isinstance(data, list) else [data]
    else:
        cases = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [_normalize(c) for c in cases]
