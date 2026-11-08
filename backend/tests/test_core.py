import pytest

from formfiller.core import codec, evidence, schema
from formfiller.core.fill import fill_pdf, read_values
from formfiller.core.form import NOT_MENTIONED
from formfiller.forms import get_form

FORM = get_form("t2201")


def every_value_once():
    """One logical values dict per enum option, plus all bools/texts set."""
    for key, f in FORM.fields.items():
        if f.kind == "enum":
            for o in f.options:
                yield {key: o.value}
        elif f.kind == "bool":
            yield {key: True}
        elif f.kind in ("year", "number"):
            yield {key: "2019"}
        else:
            yield {key: "Some text"}


def test_profile_fields_are_not_extracted():
    for key in FORM.fields:
        assert "patient_name" not in key and not key.endswith("_initial")
        assert key not in {"cert_practitioner_type", "cert_practitioner_name", "cert_date"}


def test_every_raw_field_is_reachable():
    """Every non-profile FIELD_MAP entry can be produced from some logical value."""
    produced = set()
    for values in every_value_once():
        produced |= set(codec.to_raw(FORM, values))
    profile = FORM.stamp_profile({"hearing_q8_lasted_12mo": "yes"}, {
        "patient_name": "X", "practitioner_type": "medical_doctor", "practitioner_initials": "AB",
        "practitioner_name": "Dr X", "license_number": "1", "telephone": "1", "address": "a", "date": "20260101"})
    produced |= set(profile)
    unreachable = set(FORM.field_map) - produced
    # Initials for other practitioner types / untouched sections are expected to be unreachable here.
    assert all(k.endswith("_initial") for k in unreachable), sorted(unreachable)


@pytest.mark.parametrize("values", list(every_value_once()), ids=lambda v: f"{next(iter(v))}={next(iter(v.values()))}")
def test_codec_roundtrip(values):
    back = codec.from_raw(FORM, codec.to_raw(FORM, values))
    for k, v in values.items():
        assert back[k] == v


def test_coerce_rejects_invalid_enum():
    out = codec.coerce(FORM, {"mental_q10_lasted_12mo": "/0", "hearing_q1_conditions": None})
    assert out["mental_q10_lasted_12mo"] == NOT_MENTIONED
    assert out["hearing_q1_conditions"] == ""


def test_known_option_semantics():
    """Guard the mappings the prototype got wrong (verified against the PDF's XFA captions)."""
    raw = codec.to_raw(FORM, {"mental_q10_lasted_12mo": "yes", "mental_q4_impaired_independence": "yes",
                              "mental_q11_improved": "no"})
    assert raw == {"mental_q10_lasted_12mo": "/0", "mental_q4_impaired_independence": "/1",
                   "mental_q11_improved_no": True}


def test_chunk_schemas_cover_all_fields():
    keys = [k for c in FORM.chunks for k in c.keys]
    assert sorted(keys) == sorted(FORM.fields)
    for c in FORM.chunks:
        s = schema.chunk_schema(FORM, c, evidence=True)
        assert list(s["properties"][c.keys[0]]["properties"]) == ["evidence", "value"]


def test_pdf_roundtrip():
    values = {"hearing_q1_conditions": "Sensorineural hearing loss (2018)", "hearing_q2_left_ear": "profound",
              "hearing_q8_lasted_12mo": "yes", "hearing_q9_improved": "no", "mental_q5_regulation_mood": "severe_limitations",
              "cumulative_q1_hearing": True, "vision_q2_left_measure": "count_fingers"}
    raw = codec.to_raw(FORM, values) | FORM.stamp_profile(values, {"patient_name": "Jane", "practitioner_type": "medical_doctor",
                                                                    "practitioner_initials": "AB"})
    back = read_values(fill_pdf(FORM.template_path, FORM.field_map, raw), FORM.field_map)
    assert back["hearing_doctor_initial"] == "AB" and back["cert_patient_name"] == "Jane"
    assert back["vision_doctor_initial"] == "AB"
    assert "speaking_doctor_initial" not in back  # untouched section is not initialled
    assert codec.from_raw(FORM, back) | {} == codec.from_raw(FORM, raw)


def test_rules():
    issues = {(i.field, i.rule) for i in FORM.rules({
        "hearing_q8_lasted_12mo": "yes", "hearing_q9_improved": "yes", "hearing_q7_year_impaired": "18",
        "cumulative_q1_hearing": True, "cert_year_from": "2020", "cert_year_to": "2018"})}
    assert ("hearing_q4_examples", "mandatory_examples") in issues
    assert ("hearing_q9_year", "improve_year_missing") in issues
    assert ("hearing_q7_year_impaired", "year_format") in issues
    assert ("cumulative_q1_vision", "cumulative_min_two") in issues
    assert ("cert_year_from", "cert_period") in issues


NOTES = """Patient has been under my care since 2018.
Left ear: profound hearing loss (91dB+). Right ear: severe hearing loss (71-90dB).
Adaptive functioning — performing everyday tasks: severe limitations"""


@pytest.mark.parametrize("quote,ok", [
    ("Left ear: profound hearing loss (91dB+).", True),
    ("Patient has been under my care since 2018. Right ear: severe hearing loss", True),  # stitched
    ("left ear: profound hearing loss", True),
    ("Patient has severe limitations in performing everyday tasks.", False),  # paraphrase
    ("Patient uses a cochlear implant", False),
    ("not mentioned", False),
])
def test_grounding(quote, ok):
    assert evidence.ground(quote, NOTES)["grounded"] is ok
