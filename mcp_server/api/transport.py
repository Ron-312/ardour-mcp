"""
Transport control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transport", tags=["transport"])

class SpeedRequest(BaseModel):
    """Request model for transport speed control"""
    speed: float = Field(
        ..., 
        description="Speed multiplier (-8.0 to 8.0, 1.0 = normal speed)",
        ge=-8.0,
        le=8.0
    )

@router.post("/test-connection", operation_id="test_osc_connection")
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
                "osc_address": "/transport_play"
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
                "osc_address": "/transport_stop"
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

@router.post("/rewind")
async def rewind_transport():
    """Rewind transport to beginning"""
    try:
        osc_client = get_osc_client()
        success = osc_client.transport_rewind()
        
        if success:
            logger.info("Transport rewind command sent successfully")
            return {
                "status": "success",
                "action": "rewind",
                "message": "Transport rewind command sent to Ardour",
                "osc_address": "/rewind"
            }
        else:
            logger.error("Failed to send transport rewind command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send transport rewind command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in rewind_transport: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/fast-forward")
async def fast_forward_transport():
    """Fast forward transport"""
    try:
        osc_client = get_osc_client()
        success = osc_client.transport_fast_forward()
        
        if success:
            logger.info("Transport fast forward command sent successfully")
            return {
                "status": "success",
                "action": "fast_forward",
                "message": "Transport fast forward command sent to Ardour",
                "osc_address": "/ffwd"
            }
        else:
            logger.error("Failed to send transport fast forward command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send transport fast forward command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in fast_forward_transport: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/goto-start")
async def goto_start():
    """Move playhead to start"""
    try:
        osc_client = get_osc_client()
        success = osc_client.goto_start()
        
        if success:
            logger.info("Goto start command sent successfully")
            return {
                "status": "success",
                "action": "goto_start",
                "message": "Goto start command sent to Ardour",
                "osc_address": "/goto_start"
            }
        else:
            logger.error("Failed to send goto start command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send goto start command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in goto_start: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/goto-end")
async def goto_end():
    """Move playhead to end"""
    try:
        osc_client = get_osc_client()
        success = osc_client.goto_end()
        
        if success:
            logger.info("Goto end command sent successfully")
            return {
                "status": "success",
                "action": "goto_end",
                "message": "Goto end command sent to Ardour",
                "osc_address": "/goto_end"
            }
        else:
            logger.error("Failed to send goto end command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send goto end command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in goto_end: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/toggle-roll")
async def toggle_roll():
    """Toggle between play and stop"""
    try:
        osc_client = get_osc_client()
        success = osc_client.toggle_roll()
        
        if success:
            logger.info("Toggle roll command sent successfully")
            return {
                "status": "success",
                "action": "toggle_roll",
                "message": "Toggle roll command sent to Ardour",
                "osc_address": "/toggle_roll"
            }
        else:
            logger.error("Failed to send toggle roll command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send toggle roll command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in toggle_roll: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/toggle-loop")
async def toggle_loop():
    """Toggle loop mode"""
    try:
        osc_client = get_osc_client()
        success = osc_client.toggle_loop()
        
        if success:
            logger.info("Toggle loop command sent successfully")
            return {
                "status": "success",
                "action": "toggle_loop",
                "message": "Toggle loop command sent to Ardour",
                "osc_address": "/loop_toggle"
            }
        else:
            logger.error("Failed to send toggle loop command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send toggle loop command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in toggle_loop: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/speed")
async def set_transport_speed(request: SpeedRequest):
    """Set transport speed"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_transport_speed(request.speed)
        
        if success:
            logger.info(f"Transport speed set to {request.speed}x")
            return {
                "status": "success",
                "action": "set_speed",
                "speed": request.speed,
                "message": f"Transport speed set to {request.speed}x",
                "osc_address": "/set_transport_speed"
            }
        else:
            logger.error("Failed to set transport speed")
            raise HTTPException(
                status_code=500,
                detail="Failed to set transport speed"
            )
    except Exception as e:
        logger.error(f"Error in set_transport_speed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/add-marker")
async def add_marker():
    """Add marker at current position"""
    try:
        osc_client = get_osc_client()
        success = osc_client.add_marker()
        
        if success:
            logger.info("Add marker command sent successfully")
            return {
                "status": "success",
                "action": "add_marker",
                "message": "Add marker command sent to Ardour",
                "osc_address": "/add_marker"
            }
        else:
            logger.error("Failed to send add marker command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send add marker command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in add_marker: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/next-marker")
async def next_marker():
    """Go to next marker"""
    try:
        osc_client = get_osc_client()
        success = osc_client.next_marker()
        
        if success:
            logger.info("Next marker command sent successfully")
            return {
                "status": "success",
                "action": "next_marker",
                "message": "Next marker command sent to Ardour",
                "osc_address": "/next_marker"
            }
        else:
            logger.error("Failed to send next marker command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send next marker command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in next_marker: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/prev-marker")
async def prev_marker():
    """Go to previous marker"""
    try:
        osc_client = get_osc_client()
        success = osc_client.prev_marker()
        
        if success:
            logger.info("Previous marker command sent successfully")
            return {
                "status": "success",
                "action": "prev_marker",
                "message": "Previous marker command sent to Ardour",
                "osc_address": "/prev_marker"
            }
        else:
            logger.error("Failed to send previous marker command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send previous marker command to Ardour"
            )
    except Exception as e:
        logger.error(f"Error in prev_marker: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )