"""Local telemetry ledger for Orchestra runs in Antigravity."""

from __future__ import annotations

import datetime
import json
import os
import pathlib
from typing import Any


def resolve_ledger_path() -> str:
  """Resolves the destination path for local orchestration telemetry."""
  # Prefer workspace-local .gemini directory if present
  workspace_gemini = pathlib.Path(".gemini")
  if workspace_gemini.is_dir():
    return str(workspace_gemini / "sarathi_telemetry.jsonl")

  # Default to user home Antigravity directory
  antigravity_dir = pathlib.Path.home() / ".gemini" / "antigravity"
  os.makedirs(antigravity_dir, exist_ok=True)
  return str(antigravity_dir / "sarathi_telemetry.jsonl")


def record_orchestration_event(
    task_tier: str,
    verification_outcome: str,
    conductor_model: str = "auto",
    subagents_spawned: int = 0,
    subagent_calls_offloaded: int = 0,
    test_violations_count: int = 0,
    duration_seconds: float = 0.0,
    details: str = "",
    session_id: str = "",
) -> dict[str, Any]:
  """Appends an orchestration milestone event to the local JSONL ledger.

  Args:
    task_tier: Complexity routing tier (tier_1_surgical, tier_2_standard, tier_3_architectural, research).
    verification_outcome: Final verification verdict (PASSED, FAILED, NOT_APPLICABLE).
    conductor_model: Identifier of the conductor model.
    subagents_spawned: Count of subagent workers/scouts invoked.
    subagent_calls_offloaded: Count of operations offloaded to subagents.
    test_violations_count: Detected assertion/suppression violations.
    duration_seconds: Duration in seconds.
    details: High-level task summary (no PII).
    session_id: Optional conversation ID.

  Returns:
    Dict containing record status and ledger path.
  """
  ledger_path = resolve_ledger_path()

  event = {
      "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "session_id": session_id or "unknown",
      "task_tier": task_tier,
      "verification_outcome": verification_outcome,
      "conductor_model": conductor_model,
      "subagents_spawned": subagents_spawned,
      "subagent_calls_offloaded": subagent_calls_offloaded,
      "test_violations_count": test_violations_count,
      "duration_seconds": round(duration_seconds, 2),
      "details": details[:300],
  }

  try:
    with open(ledger_path, "a", encoding="utf-8") as f:
      f.write(json.dumps(event) + "\n")
    return {
        "recorded": True,
        "ledger_path": ledger_path,
        "event": event,
    }
  except Exception as e:
    return {
        "recorded": False,
        "error": f"Failed to record event to ledger: {str(e)}",
        "ledger_path": ledger_path,
    }
