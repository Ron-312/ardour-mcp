#!/usr/bin/env python3
import logging
from fastmcp import FastMCP
from mcp_server.main import app

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

mcp = FastMCP.from_fastapi(
    app,
    name="ardour-mcp",
    version="1.0.0",
    instructions="Ardour MCP Server: control transport, tracks, sessions, plugins, etc."
)

if __name__ == "__main__":
    logger.info("Starting Ardour MCP Server…")
    for route in app.routes:
        if hasattr(route, "path"):
            logger.info(f"  {route.methods} {route.path}")
    logger.info(f"Total routes: {len(app.routes)}")
    mcp.run(transport="stdio")
