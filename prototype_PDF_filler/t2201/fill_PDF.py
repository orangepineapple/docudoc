"""
fill_pdf.py — Stamp extracted field values into the T2201 fillable PDF.
Uses pypdf to write directly into the PDF's actual form fields —
no image conversion, no coordinate math needed.
"""
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject, BooleanObject, ArrayObject, DictionaryObject, TextStringObject
)
from field_map import FIELD_MAP


def fill_pdf(
    template_path: str,
    fields: dict,
    output_path: str,
) -> None:
    """
    Fill the T2201 PDF form fields from extracted data dict.

    Args:
        template_path: Path to blank T2201 PDF
        fields: Dict of {field_key: value} from extract.py
        output_path: Where to write the filled PDF
    """
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    # Build field_id -> value mapping
    updates = {}
    for field_key, value in fields.items():
        if field_key not in FIELD_MAP:
            continue
        field_def = FIELD_MAP[field_key]
        field_id = field_def["field_id"]
        ftype = field_def["type"]

        # Skip empty values
        if value is None or value == "" or value is False:
            continue

        if ftype == "checkbox":
            if value is True or value == field_def.get("checked_value"):
                updates[field_id] = field_def["checked_value"]
        elif ftype == "radio_group":
            # value should be one of the option codes e.g. "/0"
            if str(value) in field_def["options"]:
                updates[field_id] = str(value)
        elif ftype == "choice":
            if value in field_def["options"]:
                updates[field_id] = value
        else:  # text
            updates[field_id] = str(value)

    # Write all field updates
    writer.update_page_form_field_values(
        writer.pages[0],  # pypdf applies to all pages when using full field paths
        updates,
        auto_regenerate=False,
    )

    # pypdf's update_page_form_field_values needs to be called per-page for
    # multi-page forms — use the underlying approach instead
    _fill_multipage(writer, updates)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)

    print(f"Filled PDF saved to: {output_path}")
    filled = sum(1 for v in updates.values() if v)
    print(f"Fields filled: {filled} / {len(updates)} provided values")


def _fill_multipage(writer: PdfWriter, updates: dict) -> None:
    """
    Walk the PDF's AcroForm field tree and set values directly.
    This works reliably for multi-page XFA/AcroForm PDFs.
    """
    if "/AcroForm" not in writer._root_object:
        return

    acroform = writer._root_object["/AcroForm"]
    if "/Fields" not in acroform:
        return

    def get_field_name(field_obj) -> str:
        """Build full dotted field name by walking up parent chain."""
        parts = []
        obj = field_obj
        while obj is not None:
            if "/T" in obj:
                parts.append(str(obj["/T"]))
            obj = obj.get("/Parent")
        return ".".join(reversed(parts)) if parts else ""

    def set_field_value(field_obj, value: str):
        if value.startswith("/"):
            # Radio buttons and checkboxes use NameObject (slash-prefixed codes)
            field_obj.update({
                NameObject("/V"):  NameObject(value),
                NameObject("/AS"): NameObject(value),
            })
        else:
            # Text fields and dropdowns use TextStringObject
            field_obj.update({
                NameObject("/V"):  TextStringObject(value),
                NameObject("/AS"): TextStringObject(value),
            })

    def walk_fields(fields_array):
        for field_ref in fields_array:
            try:
                field = writer.get_object(field_ref)
            except Exception:
                continue

            full_name = get_field_name(field)

            if full_name in updates:
                set_field_value(field, updates[full_name])

            # Recurse into kids
            if "/Kids" in field:
                walk_fields(field["/Kids"])

    walk_fields(acroform["/Fields"])