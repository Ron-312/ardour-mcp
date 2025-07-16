"""
Send/Aux control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sends", tags=["sends"])

class SendLevelRequest(BaseModel):
    """Request model for send level control"""
    level: float = Field(
        ..., 
        description="Send level (0.0 = -inf dB, 1.0 = 0 dB)",
        ge=0.0,
        le=1.0
    )

class SendEnableRequest(BaseModel):
    """Request model for send enable/disable"""
    enabled: bool = Field(..., description="True to enable send, False to disable")

class SendGainRequest(BaseModel):
    """Request model for send gain control"""
    gain_db: float = Field(
        ..., 
        description="Send gain in dB (-60 to +6)",
        ge=-60.0,
        le=6.0
    )

@router.post("/track/{track_number}/send/{send_number}/level")
async def set_send_level(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    send_number: int = Path(..., description="Send number (1-based)", ge=1, le=32),
    request: SendLevelRequest = ...
):
    """Set send level for a track to specific aux"""
    try:
        osc_client = get_osc_client()
        # Keep 1-based indexing for OSC (Ardour expects /strip/1/ for first track)
        track_index = track_number
        send_index = send_number - 1  # Sends might still be 0-based
        
        success = osc_client.set_send_level(track_index, send_index, request.level)
        
        if success:
            logger.info(f"Send level set: track {track_number} send {send_number} = {request.level}")
            return {
                "status": "success",
                "action": "set_send_level",
                "track": track_number,
                "send": send_number,
                "level": request.level,
                "message": f"Send {send_number} level set to {request.level:.2f} for track {track_number}",
                "osc_address": f"/strip/{track_index}/send/{send_index}/fader"
            }
        else:
            logger.error(f"Failed to set send level for track {track_number} send {send_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set send level for track {track_number} send {send_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_send_level: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/track/{track_number}/send/{send_number}/gain")
async def set_send_gain(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    send_number: int = Path(..., description="Send number (1-based)", ge=1, le=32),
    request: SendGainRequest = ...
):
    """Set send gain in dB for a track to specific aux"""
    try:
        osc_client = get_osc_client()
        track_index = track_number
        send_index = send_number - 1
        
        success = osc_client.set_send_gain(track_index, send_index, request.gain_db)
        
        if success:
            logger.info(f"Send gain set: track {track_number} send {send_number} = {request.gain_db} dB")
            return {
                "status": "success",
                "action": "set_send_gain",
                "track": track_number,
                "send": send_number,
                "gain_db": request.gain_db,
                "message": f"Send {send_number} gain set to {request.gain_db} dB for track {track_number}",
                "osc_address": f"/strip/{track_index}/send/{send_index}/gain"
            }
        else:
            logger.error(f"Failed to set send gain for track {track_number} send {send_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set send gain for track {track_number} send {send_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_send_gain: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/track/{track_number}/send/{send_number}/enable")
async def set_send_enable(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    send_number: int = Path(..., description="Send number (1-based)", ge=1, le=32),
    request: SendEnableRequest = ...
):
    """Enable or disable a send"""
    try:
        osc_client = get_osc_client()
        track_index = track_number
        send_index = send_number - 1
        
        success = osc_client.set_send_enable(track_index, send_index, request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Send {action}: track {track_number} send {send_number}")
            return {
                "status": "success",
                "action": "set_send_enable",
                "track": track_number,
                "send": send_number,
                "enabled": request.enabled,
                "message": f"Send {send_number} {action} for track {track_number}",
                "osc_address": f"/strip/{track_index}/send/{send_index}/enable"
            }
        else:
            logger.error(f"Failed to set send enable for track {track_number} send {send_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set send enable for track {track_number} send {send_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_send_enable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/track/{track_number}/sends")
async def list_track_sends(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256)
):
    """List all sends for a track"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        success = osc_client.list_track_sends(track_index)
        
        if success:
            logger.info(f"Listed sends for track {track_number}")
            return {
                "status": "success",
                "action": "list_sends",
                "track": track_number,
                "message": f"Send list requested for track {track_number}",
                "osc_address": f"/strip/{track_index}/sends"
            }
        else:
            logger.error(f"Failed to list sends for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list sends for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in list_track_sends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )