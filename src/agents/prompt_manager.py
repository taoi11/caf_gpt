"""
src/agents/prompt_manager.py

Manages loading and caching of system prompts from the prompts subdirectory.

Top-level declarations:
- PromptManager: Class for loading prompts from .md files with caching
"""

import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"


class PromptManager:
    # Class for loading prompts from .md files with caching
    MAX_CACHE_SIZE = 32  # Limit cache to prevent unbounded memory growth

    def __init__(self, prompts_dir: Optional[Path] = None):
        # Initialize with optional prompts directory; ensure dir exists
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.prompts_dir.mkdir(exist_ok=True)
        self._cache: Dict[str, str] = {}

    def get_prompt(self, prompt_name: str) -> str:
        # Load prompt from .md file with instance-level caching
        if prompt_name in self._cache:
            return self._cache[prompt_name]

        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        result = self._load_from_filesystem(prompt_path)

        # Simple cache eviction: clear oldest half if cache is full
        if len(self._cache) >= self.MAX_CACHE_SIZE:
            keys_to_remove = list(self._cache.keys())[: self.MAX_CACHE_SIZE // 2]
            for key in keys_to_remove:
                del self._cache[key]

        self._cache[prompt_name] = result
        return result

    def _load_from_filesystem(self, path: Path) -> str:
        # Read and return content from prompt file
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
