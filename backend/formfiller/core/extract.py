"""
Notes -> logical form values.

Pipeline (v1/v2):
  1. Route: one call decides which sections the notes discuss.
  2. Extract: one constrained-JSON call per chunk of a routed section.
  3. Ground: evidence quotes are located in the notes.
  4. Validate: deterministic form rules.

Variants:
  v0_baseline  The original prototype: free-form JSON with raw PDF codes,
               every section, "{}" when irrelevant. Kept for comparison.
  v1_schema    Readable enums + not_mentioned, JSON Schema constrained decoding.
  v2_evidence  v1 + an evidence quote before every value.
  v3_select    Two steps per chunk: the model first lists which fields the
               notes actually address, then fills only those (with evidence).
               Everything else is forced to not_mentioned.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import asdict, dataclass
from typing import AsyncIterator, Literal

from ..llm.ollama import Ollama, OllamaError
from . import codec, evidence, schema
from .form import NOT_MENTIONED, Chunk, FormSpec

Variant = Literal["v0_baseline", "v1_schema", "v2_evidence", "v3_select"]
VARIANTS: list[str] = ["v0_baseline", "v1_schema", "v2_evidence", "v3_select"]


@dataclass
class PipelineConfig:
    model: str = "qwen2.5:7b"
    variant: Variant = "v2_evidence"
    route: bool = True
    think: bool = False
    num_ctx: int = 8192
    concurrency: int = 2
    drop_ungrounded: bool = False   # clear values whose evidence isn't in the notes

    @property
    def name(self) -> str:
        bits = [self.model, self.variant]
        if self.variant != "v0_baseline" and not self.route:
            bits.append("noroute")
        if self.think:
            bits.append("think")
        if self.drop_ungrounded:
            bits.append("dropungrounded")
        return "|".join(bits)


# ── Prompts ──────────────────────────────────────────────────────────────────

def router_messages(form: FormSpec, notes: str) -> list[dict]:
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


def chunk_messages(form: FormSpec, chunk: Chunk, notes: str, with_evidence: bool) -> list[dict]:
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


# ── v0: the original prototype prompt, verbatim ───────────────────────────────

def _v0_section_schema(section_fields: dict) -> str:
    lines = []
    for key, field in section_fields.items():
        if "patient_name" in key:
            continue
        desc, ftype = field["description"], field["type"]
        if ftype == "radio_group":
            opts = " | ".join(f'{v}="{label}"' for v, label in field["options"].items())
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "choice":
            opts = " | ".join(f'"{o}"' for o in field["options"])
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "checkbox":
            lines.append(f'  "{key}": false  // {desc}. Set true to check.')
        else:
            lines.append(f'  "{key}": ""  // {desc}')
    return "{\n" + "\n".join(lines) + "\n}"


def v0_messages(form: FormSpec, section_id: str, notes: str) -> list[dict]:
    fields = {k: v for k, v in form.field_map.items() if k.startswith(section_id + "_")}
    system = f"""You are filling the {section_id.upper()} section of a Canadian T2201
Disability Tax Credit form based on doctor's notes.

If the notes contain NO information about {section_id}, return an empty JSON object: {{}}

Otherwise extract relevant information and return ONLY valid JSON matching this schema:
{_v0_section_schema(fields)}

Rules:
- Return ONLY valid JSON. No explanation, no markdown, no code fences.
- Leave fields as "" or false if not mentioned in the notes.
- For radio fields use the option code exactly e.g. "/0" or "/1"
- For year fields use 4-digit year only e.g. "2019"
- For improvement questions check exactly ONE of _yes, _no, or _unsure"""
    return [{"role": "system", "content": system}, {"role": "user", "content": notes}]


# ── Pipeline ─────────────────────────────────────────────────────────────────

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
    if cfg.variant != "v0_baseline" and cfg.route:
        try:
            r = await call(router_messages(form, notes), schema.router_schema(form))
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
        if cfg.variant == "v0_baseline":
            try:
                r = await call(v0_messages(form, sid, notes))
                raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", r.content.strip(), flags=re.MULTILINE).strip()
                raw = json.loads(raw_text) if raw_text else {}
                decoded = codec.from_raw(form, raw)
                out["values"] = {k: v for k, v in decoded.items() if form.fields[k].section == sid}
                out["empty"] = not raw
            except json.JSONDecodeError as e:
                out["errors"].append(f"invalid JSON: {e}")
            except OllamaError as e:
                out["errors"].append(str(e))
        else:
            with_ev = cfg.variant in ("v2_evidence", "v3_select")
            for chunk in form.chunks_for(sid):
                if cfg.variant == "v3_select":
                    for key in chunk.keys:
                        out["values"][key] = form.fields[key].empty_value()
                    try:
                        sel = await call(select_messages(form, chunk, notes), schema.select_schema(chunk))
                        picked = set(sel.json().get("answered", []))
                    except (OllamaError, json.JSONDecodeError) as e:
                        out["errors"].append(f"{chunk.id} select: {e}")
                        continue
                    keys = tuple(k for k in chunk.keys if k in picked)
                    if not keys:
                        continue
                    chunk = Chunk(chunk.id, chunk.section, keys)
                try:
                    r = await call(chunk_messages(form, chunk, notes, with_ev),
                                   schema.chunk_schema(form, chunk, with_ev))
                    data = r.json()
                except (OllamaError, json.JSONDecodeError) as e:
                    out["errors"].append(f"{chunk.id}: {e}")
                    continue
                for key in chunk.keys:
                    item = data.get(key)
                    if with_ev and isinstance(item, dict):
                        out["values"][key] = item.get("value")
                        out["meta"][key] = {"evidence": item.get("evidence") or ""}
                    else:
                        out["values"][key] = item
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
            "empty" if res.get("empty") or not any(v not in ("", False, NOT_MENTIONED) for v in section_values.values())
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
