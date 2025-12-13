import os
from os import getenv
from typing import Literal, Optional, Union
from uuid import uuid4
import json
import base64
import os.path
import sys
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

# Import OpenAI client safely
try:
    from openai import OpenAI
    # We don't need to import ImagesResponse directly to avoid pickling issues
except ImportError:
    raise ImportError("`openai` not installed. Please install using `pip install openai`")


class GPTImage1Tools(Toolkit):
    def __init__(
        self,
        model: str = "gpt-image-1",
        n: int = 1,
        size: Optional[Literal["1024x1024", "1792x1024", "1024x1792"]] = "1024x1024",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name="gptimage1", **kwargs)

        self.model = model
        self.n = n
        self.size = size
        self.api_key = api_key or getenv("OPENAI_API_KEY")

        # Validations
        if model != "gpt-image-1":
            raise ValueError("Invalid model. Please use 'gpt-image-1'.")
        if size not in ["1024x1024", "1792x1024", "1024x1792"]:
            raise ValueError(
                "Invalid size. Please choose from '1024x1024', '1792x1024', '1024x1792'."
            )
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Invalid number of images. Please provide a positive integer.")

        if not self.api_key:
            logger.error("OPENAI_API_KEY not set. Please set the OPENAI_API_KEY environment variable.")

        self.register(self.create_image)
        # TODO:
        # - Add support for response_format
        # - Add support for saving images

    async def create_image(self, agent: Union[Agent, Team], prompt: str) -> str:
        """Use this function to generate an image for a prompt.

        Args:
            prompt (str): A text description of the desired image.

        Returns:
            str: str: A message indicating if the image has been generated successfully or an error message.
        """
        if not self.api_key:
            return "Please set the OPENAI_API_KEY"

        try:
            client = OpenAI(api_key=self.api_key)
            log_debug(f"Generating image using prompt: {prompt}")
            log_debug(f"API parameters: model={self.model}, n={self.n}, size={self.size}")
            
            # Call the OpenAI API with the supported parameters for gpt-image-1
            response = client.images.generate(
                prompt=prompt,
                model=self.model,
                n=self.n,
                size=self.size,
            )
            log_debug("Image generated successfully")

            # Process the response and handle both URL and base64 formats
            response_str = ""
            if response.data:
                for img in response.data:
                    # Check if the image has a URL (unlikely for gpt-image-1)
                    if hasattr(img, 'url') and img.url:
                        # Create a unique ID for this image
                        img_id = str(uuid4())
                        
                        # Create the ImageArtifact with all required fields
                        image_artifact = Image(
                            id=img_id,  # Required by Media base class
                            url=img.url,  # Remote URL of the image
                            content=None,  # We don't have the content for URL-based images
                            mime_type='image/png',  # Assuming PNG, adjust if needed
                            alt_text=prompt[:200],  # Use first 200 chars of prompt as alt text
                            original_prompt=prompt,
                            revised_prompt=getattr(img, 'revised_prompt', None)
                        )
                        
                        # Add the image to the agent
                        agent.add_image(image_artifact)
                        
                        # Import add_message function to display image in chat
                        try:
                            # Import the add_message function from utils
                            #import sys
                            #import os
                            #parent_dir = os.path.dirname(os.path.dirname(__file__))
                            #if parent_dir not in sys.path:
                            #    sys.path.append(parent_dir)
                            from utils import add_message
                            
                            # Add message with image to chat interface
                            await add_message("assistant", f"I've generated an image based on your request: {prompt}", images=[image_artifact])
                        except Exception as import_error:
                            log_debug(f"Could not import add_message: {import_error}")
                        
                        response_str += f"Image has been generated successfully and displayed in the chat.\n"
                    # Handle base64-encoded images (typical for gpt-image-1)
                    elif hasattr(img, 'b64_json') and img.b64_json:
                        # Save the base64 image to a temporary file
                        try:
                            # Create a temporary directory if it doesn't exist
                            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'generated_images')
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            # Generate a unique filename
                            img_id = str(uuid4())
                            img_path = os.path.join(temp_dir, f"{img_id}.png")
                            
                            # Decode and save the image
                            img_data = base64.b64decode(img.b64_json)
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            
                            # Create URLs for the local file
                            file_url = f"file://{img_path}"
                            # Also create a sandbox URL format that will be recognized by our UI
                            sandbox_url = f"sandbox:/mnt/data/{img_id}.png"
                            
                            # For the ImageArtifact, we'll only set the URL and not the binary content
                            # to avoid serialization issues. The image is already saved to disk.
                            image_artifact = Image(
                                id=img_id,  # Required by Media base class
                                url=file_url,  # Remote location for file
                                content=None,  # Don't include binary content to avoid serialization issues
                                mime_type='image/png',  # MIME type for PNG
                                alt_text=prompt[:200],  # Use first 200 chars of prompt as alt text
                                original_prompt=prompt,
                                revised_prompt=getattr(img, 'revised_prompt', None)
                            )
                            
                            # Import add_message function to display image in chat
                            try:
                                # Import the add_message function from utils
                                #import sys
                                #import os
                                #parent_dir = os.path.dirname(os.path.dirname(__file__))
                                #if parent_dir not in sys.path:
                                #    sys.path.append(parent_dir)
                                from utils import add_message
                                
                                # Add message with image to chat interface
                                await add_message("assistant", f"I've generated an image based on your request: {prompt} \n The image is saved to: {img_path}", images=[image_artifact])
                            except Exception as import_error:
                                log_debug(f"Could not import add_message: {import_error}")
                            
                            # Format the response
                            response_str += f"Image has been generated successfully and displayed in the chat.\n"
                            response_str += f"The image captures: {prompt}\n"
                            response_str += f"The image is saved to: {img_path}\n"
                            log_debug(f"Saved base64 image to {img_path}")
                            
                        except Exception as save_error:
                            log_debug(f"Failed to save base64 image: {save_error}")
                            response_str += "Image was generated but could not be saved locally.\n"
            
            return response_str or "No images were generated"
        except Exception as e:
            error_msg = f"Failed to generate image: {e}"
            logger.error(error_msg)
            
            # Get more detailed error information if available
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                try:
                    error_details = json.loads(e.response.text)
                    if 'error' in error_details:
                        error_msg += f"\nDetails: {error_details['error'].get('message', '')}"
                        logger.error(f"API Error details: {error_details}")
                except Exception:
                    pass
                    
            return f"Error: {error_msg}"
