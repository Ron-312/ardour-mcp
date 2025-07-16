"""
Recording control endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recording", tags=["recording"])

class RecordingEnableRequest(BaseModel):
    """Request model for recording enable control"""
    enabled: bool = Field(..., description="True to enable recording, False to disable")

class PunchRecordingRequest(BaseModel):
    """Request model for punch recording control"""
    enabled: bool = Field(..., description="True to enable punch recording, False to disable")

class InputMonitorRequest(BaseModel):
    """Request model for input monitoring control"""
    enabled: bool = Field(..., description="True to enable input monitoring, False to disable")

@router.post("/enable")
async def set_recording_enable(request: RecordingEnableRequest):
    """Enable or disable global recording"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_recording_enable(request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Global recording {action}")
            return {
                "status": "success",
                "action": "set_recording_enable",
                "enabled": request.enabled,
                "message": f"Global recording {action}",
                "osc_address": "/rec_enable_toggle"
            }
        else:
            logger.error("Failed to set global recording enable")
            raise HTTPException(
                status_code=500,
                detail="Failed to set global recording enable"
            )
    except Exception as e:
        logger.error(f"Error in set_recording_enable: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/disable")
async def disable_recording():
    """Disable global recording (convenience endpoint)"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_recording_enable(False)
        
        if success:
            logger.info("Global recording disabled")
            return {
                "status": "success",
                "action": "disable_recording",
                "enabled": False,
                "message": "Global recording disabled",
                "osc_address": "/rec_enable_toggle"
            }
        else:
            logger.error("Failed to disable global recording")
            raise HTTPException(
                status_code=500,
                detail="Failed to disable global recording"
            )
    except Exception as e:
        logger.error(f"Error in disable_recording: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/punch-in")
async def set_punch_in(request: PunchRecordingRequest):
    """Enable or disable punch-in recording"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_punch_in(request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Punch-in recording {action}")
            return {
                "status": "success",
                "action": "set_punch_in",
                "enabled": request.enabled,
                "message": f"Punch-in recording {action}",
                "osc_address": "/toggle_punch_in"
            }
        else:
            logger.error("Failed to set punch-in recording")
            raise HTTPException(
                status_code=500,
                detail="Failed to set punch-in recording"
            )
    except Exception as e:
        logger.error(f"Error in set_punch_in: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/punch-out")
async def set_punch_out(request: PunchRecordingRequest):
    """Enable or disable punch-out recording"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_punch_out(request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Punch-out recording {action}")
            return {
                "status": "success",
                "action": "set_punch_out",
                "enabled": request.enabled,
                "message": f"Punch-out recording {action}",
                "osc_address": "/toggle_punch_out"
            }
        else:
            logger.error("Failed to set punch-out recording")
            raise HTTPException(
                status_code=500,
                detail="Failed to set punch-out recording"
            )
    except Exception as e:
        logger.error(f"Error in set_punch_out: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/input-monitor")
async def set_global_input_monitor(request: InputMonitorRequest):
    """Enable or disable global input monitoring"""
    try:
        osc_client = get_osc_client()
        success = osc_client.set_global_input_monitor(request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Global input monitoring {action}")
            return {
                "status": "success",
                "action": "set_global_input_monitor",
                "enabled": request.enabled,
                "message": f"Global input monitoring {action}",
                "osc_address": "/toggle_monitor_input"
            }
        else:
            logger.error("Failed to set global input monitoring")
            raise HTTPException(
                status_code=500,
                detail="Failed to set global input monitoring"
            )
    except Exception as e:
        logger.error(f"Error in set_global_input_monitor: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/track/{track_number}/input-monitor")
async def set_track_input_monitor(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    request: InputMonitorRequest = ...
):
    """Enable or disable input monitoring for specific track"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        success = osc_client.set_track_input_monitor(track_index, request.enabled)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            logger.info(f"Track {track_number} input monitoring {action}")
            return {
                "status": "success",
                "action": "set_track_input_monitor",
                "track": track_number,
                "enabled": request.enabled,
                "message": f"Track {track_number} input monitoring {action}",
                "osc_address": f"/strip/{track_index}/monitor_input"
            }
        else:
            logger.error(f"Failed to set input monitoring for track {track_number}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set input monitoring for track {track_number}"
            )
    except Exception as e:
        logger.error(f"Error in set_track_input_monitor: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/status")
async def get_recording_status():
    """Get current recording status"""
    try:
        osc_client = get_osc_client()
        success = osc_client.get_recording_status()
        
        if success:
            # In a real implementation, this would parse actual status from Ardour
            # For now, return example status
            status = {
                "recording_enabled": False,
                "punch_in_enabled": False,
                "punch_out_enabled": False,
                "input_monitoring_enabled": False,
                "currently_recording": False,
                "armed_tracks": [],
                "message": "Recording status retrieved",
                "osc_address": "/recording/status"
            }
            
            logger.info("Recording status retrieved")
            return status
        else:
            logger.error("Failed to get recording status")
            raise HTTPException(
                status_code=500,
                detail="Failed to get recording status"
            )
    except Exception as e:
        logger.error(f"Error in get_recording_status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/start")
async def start_recording():
    """Start recording (convenience endpoint)"""
    try:
        osc_client = get_osc_client()
        
        # Enable recording and start transport
        enable_success = osc_client.set_recording_enable(True)
        start_success = osc_client.transport_play()
        
        if enable_success and start_success:
            logger.info("Recording started")
            return {
                "status": "success",
                "action": "start_recording",
                "message": "Recording started (enabled + transport play)",
                "osc_commands": ["/rec_enable_toggle", "/transport_play"]
            }
        else:
            logger.error("Failed to start recording")
            raise HTTPException(
                status_code=500,
                detail="Failed to start recording"
            )
    except Exception as e:
        logger.error(f"Error in start_recording: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/stop")
async def stop_recording():
    """Stop recording (convenience endpoint)"""
    try:
        osc_client = get_osc_client()
        
        # Stop transport and disable recording
        stop_success = osc_client.transport_stop()
        disable_success = osc_client.set_recording_enable(False)
        
        if stop_success and disable_success:
            logger.info("Recording stopped")
            return {
                "status": "success",
                "action": "stop_recording",
                "message": "Recording stopped (transport stop + disabled)",
                "osc_commands": ["/transport_stop", "/rec_enable_toggle"]
            }
        else:
            logger.error("Failed to stop recording")
            raise HTTPException(
                status_code=500,
                detail="Failed to stop recording"
            )
    except Exception as e:
        logger.error(f"Error in stop_recording: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )