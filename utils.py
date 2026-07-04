"""General utility helpers for Corpus Analyzer."""

import copy
import json
from typing import Any, Dict, List, Optional

import streamlit as st
from agno.utils.log import logger


async def add_message(
    role: str,
    content: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    intermediate_steps_displayed: bool = False,
    images: Optional[List[Any]] = None,
) -> None:
    """Safely add a message to the session state."""
    if role == "user":
        logger.info(f"User: {content}")
    else:
        logger.info(f"Assistant: {content}")

    preserved_tool_calls = None
    if tool_calls:
        try:
            preserved_tool_calls = copy.deepcopy(tool_calls)
        except Exception as e:
            logger.warning(f"Could not deep copy tool calls: {e}")
            preserved_tool_calls = []

    message_data = {
        "role": role,
        "content": content,
        "tool_calls": preserved_tool_calls,
        "intermediate_steps_displayed": intermediate_steps_displayed,
    }

    if images:
        serialized_images = []
        for img in images:
            if hasattr(img, "model_dump"):
                serialized_images.append(img.model_dump(exclude_none=True))
            elif isinstance(img, dict):
                serialized_images.append(img)
            else:
                serialized_images.append(
                    {
                        "id": getattr(img, "id", None),
                        "url": getattr(img, "url", None),
                        "content": getattr(img, "content", None),
                        "mime_type": getattr(img, "mime_type", "image/png"),
                        "alt_text": getattr(img, "alt_text", ""),
                    }
                )
        message_data["images"] = serialized_images

    st.session_state["messages"].append(message_data)


def is_json(myjson: Any) -> bool:
    """Check if a string is valid JSON."""
    if not isinstance(myjson, str):
        return False
    try:
        json.loads(myjson)
    except (ValueError, TypeError):
        return False
    return True


def display_tool_calls(tool_calls_container, tools: Any) -> None:
    """Display tool calls in a streamlit container with expandable sections.

    Args:
        tool_calls_container: Streamlit container to display the tool calls.
        tools: List of tool call dictionaries or objects.
    """
    if tools is None:
        logger.debug("No tools provided to display_tool_calls")
        return

    if tool_calls_container is None:
        logger.warning("No container provided to display_tool_calls")
        return

    try:
        with tool_calls_container.container():
            if isinstance(tools, dict):
                tools = [tools]
            elif not isinstance(tools, list):
                try:
                    tools = list(tools)
                except (TypeError, ValueError):
                    logger.warning(f"Unexpected tools format: {type(tools)}")
                    return

            if not tools:
                return

            for tool_call in tools:
                if tool_call is None:
                    continue

                tool_name = getattr(tool_call, "tool_name", None) or getattr(
                    tool_call, "name", "Unknown Tool"
                )
                tool_args = getattr(tool_call, "tool_args", None) or getattr(tool_call, "args", {})
                content = getattr(tool_call, "content", None)

                expander_title = f"Tool: {tool_name}"
                with st.expander(expander_title, expanded=False):
                    if tool_args is not None:
                        st.json(tool_args)
                    if content is not None:
                        st.markdown("**Results:**")
                        if isinstance(content, str) and is_json(content):
                            st.json(json.loads(content))
                        else:
                            st.write(content)
    except Exception as e:
        logger.error(f"Error displaying tool calls: {e}")
        tool_calls_container.error("Failed to display tool results")
