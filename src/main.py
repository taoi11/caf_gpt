import asyncio
from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    # TODO: Start email queue processing in background thread here
    
    yield
    
    # Shutdown
    # TODO: Stop email processing thread gracefully


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
