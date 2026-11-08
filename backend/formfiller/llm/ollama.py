"""
Minimal async client for Ollama's native chat API.

Uses /api/chat (not the OpenAI-compatible endpoint) because it supports
`format` = JSON Schema for constrained decoding, `think` for Qwen3-style
reasoning models, and returns token counts and timings.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx

DEFAULT_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


class OllamaError(RuntimeError):
    pass


@dataclass
class ChatResult:
    content: str
    prompt_tokens: int
    output_tokens: int
    duration_ms: int

    def json(self) -> dict:
        return json.loads(self.content)


class Ollama:
    def __init__(self, base_url: str = DEFAULT_URL, timeout: float = 600):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()

    async def models(self) -> list[dict]:
        try:
            r = await self._client.get("/api/tags")
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise OllamaError(f"Ollama is not reachable at {self.base_url}: {e}") from e
        return r.json().get("models", [])

    async def chat(
        self,
        model: str,
        messages: list[dict],
        schema: dict | None = None,
        temperature: float = 0.0,
        num_ctx: int = 8192,
        think: bool | None = False,
        seed: int | None = 0,
    ) -> ChatResult:
        body: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }
        if seed is not None:
            body["options"]["seed"] = seed
        if schema is not None:
            body["format"] = schema
        if think is not None:
            body["think"] = think
        try:
            r = await self._client.post("/api/chat", json=body)
        except httpx.HTTPError as e:
            raise OllamaError(f"Ollama request failed: {e}") from e
        if r.status_code == 400 and "think" in r.text and think is not None:
            # Model doesn't support the think flag; retry without it.
            return await self.chat(model, messages, schema, temperature, num_ctx, None, seed)
        if r.status_code != 200:
            raise OllamaError(f"Ollama {r.status_code}: {r.text[:300]}")
        d = r.json()
        return ChatResult(
            content=d["message"]["content"],
            prompt_tokens=d.get("prompt_eval_count", 0),
            output_tokens=d.get("eval_count", 0),
            duration_ms=int(d.get("total_duration", 0) / 1e6),
        )
