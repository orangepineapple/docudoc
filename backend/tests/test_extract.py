"""Pipeline tests with a scripted fake LLM (no Ollama needed)."""
import asyncio
import json

from formfiller.core.extract import VARIANTS, PipelineConfig, extract
from formfiller.forms import get_form
from formfiller.llm.ollama import ChatResult

FORM = get_form("t2201")
NOTES = "Bilateral sensorineural hearing loss diagnosed 2018. Uses hearing aids. Lasted more than 12 months."


class FakeLLM:
    """Routes to hearing; answers hearing fields with one quoted and one invented value."""

    def __init__(self):
        self.calls = []

    async def chat(self, model, messages, schema=None, **kw):
        self.calls.append(messages[0]["content"][:40])
        props = (schema or {}).get("properties", {})
        if "sections" in props:
            body = {"sections": ["hearing"]}
        else:
            body = {}
            for key, p in props.items():
                empty = "not_mentioned" if "enum" in p.get("properties", p).get("value", p) else ""
                body[key] = {"evidence": "", "value": empty} if "properties" in p else empty
            if "hearing_q8_lasted_12mo" in body:
                body["hearing_q8_lasted_12mo"] = {"evidence": "Lasted more than 12 months.", "value": "yes"}
                body["hearing_q9_improved"] = {"evidence": "Patient expects full recovery", "value": "yes"}
        return ChatResult(json.dumps(body), 10, 5, 1)


def run(cfg):
    return asyncio.run(extract(FORM, NOTES, cfg, FakeLLM()))


def test_v2_routes_grounds_and_flags():
    r = run(PipelineConfig(variant="v2_evidence"))
    assert r["routed"] == ["hearing"]
    assert r["values"]["hearing_q8_lasted_12mo"] == "yes"
    assert r["fields"]["hearing_q8_lasted_12mo"]["grounded"] is True
    assert r["fields"]["hearing_q9_improved"]["grounded"] is False
    assert {"field": "hearing_q9_improved", "rule": "ungrounded"} in [
        {"field": i["field"], "rule": i["rule"]} for i in r["issues"]]
    assert r["sections"]["vision"]["status"] == "skipped"


def test_v2_drop_ungrounded():
    r = run(PipelineConfig(variant="v2_evidence", drop_ungrounded=True))
    assert r["values"]["hearing_q9_improved"] == "not_mentioned"
    assert r["fields"]["hearing_q9_improved"]["dropped"] is True
    assert r["values"]["hearing_q8_lasted_12mo"] == "yes"


def test_variants_are_the_typed_literal():
    assert VARIANTS == ("v1_schema", "v2_evidence", "v3_select")


def test_api_rejects_unknown_variant():
    from fastapi.testclient import TestClient

    from formfiller.api.main import app

    r = TestClient(app).post("/api/extract", json={"notes": NOTES, "variant": "v0_baseline"})
    assert r.status_code == 422


def test_v3_select_only_fills_selected():
    class SelectLLM(FakeLLM):
        async def chat(self, model, messages, schema=None, **kw):
            props = (schema or {}).get("properties", {})
            if "answered" in props:
                keys = props["answered"]["items"]["enum"]
                return ChatResult(json.dumps({"answered": [k for k in keys if k == "hearing_q8_lasted_12mo"]}), 1, 1, 1)
            if schema and "hearing_q9_improved" in props:
                raise AssertionError("unselected field was sent for extraction")
            return await super().chat(model, messages, schema, **kw)

    r = asyncio.run(extract(FORM, NOTES, PipelineConfig(variant="v3_select"), SelectLLM()))
    assert r["values"]["hearing_q8_lasted_12mo"] == "yes"
    assert r["values"]["hearing_q9_improved"] == "not_mentioned"
