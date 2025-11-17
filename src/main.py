from contextlib import asynccontextmanager
import logging
import threading

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import config
from src.email_code.simple_email_handler import SimpleEmailProcessor

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    email_processor = SimpleEmailProcessor(config.email)
    processor_thread = threading.Thread(
        target=email_processor.run_loop,
        daemon=True
    )
    processor_thread.start()

    try:
        yield
    finally:
        email_processor.stop()
        processor_thread.join(timeout=5)


app = FastAPI(
    title="CAF-GPT Email Agent",
    description="AI-powered email response system",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
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
