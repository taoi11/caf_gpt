"""
Service for managing prompt templates and variable substitution.
"""
import os
import pathlib


class PromptService:
    """
    Service for managing prompt templates and variable substitution.
    """
    def __init__(self):
        """
        Initialize the prompt service.
        """
        # Path to the base prompt template
        self.base_prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "base.md"

    def load_template(self):
        """
        Load the base prompt template.
        """
        try:
            with open(self.base_prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            # Return a simple fallback in case of error
            return "Error loading prompt template. Please try again later."

    def construct_prompt(self, user_input, competency_list, examples):
        """
        Construct a prompt using the template and variables.
        """
        try:
            template = self.load_template()
            
            # Replace variables in the template
            prompt = template.replace("{{competency_list}}", competency_list)
            prompt = prompt.replace("{{examples}}", examples)
            
            # Add user input at the beginning
            full_prompt = f"User input: {user_input}\n\n{prompt}"
            
            return full_prompt
        except Exception as e:
            print(f"Error constructing prompt: {e}")
            return "Error constructing prompt. Please try again later." 