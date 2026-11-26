"""Offline tests for eval/note_styles.py: generated cases are consistent with their gold."""
import sys
from collections import Counter
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[2] / "eval"
sys.path.insert(0, str(EVAL))

import grid_copy as gc  # noqa: E402
import note_styles as ns  # noqa: E402
from formfiller.forms import get_form  # noqa: E402

FORM = get_form("t2201")
GRID = list(next(c for c in FORM.chunks if c.id == gc.GRID_CHUNK).keys)
CASES = ns.make_cases()


def test_bank_covers_exactly_the_grid():
    assert sorted(ns.P + k for k in ns.ITEMS) == sorted(GRID)
    assert all(ns.P + k in GRID for k in ns.TRAPS)


def test_deterministic_and_complete():
    assert ns.make_cases() == CASES
    assert Counter(c["style"] for c in CASES) == {s: 8 for s in ns.STYLES}
    assert len({c["id"] for c in CASES}) == len(CASES)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_gold_matches_notes(case):
    gold, notes = case["gold"], case["notes"]
    assert gold and set(gold) <= set(GRID)
    assert all(v in ns.RATINGS for v in gold.values())
    for key, rating in gold.items():
        s = key[len(ns.P):]
        label, short, gerund, *functional = ns.ITEMS[s]
        if case["style"] == "structured":
            assert f"- {label}: {ns.STRUCT_WORD[rating]}" in notes
        elif case["style"] == "sparse":
            assert f"{short[0].upper()}{short[1:]}: {ns.SHORT_WORD[rating]}" in notes
        elif case["style"] == "functional":
            assert functional[ns.RATINGS.index(rating)] in notes
        else:
            assert gerund in notes or f"{gerund[0].upper()}{gerund[1:]}" in notes


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_style_properties(case):
    notes, n = case["notes"], len(case["gold"])
    if case["style"] == "sparse":
        assert 1 <= n <= 3
    else:
        assert 4 <= n <= 10
    if case["style"] in ("paraphrase", "functional", "distractor"):
        assert "limitation" not in notes.lower()  # no form-scale words to copy
    if case["style"] == "functional":
        assert not any(w in notes.lower() for w in ("mild", "moderate", "marked", "severe limit", "impairment"))
    if case["style"] == "distractor":
        assert len(case["traps"]) == 2
        assert not set(case["traps"]) & set(case["gold"])
        assert all(ns.TRAPS[t[len(ns.P):]] in notes for t in case["traps"])
    else:
        assert case["traps"] == []


def test_summary_counts_traps():
    c = next(c for c in CASES if c["style"] == "distractor")
    perfect = {k: c["gold"].get(k, "not_mentioned") for k in GRID}
    trapped = perfect | {c["traps"][0]: "severe_limitations"}
    s = ns.summarize(GRID, [c], {c["id"]: perfect})["distractor"]
    assert s["rated_accuracy"] == 1.0 and s["trap_filled"] == 0 and s["halluc_per_case"] == 0
    s = ns.summarize(GRID, [c], {c["id"]: trapped})["distractor"]
    assert s["trap_filled"] == 1 and s["halluc_per_case"] == 1
