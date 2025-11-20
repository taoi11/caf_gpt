
"""
src/app_logging.py

Centralized logging configuration using structlog for structured logs.

Top-level declarations:
- setup_logging: Configure structlog and stdlib logging based on app config
"""

from structlog import configure
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import LoggerFactory
from structlog.dev import ConsoleRenderer

import logging

from src.config import AppConfig

def setup_logging(config: AppConfig) -> None:
    # Configure structlog and standard library logging based on app config
    # Supports JSON or console output based on config.log.json_logging
    # Uses DEBUG level when DEV_MODE is enabled for verbose logging, else respects config.log.log_level
    effective_log_level = "DEBUG" if config.dev_mode else config.log.log_level

    if config.log.json_logging:
        configure(
            processors=[
                TimeStamper(fmt="iso"),
                JSONRenderer()
            ],
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        configure(
            processors=[ConsoleRenderer()],
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    logging.basicConfig(
        level=getattr(logging, effective_log_level.upper()),
        handlers=[logging.StreamHandler()]
    )
