"""
src/main.py

Main FastAPI application entry point, handling lifespan management for email processing and providing a health check endpoint.

Top-level declarations:
- lifespan: Async context manager to start and stop the email processor thread
- app: FastAPI application instance with title, description, and lifespan
- health_check: GET endpoint returning application health status
"""

from contextlib import asynccontextmanager
import logging
import threading
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import config
from src.email_code.simple_email_handler import SimpleEmailProcessor


def _setup_logging() -> None:
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


_setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Initialize components and start email queue processor in background thread
    logger.info("Application starting up")

    # Initialize email processor with imap_tools
    processor = SimpleEmailProcessor(config.email)

    # Start processor in daemon thread
    processor_thread = threading.Thread(target=processor.run_loop, daemon=True)
    processor_thread.start()
    logger.info("Email queue processor thread started", extra={"thread_id": processor_thread.ident})

    try:
        yield
    finally:
        logger.info("Application shutting down")
        processor.stop()
        processor_thread.join(timeout=5)
        if processor_thread.is_alive():
            logger.warning("Processor thread did not stop within timeout")
        else:
            logger.info("Email queue processor stopped gracefully")


app = FastAPI(
    title="CAF-GPT Email Agent",
    description="AI-powered email response system",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> JSONResponse:
    # Health check endpoint returning application status and version
    return JSONResponse(content={"status": "healthy", "version": "0.1.0"}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=config.dev_mode)
