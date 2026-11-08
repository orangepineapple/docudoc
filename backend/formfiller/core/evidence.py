"""
Check that an evidence quote returned by the model actually appears in the
notes, and locate it so the UI can highlight it.

Models often stitch two sentences together or add "..." between fragments, so
a quote is split into pieces and each piece is matched on its own.
"""
from __future__ import annotations

import re

from rapidfuzz import fuzz

GROUNDED_THRESHOLD = 85
_PLACEHOLDERS = {"", "not mentioned", "not_mentioned", "n/a", "na", "none", "null", "no information"}


def is_placeholder(quote: str | None) -> bool:
    return (quote or "").strip().strip(".\"'").lower() in _PLACEHOLDERS


def _pieces(quote: str) -> list[str]:
    parts = re.split(r"\.\.\.|…|(?<=[.;!?])\s+|\n+", quote)
    return [p.strip(" .;\"'") for p in parts if len(p.strip(" .;\"'")) >= 4]


def _locate(piece: str, notes_l: str) -> tuple[int, int, float]:
    p = " ".join(piece.split()).lower()
    i = notes_l.find(p)
    if i >= 0:
        return i, i + len(p), 100.0
    a = fuzz.partial_ratio_alignment(p, notes_l)
    return (a.dest_start, a.dest_end, a.score) if a else (0, 0, 0.0)


def ground(quote: str | None, notes: str) -> dict:
    """{'grounded': bool, 'spans': [[start, end], ...], 'score': min piece score}"""
    if is_placeholder(quote):
        return {"grounded": False, "spans": [], "score": 0.0}
    notes_l = notes.lower()
    hits = [_locate(p, notes_l) for p in _pieces(quote)] or [(0, 0, 0.0)]
    score = min(h[2] for h in hits)
    ok = score >= GROUNDED_THRESHOLD
    return {"grounded": ok, "spans": [[s, e] for s, e, sc in hits if sc >= GROUNDED_THRESHOLD], "score": round(score, 1)}
