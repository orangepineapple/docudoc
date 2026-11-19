"""Offline tests for eval/grid_copy.py: case generation and copy detection."""
import json
import sys
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[2] / "eval"
sys.path.insert(0, str(EVAL))

import grid_copy as gc  # noqa: E402
from formfiller.forms import get_form  # noqa: E402

FORM = get_form("t2201")
GRID = list(next(c for c in FORM.chunks if c.id == gc.GRID_CHUNK).keys)
HAND = json.loads((EVAL / "cases" / "hand.jsonl").read_text().splitlines()[0])
CASES = gc.make_cases(HAND)
BY_ID = {c["id"]: c for c in CASES}


def test_every_mapped_key_is_a_grid_field():
    assert set(gc.LINE_KEYS.values()) <= set(GRID)


def test_hand_notes_parse_to_hand_gold():
    rated = gc.parse_ratings(HAND["notes"])
    assert len(rated) == 10
    assert rated == {k: v for k, v in HAND["gold"].items() if k.startswith(gc.GRID_PREFIX)}


def test_case_set():
    kinds = [c["kind"] for c in CASES]
    assert kinds.count("base") == 1 and kinds.count("drop") == 10 and kinds.count("flip") == 10
    assert len({c["id"] for c in CASES}) == len(CASES)


@pytest.mark.parametrize("case", [c for c in CASES if c["kind"] != "base"], ids=lambda c: c["id"])
def test_edit_changes_exactly_one_line_and_its_label(case):
    key = case["target"]
    base_lines, new_lines = HAND["notes"].splitlines(), case["notes"].splitlines()
    changed_gold = {k for k in set(HAND["gold"]) | set(case["gold"]) if HAND["gold"].get(k) != case["gold"].get(k)}
    assert changed_gold == {key}
    # Notes and gold still agree after the edit.
    assert gc.parse_ratings(case["notes"]) == {k: v for k, v in case["gold"].items() if k.startswith(gc.GRID_PREFIX)}
    if case["kind"] == "drop":
        assert len(new_lines) == len(base_lines) - 1 and key not in case["gold"]
    else:
        assert len(new_lines) == len(base_lines)
        assert sum(a != b for a, b in zip(base_lines, new_lines)) == 1
        assert case["gold"][key] != HAND["gold"][key]


def test_score_buckets_copy_vs_fabrication():
    gold = {"mental_q5_judgment_consequences": "some_limitations"}
    pred = {"mental_q5_judgment_consequences": "some_limitations",
            "mental_q5_judgment_clothing": "some_limitations",       # sibling's rating
            "mental_q5_judgment_own_treatment": "severe_limitations",  # sibling rated, other value
            "mental_q5_problem_identify": "severe_limitations"}      # no rated sibling
    s = gc.score_grid(GRID, gold, pred)
    assert s["items"]["mental_q5_judgment_consequences"] == "correct"
    assert s["items"]["mental_q5_judgment_clothing"] == "copied"
    assert s["items"]["mental_q5_judgment_own_treatment"] == "other"
    assert s["items"]["mental_q5_problem_identify"] == "fabricated"
    assert s["counts"]["true_empty"] == len(GRID) - 4


def test_flip_follow_detects_tracking():
    base, flip = BY_ID["grid-base"], BY_ID["grid-flip-judgment_consequences"]
    copier = lambda gold: {k: gold.get(k, gold["mental_q5_judgment_consequences"])  # noqa: E731
                           for k in GRID if gc.category(k) == "judgment"}
    rows = gc.flip_follow(GRID, flip["target"], base["gold"], copier(base["gold"]), flip["gold"], copier(flip["gold"]))
    assert {r["item"] for r in rows} == {"mental_q5_judgment_clothing", "mental_q5_judgment_own_treatment",
                                         "mental_q5_judgment_exploitation_risk"}
    assert all(r["followed"] for r in rows)

    honest = lambda gold: dict(gold)  # noqa: E731
    rows = gc.flip_follow(GRID, flip["target"], base["gold"], honest(base["gold"]), flip["gold"], honest(flip["gold"]))
    assert not any(r["changed"] for r in rows)


def test_summary_on_perfect_and_copying_predictions():
    perfect = {c["id"]: {k: c["gold"].get(k, "not_mentioned") for k in GRID} for c in CASES}
    s = gc.summarize(GRID, CASES, perfect)
    assert s["rated_accuracy"] == 1.0 and s["halluc_per_case"] == 0 and s["flip_followed"] == 0

    def copy_all(gold):
        out = {}
        for k in GRID:
            sib = [v for s, v in gold.items() if s.startswith(gc.GRID_PREFIX) and gc.category(s) == gc.category(k)]
            out[k] = gold.get(k) or (sib[0] if sib else "not_mentioned")
        return out
    s = gc.summarize(GRID, CASES, {c["id"]: copy_all(c["gold"]) for c in CASES})
    assert s["copied_per_case"] > 5 and s["copy_share"] == 1.0
    assert s["flip_followed"] > 0 and s["dropped_filled"] > 0
