"""
Notes -> logical form values.

Pipeline:
  1. Route: one call decides which sections the notes discuss.
  2. Extract: one constrained-JSON call per chunk of a routed section.
  3. Ground: evidence quotes are located in the notes.
  4. Validate: deterministic form rules.

Variants (the model only ever sees readable enum values; core/codec.py maps
them to PDF option codes):
  v1_schema    Readable enums + not_mentioned, JSON Schema constrained decoding.
  v2_evidence  v1 + an evidence quote before every value.
  v3_select    Two steps per chunk: the model first lists which fields the
               notes actually address, then fills only those (with evidence).
               Everything else is forced to not_mentioned.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass
from typing import AsyncIterator, Literal, get_args

from ..llm.ollama import Ollama, OllamaError
from . import codec, evidence, schema
from .form import NOT_MENTIONED, Chunk, FormSpec

Variant = Literal["v1_schema", "v2_evidence", "v3_select"]
VARIANTS: tuple[Variant, ...] = get_args(Variant)


@dataclass
class PipelineConfig:
    model: str = "qwen2.5:7b"
    variant: Variant = "v3_select"
    route: bool = True
    think: bool = False
    num_ctx: int = 8192
    concurrency: int = 2
    drop_ungrounded: bool = False   # clear values whose evidence isn't in the notes

    @property
    def name(self) -> str:
        bits = [self.model, self.variant]
        if not self.route:
            bits.append("noroute")
        if self.think:
            bits.append("think")
        if self.drop_ungrounded:
            bits.append("dropungrounded")
        return "|".join(bits)


# ── Prompts ──────────────────────────────────────────────────────────────────

def detect_relevant_sections(form: FormSpec, notes: str) -> list[dict]:
    listing = "\n".join(f'- "{s.id}": {s.label} — {s.description}' for s in form.sections)
    system = f"""You triage clinical notes for the {form.title}.
List every section of the form that the notes contain information for.

Sections:
{listing}

Include a section if the notes describe the patient's condition, limitations,
treatment or history relevant to it (including explicit statements that the
patient has NO limitation in that area). Exclude sections the notes never touch.
Respond with JSON: {{"sections": [...]}}"""
    return [{"role": "system", "content": system},
            {"role": "user", "content": f"Clinical notes:\n<<<\n{notes}\n>>>"}]


def quote_and_fill_section(form: FormSpec, chunk: Chunk, notes: str, with_evidence: bool) -> list[dict]:
    section = next(s for s in form.sections if s.id == chunk.section)
    evidence_rule = """
- For every field, FIRST copy into "evidence" the exact words from the notes that
  support the value (verbatim, at most ~30 words). If nothing in the notes supports
  a value, "evidence" must be "" and the value must be "not_mentioned", false or ""."""
    system = f"""You are completing the {section.label.upper()} section of the {form.title}
on behalf of a medical practitioner, using only their clinical notes.

{form.domain_context}

Fields:
{schema.describe_chunk(form, chunk)}

Rules:
- Use only what the notes state or directly imply. Never assume typical findings.
- If the notes do not address a field, answer "{NOT_MENTIONED}" (choices), false
  (checkboxes) or "" (text). Most fields will often be unaddressed; that is expected.
- Text answers: concise clinical wording suitable for the form, based on the notes.
- Years: 4 digits only.{evidence_rule if with_evidence else ""}"""
    return [{"role": "system", "content": system},
            {"role": "user", "content": f"Clinical notes:\n<<<\n{notes}\n>>>"}]


def select_messages(form: FormSpec, chunk: Chunk, notes: str) -> list[dict]:
    section = next(s for s in form.sections if s.id == chunk.section)
    listing = "\n".join(f"- {k}: {form.fields[k].description.split('. ')[0]}" for k in chunk.keys)
    system = f"""You are preparing to complete the {section.label.upper()} section of the {form.title}.
Below are the questions in this part of the form. List ONLY the questions that the
clinical notes explicitly answer.

{listing}

Rules:
- Include a question only if the notes contain a specific statement that answers it.
- For rating grids, include only the items the notes rate or describe individually.
  Do not include items just because similar items are rated.
- Ignore questions the notes do not address. It is normal for most to be excluded.
Respond with JSON: {{"answered": [...]}}"""
    return [{"role": "system", "content": system},
            {"role": "user", "content": f"Clinical notes:\n<<<\n{notes}\n>>>"}]


# ── Pipeline ─────────────────────────────────────────────────────────────────

async def extract_chunk(form: FormSpec, chunk: Chunk, notes: str, variant: Variant, call) -> tuple[dict, dict, list[str]]:
    """One chunk through the pipeline. `call(messages, schema)` returns a ChatResult.

    Returns (values, meta, errors); meta holds the raw evidence quote per key.
    """
    values: dict = {}
    meta: dict = {}
    with_ev = variant in ("v2_evidence", "v3_select")
    if variant == "v3_select":
        for key in chunk.keys:
            values[key] = form.fields[key].empty_value()
        try:
            sel = await call(select_messages(form, chunk, notes), schema.select_schema(chunk))
            picked = set(sel.json().get("answered", []))
        except (OllamaError, json.JSONDecodeError) as e:
            return values, meta, [f"{chunk.id} select: {e}"]
        keys = tuple(k for k in chunk.keys if k in picked)
        if not keys:
            return values, meta, []
        chunk = Chunk(chunk.id, chunk.section, keys)
    try:
        r = await call(quote_and_fill_section(form, chunk, notes, with_ev), schema.chunk_schema(form, chunk, with_ev))
        data = r.json()
    except (OllamaError, json.JSONDecodeError) as e:
        return values, meta, [f"{chunk.id}: {e}"]
    for key in chunk.keys:
        item = data.get(key)
        if with_ev and isinstance(item, dict):
            values[key] = item.get("value")
            meta[key] = {"evidence": item.get("evidence") or ""}
        else:
            values[key] = item
    return values, meta, []


async def run(form: FormSpec, notes: str, cfg: PipelineConfig, llm: Ollama) -> AsyncIterator[dict]:
    """Yields progress events; the last one is {"type": "done", "result": {...}}."""
    t0 = time.monotonic()
    values = form.empty_values()
    field_meta: dict[str, dict] = {}
    sections: dict[str, dict] = {}
    tokens = {"prompt": 0, "output": 0}
    sem = asyncio.Semaphore(cfg.concurrency)

    async def call(messages, schema_=None):
        async with sem:
            r = await llm.chat(cfg.model, messages, schema=schema_, think=cfg.think, num_ctx=cfg.num_ctx)
        tokens["prompt"] += r.prompt_tokens
        tokens["output"] += r.output_tokens
        return r

    # 1. Route
    all_ids = [s.id for s in form.sections]
    routed = all_ids
    if cfg.route:
        try:
            r = await call(detect_relevant_sections(form, notes), schema.router_schema(form))
            routed = [s for s in all_ids if s in set(r.json().get("sections", []))]
        except (OllamaError, json.JSONDecodeError) as e:
            yield {"type": "warning", "message": f"Routing failed, extracting all sections: {e}"}
    yield {"type": "routed", "sections": routed}
    for sid in all_ids:
        if sid not in routed:
            sections[sid] = {"status": "skipped"}

    # 2. Extract
    async def do_section(sid: str) -> dict:
        start = time.monotonic()
        out: dict = {"section": sid, "values": {}, "meta": {}, "errors": []}
        for chunk in form.chunks_for(sid):
            v, m, errs = await extract_chunk(form, chunk, notes, cfg.variant, call)
            out["values"].update(v)
            out["meta"].update(m)
            out["errors"].extend(errs)
        out["ms"] = int((time.monotonic() - start) * 1000)
        return out

    tasks = [asyncio.create_task(do_section(sid)) for sid in routed]
    for fut in asyncio.as_completed(tasks):
        res = await fut
        sid = res["section"]
        clean = codec.coerce(form, res["values"])
        section_values = {k: clean[k] for k in res["values"] if k in clean}
        for key, m in res["meta"].items():
            quote = "" if evidence.is_placeholder(m["evidence"]) else m["evidence"]
            meta = {"evidence": quote, **evidence.ground(quote, notes)}
            is_set = section_values.get(key) not in ("", False, NOT_MENTIONED, None)
            if is_set and not meta["grounded"] and cfg.drop_ungrounded:
                section_values[key] = form.fields[key].empty_value()
                meta["dropped"] = True
            field_meta[key] = meta
        values.update(section_values)
        status = "error" if res["errors"] and not section_values else (
            "empty" if not any(v not in ("", False, NOT_MENTIONED) for v in section_values.values())
            else "extracted")
        sections[sid] = {"status": status, "errors": res["errors"], "ms": res["ms"]}
        yield {"type": "section", "section": sid, "status": status, "errors": res["errors"],
               "values": section_values, "meta": {k: field_meta[k] for k in section_values if k in field_meta}}

    # 3. Validate
    issues = [i.to_dict() for i in form.rules(values)]
    for key, m in field_meta.items():
        if values.get(key) not in ("", False, NOT_MENTIONED) and not m["grounded"]:
            issues.append({"field": key, "severity": "warning", "rule": "ungrounded",
                           "message": "No supporting quote found in the notes, please verify"})

    result = {
        "form_id": form.id,
        "config": asdict(cfg) | {"name": cfg.name},
        "routed": routed,
        "values": values,
        "fields": field_meta,
        "sections": sections,
        "issues": issues,
        "stats": {"ms": int((time.monotonic() - t0) * 1000),
                  "prompt_tokens": tokens["prompt"], "output_tokens": tokens["output"],
                  "errors": sum(len(s.get("errors", [])) for s in sections.values())},
    }
    yield {"type": "done", "result": result}


async def extract(form: FormSpec, notes: str, cfg: PipelineConfig | None = None, llm: Ollama | None = None) -> dict:
    cfg = cfg or PipelineConfig()
    own = llm is None
    llm = llm or Ollama()
    try:
        async for ev in run(form, notes, cfg, llm):
            if ev["type"] == "done":
                return ev["result"]
    finally:
        if own:
            await llm.close()
    raise RuntimeError("pipeline ended without a result")
