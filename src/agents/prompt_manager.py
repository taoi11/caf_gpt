"""
src/agents/prompt_manager.py

Manages loading system prompts from the prompts subdirectory.
Relies on Linux kernel page cache for performance - no application-level caching needed.

Top-level declarations:
- PromptManager: Class for loading prompts from .md files
"""

import logging
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


class PromptManager:
    # Class for loading prompts from .md files
    # Relies on OS-level filesystem caching for performance

    def __init__(self, prompts_dir: Path | None = None):
        # Initialize with optional prompts directory; ensure dir exists
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.prompts_dir.mkdir(exist_ok=True)

    def get_prompt(self, prompt_name: str) -> str:
        # Load prompt from .md file (OS filesystem cache handles performance)
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return self._load_from_filesystem(prompt_path)

    def _load_from_filesystem(self, path: Path) -> str:
        # Read and return content from prompt file
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
