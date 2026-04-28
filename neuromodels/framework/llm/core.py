from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SYSTEM_PROMPT = (
    "You are reviewing scoped scientific and code artifacts. Use only the "
    "material supplied in the user prompt."
)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str


def get_llm_response(
    prompt: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
) -> LLMResponse:
    """Return an LLM response for a prompt using the configured provider."""

    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    provider = os.getenv("NEUROMODELS_LLM_PROVIDER", "openai").lower()
    chosen_model = model or os.getenv("NEUROMODELS_LLM_MODEL")

    if provider == "fake":
        fake_model = chosen_model or "fake-llm"
        return LLMResponse(
            content=f"[fake llm] reviewed {len(prompt)} characters.",
            model=fake_model,
            provider="fake",
        )
    if provider == "openai":
        return _get_openai_response(
            prompt,
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
            model=chosen_model or "gpt-5.1",
        )

    raise ValueError(f"unsupported LLM provider: {provider}")


def _get_openai_response(prompt: str, *, system_prompt: str, model: str) -> LLMResponse:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI provider requires the optional OpenAI SDK. "
            "Install with `pip install -e .[openai]`."
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for the OpenAI LLM provider")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return LLMResponse(
        content=response.choices[0].message.content or "",
        model=getattr(response, "model", model),
        provider="openai",
    )
