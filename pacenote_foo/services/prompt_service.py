"""
Service for managing prompt templates and variable substitution.
"""
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
