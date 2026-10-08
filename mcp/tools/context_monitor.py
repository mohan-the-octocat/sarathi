"""Context size and subagent handoff threshold monitor for Orchestra."""

from __future__ import annotations

import os
import pathlib
from typing import Any

DEFAULT_HANDOFF_THRESHOLD = 250_000
WARNING_THRESHOLD_FRACTION = 0.80


def resolve_handoff_threshold() -> int:
  """Resolves the active context handoff token threshold.

  Precedence:
  1. Environment variable ORCHESTRA_CONTEXT_HANDOFF_TOKENS.
  2. Local config file ~/.gemini/antigravity/context_handoff_tokens.
  3. Default 250,000 tokens.
  """
  env_val = os.environ.get("ORCHESTRA_CONTEXT_HANDOFF_TOKENS")
  if env_val:
    try:
      return int(env_val.strip())
    except ValueError:
      pass

  config_path = pathlib.Path.home() / ".gemini" / "antigravity" / "context_handoff_tokens"
  if config_path.is_file():
    try:
      with open(config_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        if line:
          return int(line)
    except Exception:
      pass

  return DEFAULT_HANDOFF_THRESHOLD


def get_context_status(
    conversation_id: str | None = None,
    context_tokens: int | None = None,
) -> dict[str, Any]:
  """Evaluates context size against handoff thresholds.

  Args:
    conversation_id: Optional ID of the conversation.
    context_tokens: Estimated total tokens in the active context.

  Returns:
    Dict with token metrics, utilization percentage, and recommendation.
  """
  threshold = resolve_handoff_threshold()
  tokens = context_tokens if context_tokens is not None else 0

  utilization = (tokens / threshold) if threshold > 0 else 0.0

  if utilization >= 1.0:
    recommendation = "handoff"
    message = (
        f"Context size ({tokens:,} tokens) has exceeded threshold ({threshold:,} tokens). "
        "Complete the current atomic edit, run tests, write HANDOFF.md, and return STATUS: HANDOFF."
    )
  elif utilization >= WARNING_THRESHOLD_FRACTION:
    recommendation = "warning"
    message = (
        f"Context size ({tokens:,} tokens) is approaching handoff threshold ({threshold:,} tokens). "
        "Finish assigned work promptly or prepare for state handoff."
    )
  else:
    recommendation = "continue"
    message = f"Context healthy ({tokens:,} / {threshold:,} tokens, {utilization * 100:.1f}%)."

  return {
      "conversation_id": conversation_id or "unknown",
      "context_tokens": tokens,
      "threshold_tokens": threshold,
      "utilization_pct": round(utilization * 100, 2),
      "recommendation": recommendation,
      "message": message,
  }
