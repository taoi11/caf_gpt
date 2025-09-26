"""
Prompt service for pace note generation.

This module handles the construction of prompts for LLM models using local files.
"""
from .local_file_reader import get_base_prompt


class PromptService:
    """
    Service for managing prompt templates and variable substitution.
    """

    def __init__(self):
        """
        Initialize the prompt service.
        """
        pass  # No longer need to store file paths since we use the local_file_reader

    def load_template(self):
        """
        Load the base prompt template from local files.
        """
        try:
            return get_base_prompt()
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            # Return a simple fallback in case of error
            return "Error loading prompt template. Please try again later."

    def prepare_system_prompt(self, competency_list, examples):
        """
        Prepare the system prompt by replacing variables in the template.

        Returns:
            str: The processed system prompt with variables substituted
        """
        try:
            template = self.load_template()

            # Replace variables in the template
            system_prompt = template.replace("{{competency_list}}", competency_list)
            system_prompt = system_prompt.replace("{{examples}}", examples)

            return system_prompt
        except Exception as e:
            print(f"Error preparing system prompt: {e}")
            return "Error preparing system prompt. Please try again later."

    def get_messages(self, user_input, competency_list, examples):
        """
        Get formatted messages for the LLM API with proper role assignment.

        Returns:
            list: List of message objects with roles and content
        """
        system_prompt = self.prepare_system_prompt(competency_list, examples)

        # Format messages for the LLM API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        return messages

    def construct_prompt(self, user_input, competency_list, examples):
        """
        Construct the complete prompt for the LLM using the template.

        Args:
            user_input (str): The user's input text
            competency_list (str): The rank-specific competencies
            examples (str): The examples for reference

        Returns:
            list: The formatted messages for the LLM API
        """
        # Validate user input
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        return self.get_messages(user_input, competency_list, examples)


def construct_pace_note_prompt(user_input: str, competency_list: str, examples: dict = None) -> str:
    """
    Constructs a prompt for generating a pace note based on user input and competency data.
    
    Args:
        user_input: The user's input text
        competency_list: The competency list text
        examples: Optional dict of example types and their content
        
    Returns:
        str: The constructed prompt
    """
    prompt_parts = [
        "You are a software engineering mentor providing feedback on a programming problem.",
        "\nYou will analyze the user's code or approach and provide constructive feedback.",
        "\n\nCompetency guidelines to consider:",
        f"\n{competency_list}",
    ]
    
    # Add examples if provided
    if examples:
        prompt_parts.append("\n\nReference examples:")
        for example_type, content in examples.items():
            prompt_parts.append(f"\n{example_type.upper()} EXAMPLE:\n{content}")
    
    # Add the user input
    prompt_parts.append(f"\n\nUSER INPUT:\n{user_input}")
    
    # Add the final instruction
    prompt_parts.append("\n\nProvide a concise, constructive pace note that highlights strengths and areas for improvement. Focus on actionable feedback.")
    
    return "".join(prompt_parts)
