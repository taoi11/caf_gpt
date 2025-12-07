"""
src/main.py

Main FastAPI application entry point, handling lifespan management for email processing and providing a health check endpoint.

Top-level declarations:
- lifespan: Async context manager to start and stop the email processor thread
- app: FastAPI application instance with title, description, and lifespan
- health_check: GET endpoint returning application health status
"""

from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import config
from src.app_logging import setup_logging, get_logger

from src.email_code.simple_email_handler import SimpleEmailProcessor

setup_logging(config)

logger = get_logger(__name__)


class StoppableThread:
    # Helper to run stoppable loop in thread with graceful shutdown
    def __init__(self, target, args=()):
        self.target = target
        self.args = args
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self.stop_event.wait(timeout=1):  # Check every second
            self.target(*self.args)

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize components and start email queue processor in background thread
    logger.info("Application starting up")

    # Initialize email processor with imap_tools
    processor = SimpleEmailProcessor(config.email)

    # Start processor in stoppable thread
    processor_thread = StoppableThread(target=processor.run_loop)
    logger.info("Email queue processor thread started", extra={"thread_id": processor_thread.thread.ident})

    try:
        yield
    finally:
        logger.info("Application shutting down")
        processor.stop()
        processor_thread.stop()
        if processor_thread.thread.is_alive():
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
async def health_check():
    # Health check endpoint returning application status and version
    return JSONResponse(content={"status": "healthy", "version": "0.1.0"}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=config.dev_mode)
