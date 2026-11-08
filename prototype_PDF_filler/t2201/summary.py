# summarize.py
from datetime import datetime
from field_map import FIELD_MAP

# Fields CRA explicitly marks as mandatory
MANDATORY_FIELDS = {
    "hearing_q4_examples",
    "vision_q4_examples",
    "speaking_q4_examples",
    "walking_q4_examples",
    "eliminating_q4_examples",
    "feeding_q4_examples",
    "dressing_q4_examples",
    "cumulative_q2_examples",
}

SECTION_LABELS = {
    "vision":       "Vision",
    "speaking":     "Speaking",
    "hearing":      "Hearing",
    "walking":      "Walking",
    "eliminating":  "Eliminating",
    "feeding":      "Feeding",
    "dressing":     "Dressing",
    "mental":       "Mental Functions",
    "cumulative":   "Cumulative Effect",
    "lst":          "Life-Sustaining Therapy",
    "cert":         "Certification",
}

def _is_filled(value) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True

def _display_value(key: str, value) -> str:
    """Human readable version of a field value."""
    field = FIELD_MAP.get(key, {})
    ftype = field.get("type", "text")
    if ftype == "checkbox":
        return "✓ checked" if value else "unchecked"
    if ftype == "radio_group" and isinstance(value, str):
        options = field.get("options", {})
        return options.get(value, value)
    return str(value)

def _progress_bar(filled: int, total: int, width: int = 12) -> str:
    if total == 0:
        return ""
    blocks = int((filled / total) * width)
    return "█" * blocks + "░" * (width - blocks)

def print_summary(
    fields: dict,
    patient_name: str,
    output_path: str,
):
    # Group field keys by section prefix
    section_keys: dict[str, list[str]] = {s: [] for s in SECTION_LABELS}
    for key in FIELD_MAP:
        if "patient_name" in key:
            continue
        prefix = key.split("_")[0]
        if prefix in section_keys:
            section_keys[prefix].append(key)

    # Determine which sections have any filled fields
    filled_sections = {}
    skipped_sections = []
    for section, keys in section_keys.items():
        section_filled = {k: fields[k] for k in keys if k in fields and _is_filled(fields.get(k))}
        if section_filled or section == "cert":
            filled_sections[section] = section_filled
        else:
            skipped_sections.append(section)

    # Print header
    width = 52
    print("\n" + "━" * width)
    print(f"  T2201 FORM SUMMARY — {patient_name}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  ⚠  AI-assisted. Review all fields before submitting.")
    print("━" * width)

    # Sections filled
    print("\nSECTIONS FILLED")
    print("─" * 40)
    for section, section_filled in filled_sections.items():
        total = len([k for k in section_keys[section]])
        count = len(section_filled)
        bar = _progress_bar(count, total)
        label = SECTION_LABELS[section]
        print(f"  ✓  {label:<20} {count}/{total} fields  {bar}")

    # Sections skipped
    if skipped_sections:
        print("\nSECTIONS SKIPPED  (no relevant info found in notes)")
        print("─" * 40)
        for section in skipped_sections:
            print(f"  ○  {SECTION_LABELS[section]}")

    # Fields needing review — empty fields within filled sections
    flagged = {}
    for section, section_filled in filled_sections.items():
        all_keys = section_keys[section]
        missing = []
        for key in all_keys:
            if not _is_filled(fields.get(key)):
                label = FIELD_MAP[key]["description"]
                is_mandatory = key in MANDATORY_FIELDS
                missing.append((key, label, is_mandatory))
        if missing:
            flagged[section] = missing

    if flagged:
        print("\nFIELDS NEEDING REVIEW")
        print("─" * 40)
        for section, missing_fields in flagged.items():
            print(f"  {SECTION_LABELS[section]}")
            for key, label, mandatory in missing_fields:
                tag = "← MANDATORY" if mandatory else ""
                print(f"    ⚠  {key:<45} {tag}")

    # What was filled — section by section
    print("\nWHAT WAS FILLED")
    print("─" * 40)
    for section, section_filled in filled_sections.items():
        if not section_filled:
            continue
        print(f"  {SECTION_LABELS[section]}")
        for key, value in section_filled.items():
            display = _display_value(key, value)
            print(f"    {key:<45}  {display}")

    # Footer
    print("\n" + "━" * width)
    print(f"  PDF saved to: {output_path}")
    print(f"  Open in Acrobat/Preview to review and sign.")
    print("━" * width + "\n")