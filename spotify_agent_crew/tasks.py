"""Task stubs for the crew workflow.

Define high-level tasks the crew will perform. These are placeholders and do
not implement any business logic yet.
"""

from __future__ import annotations
from typing import Any, Dict


def analyze_prompt(prompt: str) -> Dict[str, Any]:  # pragma: no cover - placeholder
    """Analyze the user prompt and return a plan (not implemented)."""
    raise NotImplementedError("analyze_prompt is not implemented yet.")


def curate_playlist(plan: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - placeholder
    """Use the plan to curate a playlist (not implemented)."""
    raise NotImplementedError("curate_playlist is not implemented yet.")
