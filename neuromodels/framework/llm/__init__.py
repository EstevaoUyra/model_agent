"""Shared LLM access for framework modules."""

from neuromodels.framework.llm.core import DEFAULT_SYSTEM_PROMPT, LLMResponse, get_llm_response

__all__ = ["DEFAULT_SYSTEM_PROMPT", "LLMResponse", "get_llm_response"]
