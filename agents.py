"""
Agents module for the Universal Agent Interface.
This module provides a factory function to get an agent by name.

This file is kept for backward compatibility. The actual implementation
has been moved to the agents package.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import SerperSearchTool
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment
cwd = Path(__file__).parent.resolve()
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(exist_ok=True, parents=True)

import dotenv
dotenv.load_dotenv(override=True)

# Import and re-export the get_agent function from the agents package
from agents import get_agent

# For backward compatibility, explicitly export the get_agent function
__all__ = ["get_agent"]
