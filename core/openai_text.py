"""Shared text generation through the existing OpenAI connection."""
from __future__ import annotations

import os
from typing import Callable

import requests


DEFAULT_MODEL = "gpt-5.6-luna"


def generate_text(instructions: str, content: str, *, api_key: str,
                  model: str | None = None, max_output_tokens: int = 8000,
                  requester: Callable | None = None) -> str:
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    response = (requester or requests.post)(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL,
              "instructions": instructions, "input": content,
              "max_output_tokens": max_output_tokens, "store": False},
        timeout=55, allow_redirects=False,
    )
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI HTTP {response.status_code}")
    data = response.json()
    if data.get("status") != "completed":
        raise ValueError("OpenAI response is not complete")
    text = "\n".join(
        block["text"] for item in data.get("output", [])
        if item.get("type") == "message"
        for block in item.get("content", [])
        if block.get("type") == "output_text" and isinstance(block.get("text"), str)
    ).strip()
    if not text:
        raise ValueError("OpenAI response has no text")
    return text
