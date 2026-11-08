"""Form registry. Add a form by creating forms/<id>/ that exposes FORM."""
from __future__ import annotations

from importlib import import_module

from ..core.form import FormSpec

FORM_IDS = ["t2201"]
_cache: dict[str, FormSpec] = {}


def get_form(form_id: str) -> FormSpec:
    if form_id not in FORM_IDS:
        raise KeyError(f"Unknown form {form_id!r}. Available: {FORM_IDS}")
    if form_id not in _cache:
        _cache[form_id] = import_module(f"{__name__}.{form_id}").FORM
    return _cache[form_id]


def list_forms() -> list[FormSpec]:
    return [get_form(i) for i in FORM_IDS]
