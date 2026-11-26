"""Offline tests for eval/raw_notes.py: the raw notes, their variations, and the saved cases."""
import json
import sys
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[2] / "eval"
sys.path.insert(0, str(EVAL))

import raw_notes as rn  # noqa: E402
from formfiller.forms import get_form  # noqa: E402

FORM = get_form("t2201")
NOTES = rn.load_raw_notes()
CASES = rn.make_cases(NOTES)
BY_ID = {c["id"]: c for c in CASES}


def test_raw_notes_are_valid():
    assert rn.validate(FORM, NOTES) == []


def test_every_form_section_is_covered():
    covered = {FORM.fields[k].section for n in NOTES for k, v in n["gold"].items() if v != "*"}
    assert covered == {s.id for s in FORM.sections}


def test_saved_cases_are_up_to_date():
    saved = [json.loads(line) for line in rn.OUT.read_text().splitlines()]
    assert saved == CASES, "run: python eval/raw_notes.py --write-cases"


def test_drop_removes_line_and_gold():
    c = BY_ID["raw_note_vision_lst--drop-lst-hours"]
    assert "16 hours per week" not in c["notes"]
    assert "lst_q6_hours_per_week" not in c["gold"]
    assert c["target"] == ["lst_q6_hours_per_week"]


def test_drop_section_clears_section_but_keeps_wildcard():
    c = BY_ID["raw_note_spina_bifida--drop-mobility"]
    walking = {k: v for k, v in c["gold"].items() if k.startswith("walking_")}
    assert walking == {"walking_q1_conditions": "*"}
    assert "walking" not in c["sections"]


def test_distractor_keeps_gold():
    for c in CASES:
        if c["kind"] == "distractor":
            assert c["gold"] == BY_ID[c["note"]]["gold"]
            assert len(c["notes"]) > len(BY_ID[c["note"]]["notes"])


def test_edit_must_match_exactly_once():
    with pytest.raises(ValueError):
        rn.apply_edits(["a", "b", "a"], [{"replace": ["a"], "with": []}])
    with pytest.raises(ValueError):
        rn.apply_edits(["a"], [{"after": "missing", "insert": ["x"]}])


def test_gold_patch_wildcard_then_specific():
    gold = {"vision_q1": "x", "vision_q2": "y", "cert_q1": "z"}
    assert rn.apply_gold(gold, {"vision_*": None, "vision_q1": "*"}) == {"cert_q1": "z", "vision_q1": "*"}
