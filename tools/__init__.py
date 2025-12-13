from pathlib import Path
from typing import Optional
import sys
import os

# Add the parent directory to the path to import necessary modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.tools import Toolkit
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from .gptimage1 import GPTImage1Tools

cwd = Path(__file__).parent.parent.resolve()
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(exist_ok=True, parents=True)


def get_toolkit(tool_name: str) -> Optional[Toolkit]:
    if tool_name == "file_tools":
        return FileTools(base_dir=cwd)
    elif tool_name == "shell_tools":
        return ShellTools()
    elif tool_name == "gptimage1":
        return GPTImage1Tools()

    return None
