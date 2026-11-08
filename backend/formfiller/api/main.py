"""
HTTP API for the review UI.

  uvicorn formfiller.api.main:app --reload --port 8000
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from ..core import codec
from ..core.extract import VARIANTS, PipelineConfig, run
from ..core.fill import fill_pdf
from ..forms import get_form, list_forms
from ..llm.ollama import Ollama, OllamaError

REPO = Path(__file__).resolve().parents[3]
EVAL_DIR = REPO / "eval"
DEFAULT_MODEL = "qwen2.5:7b"

app = FastAPI(title="FormFiller API", version="0.2.0")


def _form(form_id: str):
    try:
        return get_form(form_id)
    except KeyError as e:
        raise HTTPException(404, str(e))


@app.get("/api/forms")
def forms():
    return [{"id": f.id, "title": f.title} for f in list_forms()]


@app.get("/api/forms/{form_id}")
def form_schema(form_id: str):
    f = _form(form_id)
    return {
        "id": f.id,
        "title": f.title,
        "sections": [{"id": s.id, "label": s.label, "description": s.description} for s in f.sections],
        "fields": [
            {"key": x.key, "section": x.section, "kind": x.kind, "description": x.description,
             "mandatory": x.mandatory, "options": [{"value": o.value, "label": o.label} for o in x.options]}
            for x in f.fields.values()
        ],
        "profile_fields": f.profile_fields,
        "practitioner_types": f.extra.get("practitioner_types", []),
        "variants": VARIANTS,
    }


@app.get("/api/models")
async def models():
    async with Ollama() as llm:
        try:
            ms = await llm.models()
        except OllamaError as e:
            return {"ok": False, "error": str(e), "models": [], "default": DEFAULT_MODEL}
    return {"ok": True, "models": [{"name": m["name"], "size": m.get("size")} for m in ms], "default": DEFAULT_MODEL}


class ExtractRequest(BaseModel):
    form_id: str = "t2201"
    notes: str = Field(min_length=1, max_length=50_000)
    model: str = DEFAULT_MODEL
    variant: str = "v2_evidence"
    route: bool = True


@app.post("/api/extract")
async def extract_stream(req: ExtractRequest, request: Request):
    """Server-sent events: routed, section (one per section), done."""
    form = _form(req.form_id)
    if req.variant not in VARIANTS:
        raise HTTPException(400, f"variant must be one of {VARIANTS}")
    cfg = PipelineConfig(model=req.model, variant=req.variant, route=req.route)

    async def events():
        async with Ollama() as llm:
            try:
                async for ev in run(form, req.notes, cfg, llm):
                    if await request.is_disconnected():
                        return
                    yield f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n"
            except OllamaError as e:
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class ValuesRequest(BaseModel):
    form_id: str = "t2201"
    values: dict
    profile: dict = {}


@app.post("/api/validate")
def validate(req: ValuesRequest):
    form = _form(req.form_id)
    values = codec.coerce(form, req.values)
    return {"issues": [i.to_dict() for i in form.rules(values)]}


@app.post("/api/fill")
def fill(req: ValuesRequest):
    form = _form(req.form_id)
    values = codec.coerce(form, req.values)
    raw = codec.to_raw(form, values) | form.stamp_profile(values, req.profile)
    pdf = fill_pdf(form.template_path, form.field_map, raw)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{form.id}-draft.pdf"'})


@app.get("/api/samples")
def samples():
    """Demo notes: the hand-labelled case plus hand-verified synthetic cases."""
    out = []
    for name in ("hand.jsonl", "synthetic.jsonl"):
        p = EVAL_DIR / "cases" / name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            c = json.loads(line)
            if c.get("verified") or c.get("source") == "hand":
                out.append({"id": c["id"], "style": c.get("style"), "sections": c.get("sections", []), "notes": c["notes"]})
    return out


@app.get("/api/eval")
def eval_results():
    """Aggregates from every eval run (per-case detail stripped)."""
    runs = {}
    for p in sorted((EVAL_DIR / "results").glob("*.json")):
        d = json.loads(p.read_text())
        runs[d.get("run", p.stem)] = {
            name: {"config": c["config"], "aggregate": c["aggregate"]} for name, c in d.get("configs", {}).items()
        }
    return runs


@app.get("/api/eval/{run_name}/{config}/errors")
def eval_errors(run_name: str, config: str, limit: int = 20):
    """Per-case error lists for one config, for the error browser."""
    p = EVAL_DIR / "results" / f"{run_name}.json"
    if not p.exists():
        raise HTTPException(404)
    c = json.loads(p.read_text())["configs"].get(config)
    if not c:
        raise HTTPException(404)
    return [{"case_id": s["case_id"], "style": s.get("style"), "errors": s["errors"], "counts": s["counts"]}
            for s in c["cases"][:limit]]
