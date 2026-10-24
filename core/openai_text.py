"""Shared text generation through the existing OpenAI connection."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import requests
from dotenv import dotenv_values


DEFAULT_MODEL = "gpt-5.6-luna"


def configured_api_key(root: Path | None = None) -> str:
    """Reuse existing project/shared configuration without copying or rewriting keys."""
    if os.getenv("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    root = root or Path(__file__).resolve().parents[1]
    locations = [root / ".env", root / ".env.shared"]
    # Worktrees keep .git as a file. The nearest ancestor owning .git is the
    # same business checkout; do not search unrelated workspace or HOME files.
    owner = next((path for path in [root, *root.parents] if (path / ".git").is_dir()), None)
    if owner is not None and owner != root:
        locations.append(owner / ".env.shared")
    for path in locations:
        if path.is_file():
            value = dotenv_values(path).get("OPENAI_API_KEY")
            if value:
                return value
    return ""


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
