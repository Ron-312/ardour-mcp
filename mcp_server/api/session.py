"""
Session management endpoints for Ardour MCP Server
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["session"])

class SnapshotRequest(BaseModel):
    """Request model for session snapshots"""
    switch_to_new: bool = Field(False, description="Switch to new snapshot after creation")

@router.post("/add-track-dialog")
async def open_add_track_dialog():
    """Open Ardour's Add Track/Bus dialog"""
    try:
        osc_client = get_osc_client()
        success = osc_client.open_add_track_dialog()
        
        if success:
            logger.info("Add Track/Bus dialog opened")
            return {
                "status": "success",
                "action": "open_add_track_dialog",
                "message": "Add Track/Bus dialog opened in Ardour",
                "osc_address": "/access_action",
                "osc_args": "Main/AddTrackBus"
            }
        else:
            logger.error("Failed to open Add Track/Bus dialog")
            raise HTTPException(
                status_code=500,
                detail="Failed to open Add Track/Bus dialog"
            )
    except Exception as e:
        logger.error(f"Error in open_add_track_dialog: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/save")
async def save_session():
    """Save current session"""
    try:
        osc_client = get_osc_client()
        success = osc_client.save_session()
        
        if success:
            logger.info("Session save initiated")
            return {
                "status": "success",
                "action": "save_session",
                "message": "Session save command sent to Ardour",
                "osc_address": "/access_action",
                "osc_args": "Main/Save"
            }
        else:
            logger.error("Failed to save session")
            raise HTTPException(
                status_code=500,
                detail="Failed to save session"
            )
    except Exception as e:
        logger.error(f"Error in save_session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/save-as")
async def save_session_as():
    """Open Save Session As dialog"""
    try:
        osc_client = get_osc_client()
        success = osc_client.save_session_as()
        
        if success:
            logger.info("Save Session As dialog opened")
            return {
                "status": "success",
                "action": "save_session_as",
                "message": "Save Session As dialog opened in Ardour",
                "osc_address": "/access_action",
                "osc_args": "Main/SaveAs"
            }
        else:
            logger.error("Failed to open Save Session As dialog")
            raise HTTPException(
                status_code=500,
                detail="Failed to open Save Session As dialog"
            )
    except Exception as e:
        logger.error(f"Error in save_session_as: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/snapshot")
async def create_snapshot(request: SnapshotRequest = SnapshotRequest()):
    """Create a session snapshot"""
    try:
        osc_client = get_osc_client()
        success = osc_client.create_snapshot(request.switch_to_new)
        
        if success:
            action_type = "switch" if request.switch_to_new else "stay"
            logger.info(f"Session snapshot created ({action_type})")
            return {
                "status": "success",
                "action": "create_snapshot",
                "switch_to_new": request.switch_to_new,
                "message": f"Session snapshot created ({'switching to new' if request.switch_to_new else 'staying on current'})",
                "osc_address": "/access_action",
                "osc_args": f"Main/QuickSnapshot{'Switch' if request.switch_to_new else 'Stay'}"
            }
        else:
            logger.error("Failed to create session snapshot")
            raise HTTPException(
                status_code=500,
                detail="Failed to create session snapshot"
            )
    except Exception as e:
        logger.error(f"Error in create_snapshot: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/undo")
async def undo_action():
    """Undo last action"""
    try:
        osc_client = get_osc_client()
        success = osc_client.undo_last_action()
        
        if success:
            logger.info("Undo command sent")
            return {
                "status": "success",
                "action": "undo",
                "message": "Undo command sent to Ardour",
                "osc_address": "/access_action",
                "osc_args": "Editor/undo"
            }
        else:
            logger.error("Failed to send undo command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send undo command"
            )
    except Exception as e:
        logger.error(f"Error in undo_action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/redo")
async def redo_action():
    """Redo last action"""
    try:
        osc_client = get_osc_client()
        success = osc_client.redo_last_action()
        
        if success:
            logger.info("Redo command sent")
            return {
                "status": "success",
                "action": "redo",
                "message": "Redo command sent to Ardour",
                "osc_address": "/access_action",
                "osc_args": "Editor/redo"
            }
        else:
            logger.error("Failed to send redo command")
            raise HTTPException(
                status_code=500,
                detail="Failed to send redo command"
            )
    except Exception as e:
        logger.error(f"Error in redo_action: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )