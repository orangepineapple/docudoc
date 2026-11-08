"""
Write raw FIELD_MAP values into a fillable PDF.

Notes on the CRA templates:
  - They are hybrid AcroForm + XFA. Acrobat renders the XFA layer and would
    ignore AcroForm values, so the XFA entry is removed from the output.
  - They are AES-encrypted (permissions only), which needs `cryptography`.
  - Dropdowns store export values ("5") behind display text ("severe: 71-90dB").
"""
from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject


def fill_pdf(template_path: str | Path, field_map: dict, raw: dict) -> bytes:
    reader = PdfReader(str(template_path))
    writer = PdfWriter(clone_from=reader)

    acroform = writer._root_object["/AcroForm"]
    if "/XFA" in acroform:
        del acroform["/XFA"]
    acroform[NameObject("/NeedAppearances")] = BooleanObject(True)

    choice_exports = _choice_exports(reader)
    updates: dict[str, str] = {}
    for key, value in raw.items():
        f = field_map.get(key)
        if f is None or value in (None, "", False):
            continue
        fid, t = f["field_id"], f["type"]
        if t == "checkbox":
            updates[fid] = f["checked_value"]
        elif t == "radio_group":
            if value in f["options"]:
                updates[fid] = value
        elif t == "choice":
            export = choice_exports.get(fid, {}).get(value)
            if export is not None:
                updates[fid] = export
        else:
            updates[fid] = str(value)

    for page in writer.pages:
        writer.update_page_form_field_values(page, updates, auto_regenerate=False)

    # pypdf's generated appearances don't wrap multi-line text and show
    # dropdown export values instead of labels. Drop them for text/choice
    # widgets; NeedAppearances makes the viewer regenerate them properly.
    text_ids = {field_map[k]["field_id"] for k in raw if k in field_map
                and field_map[k]["type"] in ("text", "choice")}
    for page in writer.pages:
        for annot in page.get("/Annots", []) or []:
            w = annot.get_object()
            if "/AP" in w and _qualified_name(w) in text_ids:
                del w["/AP"]

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _qualified_name(obj) -> str:
    parts = []
    while obj is not None:
        if "/T" in obj:
            parts.append(str(obj["/T"]))
        obj = obj["/Parent"].get_object() if "/Parent" in obj else None
    return ".".join(reversed(parts))


def _choice_exports(reader: PdfReader) -> dict[str, dict[str, str]]:
    """field_id -> {display text: export value} for dropdowns with [export, display] /Opt pairs."""
    out = {}
    for fid, f in (reader.get_fields() or {}).items():
        opts = f.get("/Opt")
        if f.get("/FT") == "/Ch" and opts:
            pairs = {}
            for o in opts:
                if isinstance(o, list) and len(o) == 2:
                    pairs[str(o[1])] = str(o[0])
                else:
                    pairs[str(o)] = str(o)
            out[fid] = pairs
    return out


def read_values(pdf: bytes | str | Path, field_map: dict) -> dict:
    """Read raw FIELD_MAP values back out of a filled PDF (used by tests)."""
    reader = PdfReader(io.BytesIO(pdf) if isinstance(pdf, bytes) else str(pdf))
    fields = reader.get_fields() or {}
    out = {}
    for key, f in field_map.items():
        v = fields.get(f["field_id"], {}).get("/V")
        if v in (None, "", "/Off"):
            continue
        v = str(v)
        if f["type"] == "checkbox":
            out[key] = v == f["checked_value"]
        elif f["type"] == "choice":
            opts = fields[f["field_id"]].get("/Opt") or []
            out[key] = next((str(o[1]) for o in opts if isinstance(o, list) and str(o[0]) == v), v)
        else:
            out[key] = v
    return out
