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

class NameRequest(BaseModel):
    """Request model for track naming"""
    name: str = Field(..., description="New name for the track", min_length=1, max_length=100)

class RecordEnableRequest(BaseModel):
    """Request model for record enable control"""
    enabled: bool = Field(..., description="True to enable recording, False to disable")

class RecordSafeRequest(BaseModel):
    """Request model for record safe control"""
    safe: bool = Field(..., description="True to enable record safe, False to disable")

class PanRequest(BaseModel):
    """Request model for pan control"""
    pan_position: float = Field(
        ..., 
        description="Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)",
        ge=-1.0,
        le=1.0
    )

@router.post(
    "/{track_number}/fader",
    operation_id="set_fader"
)
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

@router.post(
    "/{track_number}/mute",
    operation_id="set_mute"
)
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

@router.post(
    "/{track_number}/solo",
    operation_id="set_solo"
)
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

@router.post(
    "/{track_number}/name",
    operation_id="set_track_name"
)
async def set_track_name(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: NameRequest = ...
):
    """Set track name"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_strip_name(track_number, request.name)
        
        if success:
            logger.info(f"Track {track_number} renamed to '{request.name}'")
            return {
                "status": "success",
                "action": "set_name",
                "track": track_number,
                "name": request.name,
                "message": f"Track {track_number} renamed to '{request.name}'",
                "osc_address": f"/strip/{track_number-1}/name"
            }
        else:
            logger.error(f"Failed to rename track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to rename track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_track_name: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/{track_number}/record-enable",
    operation_id="set_record_enable"
)
async def set_record_enable(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: RecordEnableRequest = ...
):
    """Enable/disable recording for track"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_strip_record_enable(track_number, request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Track {track_number} recording {action}")
            return {
                "status": "success",
                "action": "set_record_enable",
                "track": track_number,
                "enabled": request.enabled,
                "message": f"Track {track_number} recording {action}",
                "osc_address": f"/strip/{track_number-1}/recenable"
            }
        else:
            logger.error(f"Failed to set record enable for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set record enable for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_record_enable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/{track_number}/record-safe",
    operation_id="set_record_safe"
)
async def set_record_safe(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: RecordSafeRequest = ...
):
    """Enable/disable record safe for track"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_strip_record_safe(track_number, request.safe)
        
        if success:
            action = "enabled" if request.safe else "disabled"
            logger.info(f"Track {track_number} record safe {action}")
            return {
                "status": "success",
                "action": "set_record_safe",
                "track": track_number,
                "safe": request.safe,
                "message": f"Track {track_number} record safe {action}",
                "osc_address": f"/strip/{track_number-1}/record_safe"
            }
        else:
            logger.error(f"Failed to set record safe for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set record safe for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_record_safe: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/{track_number}/pan",
    operation_id="set_pan"
)
async def set_pan(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: PanRequest = ...
):
    """Set track pan position"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_strip_pan(track_number, request.pan_position)
        
        if success:
            # Create descriptive pan position
            if request.pan_position < -0.5:
                pos_desc = f"left ({request.pan_position:.2f})"
            elif request.pan_position > 0.5:
                pos_desc = f"right ({request.pan_position:.2f})"
            else:
                pos_desc = f"center ({request.pan_position:.2f})"
                
            logger.info(f"Track {track_number} pan set to {pos_desc}")
            return {
                "status": "success",
                "action": "set_pan",
                "track": track_number,
                "pan_position": request.pan_position,
                "message": f"Track {track_number} pan set to {pos_desc}",
                "osc_address": f"/strip/{track_number-1}/pan_stereo_position"
            }
        else:
            logger.error(f"Failed to set pan for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set pan for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_pan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/list",
    operation_id="list_tracks"
)
async def list_tracks():
    """Query Ardour for list of all tracks"""
    try:
        osc_client = get_osc_client()
        success = osc_client.query_strip_list()
        
        if success:
            logger.info("Strip list query sent to Ardour")
            return {
                "status": "success",
                "action": "list_tracks",
                "message": "Strip list query sent to Ardour - check Ardour logs for results",
                "osc_address": "/strip/list"
            }
        else:
            logger.error("Failed to query strip list")
            raise HTTPException(
                status_code=500,
                detail="Failed to query strip list from Ardour"
            )
    except Exception as e:
        logger.error(f"Error in list_tracks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )