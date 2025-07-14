"""
Transport control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, HTTPException
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transport", tags=["transport"])

@router.get("/test-connection")
async def test_osc_connection():
    """Test OSC connection to Ardour"""
    try:
        osc_client = get_osc_client()
        connection_info = osc_client.get_connection_info()
        
        # Test the connection
        test_success = osc_client.test_connection()
        
        return {
            "status": "success" if test_success else "failed",
            "connection_info": connection_info,
            "test_result": test_success,
            "message": "Connection test completed"
        }
    except Exception as e:
        logger.error(f"Error in test_osc_connection: {e}")
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }

@router.post("/play")
async def play_transport():
    """Start transport playback"""
    try:
        osc_client = get_osc_client()
        success = osc_client.transport_play()
        
        if success:
            logger.info("Transport play command sent successfully")
            return {
                "status": "success",
                "action": "play", 
                "message": "Transport play command sent to Ardour",
                "osc_address": "/ardour/transport_play"
            }
        else:
            logger.error("Failed to send transport play command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send transport play command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in play_transport: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/stop")
async def stop_transport():
    """Stop transport playback"""
    try:
        osc_client = get_osc_client()
        success = osc_client.transport_stop()
        
        if success:
            logger.info("Transport stop command sent successfully")
            return {
                "status": "success",
                "action": "stop",
                "message": "Transport stop command sent to Ardour",
                "osc_address": "/ardour/transport_stop"
            }
        else:
            logger.error("Failed to send transport stop command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send transport stop command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in stop_transport: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )