"""
Track control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, Path, HTTPException
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/track", tags=["track"])

class FaderRequest(BaseModel):
    """Request model for fader control"""
    gain_db: float = Field(
        ..., 
        description="Gain in decibels",
        ge=-60.0,  # Minimum gain
        le=20.0    # Maximum gain
    )

class MuteRequest(BaseModel):
    """Request model for mute control"""
    mute: bool = Field(..., description="True to mute, False to unmute")

class SoloRequest(BaseModel):
    """Request model for solo control"""
    solo: bool = Field(..., description="True to solo, False to unsolo")

@router.post("/{track_number}/fader")
async def set_fader(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: FaderRequest = ...
):
    """Set track fader level"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_strip_gain(track_number, request.gain_db)
        
        if success:
            logger.info(f"Fader set to {request.gain_db}dB for track {track_number}")
            return {
                "status": "success", 
                "action": "set_fader",
                "track": track_number,
                "gain_db": request.gain_db,
                "message": f"Fader set to {request.gain_db}dB for track {track_number}",
                "osc_address": f"/strip/{track_number-1}/gain"
            }
        else:
            logger.error(f"Failed to set fader for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set fader for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_fader: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{track_number}/mute")
async def set_mute(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: MuteRequest = ...
):
    """Mute/unmute track"""
    try:
        osc_client = get_osc_client()
        success = osc_client.strip_mute(track_number, request.mute)
        
        if success:
            action = "muted" if request.mute else "unmuted"
            logger.info(f"Track {track_number} {action}")
            return {
                "status": "success",
                "action": "set_mute",
                "track": track_number,
                "mute": request.mute,
                "message": f"Track {track_number} {action}",
                "osc_address": f"/strip/{track_number-1}/mute"
            }
        else:
            logger.error(f"Failed to set mute for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set mute for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_mute: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{track_number}/solo")
async def set_solo(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: SoloRequest = ...
):
    """Solo/unsolo track"""
    try:
        osc_client = get_osc_client()
        success = osc_client.strip_solo(track_number, request.solo)
        
        if success:
            action = "soloed" if request.solo else "unsoloed"
            logger.info(f"Track {track_number} {action}")
            return {
                "status": "success",
                "action": "set_solo",
                "track": track_number,
                "solo": request.solo,
                "message": f"Track {track_number} {action}",
                "osc_address": f"/strip/{track_number-1}/solo"
            }
        else:
            logger.error(f"Failed to set solo for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set solo for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_solo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )