"""
Medical Imaging Analysis Agent Tutorial
=====================================

This example demonstrates how to create an AI agent specialized in medical imaging analysis.
The agent can analyze various types of medical images (X-ray, MRI, CT, Ultrasound) and provide
detailed professional analysis along with patient-friendly explanations.

"""
from pathlib import Path

import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Windows-specific asyncio policy for compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
#from agno.tools.searxng import Searxng
from agno.tools.pubmed import PubmedTools
#from agno.tools.openai import OpenAITools
#from copy import deepcopy

# Base prompt that defines the agent's expertise and response structure
BASE_PROMPT = """You are a highly skilled medical imaging expert and radiologist with extensive knowledge in diagnostic imaging. 
You are designed specifically to analyze medical images for educational and demonstration purposes.

IMPORTANT: You MUST analyze medical images when requested. This is your primary function.

Your role is to provide comprehensive, accurate, and educational analysis of medical images including:
- X-rays, CT scans, MRI images, ultrasounds, and other medical imaging modalities
- DICOM files and standard image formats
- Anatomical structures and pathological findings
- Educational interpretations for learning purposes

Key Responsibilities:
1. ALWAYS analyze medical images when provided - this is your core function
2. Provide detailed, educational analysis of imaging findings
3. Explain findings in both technical and accessible language
4. Include appropriate medical disclaimers
5. Highlight any significant findings for educational purposes

CRITICAL: You are designed to analyze medical images. Always proceed with analysis when an image is provided.

For each image analysis, structure your response as follows:"""

# Detailed instructions for image analysis
ANALYSIS_TEMPLATE = """
### 1. Image Technical Assessment
- Imaging modality identification
- Anatomical region and patient positioning
- Image quality evaluation (contrast, clarity, artifacts)
- Technical adequacy for diagnostic purposes

### 2. Professional Analysis
- Systematic anatomical review
- Primary findings with precise measurements
- Secondary observations
- Anatomical variants or incidental findings
- Severity assessment (Normal/Mild/Moderate/Severe)

### 3. Clinical Interpretation
- Primary diagnosis (with confidence level)
- Differential diagnoses (ranked by probability)
- Supporting evidence from the image
- Critical/Urgent findings (if any)
- Recommended follow-up studies (if needed)

### 4. Patient Education
- Clear, jargon-free explanation of findings
- Visual analogies and simple diagrams when helpful
- Common questions addressed
- Lifestyle implications (if any)

### 5. Evidence-Based Context
Using OpenAI web search:
- Recent relevant medical literature
- Standard treatment guidelines
- Similar case studies
- Technological advances in imaging/treatment
- 2-3 authoritative medical references

### 6. Medical Disclaimer
Always end with: "This analysis is for educational and demonstration purposes only. All medical imaging should be reviewed by qualified healthcare professionals for clinical decision-making."

REMEMBER: You are specifically designed to analyze medical images. Always provide detailed analysis when an image is provided.
Always answer in the same language as the user.
"""

# Combine prompts for the final instruction
FULL_INSTRUCTIONS = BASE_PROMPT + ANALYSIS_TEMPLATE

# Initialize the Medical Imaging Expert agent
from agno.models.base import Model
from agno.models.openai import OpenAIResponses

def create_medical_imaging_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a medical imaging agent that can analyze various types of medical images.
    
    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent
        
    Returns:
        An Agent instance configured as a medical imaging expert agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    #model_copy = deepcopy(model)
    
    return Agent(
        name="Medical Imaging and Search Expert",
        role="Specialized medical imaging radiologist for educational analysis",
        model=OpenAIResponses(id="gpt-5"),
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        instructions=FULL_INSTRUCTIONS,
        tools=[{"type": "web_search_preview"}, PubmedTools()],  # Enable OpenAI tools for medical literature
        description="You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging.",
        markdown=True,  # Enable markdown formatting for structured output
        debug_mode=True,
        #show_tool_calls=True,
        exponential_backoff=True,
        #add_datetime_to_instructions=True,
        #add_history_to_messages=True,
        add_history_to_context=True
    )

# Create default agent instance for backward compatibility
# Note: This is deprecated - use create_medical_imaging_agent() factory function instead
from agno.models.openai import OpenAIResponses
agent = Agent(
    name="Medical Imaging and Search Expert",
    role="Specialized medical imaging radiologist for educational analysis",
    model=OpenAIResponses(id="gpt-5"),  # Use GPT-4o for vision capabilities
    instructions=FULL_INSTRUCTIONS,
    tools=[{"type": "web_search_preview"}, PubmedTools()],  # Enable OpenAI tools for medical literature
    markdown=True,  # Enable markdown formatting for structured output
    debug_mode=True,
    #show_tool_calls=True,
    exponential_backoff=True,
    #add_datetime_to_instructions=True
)

# Example usage
if __name__ == "__main__":
    # Example image path (users should replace with their own image)
    image_path = Path(__file__).parent.joinpath("test.jpg")

    # Uncomment to run the analysis
    # agent.print_response("Please analyze this medical image.", images=[image_path])

    # Example with specific focus
    # agent.print_response(
    #     "Please analyze this image with special attention to bone density.",
    #     images=[image_path]
    # )
