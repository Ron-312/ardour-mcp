"""
FastAPI application entry point for Ardour MCP Server
"""

import logging
import sys
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

from mcp_server.api import transport, track, session, sends, plugins, recording
from mcp_server.config import get_settings
from mcp_server.osc_listener import start_osc_listener

# Load environment variables
load_dotenv()

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ardour_mcp.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Ardour MCP Server",
    description="A FastAPI server for controlling Ardour DAW via OSC messages",
    version="1.0.0"
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc} - {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    return response

# Include routers
app.include_router(transport.router)
app.include_router(track.router)
app.include_router(session.router)
app.include_router(sends.router)
app.include_router(plugins.router)
app.include_router(recording.router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint returning server information"""
    return {
        "message": "Ardour MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "transport": "/transport/{play,stop}",
            "track": "/track/{n}/fader",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize OSC listener on startup"""
    logger.info("Starting OSC listener for plugin discovery...")
    try:
        start_osc_listener()
        logger.info("OSC listener started successfully")
    except Exception as e:
        logger.error(f"Failed to start OSC listener: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up OSC listener on shutdown"""
    logger.info("Stopping OSC listener...")
    try:
        from mcp_server.osc_listener import stop_osc_listener
        stop_osc_listener()
        logger.info("OSC listener stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop OSC listener: {e}")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("HTTP_PORT", "8000"))
    
    uvicorn.run(
        "mcp_server.main:app",
        host=host,
        port=port,
        reload=True
    )