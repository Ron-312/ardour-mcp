"""
Track control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, Path, HTTPException
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client
from mcp_server.osc_listener import get_osc_listener

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
        osc_listener = get_osc_listener()  # Get the listener
        
        logger.info("[TRACK LIST] Starting track discovery process")
        
        # CRITICAL: Check if OSC listener is actually running
        logger.info(f"[TRACK LIST] OSC Listener state check - running: {osc_listener.running}")
        logger.info(f"[TRACK LIST] OSC Listener server object: {osc_listener.server}")
        logger.info(f"[TRACK LIST] OSC Listener thread: {osc_listener.server_thread}")
        
        # Force-start OSC listener if not running
        if not osc_listener.running:
            logger.warning("[TRACK LIST] OSC Listener not running! Force-starting...")
            try:
                osc_listener.start()
                import time
                time.sleep(0.2)  # Give it a moment to initialize
                logger.info(f"[TRACK LIST] After force-start - running: {osc_listener.running}")
                if not osc_listener.running:
                    raise Exception("Failed to start OSC listener")
            except Exception as e:
                logger.error(f"[TRACK LIST] Failed to force-start OSC listener: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"OSC Listener startup failed: {str(e)}"
                )
        
        # Clear any existing strip data and reset state
        osc_listener.strips.clear()
        osc_listener.strip_data.clear()  # Clear smart strip data
        osc_listener.strip_list_complete = False
        osc_listener.strip_feedback_complete = False
        osc_listener.strip_feedback_start_time = None
        osc_listener.strip_list_session_framerate = None
        osc_listener.strip_list_last_frame = None
        
        # Step 1: Setup OSC surface (required before strip list query)
        # Use strip_types=3 for Audio (1) + MIDI (2) tracks only
        # Use feedback=7 (1+2+4) for: button status + variable controls + SSID extension
        logger.info("[TRACK LIST] Setting up OSC surface with feedback enabled")
        logger.info(f"[TRACK LIST] OSC Listener running on port: {osc_listener.listen_port}")
        logger.info(f"[TRACK LIST] OSC Listener server running: {osc_listener.running}")
        logger.info(f"[TRACK LIST] Current strip_data keys: {list(osc_listener.strip_data.keys())}")
        surface_success = osc_client.setup_surface(bank_size=0, strip_types=3, feedback=7)
        
        if not surface_success:
            logger.error("[TRACK LIST] Failed to setup OSC surface")
            raise HTTPException(
                status_code=500,
                detail="Failed to setup OSC surface with Ardour"
            )
            
        # Small delay to let surface setup complete
        import time
        time.sleep(0.1)
        
        # Step 2: Send the strip list query
        logger.info("[TRACK LIST] Requesting strip list from Ardour")
        query_success = osc_client.query_strip_list()
        
        if not query_success:
            logger.error("[TRACK LIST] Failed to send strip list query")
            raise HTTPException(
                status_code=500,
                detail="Failed to send strip list query to Ardour"
            )
        
        # Step 3: Wait for strip feedback to complete
        start_time = time.time()
        timeout = 3.0  # 3 seconds timeout for feedback
        check_interval = 0.1  # Check every 100ms
        
        logger.info(f"[TRACK LIST] Waiting for strip feedback (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            # Log current state during wait
            current_strips = len(osc_listener.strip_data)
            if current_strips > 0:
                logger.info(f"[TRACK LIST] Found {current_strips} strips so far: {list(osc_listener.strip_data.keys())}")
                
            # Check if strip feedback collection is complete
            if osc_listener.check_strip_feedback_complete():
                logger.info("[TRACK LIST] Strip feedback collection complete")
                break
                
            time.sleep(check_interval)
        
        elapsed = time.time() - start_time
        
        # DEBUG: Log final state
        logger.info(f"[TRACK LIST] Final strip_data contents: {osc_listener.strip_data}")
        logger.info(f"[TRACK LIST] Strip feedback start time: {osc_listener.strip_feedback_start_time}")
        logger.info(f"[TRACK LIST] Strip feedback complete: {osc_listener.strip_feedback_complete}")
        
        # Get track summaries from smart strip data
        track_summaries = osc_listener.get_all_strip_summaries()
        logger.info(f"[TRACK LIST] Generated {len(track_summaries)} track summaries")
        
        logger.info(f"[TRACK LIST] Discovery completed in {elapsed:.2f}s, found {len(track_summaries)} tracks")
        
        # Return basic track summary for MCP client
        result = {
            "status": "success",
            "action": "list_tracks",
            "tracks": track_summaries,  # Using 'tracks' instead of 'strips' for clarity
            "count": len(track_summaries),
            "discovery_time": f"{elapsed:.2f}s",
            "message": f"Found {len(track_summaries)} tracks"
        }
        
        logger.info(f"[TRACK LIST] Returning {len(track_summaries)} tracks to MCP client")
        for track in track_summaries:
            logger.info(f"[TRACK LIST]   - {track['name']} (SSID {track['ssid']})")
            
        return result
        
    except Exception as e:
        logger.error(f"Error in list_tracks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/{track_id}/details",
    operation_id="get_track_details"
)
async def get_track_details(
    track_id: int = Path(..., description="Track/Strip ID (1-based)", ge=1, le=256)
):
    """Get detailed information about a specific track"""
    try:
        osc_listener = get_osc_listener()
        
        logger.info(f"[TRACK DETAILS] Getting details for track {track_id}")
        
        # Get detailed track info from smart strip data
        track_details = osc_listener.get_strip_details(track_id)
        
        if track_details is None:
            logger.warning(f"[TRACK DETAILS] Track {track_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Track {track_id} not found. Use /track/list to see available tracks."
            )
        
        logger.info(f"[TRACK DETAILS] Found track: {track_details['name']}")
        
        return {
            "status": "success",
            "action": "get_track_details",
            "track": track_details,
            "message": f"Details for track {track_id}: {track_details['name']}"
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error in get_track_details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )