"""Medical imaging agent factory.

This module provides a factory function that creates a routed Agno agent
specialized in medical imaging analysis. The medical instructions live in
``skills/core/medical-image-analysis/SKILL.md`` and are injected dynamically
by the skill router.
"""

import sys
from pathlib import Path
from typing import Optional

from agno.tools.pubmed import PubmedTools

from agent_config import create_routed_agent, discover_tools

# Windows-specific asyncio policy for compatibility
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOTS = [REPO_ROOT / "skills" / "core"]
PROMPT_PATH = REPO_ROOT / "skills" / "core" / "medical-image-analysis" / "SKILL.md"


def _discover_web_fetcher() -> list:
    """Discover the web-fetcher tool if enabled and its dependencies are present.

    Returns:
        A list containing the web_fetch tool callable, or an empty list if the
        tool is disabled or cannot be imported.
    """
    import os

    if os.environ.get("ENABLE_WEB_FETCHER", "true").lower() not in ("true", "1", "yes"):
        return []

    tools = discover_tools(SKILL_ROOTS[0])
    if "web_fetch" in tools:
        return [tools["web_fetch"]]
    return []


def create_medical_imaging_agent(model_id: Optional[str] = None):
    """Create a routed medical imaging agent.

    Args:
        model_id: OpenAI model identifier. Defaults to the configured default model.

    Returns:
        A RoutedAgent instance configured as a medical imaging expert.
    """
    from models import get_model_id

    resolved_model_id = model_id or get_model_id()
    # OpenAIResponses expects the model name without the "openai:" prefix.
    model_name = resolved_model_id.split(":", 1)[-1]

    extra_tools: list = [
        {"type": "web_search_preview"},
        PubmedTools(),
    ]
    extra_tools.extend(_discover_web_fetcher())

    return create_routed_agent(
        name="Medical Imaging and Search Expert",
        model_id=model_name,
        skill_roots=SKILL_ROOTS,
        extra_tools=extra_tools,
        debug_mode=True,
        exponential_backoff=True,
    )
