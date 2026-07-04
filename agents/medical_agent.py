"""Medical imaging agent factory.

This module provides a factory function that creates an Agno agent specialized in
medical imaging analysis. The agent prompt is loaded from an external Markdown file.
"""

import sys
from pathlib import Path
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.pubmed import PubmedTools

# Windows-specific asyncio policy for compatibility
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


PROMPT_PATH = Path(__file__).parent / "medical_agent_prompt.md"


def _load_prompt() -> str:
    """Load the medical agent prompt from the adjacent Markdown file."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Medical agent prompt not found: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def create_medical_imaging_agent(model_id: Optional[str] = None) -> Agent:
    """Create a medical imaging agent.

    Args:
        model_id: OpenAI model identifier. Defaults to the configured default model.

    Returns:
        An Agent instance configured as a medical imaging expert.
    """
    from models import get_model_id

    resolved_model_id = model_id or get_model_id()
    # OpenAIResponses expects the model name without the "openai:" prefix.
    model_name = resolved_model_id.split(":", 1)[-1]

    return Agent(
        name="Medical Imaging and Search Expert",
        role="Specialized medical imaging radiologist for educational analysis",
        model=OpenAIResponses(id=model_name),
        instructions=_load_prompt(),
        tools=[
            {"type": "web_search_preview"},
            PubmedTools(),
        ],
        description="You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging.",
        markdown=True,
        debug_mode=True,
        exponential_backoff=True,
    )
