"""
src/app_logging.py

Centralized logging configuration using standard library logging.

Top-level declarations:
- setup_logging: Configure stdlib logging based on app config
- get_logger: Get a logger instance by name
"""

import logging

from src.config import AppConfig


def setup_logging(config: AppConfig) -> None:
    # Configure standard library logging based on app config
    # Uses DEBUG level when DEV_MODE is enabled for verbose logging, else respects config.log.log_level
    effective_log_level = "DEBUG" if config.dev_mode else config.log.log_level

    logging.basicConfig(
        level=getattr(logging, effective_log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
