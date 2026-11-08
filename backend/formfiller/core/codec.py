"""
Translate between logical values (readable enums, used by the LLM and UI) and
raw FIELD_MAP values (PDF option codes, used by fill.py).

Raw format is the same one the original prototype produced:
  radio_group -> option code "/0"
  choice      -> option text
  checkbox    -> True
  text        -> str
"""
from __future__ import annotations

from .form import NOT_MENTIONED, FormSpec


def to_raw(form: FormSpec, values: dict) -> dict:
    raw: dict = {}
    for key, v in values.items():
        f = form.fields.get(key)
        if f is None or v in (None, "", False, NOT_MENTIONED):
            continue
        if f.kind == "enum":
            opt = next((o for o in f.options if o.value == v), None)
            if opt is None:
                continue
            if f.members:                 # exclusive checkbox group
                raw[opt.raw] = True
            else:
                raw[key] = opt.raw
        elif f.kind == "bool":
            raw[key] = True
        else:
            raw[key] = str(v).strip()
    return raw


def from_raw(form: FormSpec, raw: dict) -> dict:
    """Inverse of to_raw. Unknown or invalid raw values become empty."""
    values = form.empty_values()
    for key, f in form.fields.items():
        if f.members:
            checked = [o for o in f.options if _truthy(raw.get(o.raw), form.field_map[o.raw])]
            if len(checked) == 1:
                values[key] = checked[0].value
            continue
        v = raw.get(key)
        if v in (None, "", False):
            continue
        if f.kind == "enum":
            opt = next((o for o in f.options if o.raw == v), None)
            if opt:
                values[key] = opt.value
        elif f.kind == "bool":
            values[key] = _truthy(v, form.field_map[key])
        else:
            values[key] = str(v)
    return values


def _truthy(v, field_def: dict) -> bool:
    return v is True or (v is not None and v == field_def.get("checked_value"))


def coerce(form: FormSpec, values: dict) -> dict:
    """Clamp arbitrary input (LLM output, API edits) to valid logical values."""
    out = form.empty_values()
    for key, f in form.fields.items():
        if key not in values:
            continue
        v = values[key]
        if f.kind == "enum":
            out[key] = v if v in f.enum_values else NOT_MENTIONED
        elif f.kind == "bool":
            out[key] = v is True or (isinstance(v, str) and v.lower() == "true")
        else:
            out[key] = "" if v is None else str(v).strip()
    return out
