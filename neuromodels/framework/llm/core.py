from __future__ import annotations

import base64
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path

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


def get_vision_response(
    prompt: str,
    image_paths: list[str | Path],
    *,
    system_prompt: str | None = None,
    model: str | None = None,
) -> LLMResponse:
    """Return an LLM response for a prompt plus one or more images."""

    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    if not image_paths:
        raise ValueError("at least one image path is required")

    paths = [Path(path) for path in image_paths]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    provider = os.getenv("NEUROMODELS_LLM_PROVIDER", "openai").lower()
    chosen_model = model or os.getenv("NEUROMODELS_LLM_MODEL")

    if provider == "fake":
        fake_model = chosen_model or "fake-vlm"
        return LLMResponse(
            content=(
                f"[fake vlm] reviewed {len(prompt)} characters and "
                f"{len(paths)} image(s)."
            ),
            model=fake_model,
            provider="fake",
        )
    if provider == "openai":
        return _get_openai_vision_response(
            prompt,
            paths,
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


def _get_openai_vision_response(
    prompt: str,
    image_paths: list[Path],
    *,
    system_prompt: str,
    model: str,
) -> LLMResponse:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI provider requires the optional OpenAI SDK. "
            "Install with `pip install -e .[openai]`."
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for the OpenAI LLM provider")

    content: list[dict] = [{"type": "input_text", "text": prompt}]
    for path in image_paths:
        content.append(
            {
                "type": "input_image",
                "image_url": _image_data_url(path),
            }
        )

    client = OpenAI()
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )
    return LLMResponse(
        content=getattr(response, "output_text", ""),
        model=getattr(response, "model", model),
        provider="openai",
    )


def _image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
