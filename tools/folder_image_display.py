import os
import sys
from typing import List, Optional, Union
from pathlib import Path
import asyncio

from agno.agent import Agent
from agno.media import Image
from agno.team.team import Team
from agno.tools import Toolkit
from agno.utils.log import log_debug, logger

# Windows-specific event loop policy for asyncio compatibility
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class FolderImageDisplayTools(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(name="folder_image_display", **kwargs)
        self.register(self.display_images_from_folder)
        self.register(self.list_images_in_folder)

    async def display_images_from_folder(
        self, 
        agent: Union[Agent, Team], 
        folder_path: str,
        image_extensions: Optional[List[str]] = None,
        max_images: Optional[int] = 10
    ) -> str:
        """Display images from a specified folder directly in the chat interface.

        Args:
            folder_path (str): Path to the folder containing images
            image_extensions (List[str], optional): List of image extensions to include. 
                                                   Defaults to ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
            max_images (int, optional): Maximum number of images to display. Defaults to 10.

        Returns:
            str: A message indicating the result of the operation
        """
        if image_extensions is None:
            image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        
        # Convert to lowercase for case-insensitive matching
        image_extensions = [ext.lower() for ext in image_extensions]
        
        try:
            # Validate folder path
            folder_path = os.path.abspath(folder_path)
            if not os.path.exists(folder_path):
                return f"Error: Folder '{folder_path}' does not exist."
            
            if not os.path.isdir(folder_path):
                return f"Error: '{folder_path}' is not a directory."
            
            # Find image files in the folder
            image_files = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file_name)[1][1:].lower()  # Remove dot and convert to lowercase
                    if file_ext in image_extensions:
                        image_files.append(file_path)
            
            if not image_files:
                return f"No image files found in '{folder_path}' with extensions: {', '.join(image_extensions)}"
            
            # Sort files for consistent ordering
            image_files.sort()
            
            # Limit number of images if specified
            total_files_count = len(image_files)
            if max_images and len(image_files) > max_images:
                image_files = image_files[:max_images]
                truncated_msg = f" (showing first {max_images} of {total_files_count} image files)"
            else:
                truncated_msg = ""
            
            # Create ImageArtifact objects for each image
            image_artifacts = []
            for img_path in image_files:
                try:
                    # Create ImageArtifact with proper file URL format
                    img_name = os.path.basename(img_path)
                    # Convert to absolute path and format as proper file URL
                    abs_path = os.path.abspath(img_path).replace("\\", "/")
                    file_url = f"file:///{abs_path}"
                    
                    image_artifact = Image(
                        id=f"folder_img_{img_name}",
                        url=file_url,
                        content=None,  # Don't load binary content to avoid serialization issues
                        mime_type=self._get_mime_type(img_path),
                        alt_text=f"Image from folder: {img_name}",
                        original_prompt=f"Display image from folder: {folder_path}"
                    )
                    
                    # Add to agent
                    agent.add_image(image_artifact)
                    image_artifacts.append(image_artifact)
                    
                except Exception as img_error:
                    log_debug(f"Error processing image {img_path}: {img_error}")
                    continue
            
            if not image_artifacts:
                return f"Error: Could not process any images from '{folder_path}'"
            
            # Import add_message function to display images in chat
            try:
                # Import the add_message function from utils
                parent_dir = os.path.dirname(os.path.dirname(__file__))
                if parent_dir not in sys.path:
                    sys.path.append(parent_dir)
                from utils import add_message
                
                # Create descriptive message
                message_text = f"Displaying {len(image_artifacts)} images from folder: {folder_path}{truncated_msg}"
                
                # Add message with images to chat interface
                await add_message("assistant", message_text, images=image_artifacts)
                
                return f"Successfully displayed {len(image_artifacts)} images from '{folder_path}'{truncated_msg}"
                
            except Exception as import_error:
                log_debug(f"Could not import add_message: {import_error}")
                return f"Images processed but could not display in chat: {import_error}"
                
        except Exception as e:
            error_msg = f"Error displaying images from folder '{folder_path}': {e}"
            logger.error(error_msg)
            return error_msg

    def list_images_in_folder(
        self, 
        agent: Union[Agent, Team], 
        folder_path: str,
        image_extensions: Optional[List[str]] = None
    ) -> str:
        """List all image files in a specified folder without displaying them.

        Args:
            folder_path (str): Path to the folder containing images
            image_extensions (List[str], optional): List of image extensions to include. 
                                                   Defaults to ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']

        Returns:
            str: A formatted list of image files found in the folder
        """
        if image_extensions is None:
            image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        
        # Convert to lowercase for case-insensitive matching
        image_extensions = [ext.lower() for ext in image_extensions]
        
        try:
            # Validate folder path
            folder_path = os.path.abspath(folder_path)
            if not os.path.exists(folder_path):
                return f"Error: Folder '{folder_path}' does not exist."
            
            if not os.path.isdir(folder_path):
                return f"Error: '{folder_path}' is not a directory."
            
            # Find image files in the folder
            image_files = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file_name)[1][1:].lower()
                    if file_ext in image_extensions:
                        # Get file size
                        file_size = os.path.getsize(file_path)
                        size_mb = file_size / (1024 * 1024)
                        image_files.append((file_name, size_mb))
            
            if not image_files:
                return f"No image files found in '{folder_path}' with extensions: {', '.join(image_extensions)}"
            
            # Sort files alphabetically
            image_files.sort(key=lambda x: x[0])
            
            # Format the response
            response = f"Found {len(image_files)} image files in '{folder_path}':\n\n"
            for file_name, size_mb in image_files:
                response += f"• {file_name} ({size_mb:.2f} MB)\n"
            
            return response
            
        except Exception as e:
            error_msg = f"Error listing images in folder '{folder_path}': {e}"
            logger.error(error_msg)
            return error_msg

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension."""
        ext = os.path.splitext(file_path)[1][1:].lower()
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/png')
