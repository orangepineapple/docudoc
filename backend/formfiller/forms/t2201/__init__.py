"""
CRA T2201 Disability Tax Credit Certificate — Part B (medical practitioner).
"""
from __future__ import annotations

import re
from pathlib import Path

from ...core.form import (
    Chunk, EnumOption, FormSpec, LogicalField, Section,
    enum_options, infer_text_kind,
)
from .field_map import FIELD_MAP
from .rules import check

HERE = Path(__file__).parent

SECTIONS = [
    Section("vision", "Vision", "visual acuity, visual field, blindness, eye conditions"),
    Section("speaking", "Speaking", "ability to speak so as to be understood, voice/speech disorders"),
    Section("hearing", "Hearing", "hearing loss, deafness, hearing aids, cochlear implants"),
    Section("walking", "Walking", "mobility, walking distance, gait, canes/walkers/wheelchairs"),
    Section("eliminating", "Eliminating", "bowel or bladder function, incontinence, ostomy, catheters"),
    Section("feeding", "Feeding", "preparing food or feeding oneself, swallowing, utensils"),
    Section("dressing", "Dressing", "ability to dress oneself, buttons, assistive dressing devices"),
    Section("mental", "Mental functions", "cognition, memory, attention, mood/behaviour regulation, psychiatric or neurodevelopmental conditions, independent living"),
    Section("cumulative", "Cumulative effect", "multiple significant limitations that together amount to a marked restriction"),
    Section("lst", "Life-sustaining therapy", "insulin therapy, dialysis, oxygen, tube feeding, chest physiotherapy and time spent on therapy"),
    Section("cert", "Certification", "how long the patient has been under the practitioner's care, whether medical records are on file"),
]

MANDATORY_FIELDS = {
    "hearing_q4_examples", "speaking_q4_examples",
    "walking_q4_examples", "eliminating_q4_examples", "feeding_q4_examples",
    "dressing_q4_examples", "cumulative_q2_examples",
}

# Filled from the practitioner/patient profile, never extracted from notes.
PROFILE_FIELDS = {
    "patient_name": "Patient's full name (printed on every page)",
    "practitioner_type": "Type of medical practitioner signing",
    "practitioner_initials": "Practitioner's initials (printed on each completed section)",
    "practitioner_name": "Practitioner's printed name",
    "license_number": "Licence/registration number",
    "telephone": "Practitioner telephone number",
    "address": "Practitioner address",
    "date": "Date signed (YYYYMMDD)",
}
_PROFILE_RAW = {
    "practitioner_name": "cert_practitioner_name",
    "license_number": "cert_license_number",
    "telephone": "cert_telephone",
    "address": "cert_address",
    "date": "cert_date",
}

# Which initials box each practitioner type signs, by FIELD_MAP key suffix.
_INITIAL_SUFFIX = {
    "medical_doctor": "doctor_initial",
    "nurse_practitioner": "nurse_initial",
    "optometrist": "optometrist_initial",
    "occupational_therapist": "therapist_initial",
    "audiologist": "audiologist_initial",
    "physiotherapist": "physio_initial",
    "psychologist": "psychologist_initial",
    "speech_language_pathologist": "pathologist_initial",
}


def _is_profile_raw(key: str) -> bool:
    return ("patient_name" in key or key.endswith("_initial")
            or key == "cert_practitioner_type" or key in _PROFILE_RAW.values())


# Mutually-exclusive checkbox sets → one enum each.
#   *_improved_{yes,no,unsure}            (all sections)
#   vision_q2_{left,right}_<measure>      (how acuity was measured, per eye)
_VISION_MEASURES = ["snellen", "count_fingers", "hand_motion", "light_perception", "no_light"]


def _exclusive_groups() -> dict[str, list[tuple[str, str]]]:
    groups: dict[str, list[tuple[str, str]]] = {}
    for key in FIELD_MAP:
        m = re.match(r"(.+_improved)_(yes|no|unsure)$", key)
        if m:
            groups.setdefault(m.group(1), []).append((m.group(2), key))
    for eye in ("left", "right"):
        groups[f"vision_q2_{eye}_measure"] = [(m, f"vision_q2_{eye}_{m}") for m in _VISION_MEASURES]
    return groups


_GROUP_LABELS = {
    "yes": "Yes - has improved or is likely to improve",
    "no": "No - will not improve",
    "unsure": "Unsure",
    "snellen": "Visual acuity measurable on a Snellen chart",
    "count_fingers": "Count fingers (CF)",
    "hand_motion": "Hand motion (HM)",
    "light_perception": "Light perception (LP)",
    "no_light": "No light perception (NLP)",
}


def _build_fields() -> dict[str, LogicalField]:
    groups = _exclusive_groups()
    member_to_group = {k: g for g, ms in groups.items() for _, k in ms}
    fields: dict[str, LogicalField] = {}

    for key, f in FIELD_MAP.items():
        if _is_profile_raw(key):
            continue
        section = key.split("_")[0]
        if key in member_to_group:
            g = member_to_group[key]
            if g in fields:
                continue
            members = groups[g]
            desc = re.sub(r"\s*[-:].*$", "", f["description"]).strip()
            if g.endswith("_improved"):
                desc = f"{desc}: has the impairment improved, or is it likely to improve?"
            else:
                eye = "Left" if "_left_" in g else "Right"
                desc = f"Q2 {eye} eye: how visual acuity was measured"
            fields[g] = LogicalField(
                key=g, section=section, kind="enum", description=desc,
                options=tuple(EnumOption(v, _GROUP_LABELS[v], member) for v, member in members),
                members=tuple(m for _, m in members),
            )
            continue

        t = f["type"]
        if t == "radio_group":
            opts = enum_options(list(f["options"].items()))
            fields[key] = LogicalField(key, section, "enum", f["description"], opts)
        elif t == "choice":
            opts = enum_options([(o, o) for o in f["options"]])
            fields[key] = LogicalField(key, section, "enum", f["description"], opts)
        elif t == "checkbox":
            fields[key] = LogicalField(key, section, "bool", f["description"])
        else:
            fields[key] = LogicalField(
                key, section, infer_text_kind(key, f["description"]), _text_hint(key, f["description"]),
                mandatory=key in MANDATORY_FIELDS,
            )
    return fields


def _text_hint(key: str, description: str) -> str:
    """Spell out what a good answer looks like; the raw descriptions are terse."""
    if key.endswith("_q1_conditions"):
        return description + ". Write the diagnosis name(s) with the year in brackets, e.g. 'Rheumatoid arthritis (2015)'"
    if key.endswith("_examples"):
        return description + ". 1-3 sentences describing concrete day-to-day limitations from the notes"
    if key.endswith("_devices_therapy"):
        return description + ". Name the devices, medications or therapies"
    return description


def _build_chunks(fields: dict[str, LogicalField]) -> list[Chunk]:
    chunks = []
    for s in SECTIONS:
        keys = [k for k, f in fields.items() if f.section == s.id]
        if s.id == "mental":
            # ~50 fields is too much for a 7-8B model in one pass.
            q = lambda k: int(re.match(r"mental_q(\d+)", k).group(1))
            parts = {
                "mental_a": [k for k in keys if q(k) <= 4],
                "mental_b": [k for k in keys if q(k) == 5],
                "mental_c": [k for k in keys if q(k) >= 6],
            }
            chunks += [Chunk(cid, s.id, tuple(ks)) for cid, ks in parts.items()]
        else:
            chunks.append(Chunk(s.id, s.id, tuple(keys)))
    return chunks


def stamp_profile(values: dict, profile: dict) -> dict:
    """Raw FIELD_MAP values derived from the profile (not from the notes)."""
    raw: dict = {}
    name = (profile.get("patient_name") or "").strip()
    if name:
        raw.update({k: name for k in FIELD_MAP if "patient_name" in k})

    for attr, key in _PROFILE_RAW.items():
        if profile.get(attr):
            raw[key] = str(profile[attr])

    ptype = profile.get("practitioner_type")
    cert_opts = FIELD_MAP["cert_practitioner_type"]["options"]
    code = next((c for c, label in cert_opts.items()
                 if label.lower().replace("-", "_").replace(" ", "_") == ptype), None)
    if code:
        raw["cert_practitioner_type"] = code

    initials = (profile.get("practitioner_initials") or "").strip()
    suffix = _INITIAL_SUFFIX.get(ptype or "")
    if initials and suffix:
        # Initial each impairment section that has content.
        touched = {FORM.fields[k].section for k, v in values.items()
                   if k in FORM.fields and v not in ("", False, None, "not_mentioned")}
        for s in touched:
            key = f"{s}_{suffix}"
            if key in FIELD_MAP:
                raw[key] = initials
    return raw


DOMAIN_CONTEXT = """\
The T2201 Disability Tax Credit Certificate is completed by a medical practitioner.
Key terms:
- "Marked restriction": the patient is unable, or takes an inordinate amount of time
  (about 3x longer than someone of similar age without the impairment), to perform the
  activity, even with appropriate therapy, medication and devices.
- "All or substantially all of the time": at least 90% of the time.
- Impairments must have lasted, or be expected to last, at least 12 continuous months."""

_fields = _build_fields()
FORM = FormSpec(
    id="t2201",
    title="T2201 Disability Tax Credit Certificate (Part B)",
    template_path=HERE / "template.pdf",
    field_map=FIELD_MAP,
    sections=SECTIONS,
    fields=_fields,
    chunks=_build_chunks(_fields),
    profile_fields=PROFILE_FIELDS,
    rules=check,
    stamp_profile=stamp_profile,
    domain_context=DOMAIN_CONTEXT,
    extra={"practitioner_types": list(_INITIAL_SUFFIX)},
)
