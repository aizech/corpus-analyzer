"""Discover and load skill-specific tools for routed agents.

Skills may expose Agno tools in a ``tools/`` subdirectory. This module walks the
skills tree, imports those tools, and exposes them to ``create_agent`` and the
CLI without hard-coding import paths.
"""

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from agno.tools.function import Function


def _tool_dirs(skills_dir: str | Path) -> list[Path]:
    """Return every ``tools/`` subdirectory inside ``skills_dir``."""
    base = Path(skills_dir)
    dirs: list[Path] = []
    if not base.exists():
        return dirs
    for skill_dir in sorted(d for d in base.iterdir() if d.is_dir()):
        tools_dir = skill_dir / "tools"
        if tools_dir.is_dir():
            dirs.append(tools_dir)
    return dirs


def _is_tool(obj: Any) -> bool:
    """Return True if ``obj`` looks like an Agno ``@tool`` Function."""
    # Agno's @tool decorator returns a Function dataclass that wraps the original callable.
    return isinstance(obj, Function)


def _add_to_sys_path(path: Path) -> None:
    """Add ``path`` to ``sys.path`` idempotently."""
    p = str(path)
    if p not in sys.path:
        sys.path.insert(0, p)


def load_tool_module(skill_name: str, module_name: str, skills_dir: str | Path) -> ModuleType:
    """Load a single Python module from a skill's ``tools/`` directory.

    Skill folder names may contain hyphens, which are valid directory names but
    invalid Python package names. This function works around that by loading the
    module directly from its file path.

    Args:
        skill_name: Name of the skill folder (e.g. ``web-fetcher``).
        module_name: Stem of the Python file inside the skill's ``tools/`` dir
            (e.g. ``web_fetch``).
        skills_dir: Directory containing skill folders.

    Returns:
        The loaded module.

    Raises:
        FileNotFoundError: If the skill or module file does not exist.
        ImportError: If the module cannot be imported.
    """
    tools_dir = Path(skills_dir) / skill_name / "tools"
    module_path = tools_dir / f"{module_name}.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Tool module not found: {module_path}")

    _add_to_sys_path(tools_dir)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def discover_tools(skills_dir: str | Path) -> dict[str, Callable[..., Any]]:
    """Import every tool module found under skill ``tools/`` directories.

    Each ``tools/`` directory is added to ``sys.path`` so sibling imports inside
    the skill work (e.g. ``from web_fetch_lib import ...``). Every ``.py`` file
    is imported and any callables decorated with ``@tool`` are collected.

    Args:
        skills_dir: Directory containing skill folders.

    Returns:
        Mapping of ``tool_name -> callable`` for all discovered tools.
    """
    tools: dict[str, Callable[..., Any]] = {}
    loaded_modules: set[str] = set()

    for tools_dir in _tool_dirs(skills_dir):
        _add_to_sys_path(tools_dir)
        for py_file in sorted(tools_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            module_name = py_file.stem
            try:
                module = load_tool_module(tools_dir.parent.name, module_name, skills_dir)
            except Exception:
                # Skip tool modules that fail to import (e.g. missing optional deps).
                continue
            loaded_modules.add(module_name)

            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if _is_tool(obj):
                    # Prefer the function name over the tool registry name so
                    # downstream code can reference tools predictably.
                    name = getattr(obj, "__name__", attr_name)
                    tools[name] = obj

    return tools


def load_tools_for_skills(skills_dir: str | Path) -> list[Callable[..., Any]]:
    """Return all discovered Agno tool callables for the given skills directory.

    Args:
        skills_dir: Directory containing skill folders.

    Returns:
        Ordered list of tool callables ready for ``Agent(tools=...)``.
    """
    return list(discover_tools(skills_dir).values())
