"""
Load the Knowledge Base for the Halo Agent Interface
"""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from halo import halo_knowledge
from dotenv import load_dotenv

load_dotenv()

# Create a Rich console for enhanced output
console = Console()


def load_knowledge(recreate: bool = False):
    """
    Load the Halo Agent Interface knowledge base.

    Args:
        recreate (bool, optional): Whether to recreate the knowledge base.
            Defaults to False.
    """
    with Progress(
        SpinnerColumn(), TextColumn("[bold blue]{task.description}"), console=console
    ) as progress:
        task = progress.add_task(
            "Loading HALO knowledge...", total=None
        )

        try:
            # If recreate is True, try to clear the vector database first
            if recreate:
                console.print("[yellow]Recreating knowledge base...")
                try:
                    # Try to reset the vector database
                    if hasattr(halo_knowledge, 'reset_vector_db'):
                        halo_knowledge.reset_vector_db()
                    # Delete all files in the knowledge directory
                    knowledge_dir = halo_knowledge.knowledge_dir
                    for file_path in knowledge_dir.glob("*.*"):
                        console.print(f"Removing {file_path}")
                        file_path.unlink()
                except Exception as e:
                    console.print(f"[red]Warning: Error during cleanup: {e}")
            else:
                # Just get the knowledge directory
                knowledge_dir = halo_knowledge.knowledge_dir
            
            # Add a sample document if no documents exist or recreate is True
            if recreate or not any(knowledge_dir.glob("*.*")):
                console.print("Adding sample knowledge document...")
                sample_content = """
# Halo Agent Interface (HALO)

The Halo Agent Interface (HALO) is a multi-modal interface for interacting with 
multiple AI agents using a single entrypoint. It provides a unified way to coordinate 
different specialized agents to solve complex tasks.

## Key Features

- Orchestrates multiple specialized agents
- Provides a single interface for all agent interactions
- Supports knowledge base for storing and retrieving information
- Integrates with various tools like web search, reasoning, and more
- Handles complex requests by breaking them down into manageable tasks

## Architecture

HALO uses a team-based approach where a coordinator agent delegates tasks to specialized 
agents based on their capabilities. The system includes:

1. A memory system for maintaining conversation context
2. A knowledge base for storing domain-specific information
3. A toolkit system for accessing external tools and APIs
4. A team coordination mechanism for managing agent interactions
                """
                # Write the file first
                with open(knowledge_dir / "halo_overview.md", "w", encoding="utf-8") as f:
                    f.write(sample_content)
                
                console.print("Sample document created successfully")

            # Load the knowledge base with proper error handling
            console.print("Loading knowledge base")
            # Force recreate if we're explicitly asked to
            halo_knowledge.load(recreate=recreate)
            progress.update(task, completed=True)
            
        except ValueError as ve:
            if "Field 'vector' not found in target schema" in str(ve):
                console.print("[red]Schema mismatch detected. Attempting to fix...")
                # Try to fix by manually deleting the database files and recreating
                try:
                    # Find and remove the LanceDB database files
                    import shutil
                    import os
                    
                    # Common locations for LanceDB files
                    possible_db_paths = [
                        Path.home() / "halo_knowledge",
                        Path.cwd() / "halo_knowledge",
                        Path(os.environ.get("USERPROFILE", "")) / "halo_knowledge"
                    ]
                    
                    for db_path in possible_db_paths:
                        if db_path.exists():
                            console.print(f"[yellow]Removing database directory: {db_path}")
                            try:
                                shutil.rmtree(db_path)
                                console.print(f"[green]Successfully removed {db_path}")
                            except Exception as rm_err:
                                console.print(f"[red]Failed to remove {db_path}: {rm_err}")
                    
                    # Now try loading again with recreate=True
                    console.print("[yellow]Attempting to reload knowledge base...")
                    halo_knowledge.load(recreate=True)
                    progress.update(task, completed=True)
                    console.print("[green]Knowledge base recreated successfully!")
                except Exception as inner_e:
                    console.print(f"[red]Failed to recreate knowledge base: {inner_e}")
                    raise
            else:
                console.print(f"[red]Error loading knowledge base: {ve}")
                raise
        except Exception as e:
            console.print(f"[red]Error: {e}")
            raise

    # Display success message in a panel
    console.print(
        Panel.fit(
            "[bold green]HALO interface knowledge loaded successfully!",
            title="Knowledge Loaded",
        )
    )


if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Load the Halo Agent Interface knowledge base")
    parser.add_argument("--recreate", action="store_true", help="Recreate the knowledge base")
    args = parser.parse_args()
    
    # Load the knowledge base with the specified options
    load_knowledge(recreate=args.recreate)
