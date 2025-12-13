"""
Agent module initialization file.
This file dynamically exports all agent factory functions from the agents package.
"""

import os
import importlib
import inspect
from typing import Optional

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model

# Dynamically discover and import agent modules
agent_modules = {}
agent_factory_funcs = {}
current_dir = os.path.dirname(os.path.abspath(__file__))

# Find all potential agent modules (files ending with _agent.py)
for filename in os.listdir(current_dir):
    if filename.endswith('_agent.py') and filename != '__init__.py':
        module_name = filename[:-3]  # Remove .py extension
        
        # Skip commented out modules
        #if module_name == 'crawler_agent':
        #    continue
            
        try:
            # Import the module
            module = importlib.import_module(f'.{module_name}', package='agents')
            agent_modules[module_name] = module
            
            # Find factory functions (those starting with create_)
            for name, obj in inspect.getmembers(module):
                if name.startswith('create_') and inspect.isfunction(obj):
                    agent_factory_funcs[name] = obj
                    # Make the function available at the package level
                    globals()[name] = obj
        except ImportError as e:
            print(f"Warning: Could not import agent module {module_name}: {e}")

# Dynamically build __all__ list from discovered factory functions
__all__ = list(agent_factory_funcs.keys()) + ["get_agent"]

def get_agent(
    agent_name: str, model: Model, memory: MemoryManager, knowledge: Knowledge,
    debug_mode: bool = True
) -> Optional[Agent]:
    """
    Get an agent by name.
    
    Args:
        agent_name: The name of the agent to get
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        debug_mode: Whether to enable debug mode for the agent
        
    Returns:
        An Agent instance if the agent_name is recognized, None otherwise
    """
    # Dynamically build agent factories dictionary
    agent_factories = {}
    
    # Map agent names to their factory functions
    for func_name, func in agent_factory_funcs.items():
        # Extract agent name from function name (remove 'create_' and '_agent' if present)
        name = func_name.replace('create_', '', 1)
        if name.endswith('_agent'):
            name = name[:-6]
        agent_factories[name] = func
    
    # Get the factory function for the requested agent
    factory = agent_factories.get(agent_name)
    
    # If the factory exists, create and return the agent
    if factory:
        # Enable debug mode specifically for MCP agents to show raw MCP responses
        if agent_name in ["airbnb", "onlyfy_mcp"]:
            return factory(model, memory, knowledge, debug_mode=debug_mode)
        else:
            try:
                # Try with debug_mode parameter first
                return factory(model, memory, knowledge, debug_mode=debug_mode)
            except TypeError:
                # Fall back to standard parameters if debug_mode isn't supported
                return factory(model, memory, knowledge)
    
    # If no factory exists for the agent name, return None
    return None