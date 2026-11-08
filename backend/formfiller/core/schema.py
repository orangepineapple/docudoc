"""
Build JSON Schemas (for Ollama constrained decoding) and prompt field listings
from a form's logical fields.
"""
from __future__ import annotations

from .form import NOT_MENTIONED, Chunk, FormSpec, LogicalField


def value_schema(f: LogicalField) -> dict:
    if f.kind == "enum":
        return {"type": "string", "enum": f.enum_values}
    if f.kind == "bool":
        return {"type": "boolean"}
    return {"type": "string"}


def chunk_schema(form: FormSpec, chunk: Chunk, evidence: bool) -> dict:
    props = {}
    for key in chunk.keys:
        f = form.fields[key]
        if evidence:
            # Evidence comes first so the model commits to a quote before a value.
            props[key] = {
                "type": "object",
                "properties": {"evidence": {"type": "string"}, "value": value_schema(f)},
                "required": ["evidence", "value"],
            }
        else:
            props[key] = value_schema(f)
    return {"type": "object", "properties": props, "required": list(chunk.keys)}


def describe_field(f: LogicalField) -> str:
    if f.kind == "enum":
        opts = "; ".join(f'"{o.value}" = {o.label}' for o in f.options)
        return f'- {f.key}: {f.description}\n    options: {opts}; "{NOT_MENTIONED}" = notes do not say'
    if f.kind == "bool":
        return f"- {f.key}: {f.description} (true only if the notes say so, otherwise false)"
    hint = {"year": " (4-digit year, or empty)", "number": " (number, or empty)"}.get(f.kind, " (text, or empty)")
    req = " [MANDATORY if this section applies]" if f.mandatory else ""
    return f"- {f.key}: {f.description}{hint}{req}"


def describe_chunk(form: FormSpec, chunk: Chunk) -> str:
    return "\n".join(describe_field(form.fields[k]) for k in chunk.keys)


def router_schema(form: FormSpec) -> dict:
    ids = [s.id for s in form.sections]
    return {
        "type": "object",
        "properties": {"sections": {"type": "array", "items": {"type": "string", "enum": ids}}},
        "required": ["sections"],
    }


def select_schema(chunk: Chunk) -> dict:
    return {
        "type": "object",
        "properties": {"answered": {"type": "array", "items": {"type": "string", "enum": list(chunk.keys)}}},
        "required": ["answered"],
    }
