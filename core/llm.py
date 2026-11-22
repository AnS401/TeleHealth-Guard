"""Groq first, OpenRouter as fallback. Both are OpenAI-compatible, so one client library serves both."""
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GROQ_URL = "https://api.groq.com/openai/v1"
OPENROUTER_URL = "https://openrouter.ai/api/v1"


class LLMUnavailable(Exception):
    pass


def available() -> bool:
    return bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY"))


def _providers():
    p = []
    if os.getenv("GROQ_API_KEY"):
        p.append(("groq", GROQ_URL, os.environ["GROQ_API_KEY"],
                  os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")))
    if os.getenv("OPENROUTER_API_KEY"):
        p.append(("openrouter", OPENROUTER_URL, os.environ["OPENROUTER_API_KEY"],
                  os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")))
    return p


def chat(messages: list[dict], json_mode: bool = False, max_tokens: int = 300) -> tuple[str, str]:
    """Returns (text, provider_name). Raises LLMUnavailable if every provider fails."""
    from openai import OpenAI  # lazy import so tests run without the package
    errors = []
    for name, url, key, model in _providers():
        try:
            client = OpenAI(base_url=url, api_key=key, timeout=20, max_retries=0)
            kwargs = dict(model=model, messages=messages, temperature=0, max_tokens=max_tokens)
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            r = client.chat.completions.create(**kwargs)
            return r.choices[0].message.content or "", name
        except Exception as e:  # try the next provider
            errors.append(f"{name}: {type(e).__name__}")
    raise LLMUnavailable("; ".join(errors) or "no API keys set")
