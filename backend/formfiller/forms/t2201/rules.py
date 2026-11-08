"""
Deterministic checks on logical T2201 values. These run after extraction and
again after every edit in the UI. They never change values, only report.
"""
from __future__ import annotations

import re
from datetime import date

from ...core.form import NOT_MENTIONED, Issue

IMPAIRMENT_SECTIONS = ["vision", "speaking", "hearing", "walking", "eliminating", "feeding", "dressing", "mental"]
MANDATORY_EXAMPLES = {
    s: f"{s}_q4_examples" for s in ["speaking", "hearing", "walking", "eliminating", "feeding", "dressing"]
} | {"cumulative": "cumulative_q2_examples"}


def _set(v) -> bool:
    return v not in (None, "", False, NOT_MENTIONED)


def _touched(values: dict, section: str) -> bool:
    return any(_set(v) for k, v in values.items() if k.startswith(section + "_"))


def check(values: dict) -> list[Issue]:
    issues: list[Issue] = []
    this_year = date.today().year

    # Year formats and plausibility.
    for key, v in values.items():
        if "year" not in key or "years" in key or not _set(v):
            continue
        s = str(v).strip()
        if key == "cert_year_to" and s.lower() == "present":
            continue
        if not re.fullmatch(r"\d{4}", s):
            issues.append(Issue(key, "error", f"Expected a 4-digit year, got {s!r}", "year_format"))
            continue
        y = int(s)
        future_ok = re.search(r"_q\d+_year$", key)  # expected-improvement years, e.g. mental_q11_year
        if y < 1900 or (y > this_year and not future_ok):
            issues.append(Issue(key, "error", f"Year {y} is out of range", "year_range"))

    # Improvement answer ↔ improvement year.
    for key, v in values.items():
        m = re.fullmatch(r"(\w+_q\d+)_improved", key)
        if not m:
            continue
        year_key = f"{m.group(1)}_year"
        has_year = _set(values.get(year_key))
        if v == "yes" and not has_year:
            issues.append(Issue(year_key, "warning", "Improvement expected: provide the expected year", "improve_year_missing"))
        elif v != "yes" and has_year:
            issues.append(Issue(year_key, "warning", "Year given but improvement is not marked 'Yes'", "improve_year_unexpected"))

    # Section-level completeness.
    for s in IMPAIRMENT_SECTIONS + ["cumulative"]:
        if not _touched(values, s):
            continue
        ex = MANDATORY_EXAMPLES.get(s)
        if ex and not _set(values.get(ex)):
            issues.append(Issue(ex, "error", "Mandatory: CRA requires examples for this section", "mandatory_examples"))
        cond = f"{s}_q1_conditions"
        if cond in values and not _set(values.get(cond)):
            issues.append(Issue(cond, "warning", "No diagnosis listed for a section that is filled in", "missing_diagnosis"))
        for key, v in values.items():
            if key.startswith(s + "_") and key.endswith("_lasted_12mo") and v == "no":
                issues.append(Issue(key, "info", "Under 12 months: the patient will not qualify on this section", "duration_ineligible"))

    # Cumulative effect needs at least two categories.
    if _touched(values, "cumulative"):
        n = sum(1 for k, v in values.items() if k.startswith("cumulative_q1_") and v is True)
        if n < 2:
            issues.append(Issue("cumulative_q1_vision", "warning",
                                f"Cumulative effect requires at least 2 categories ({n} selected)", "cumulative_min_two"))

    # Life-sustaining therapy: type 1 diabetes diagnosed 2021+ needs the year.
    if values.get("lst_q1_type1_diabetes_timing") == "2021_and_later" and not _set(values.get("lst_q1_year_diagnosed")):
        issues.append(Issue("lst_q1_year_diagnosed", "warning", "Provide the year of diagnosis", "lst_year_missing"))

    # Certification period.
    a, b = str(values.get("cert_year_from") or ""), str(values.get("cert_year_to") or "")
    if a.isdigit() and b.isdigit() and int(a) > int(b):
        issues.append(Issue("cert_year_from", "error", "'From' year is after 'to' year", "cert_period"))

    return issues
