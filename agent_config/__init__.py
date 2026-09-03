"""Agent configuration, skill routing, and tool discovery for Corpus Analyzer."""

from agent_config.agent_config import (
    RoutedAgent,
    create_agent,
    create_routed_agent,
    get_model_id,
)
from agent_config.skill_router import (
    DEFAULT_MAX_INSTRUCTION_CHARS,
    DEFAULT_MAX_SKILLS,
    RoutingResult,
    SkillRecord,
    compose_routed_prompt,
    discover_catalog,
    route_prompt,
    select_candidates,
)
from agent_config.tool_registry import (
    discover_tools,
    load_tool_module,
    load_tools_for_skills,
)

__all__ = [
    "RoutedAgent",
    "create_agent",
    "create_routed_agent",
    "get_model_id",
    "DEFAULT_MAX_INSTRUCTION_CHARS",
    "DEFAULT_MAX_SKILLS",
    "RoutingResult",
    "SkillRecord",
    "compose_routed_prompt",
    "discover_catalog",
    "route_prompt",
    "select_candidates",
    "discover_tools",
    "load_tool_module",
    "load_tools_for_skills",
]
