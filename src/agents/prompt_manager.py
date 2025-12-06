"""
/workspace/caf_gpt/src/agents/prompt_manager.py

Manages loading and caching of system prompts from the prompts subdirectory.

Top-level declarations:
- PromptManager: Class for loading prompts from .md files with caching and fallbacks
"""

import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"


class PromptManager:
    def __init__(self, prompts_dir: Optional[Path] = None):
        # Initialize with optional prompts directory; ensure dir exists
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.prompts_dir.mkdir(exist_ok=True)

    @lru_cache(maxsize=32)
    def get_prompt(self, prompt_name: str) -> str:
        # Load prompt from .md file or return default if not found
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if not prompt_path.exists():
            logger.warning(f"Prompt file not found: {prompt_path}")
            return self._get_default_prompt(prompt_name)
        return self._load_from_filesystem(prompt_path)

    def _load_from_filesystem(self, path: Path) -> str:
        # Read and return content from prompt file with error handling
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except IOError as e:
            logger.error(f"Error loading prompt from {path}: {e}")
            return self._get_default_prompt(path.stem)

    def _get_default_prompt(self, prompt_name: str) -> str:
        # Return fallback prompt if file loading fails
        return f"Default system prompt for {prompt_name}. Please provide the actual prompt."
