import asyncio
from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import config

# TODO: Import EmailQueueProcessor once implemented
# from src.email.email_queue_processor import EmailQueueProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    email_processor = None
    try:
        # TODO: Uncomment once EmailQueueProcessor is implemented
        # email_processor = EmailQueueProcessor(config.email)
        # processor_thread = threading.Thread(
        #     target=email_processor.start_queue_processing,
        #     daemon=True  # Thread dies with main process
        # )
        # processor_thread.start()

        yield

    except KeyboardInterrupt:
        pass
    finally:
        # Shutdown
        if email_processor:
            # TODO: Implement graceful shutdown in EmailQueueProcessor
            # email_processor.stop_processing()
            pass


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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.dev_mode
    )
