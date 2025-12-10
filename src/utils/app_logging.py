"""
src/utils/app_logging.py

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
    # Format includes optional UID context from LoggerAdapter for email processing
    effective_log_level = "DEBUG" if config.dev_mode else config.log.log_level

    # Custom formatter to include UID from LoggerAdapter extra context
    class UIDFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            # Add UID prefix if present in extra context
            if hasattr(record, "uid"):
                record.msg = f"[uid={record.uid}] {record.msg}"
            return super().format(record)

    handler = logging.StreamHandler()
    handler.setFormatter(UIDFormatter("%(asctime)s %(name)s: %(message)s"))

    logging.basicConfig(
        level=getattr(logging, effective_log_level.upper()),
        handlers=[handler],
    )


def get_logger(name: str) -> logging.Logger:
    # Get a logger instance by name
    return logging.getLogger(name)
