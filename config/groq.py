"""Helper utilities for loading and initializing Groq API credentials.

Provides:
- `get_groq_api_key()` - read and optionally validate the API key from env
- `get_auth_headers()` - common Authorization headers for HTTP calls
- `init_groq_client()` - try to initialize the Groq SDK client if available

The project loads `.env` at runtime (see `run_ui.py` / `run_mcp_server.py`) so this
module also calls `load_dotenv()` to be safe when imported directly in scripts.
"""
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_groq_api_key(required: bool = True) -> Optional[str]:
    """Return the `GROQ_API_KEY` from environment.

    Args:
        required: If True, raise RuntimeError when the key is not present.

    Returns:
        The API key string or None if not set and `required` is False.
    """
    key = os.getenv("GROQ_API_KEY")
    if required and not key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Add it to your `.env` (GROQ_API_KEY=...)"
        )
    return key


def validate_groq_key(key: Optional[str]) -> bool:
    """Basic heuristic validation for a Groq API key.

    This is intentionally lightweight: it accepts keys that look like the
    example `gsk_...` but won't enforce a strict format.
    """
    if not key:
        return False
    if key.startswith("gsk_"):
        return True
    return len(key) >= 16


def get_auth_headers() -> dict:
    """Return headers suitable for HTTP calls to Groq endpoints.

    If no key is present, returns an empty dict.
    """
    key = get_groq_api_key(required=False)
    if not key:
        return {}
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def init_groq_client():
    """Attempt to initialize the Groq SDK client.

    This tries a few common constructor names and gracefully returns `None`
    if the SDK isn't installed or the constructor shape is unexpected.

    Usage:
        client = init_groq_client()
        if client is None:
            # fallback to HTTP requests using `get_auth_headers()`
    """
    key = get_groq_api_key(required=False)
    if not key:
        return None

    try:
        import groq
    except Exception:
        return None

    # Try a few common constructor patterns used across SDK versions
    try:
        if hasattr(groq, "Client"):
            return groq.Client(api_key=key)
    except Exception:
        pass

    try:
        if hasattr(groq, "GroqClient"):
            return groq.GroqClient(api_key=key)
    except Exception:
        pass

    # Last-resort attempt: call module as constructor
    try:
        return groq.Client(key)  # type: ignore
    except Exception:
        return None
