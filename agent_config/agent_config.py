"""Centralized agent configuration and factory functions."""

import os
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from dotenv import load_dotenv

from agent_config.skill_router import (
    DEFAULT_MAX_INSTRUCTION_CHARS,
    DEFAULT_MAX_SKILLS,
    compose_routed_prompt,
    discover_catalog,
    route_prompt,
)

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = os.getenv("OPENAI_MODEL") or "gpt-5.2"
DEFAULT_FALLBACK_MODEL = os.getenv("OPENAI_FALLBACK_MODEL") or "gpt-4o-mini"
DEFAULT_SKILLS_DIR = os.getenv("AGENT_SKILLS_DIR", str(REPO_ROOT / "skills" / "core"))
DEFAULT_SKILL_ROOTS = [
    REPO_ROOT / "skills" / "core",
    REPO_ROOT / "skills" / "extra",
]


def get_model_id(use_fallback: bool = False) -> str:
    """Return the model ID from env.

    Args:
        use_fallback: If True, return the fallback model instead of the primary.

    The primary default is gpt-5.2; the fallback default is gpt-4o-mini.
    """
    if use_fallback:
        return DEFAULT_FALLBACK_MODEL
    return DEFAULT_MODEL


def create_agent(
    extra_tools: list | None = None,
    model_id: str | None = None,
    name: str | None = None,
    instructions: list[str] | None = None,
    **agent_kwargs,
) -> Agent:
    """Create a standard CLI-style Agno agent with the configured model and tools."""
    tools: list = []
    if extra_tools:
        tools.extend(extra_tools)

    kwargs: dict = dict(agent_kwargs)
    if name:
        kwargs["name"] = name
    if instructions:
        kwargs["instructions"] = instructions

    return Agent(
        model=OpenAIResponses(id=model_id or get_model_id()),
        tools=tools,
        markdown=True,
        **kwargs,
    )


class RoutedAgent:
    """Run an Agno agent after selecting relevant active skill instructions."""

    def __init__(
        self,
        agent: Agent,
        skill_roots: list[str | Path],
        *,
        model_id: str,
        max_skills: int = DEFAULT_MAX_SKILLS,
        max_instruction_chars: int = DEFAULT_MAX_INSTRUCTION_CHARS,
    ) -> None:
        self._agent = agent
        self._catalog = discover_catalog(skill_roots)
        self._model_id = model_id
        self._max_skills = max_skills
        self._max_instruction_chars = max_instruction_chars

    def __getattr__(self, name: str):
        return getattr(self._agent, name)

    def _routed_prompt(self, prompt: str) -> str:
        result = route_prompt(
            prompt,
            self._catalog,
            model_id=self._model_id,
            max_skills=self._max_skills,
        )
        return compose_routed_prompt(
            prompt,
            result,
            max_chars=self._max_instruction_chars,
        )

    def run(self, prompt: str, *args, **kwargs):
        return self._agent.run(self._routed_prompt(prompt), *args, **kwargs)

    def print_response(self, prompt: str, *args, **kwargs):
        return self._agent.print_response(self._routed_prompt(prompt), *args, **kwargs)


def create_routed_agent(
    *,
    skill_roots: list[str | Path] | None = None,
    model_id: str | None = None,
    **kwargs,
) -> RoutedAgent:
    """Create an agent that routes each request through active skill metadata."""
    roots = skill_roots or DEFAULT_SKILL_ROOTS
    selected_model = model_id or get_model_id()
    agent = create_agent(model_id=selected_model, **kwargs)
    return RoutedAgent(agent, roots, model_id=selected_model)
