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

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import structlog

from src.config import config
from src.email_code.simple_email_handler import SimpleEmailProcessor
from src.app_logging import setup_logging

setup_logging(config)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Async context manager for application lifespan: starts email processor thread on startup, stops on shutdown
    # Manages daemon thread for continuous email polling with graceful shutdown
    logger.info("starting email processor")
    email_processor = SimpleEmailProcessor(config.email)
    processor_thread = threading.Thread(
        target=email_processor.run_loop,
        daemon=True
    )
    processor_thread.start()
    logger.info("email processor thread started", thread_id=processor_thread.ident)

    try:
        yield
    finally:
        logger.info("stopping email processor")
        email_processor.stop()
        processor_thread.join(timeout=5)
        if processor_thread.is_alive():
            logger.warning("processor thread did not stop within timeout")
        else:
            logger.info("email processor stopped gracefully")

app = FastAPI(
    title="CAF-GPT Email Agent",
    description="AI-powered email response system",
    version="0.1.0",
    lifespan=lifespan
)
# FastAPI application instance with title, description, version, and lifespan context manager

@app.get("/health")
async def health_check():
    # Health check endpoint returning JSON status for application monitoring
    # Used for container orchestration and load balancer health checks
    return JSONResponse(
        content={"status": "healthy", "version": "0.1.0"},
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.dev_mode
    )
