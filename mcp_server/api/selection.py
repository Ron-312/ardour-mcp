"""
Selection control endpoints for Ardour MCP Server
Implements Selected Strip Operations and Selected Plugin Operations
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client
from mcp_server.selection_manager import get_selection_manager, SelectionType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/selection", tags=["selection"])

# Request Models

class StripSelectRequest(BaseModel):
    """Request model for strip selection"""
    strip_id: int = Field(..., description="Strip ID to select", ge=0)
    select: bool = Field(True, description="True to select, False ignored")

class StripExpandRequest(BaseModel):
    """Request model for strip expansion"""
    strip_id: int = Field(..., description="Strip ID to expand", ge=0)
    expand: bool = Field(True, description="True to expand, False to contract")

class ExpandRequest(BaseModel):
    """Request model for expansion mode"""
    expand: bool = Field(..., description="True for expanded mode, False for select mode")

class HideRequest(BaseModel):
    """Request model for hide/show strip"""
    hide: bool = Field(..., description="True to hide, False to show")

class NameRequest(BaseModel):
    """Request model for strip name"""
    name: str = Field(..., description="Strip name", min_length=1, max_length=100)

class CommentRequest(BaseModel):
    """Request model for strip comment"""
    comment: str = Field(..., description="Strip comment", max_length=500)

class GroupRequest(BaseModel):
    """Request model for group assignment"""
    group_name: str = Field(..., description="Group name", max_length=100)

class GroupStateRequest(BaseModel):
    """Request model for group state"""
    state: int = Field(..., description="Group state (0 or 1)")

class BooleanRequest(BaseModel):
    """Request model for boolean operations"""
    enabled: bool = Field(..., description="True to enable, False to disable")

class GainRequest(BaseModel):
    """Request model for gain control"""
    gain_db: float = Field(..., description="Gain in dB", ge=-193, le=6)

class FaderRequest(BaseModel):
    """Request model for fader control"""
    position: float = Field(..., description="Fader position", ge=0.0, le=1.0)

class DeltaRequest(BaseModel):
    """Request model for delta operations"""
    delta: float = Field(..., description="Delta value")

class VCARequest(BaseModel):
    """Request model for VCA control"""
    name: str = Field(..., description="VCA name", max_length=100)
    state: int = Field(..., description="VCA state (0 or 1)")

class VCAToggleRequest(BaseModel):
    """Request model for VCA toggle"""
    name: str = Field(..., description="VCA name", max_length=100)

class AutomationRequest(BaseModel):
    """Request model for automation control"""
    mode: int = Field(..., description="Automation mode (0-3)")

class TouchRequest(BaseModel):
    """Request model for touch control"""
    state: int = Field(..., description="Touch state (0 or 1)")

class TrimRequest(BaseModel):
    """Request model for trim control"""
    trim_db: float = Field(..., description="Trim in dB", ge=-20, le=20)

class PanRequest(BaseModel):
    """Request model for pan control"""
    position: float = Field(..., description="Pan position", ge=0.0, le=1.0)

class SendGainRequest(BaseModel):
    """Request model for send gain control"""
    send_id: int = Field(..., description="Send ID", ge=0)
    gain_db: float = Field(..., description="Send gain in dB", ge=-193, le=6)

class SendFaderRequest(BaseModel):
    """Request model for send fader control"""
    send_id: int = Field(..., description="Send ID", ge=0)
    position: float = Field(..., description="Send fader position", ge=0.0, le=1.0)

class SendEnableRequest(BaseModel):
    """Request model for send enable control"""
    send_id: int = Field(..., description="Send ID", ge=0)
    enabled: bool = Field(..., description="Send enabled state")

class PluginSelectRequest(BaseModel):
    """Request model for plugin selection"""
    delta: int = Field(..., description="Plugin delta (-8 to 8)")

class PluginPageRequest(BaseModel):
    """Request model for plugin page"""
    direction: int = Field(..., description="Page direction (1 for up, -1 for down)")

class PluginActivateRequest(BaseModel):
    """Request model for plugin activation"""
    active: bool = Field(..., description="True to activate, False to bypass")

class PluginParameterRequest(BaseModel):
    """Request model for plugin parameter"""
    parameter_id: int = Field(..., description="Parameter ID (1-based)", ge=1)
    value: float = Field(..., description="Parameter value", ge=0.0, le=1.0)

# API Endpoints

@router.get(
    "/current",
    operation_id="get_current_selection"
)
async def get_current_selection():
    """Get current selection state"""
    try:
        selection_manager = get_selection_manager()
        return {
            "status": "success",
            "selection": selection_manager.to_dict()
        }
    except Exception as e:
        logger.error(f"Error getting current selection: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/strip/select",
    operation_id="select_strip"
)
async def select_strip(request: StripSelectRequest):
    """Select a strip (GUI selection)"""
    try:
        if not request.select:
            # 0 is ignored per Ardour spec
            return {"status": "ignored", "message": "Select=0 is ignored"}
        
        selection_manager = get_selection_manager()
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/strip/select", request.strip_id, 1)
        
        if success:
            # Update selection state
            selection_manager.select_strip(request.strip_id, force_gui_selection=True)
            
            logger.info(f"Strip {request.strip_id} selected")
            return {
                "status": "success",
                "action": "strip_select",
                "strip_id": request.strip_id,
                "message": f"Strip {request.strip_id} selected (GUI selection and expanded)",
                "osc_address": "/strip/select"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in select_strip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/strip/expand",
    operation_id="expand_strip"
)
async def expand_strip(request: StripExpandRequest):
    """Expand a strip (local expansion)"""
    try:
        selection_manager = get_selection_manager()
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/strip/expand", request.strip_id, 1 if request.expand else 0)
        
        if success:
            # Update selection state
            selection_manager.expand_strip(request.strip_id, request.expand)
            
            action = "expanded" if request.expand else "contracted"
            logger.info(f"Strip {request.strip_id} {action}")
            return {
                "status": "success",
                "action": "strip_expand",
                "strip_id": request.strip_id,
                "expanded": request.expand,
                "message": f"Strip {request.strip_id} {action}",
                "osc_address": "/strip/expand"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in expand_strip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/expand",
    operation_id="set_expansion_mode"
)
async def set_expansion_mode(request: ExpandRequest):
    """Set expansion mode for current selection"""
    try:
        selection_manager = get_selection_manager()
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/expand", 1 if request.expand else 0)
        
        if success:
            # Update selection state
            current_strip = selection_manager.get_selected_strip_id()
            if current_strip is not None:
                selection_manager.expand_strip(current_strip, request.expand)
            
            mode = "expanded" if request.expand else "select"
            logger.info(f"Selection mode set to {mode}")
            return {
                "status": "success",
                "action": "set_expansion_mode",
                "expanded": request.expand,
                "message": f"Selection mode set to {mode}",
                "osc_address": "/select/expand"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in set_expansion_mode: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/hide",
    operation_id="hide_strip"
)
async def hide_strip(request: HideRequest):
    """Hide/show selected strip"""
    try:
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/hide", 1 if request.hide else 0)
        
        if success:
            action = "hidden" if request.hide else "shown"
            logger.info(f"Selected strip {action}")
            return {
                "status": "success",
                "action": "hide_strip",
                "hidden": request.hide,
                "message": f"Selected strip {action}",
                "osc_address": "/select/hide"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in hide_strip: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/name",
    operation_id="set_strip_name"
)
async def set_strip_name(request: NameRequest):
    """Set name for selected strip"""
    try:
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/name", request.name)
        
        if success:
            logger.info(f"Selected strip renamed to '{request.name}'")
            return {
                "status": "success",
                "action": "set_strip_name",
                "name": request.name,
                "message": f"Selected strip renamed to '{request.name}'",
                "osc_address": "/select/name"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in set_strip_name: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/comment",
    operation_id="set_strip_comment"
)
async def set_strip_comment(request: CommentRequest):
    """Set comment for selected strip"""
    try:
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/comment", request.comment)
        
        if success:
            logger.info(f"Selected strip comment set to '{request.comment}'")
            return {
                "status": "success",
                "action": "set_strip_comment",
                "comment": request.comment,
                "message": f"Selected strip comment set",
                "osc_address": "/select/comment"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in set_strip_comment: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group",
    operation_id="set_strip_group"
)
async def set_strip_group(request: GroupRequest):
    """Set group for selected strip"""
    try:
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/group", request.group_name)
        
        if success:
            logger.info(f"Selected strip assigned to group '{request.group_name}'")
            return {
                "status": "success",
                "action": "set_strip_group",
                "group_name": request.group_name,
                "message": f"Selected strip assigned to group '{request.group_name}'",
                "osc_address": "/select/group"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
            
    except Exception as e:
        logger.error(f"Error in set_strip_group: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Group state operations
@router.post(
    "/group/enable",
    operation_id="set_group_enable"
)
async def set_group_enable(request: GroupStateRequest):
    """Set group enable state"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/enable", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_enable",
                "state": request.state,
                "message": f"Group enable state set to {request.state}",
                "osc_address": "/select/group/enable"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_enable: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/gain",
    operation_id="set_group_gain"
)
async def set_group_gain(request: GroupStateRequest):
    """Set group gain sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/gain", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_gain",
                "state": request.state,
                "message": f"Group gain sharing set to {request.state}",
                "osc_address": "/select/group/gain"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_gain: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/relative",
    operation_id="set_group_relative"
)
async def set_group_relative(request: GroupStateRequest):
    """Set group relative state"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/relative", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_relative",
                "state": request.state,
                "message": f"Group relative state set to {request.state}",
                "osc_address": "/select/group/relative"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_relative: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/mute",
    operation_id="set_group_mute"
)
async def set_group_mute(request: GroupStateRequest):
    """Set group mute sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/mute", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_mute",
                "state": request.state,
                "message": f"Group mute sharing set to {request.state}",
                "osc_address": "/select/group/mute"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_mute: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/solo",
    operation_id="set_group_solo"
)
async def set_group_solo(request: GroupStateRequest):
    """Set group solo sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/solo", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_solo",
                "state": request.state,
                "message": f"Group solo sharing set to {request.state}",
                "osc_address": "/select/group/solo"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_solo: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/recenable",
    operation_id="set_group_recenable"
)
async def set_group_recenable(request: GroupStateRequest):
    """Set group recenable sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/recenable", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_recenable",
                "state": request.state,
                "message": f"Group recenable sharing set to {request.state}",
                "osc_address": "/select/group/recenable"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_recenable: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/select",
    operation_id="set_group_select"
)
async def set_group_select(request: GroupStateRequest):
    """Set group select sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/select", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_select",
                "state": request.state,
                "message": f"Group select sharing set to {request.state}",
                "osc_address": "/select/group/select"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_select: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/active",
    operation_id="set_group_active"
)
async def set_group_active(request: GroupStateRequest):
    """Set group active sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/active", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_active",
                "state": request.state,
                "message": f"Group active sharing set to {request.state}",
                "osc_address": "/select/group/active"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_active: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/color",
    operation_id="set_group_color"
)
async def set_group_color(request: GroupStateRequest):
    """Set group color sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/color", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_color",
                "state": request.state,
                "message": f"Group color sharing set to {request.state}",
                "osc_address": "/select/group/color"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_color: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/group/monitoring",
    operation_id="set_group_monitoring"
)
async def set_group_monitoring(request: GroupStateRequest):
    """Set group monitoring sharing"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/group/monitoring", request.state)
        
        if success:
            return {
                "status": "success",
                "action": "set_group_monitoring",
                "state": request.state,
                "message": f"Group monitoring sharing set to {request.state}",
                "osc_address": "/select/group/monitoring"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_group_monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Basic strip operations
@router.post(
    "/recenable",
    operation_id="set_recenable"
)
async def set_recenable(request: BooleanRequest):
    """Set record enable for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/recenable", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_recenable",
                "enabled": request.enabled,
                "message": f"Record enable {action} for selected strip",
                "osc_address": "/select/recenable"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_recenable: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/record_safe",
    operation_id="set_record_safe"
)
async def set_record_safe(request: BooleanRequest):
    """Set record safe for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/record_safe", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_record_safe",
                "enabled": request.enabled,
                "message": f"Record safe {action} for selected strip",
                "osc_address": "/select/record_safe"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_record_safe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/mute",
    operation_id="set_mute"
)
async def set_mute(request: BooleanRequest):
    """Set mute for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/mute", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_mute",
                "enabled": request.enabled,
                "message": f"Mute {action} for selected strip",
                "osc_address": "/select/mute"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_mute: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/solo",
    operation_id="set_solo"
)
async def set_solo(request: BooleanRequest):
    """Set solo for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/solo", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_solo",
                "enabled": request.enabled,
                "message": f"Solo {action} for selected strip",
                "osc_address": "/select/solo"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_solo: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/solo_iso",
    operation_id="set_solo_iso"
)
async def set_solo_iso(request: BooleanRequest):
    """Set solo isolate for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/solo_iso", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_solo_iso",
                "enabled": request.enabled,
                "message": f"Solo isolate {action} for selected strip",
                "osc_address": "/select/solo_iso"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_solo_iso: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/solo_safe",
    operation_id="set_solo_safe"
)
async def set_solo_safe(request: BooleanRequest):
    """Set solo safe for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/solo_safe", 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_solo_safe",
                "enabled": request.enabled,
                "message": f"Solo safe {action} for selected strip",
                "osc_address": "/select/solo_safe"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_solo_safe: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/monitor_input",
    operation_id="set_monitor_input"
)
async def set_monitor_input(request: BooleanRequest):
    """Set monitor input for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/monitor_input", 1 if request.enabled else 0)
        
        if success:
            mode = "input" if request.enabled else "auto"
            return {
                "status": "success",
                "action": "set_monitor_input",
                "enabled": request.enabled,
                "message": f"Monitor mode set to {mode} for selected strip",
                "osc_address": "/select/monitor_input"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_monitor_input: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/monitor_disk",
    operation_id="set_monitor_disk"
)
async def set_monitor_disk(request: BooleanRequest):
    """Set monitor disk for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/monitor_disk", 1 if request.enabled else 0)
        
        if success:
            mode = "disk" if request.enabled else "auto"
            return {
                "status": "success",
                "action": "set_monitor_disk",
                "enabled": request.enabled,
                "message": f"Monitor mode set to {mode} for selected strip",
                "osc_address": "/select/monitor_disk"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_monitor_disk: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/polarity",
    operation_id="set_polarity"
)
async def set_polarity(request: BooleanRequest):
    """Set polarity invert for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/polarity", 1 if request.enabled else 0)
        
        if success:
            action = "inverted" if request.enabled else "normal"
            return {
                "status": "success",
                "action": "set_polarity",
                "enabled": request.enabled,
                "message": f"Polarity set to {action} for selected strip",
                "osc_address": "/select/polarity"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_polarity: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/gain",
    operation_id="set_gain"
)
async def set_gain(request: GainRequest):
    """Set gain for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/gain", request.gain_db)
        
        if success:
            return {
                "status": "success",
                "action": "set_gain",
                "gain_db": request.gain_db,
                "message": f"Gain set to {request.gain_db}dB for selected strip",
                "osc_address": "/select/gain"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_gain: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/fader",
    operation_id="set_fader"
)
async def set_fader(request: FaderRequest):
    """Set fader position for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/fader", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_fader",
                "position": request.position,
                "message": f"Fader set to {request.position} for selected strip",
                "osc_address": "/select/fader"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_fader: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/db_delta",
    operation_id="set_db_delta"
)
async def set_db_delta(request: DeltaRequest):
    """Apply gain delta to selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/db_delta", request.delta)
        
        if success:
            return {
                "status": "success",
                "action": "set_db_delta",
                "delta": request.delta,
                "message": f"Gain delta {request.delta}dB applied to selected strip",
                "osc_address": "/select/db_delta"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_db_delta: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/vca",
    operation_id="set_vca"
)
async def set_vca(request: VCARequest):
    """Set VCA control for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/vca", request.name, request.state)
        
        if success:
            action = "enabled" if request.state else "disabled"
            return {
                "status": "success",
                "action": "set_vca",
                "name": request.name,
                "state": request.state,
                "message": f"VCA '{request.name}' {action} for selected strip",
                "osc_address": "/select/vca"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_vca: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/vca/toggle",
    operation_id="toggle_vca"
)
async def toggle_vca(request: VCAToggleRequest):
    """Toggle VCA control for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/vca/toggle", request.name)
        
        if success:
            return {
                "status": "success",
                "action": "toggle_vca",
                "name": request.name,
                "message": f"VCA '{request.name}' toggled for selected strip",
                "osc_address": "/select/vca/toggle"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in toggle_vca: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/spill",
    operation_id="spill_strips"
)
async def spill_strips():
    """Spill strips related to selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/spill")
        
        if success:
            return {
                "status": "success",
                "action": "spill_strips",
                "message": "Strips spilled for selected strip",
                "osc_address": "/select/spill"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in spill_strips: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/trim",
    operation_id="set_trim"
)
async def set_trim(request: TrimRequest):
    """Set trim for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/trimdB", request.trim_db)
        
        if success:
            return {
                "status": "success",
                "action": "set_trim",
                "trim_db": request.trim_db,
                "message": f"Trim set to {request.trim_db}dB for selected strip",
                "osc_address": "/select/trimdB"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_trim: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Pan operations
@router.post(
    "/pan_stereo_position",
    operation_id="set_pan_stereo_position"
)
async def set_pan_stereo_position(request: PanRequest):
    """Set stereo pan position for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/pan_stereo_position", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_pan_stereo_position",
                "position": request.position,
                "message": f"Pan position set to {request.position} for selected strip",
                "osc_address": "/select/pan_stereo_position"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_pan_stereo_position: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/pan_stereo_width",
    operation_id="set_pan_stereo_width"
)
async def set_pan_stereo_width(request: PanRequest):
    """Set stereo pan width for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/pan_stereo_width", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_pan_stereo_width",
                "width": request.position,
                "message": f"Pan width set to {request.position} for selected strip",
                "osc_address": "/select/pan_stereo_width"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_pan_stereo_width: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/pan_elevation_position",
    operation_id="set_pan_elevation_position"
)
async def set_pan_elevation_position(request: PanRequest):
    """Set pan elevation position for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/pan_elevation_position", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_pan_elevation_position",
                "position": request.position,
                "message": f"Pan elevation set to {request.position} for selected strip",
                "osc_address": "/select/pan_elevation_position"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_pan_elevation_position: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/pan_frontback_position",
    operation_id="set_pan_frontback_position"
)
async def set_pan_frontback_position(request: PanRequest):
    """Set pan front/back position for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/pan_frontback_position", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_pan_frontback_position",
                "position": request.position,
                "message": f"Pan front/back set to {request.position} for selected strip",
                "osc_address": "/select/pan_frontback_position"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_pan_frontback_position: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/pan_lfe_control",
    operation_id="set_pan_lfe_control"
)
async def set_pan_lfe_control(request: PanRequest):
    """Set LFE control for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/pan_lfe_control", request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_pan_lfe_control",
                "value": request.position,
                "message": f"LFE control set to {request.position} for selected strip",
                "osc_address": "/select/pan_lfe_control"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_pan_lfe_control: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Send operations
@router.post(
    "/send_gain",
    operation_id="set_send_gain"
)
async def set_send_gain(request: SendGainRequest):
    """Set send gain for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/send_gain", request.send_id, request.gain_db)
        
        if success:
            return {
                "status": "success",
                "action": "set_send_gain",
                "send_id": request.send_id,
                "gain_db": request.gain_db,
                "message": f"Send {request.send_id} gain set to {request.gain_db}dB for selected strip",
                "osc_address": "/select/send_gain"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_send_gain: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/send_fader",
    operation_id="set_send_fader"
)
async def set_send_fader(request: SendFaderRequest):
    """Set send fader for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/send_fader", request.send_id, request.position)
        
        if success:
            return {
                "status": "success",
                "action": "set_send_fader",
                "send_id": request.send_id,
                "position": request.position,
                "message": f"Send {request.send_id} fader set to {request.position} for selected strip",
                "osc_address": "/select/send_fader"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_send_fader: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/send_enable",
    operation_id="set_send_enable"
)
async def set_send_enable(request: SendEnableRequest):
    """Set send enable for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/send_enable", request.send_id, 1 if request.enabled else 0)
        
        if success:
            action = "enabled" if request.enabled else "disabled"
            return {
                "status": "success",
                "action": "set_send_enable",
                "send_id": request.send_id,
                "enabled": request.enabled,
                "message": f"Send {request.send_id} {action} for selected strip",
                "osc_address": "/select/send_enable"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_send_enable: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/send_page",
    operation_id="set_send_page"
)
async def set_send_page(request: DeltaRequest):
    """Navigate send pages for selected strip"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/send_page", request.delta)
        
        if success:
            direction = "up" if request.delta > 0 else "down"
            return {
                "status": "success",
                "action": "set_send_page",
                "delta": request.delta,
                "message": f"Send page moved {direction} by {abs(request.delta)} for selected strip",
                "osc_address": "/select/send_page"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_send_page: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Plugin operations
@router.post(
    "/plugin",
    operation_id="select_plugin"
)
async def select_plugin(request: PluginSelectRequest):
    """Select plugin by delta from current plugin"""
    try:
        selection_manager = get_selection_manager()
        osc_client = get_osc_client()
        
        # Send OSC message
        success = osc_client.send_message("/select/plugin", request.delta)
        
        if success:
            # Update selection state
            selection_manager.select_plugin_delta(request.delta)
            
            current_plugin = selection_manager.get_selected_plugin_id()
            return {
                "status": "success",
                "action": "select_plugin",
                "delta": request.delta,
                "current_plugin": current_plugin,
                "message": f"Plugin selection moved by {request.delta}",
                "osc_address": "/select/plugin"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in select_plugin: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/plugin_page",
    operation_id="set_plugin_page"
)
async def set_plugin_page(request: PluginPageRequest):
    """Navigate plugin pages"""
    try:
        if request.direction == 0:
            # 0 is ignored per Ardour spec
            return {"status": "ignored", "message": "Direction=0 is ignored"}
        
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/plug_page", request.direction)
        
        if success:
            direction = "up" if request.direction > 0 else "down"
            return {
                "status": "success",
                "action": "set_plugin_page",
                "direction": request.direction,
                "message": f"Plugin page moved {direction}",
                "osc_address": "/select/plug_page"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_plugin_page: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/plugin/activate",
    operation_id="set_plugin_activate"
)
async def set_plugin_activate(request: PluginActivateRequest):
    """Activate/bypass selected plugin"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/plugin/activate", 1 if request.active else 0)
        
        if success:
            action = "activated" if request.active else "bypassed"
            return {
                "status": "success",
                "action": "set_plugin_activate",
                "active": request.active,
                "message": f"Selected plugin {action}",
                "osc_address": "/select/plugin/activate"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_plugin_activate: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/plugin/parameter",
    operation_id="set_plugin_parameter"
)
async def set_plugin_parameter(request: PluginParameterRequest):
    """Set parameter for selected plugin"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message("/select/plugin/parameter", request.parameter_id, request.value)
        
        if success:
            return {
                "status": "success",
                "action": "set_plugin_parameter",
                "parameter_id": request.parameter_id,
                "value": request.value,
                "message": f"Plugin parameter {request.parameter_id} set to {request.value}",
                "osc_address": "/select/plugin/parameter"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_plugin_parameter: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Automation and touch controls
@router.post(
    "/automation/{control_name}",
    operation_id="set_automation"
)
async def set_automation(
    control_name: str = Path(..., description="Control name (gain, mute, solo, etc.)"),
    request: AutomationRequest = ...
):
    """Set automation mode for selected strip control"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message(f"/select/{control_name}/automation", request.mode)
        
        if success:
            mode_names = {0: "Manual", 1: "Play", 2: "Write", 3: "Touch"}
            mode_name = mode_names.get(request.mode, f"Mode {request.mode}")
            
            return {
                "status": "success",
                "action": "set_automation",
                "control": control_name,
                "mode": request.mode,
                "mode_name": mode_name,
                "message": f"Automation mode for {control_name} set to {mode_name}",
                "osc_address": f"/select/{control_name}/automation"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_automation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/touch/{control_name}",
    operation_id="set_touch"
)
async def set_touch(
    control_name: str = Path(..., description="Control name (gain, mute, solo, etc.)"),
    request: TouchRequest = ...
):
    """Set touch state for selected strip control"""
    try:
        osc_client = get_osc_client()
        success = osc_client.send_message(f"/select/{control_name}/touch", request.state)
        
        if success:
            action = "touched" if request.state else "released"
            return {
                "status": "success",
                "action": "set_touch",
                "control": control_name,
                "state": request.state,
                "message": f"Touch state for {control_name} set to {action}",
                "osc_address": f"/select/{control_name}/touch"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send OSC message")
    except Exception as e:
        logger.error(f"Error in set_touch: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete(
    "/clear",
    operation_id="clear_selection"
)
async def clear_selection():
    """Clear current selection"""
    try:
        selection_manager = get_selection_manager()
        selection_manager.clear_selection()
        
        return {
            "status": "success",
            "action": "clear_selection",
            "message": "Selection cleared"
        }
    except Exception as e:
        logger.error(f"Error in clear_selection: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")