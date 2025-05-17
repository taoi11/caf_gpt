"""
Pace Note services orchestration module.

This module coordinates the different services needed for generating pace notes.
"""
import logging
from .s3_reader import get_competency_list, get_examples
from .prompt_service import PromptService
from core.services.open_router_service import OpenRouterService

logger = logging.getLogger(__name__)

def generate_pace_note(user_input: str, rank: str) -> dict:
    """
    Main orchestration function to generate a pace note.
    
    This function handles the complete workflow:
    1. Fetches competency list and examples from S3
    2. Constructs the prompt using PromptService
    3. Generates the pace note using OpenRouterService
    
    Args:
        user_input: The user's input text
        rank: The rank level (e.g., 'cpl', 'mcpl', 'sgt', 'wo')
        
    Returns:
        dict: Result with 'status' ('success' or 'error') and 'pace_note'/'message'
    """
    try:
        # Initialize services
        prompt_service = PromptService()
        open_router_service = OpenRouterService()
        
        # Get competency list and examples from S3
        try:
            competency_list = get_competency_list(rank)
            examples = get_examples()
        except Exception as e:
            logger.error(f"Error retrieving S3 content: {e}")
            return {
                'status': 'error',
                'message': f"Error retrieving content from S3: {str(e)}"
            }
            
        # Construct prompt
        messages = prompt_service.construct_prompt(user_input, competency_list, examples)
        
        # Generate pace note using the AI service
        pace_note_content = open_router_service.generate_completion(prompt=messages)
        
        # Check if the response indicates an error
        if (isinstance(pace_note_content, str) and
            (pace_note_content.startswith("OpenRouter API error") or 
             pace_note_content.startswith("Error"))):
            logger.error(f"PaceNote generation failed: {pace_note_content}")
            return {'status': 'error', 'message': pace_note_content}
            
        return {'status': 'success', 'pace_note': pace_note_content}
        
    except Exception as e:
        logger.error(f"Error in pace note generation workflow: {e}")
        return {'status': 'error', 'message': str(e)}
