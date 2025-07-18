"""
Plugin control endpoints for Ardour MCP Server
"""

import logging
from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from mcp_server.osc_client import get_osc_client
from mcp_server.parameter_conversion import SmartParameterValue, ParameterType
from mcp_server.osc_listener import get_osc_listener, start_osc_listener
from mcp_server.plugin_parameter_mapper import get_parameter_mapper

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/plugins", tags=["plugins"])

class PluginInfo(BaseModel):
    """Plugin information model"""
    id: int = Field(..., description="Plugin ID (0-based)")
    name: str = Field(..., description="Plugin name")
    active: bool = Field(..., description="Plugin active/bypassed status")
    type: Optional[str] = Field(None, description="Plugin type hint (compressor, eq, etc)")

class PluginListResponse(BaseModel):
    """Response model for plugin list"""
    track: int = Field(..., description="Track number")
    plugins: List[PluginInfo] = Field(..., description="List of plugins on track")
    count: int = Field(..., description="Number of plugins")

class ParameterInfo(BaseModel):
    """Plugin parameter information"""
    id: int = Field(..., description="Parameter ID (1-based)")
    name: str = Field(..., description="Parameter name")
    value_raw: float = Field(..., description="Raw OSC value (0.0-1.0)")
    value_display: Optional[str] = Field(None, description="Human-readable value")
    min_value: Optional[float] = Field(None, description="Minimum parameter value")
    max_value: Optional[float] = Field(None, description="Maximum parameter value")
    unit: Optional[str] = Field(None, description="Parameter unit (dB, Hz, etc)")

class PluginParametersResponse(BaseModel):
    """Response model for plugin parameters"""
    track: int = Field(..., description="Track number")
    plugin_id: int = Field(..., description="Plugin ID")
    plugin_name: str = Field(..., description="Plugin name")
    parameters: List[ParameterInfo] = Field(..., description="List of parameters")
    count: int = Field(..., description="Number of parameters")

class PluginActivateRequest(BaseModel):
    """Request model for plugin activation control"""
    active: bool = Field(..., description="True to activate plugin, False to bypass")

class SmartParameterRequest(BaseModel):
    """Request model for smart parameter control with real-world values"""
    # dB values
    db: Optional[float] = Field(None, description="dB value (-60 to +12)")
    
    # Frequency values  
    hz: Optional[float] = Field(None, description="Frequency in Hz (20 to 20000)")
    
    # Ratio values
    ratio: Optional[float] = Field(None, description="Compression ratio (1.0 to 20.0)")
    
    # Percentage values
    percent: Optional[float] = Field(None, description="Percentage (0 to 100)")
    
    # Time values
    ms: Optional[float] = Field(None, description="Time in milliseconds (0.1 to 1000)")
    sec: Optional[float] = Field(None, description="Time in seconds (0.001 to 10)")
    
    # Q factor
    q: Optional[float] = Field(None, description="Q factor (0.1 to 30)")
    
    # Raw fallback
    value: Optional[float] = Field(None, description="Raw OSC value (0.0 to 1.0)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.dict().items() if v is not None}

@router.get(
    "/track/{track_number}/plugins", 
    response_model=PluginListResponse,
    operation_id="list_track_plugins"
)
async def list_track_plugins(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256)
):
    """List all plugins on a specific track using real OSC discovery"""
    try:
        # Ensure OSC listener is running
        start_osc_listener()
        
        osc_listener = get_osc_listener()
        track_index = track_number - 1
        
        # Use real plugin discovery
        discovered_plugins = osc_listener.discover_plugins(track_index, timeout=5.0)
        
        # Convert discovered plugins to API format
        plugins = []
        for plugin_info in discovered_plugins:
            plugin_type = _determine_plugin_type(plugin_info.name)
            
            plugins.append(PluginInfo(
                id=plugin_info.id,
                name=plugin_info.name,
                active=plugin_info.enabled,
                type=plugin_type
            ))
            
        logger.info(f"Discovered {len(plugins)} plugins for track {track_number}")
        
        return PluginListResponse(
            track=track_number,
            plugins=plugins,
            count=len(plugins)
        )
        
    except Exception as e:
        logger.error(f"Error in list_track_plugins: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/parameters", 
    response_model=PluginParametersResponse,
    operation_id="get_plugin_parameters"
)
async def get_plugin_parameters(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32)
):
    """Get detailed parameter information for a specific plugin using real OSC discovery"""
    try:
        # Ensure OSC listener is running
        start_osc_listener()
        
        osc_listener = get_osc_listener()
        track_index = track_number - 1
        
        # Use real parameter discovery
        discovered_params = osc_listener.discover_plugin_parameters(track_index, plugin_id, timeout=5.0)
        
        # Convert discovered parameters to API format
        parameters = []
        for param in discovered_params:
            # Generate display value based on parameter type
            display_value = _format_parameter_value(param.value, param.type, param.unit)
            
            parameters.append(ParameterInfo(
                id=param.id,
                name=param.name,
                value_raw=param.value,
                value_display=display_value,
                min_value=param.min_value,
                max_value=param.max_value,
                unit=param.unit
            ))
            
        # Get plugin name from discovered data
        plugin_name = "Unknown Plugin"
        tracks = osc_listener.get_all_tracks()
        if track_index in tracks:
            for plugin in tracks[track_index].plugins:
                if plugin.id == plugin_id:
                    plugin_name = plugin.name
                    break
        
        logger.info(f"Discovered {len(parameters)} parameters for track {track_number} plugin {plugin_id}")
        
        return PluginParametersResponse(
            track=track_number,
            plugin_id=plugin_id,
            plugin_name=plugin_name,
            parameters=parameters,
            count=len(parameters)
        )
        
    except Exception as e:
        logger.error(f"Error in get_plugin_parameters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/info",
    operation_id="get_plugin_info"
)
async def get_plugin_info(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32)
):
    """Get detailed information about a specific plugin"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        # Request plugin info
        success = osc_client.get_plugin_info(track_index, plugin_id)
        
        if success:
            # Example plugin info - in real implementation, parse OSC feedback
            plugin_info = {
                "track": track_number,
                "plugin_id": plugin_id,
                "name": "ACE Compressor" if plugin_id == 0 else "ACE EQ",
                "active": True,
                "type": "compressor" if plugin_id == 0 else "eq",
                "vendor": "Ardour Community Edition",
                "version": "1.0",
                "parameter_count": 4 if plugin_id == 0 else 3,
                "osc_address": f"/select/plugin",
                "capabilities": [
                    "parameter_control",
                    "bypass",
                    "automation"
                ]
            }
            
            logger.info(f"Got plugin info for track {track_number} plugin {plugin_id}")
            return plugin_info
        else:
            logger.error(f"Failed to get plugin info for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get plugin info for track {track_number} plugin {plugin_id}"
            )
    except Exception as e:
        logger.error(f"Error in get_plugin_info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/discovery/scan",
    operation_id="scan_all_plugins"
)
async def scan_all_plugins():
    """Scan all tracks for plugins and return comprehensive plugin map using real OSC discovery"""
    try:
        # Ensure OSC listener is running
        start_osc_listener()
        
        osc_listener = get_osc_listener()
        
        # Scan multiple tracks (typical session might have 8-32 tracks)
        tracks_to_scan = range(8)  # Scan first 8 tracks
        total_plugins = 0
        plugin_types = {}
        tracks_data = {}
        
        for track_index in tracks_to_scan:
            plugins = osc_listener.discover_plugins(track_index, timeout=3.0)
            if plugins:
                track_plugins = []
                for plugin in plugins:
                    plugin_type = _determine_plugin_type(plugin.name)
                    
                    track_plugins.append({
                        "id": plugin.id,
                        "name": plugin.name,
                        "type": plugin_type,
                        "active": plugin.enabled
                    })
                    
                    # Count plugin types
                    if plugin_type in plugin_types:
                        plugin_types[plugin_type] += 1
                    else:
                        plugin_types[plugin_type] = 1
                        
                    total_plugins += 1
                    
                tracks_data[str(track_index + 1)] = track_plugins
                
        from datetime import datetime
        
        plugin_map = {
            "scan_time": datetime.now().isoformat() + "Z",
            "total_tracks": len([k for k, v in tracks_data.items() if v]),
            "total_plugins": total_plugins,
            "tracks": tracks_data,
            "plugin_types": plugin_types
        }
        
        logger.info(f"Completed plugin discovery scan: {total_plugins} plugins across {len(tracks_data)} tracks")
        return plugin_map
        
    except Exception as e:
        logger.error(f"Error in scan_all_plugins: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/activate",
    operation_id="set_plugin_activate"
)
async def set_plugin_activate(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    request: PluginActivateRequest = ...
):
    """Activate or bypass a plugin"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        # Select track and plugin, then activate/deactivate
        success = osc_client.set_plugin_activate(track_index, plugin_id, request.active)
        
        if success:
            action = "activated" if request.active else "bypassed"
            logger.info(f"Plugin {action}: track {track_number} plugin {plugin_id}")
            return {
                "status": "success",
                "action": "set_plugin_activate",
                "track": track_number,
                "plugin_id": plugin_id,
                "active": request.active,
                "message": f"Plugin {plugin_id} {action} on track {track_number}",
                "osc_address": "/select/plugin/activate"
            }
        else:
            logger.error(f"Failed to set plugin activation for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set plugin activation for track {track_number} plugin {plugin_id}"
            )
    except Exception as e:
        logger.error(f"Error in set_plugin_activate: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/bypass",
    operation_id="bypass_plugin"
)
async def bypass_plugin(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32)
):
    """Bypass a plugin (convenience endpoint)"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        success = osc_client.set_plugin_activate(track_index, plugin_id, False)
        
        if success:
            logger.info(f"Plugin bypassed: track {track_number} plugin {plugin_id}")
            return {
                "status": "success",
                "action": "bypass_plugin",
                "track": track_number,
                "plugin_id": plugin_id,
                "active": False,
                "message": f"Plugin {plugin_id} bypassed on track {track_number}",
                "osc_address": "/select/plugin/activate"
            }
        else:
            logger.error(f"Failed to bypass plugin for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to bypass plugin for track {track_number} plugin {plugin_id}"
            )
    except Exception as e:
        logger.error(f"Error in bypass_plugin: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/enable",
    operation_id="enable_plugin"
)
async def enable_plugin(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32)
):
    """Enable a plugin (convenience endpoint)"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        success = osc_client.set_plugin_activate(track_index, plugin_id, True)
        
        if success:
            logger.info(f"Plugin enabled: track {track_number} plugin {plugin_id}")
            return {
                "status": "success",
                "action": "enable_plugin",
                "track": track_number,
                "plugin_id": plugin_id,
                "active": True,
                "message": f"Plugin {plugin_id} enabled on track {track_number}",
                "osc_address": "/select/plugin/activate"
            }
        else:
            logger.error(f"Failed to enable plugin for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to enable plugin for track {track_number} plugin {plugin_id}"
            )
    except Exception as e:
        logger.error(f"Error in enable_plugin: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/parameter/{parameter_name}",
    operation_id="set_smart_parameter"
)
async def set_smart_parameter(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    parameter_name: str = Path(..., description="Parameter name (e.g., 'threshold', 'frequency')"),
    request: SmartParameterRequest = ...
):
    """Set plugin parameter with smart real-world value conversion"""
    try:
        osc_client = get_osc_client()
        track_index = track_number - 1
        
        # Determine parameter type based on name and available values
        param_type = _determine_parameter_type(parameter_name, request.to_dict())
        
        # Create smart parameter converter
        smart_param = SmartParameterValue(param_type)
        
        # Convert real-world value to OSC 0-1 value
        osc_value = smart_param.to_osc(request.to_dict())
        
        # Get parameter ID for this parameter name (simplified for now)
        parameter_id = _get_parameter_id(parameter_name)
        
        # Send OSC message
        success = osc_client.set_plugin_parameter(track_index, plugin_id, parameter_id, osc_value)
        
        if success:
            # Convert back to show what was actually set
            actual_value = smart_param.from_osc(osc_value)
            
            logger.info(f"Parameter set: track {track_number} plugin {plugin_id} {parameter_name} = {actual_value}")
            return {
                "status": "success",
                "action": "set_smart_parameter",
                "track": track_number,
                "plugin_id": plugin_id,
                "parameter_name": parameter_name,
                "parameter_id": parameter_id,
                "input_value": request.to_dict(),
                "actual_value": actual_value,
                "osc_value": osc_value,
                "message": f"Parameter '{parameter_name}' set to {actual_value}",
                "osc_address": f"/select/plugin/parameter"
            }
        else:
            logger.error(f"Failed to set parameter {parameter_name} for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set parameter {parameter_name} for track {track_number} plugin {plugin_id}"
            )
    except ValueError as e:
        logger.error(f"Parameter conversion error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Parameter conversion error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in set_smart_parameter: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/compressor/threshold",
    operation_id="set_compressor_threshold"
)
async def set_compressor_threshold(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    request: SmartParameterRequest = ...
):
    """Set compressor threshold (convenience endpoint)"""
    if request.db is None:
        raise HTTPException(status_code=422, detail="Compressor threshold requires 'db' value")
    
    # Use the generic smart parameter endpoint
    return await set_smart_parameter(track_number, plugin_id, "threshold", request)

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/compressor/ratio",
    operation_id="set_compressor_ratio"
)
async def set_compressor_ratio(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    request: SmartParameterRequest = ...
):
    """Set compressor ratio (convenience endpoint)"""
    if request.ratio is None:
        raise HTTPException(status_code=422, detail="Compressor ratio requires 'ratio' value")
    
    return await set_smart_parameter(track_number, plugin_id, "ratio", request)

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/eq/frequency",
    operation_id="set_eq_frequency"
)
async def set_eq_frequency(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    request: SmartParameterRequest = ...
):
    """Set EQ frequency (convenience endpoint)"""
    if request.hz is None:
        raise HTTPException(status_code=422, detail="EQ frequency requires 'hz' value")
    
    return await set_smart_parameter(track_number, plugin_id, "frequency", request)

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/eq/gain",
    operation_id="set_eq_gain"
)
async def set_eq_gain(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    request: SmartParameterRequest = ...
):
    """Set EQ gain (convenience endpoint)"""
    if request.db is None:
        raise HTTPException(status_code=422, detail="EQ gain requires 'db' value")
    
    return await set_smart_parameter(track_number, plugin_id, "gain", request)

# Dynamic Parameter Mapping Endpoints

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/parameters/names",
    operation_id="list_parameter_names"
)
async def list_parameter_names(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32)
):
    """List all available parameter names for a plugin"""
    try:
        track_index = track_number - 1
        parameter_mapper = get_parameter_mapper()
        
        parameter_names = parameter_mapper.list_parameter_names(track_index, plugin_id)
        
        if parameter_names:
            logger.info(f"Found {len(parameter_names)} parameter names for track {track_number} plugin {plugin_id}")
            return {
                "track": track_number,
                "plugin_id": plugin_id,
                "parameter_names": parameter_names,
                "count": len(parameter_names)
            }
        else:
            logger.warning(f"No parameter names found for track {track_number} plugin {plugin_id}")
            return {
                "track": track_number,
                "plugin_id": plugin_id,
                "parameter_names": [],
                "count": 0
            }
            
    except Exception as e:
        logger.error(f"Error listing parameter names: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/parameter/{parameter_name}/info",
    operation_id="get_parameter_info"
)
async def get_parameter_info(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    parameter_name: str = Path(..., description="Parameter name")
):
    """Get detailed information about a specific parameter"""
    try:
        track_index = track_number - 1
        parameter_mapper = get_parameter_mapper()
        
        param_info = parameter_mapper.get_parameter_info(track_index, plugin_id, parameter_name)
        
        if param_info:
            logger.info(f"Found parameter info for {parameter_name} on track {track_number} plugin {plugin_id}")
            return {
                "track": track_number,
                "plugin_id": plugin_id,
                "parameter": param_info
            }
        else:
            logger.warning(f"Parameter {parameter_name} not found for track {track_number} plugin {plugin_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Parameter '{parameter_name}' not found for track {track_number} plugin {plugin_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parameter info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/parameters/search",
    operation_id="search_parameters"
)
async def search_parameters(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    pattern: str = Path(..., description="Search pattern")
):
    """Search for parameters by name pattern"""
    try:
        track_index = track_number - 1
        parameter_mapper = get_parameter_mapper()
        
        matches = parameter_mapper.find_parameter_by_pattern(track_index, plugin_id, pattern)
        
        results = []
        for match in matches:
            results.append({
                "name": match.parameter_name,
                "id": match.parameter_id,
                "type": match.parameter_type,
                "unit": match.unit,
                "current_value": match.current_value
            })
            
        logger.info(f"Found {len(results)} parameters matching pattern '{pattern}'")
        return {
            "track": track_number,
            "plugin_id": plugin_id,
            "pattern": pattern,
            "matches": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching parameters: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/track/{track_number}/plugin/{plugin_id}/parameters/suggestions",
    operation_id="get_parameter_suggestions"
)
async def get_parameter_suggestions(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    input_name: str = Path(..., description="Input parameter name for suggestions")
):
    """Get smart parameter name suggestions"""
    try:
        track_index = track_number - 1
        parameter_mapper = get_parameter_mapper()
        
        suggestions = parameter_mapper.get_smart_parameter_suggestions(track_index, plugin_id, input_name)
        
        logger.info(f"Generated {len(suggestions)} suggestions for input '{input_name}'")
        return {
            "track": track_number,
            "plugin_id": plugin_id,
            "input_name": input_name,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error getting parameter suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post(
    "/track/{track_number}/plugin/{plugin_id}/parameter/{parameter_name}/dynamic",
    operation_id="set_dynamic_parameter"
)
async def set_dynamic_parameter(
    track_number: int = Path(..., description="Track number (1-based)", ge=1, le=256),
    plugin_id: int = Path(..., description="Plugin ID (0-based)", ge=0, le=32),
    parameter_name: str = Path(..., description="Parameter name"),
    request: SmartParameterRequest = ...
):
    """Set plugin parameter using dynamic mapping (replaces hardcoded parameter ID lookup)"""
    try:
        track_index = track_number - 1
        parameter_mapper = get_parameter_mapper()
        osc_client = get_osc_client()
        
        # Get parameter ID using dynamic mapping
        parameter_id = parameter_mapper.get_parameter_id(track_index, plugin_id, parameter_name)
        
        if parameter_id is None:
            # Try to get suggestions for the parameter name
            suggestions = parameter_mapper.get_smart_parameter_suggestions(track_index, plugin_id, parameter_name)
            
            if suggestions:
                raise HTTPException(
                    status_code=404,
                    detail=f"Parameter '{parameter_name}' not found. Did you mean: {', '.join(suggestions)}?"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Parameter '{parameter_name}' not found for track {track_number} plugin {plugin_id}"
                )
        
        # Get parameter info for smart conversion
        param_info = parameter_mapper.get_parameter_info(track_index, plugin_id, parameter_name)
        
        # Determine parameter type based on discovered parameter info
        param_type = _determine_parameter_type_from_info(param_info, request.to_dict())
        
        # Create smart parameter converter
        smart_param = SmartParameterValue(param_type)
        
        # Convert real-world value to OSC 0-1 value
        osc_value = smart_param.to_osc(request.to_dict())
        
        # Send OSC message using discovered parameter ID
        success = osc_client.set_plugin_parameter(track_index, plugin_id, parameter_id, osc_value)
        
        if success:
            # Update cached value
            parameter_mapper.update_parameter_value(track_index, plugin_id, parameter_name, osc_value)
            
            # Convert back to show what was actually set
            actual_value = smart_param.from_osc(osc_value)
            
            logger.info(f"Dynamic parameter set: track {track_number} plugin {plugin_id} {parameter_name} = {actual_value}")
            return {
                "status": "success",
                "action": "set_dynamic_parameter",
                "track": track_number,
                "plugin_id": plugin_id,
                "parameter_name": parameter_name,
                "parameter_id": parameter_id,
                "input_value": request.to_dict(),
                "actual_value": actual_value,
                "osc_value": osc_value,
                "parameter_info": param_info,
                "message": f"Parameter '{parameter_name}' set to {actual_value}",
                "osc_address": f"/select/plugin/parameter"
            }
        else:
            logger.error(f"Failed to set dynamic parameter {parameter_name}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set parameter {parameter_name}"
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Dynamic parameter conversion error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Parameter conversion error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in set_dynamic_parameter: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def _determine_parameter_type_from_info(param_info: Dict[str, Any], value_dict: Dict[str, Any]) -> ParameterType:
    """Determine parameter type based on discovered parameter info and provided values"""
    
    # First check what type of value was provided
    if "db" in value_dict:
        if "threshold" in param_info['name'].lower():
            return ParameterType.DB_THRESHOLD
        else:
            return ParameterType.DB_GAIN
    elif "hz" in value_dict:
        return ParameterType.FREQUENCY
    elif "ratio" in value_dict:
        return ParameterType.RATIO
    elif "percent" in value_dict:
        return ParameterType.PERCENTAGE
    elif "ms" in value_dict:
        return ParameterType.TIME_MS
    elif "sec" in value_dict:
        return ParameterType.TIME_SEC
    elif "q" in value_dict:
        return ParameterType.Q_FACTOR
    elif "value" in value_dict:
        return ParameterType.RAW
    else:
        # Fallback to parameter type from discovery
        param_type = param_info.get('type', 'generic')
        if param_type == 'frequency':
            return ParameterType.FREQUENCY
        elif param_type == 'gain' or param_type == 'threshold':
            return ParameterType.DB_GAIN if param_type == 'gain' else ParameterType.DB_THRESHOLD
        elif param_type == 'ratio':
            return ParameterType.RATIO
        elif param_type == 'time':
            return ParameterType.TIME_MS
        else:
            return ParameterType.RAW

def _determine_parameter_type(parameter_name: str, value_dict: Dict[str, Any]) -> ParameterType:
    """Determine parameter type based on parameter name and available values"""
    
    # Check what type of value was provided
    if "db" in value_dict:
        if "threshold" in parameter_name.lower():
            return ParameterType.DB_THRESHOLD
        else:
            return ParameterType.DB_GAIN
    elif "hz" in value_dict:
        return ParameterType.FREQUENCY
    elif "ratio" in value_dict:
        return ParameterType.RATIO
    elif "percent" in value_dict:
        return ParameterType.PERCENTAGE
    elif "ms" in value_dict:
        return ParameterType.TIME_MS
    elif "sec" in value_dict:
        return ParameterType.TIME_SEC
    elif "q" in value_dict:
        return ParameterType.Q_FACTOR
    elif "value" in value_dict:
        return ParameterType.RAW
    else:
        # Fallback based on parameter name
        param_lower = parameter_name.lower()
        if "threshold" in param_lower:
            return ParameterType.DB_THRESHOLD
        elif "gain" in param_lower:
            return ParameterType.DB_GAIN
        elif "freq" in param_lower:
            return ParameterType.FREQUENCY
        elif "ratio" in param_lower:
            return ParameterType.RATIO
        elif "attack" in param_lower or "release" in param_lower:
            return ParameterType.TIME_MS
        else:
            return ParameterType.RAW

def _get_parameter_id(parameter_name: str) -> int:
    """Get parameter ID for parameter name (simplified mapping)"""
    # In a real implementation, this would query Ardour for parameter mappings
    # For now, use a simple mapping based on common parameter names
    parameter_map = {
        "threshold": 1,
        "ratio": 2,
        "attack": 3,
        "release": 4,
        "gain": 1,
        "frequency": 1,
        "freq": 1,
        "low_freq": 1,
        "mid_freq": 2,
        "high_freq": 3,
        "low_gain": 2,
        "mid_gain": 3,
        "high_gain": 4,
        "q": 4,
        "bandwidth": 5
    }
    
    return parameter_map.get(parameter_name.lower(), 1)

def _determine_plugin_type(plugin_name: str) -> str:
    """Determine plugin type based on plugin name"""
    name_lower = plugin_name.lower()
    
    if 'compressor' in name_lower or 'comp' in name_lower:
        return 'compressor'
    elif 'eq' in name_lower or 'equalizer' in name_lower:
        return 'eq'
    elif 'reverb' in name_lower or 'verb' in name_lower:
        return 'reverb'
    elif 'delay' in name_lower or 'echo' in name_lower:
        return 'delay'
    elif 'limiter' in name_lower or 'limit' in name_lower:
        return 'limiter'
    elif 'gate' in name_lower or 'expander' in name_lower:
        return 'gate'
    elif 'distortion' in name_lower or 'overdrive' in name_lower:
        return 'distortion'
    elif 'chorus' in name_lower or 'flanger' in name_lower or 'phaser' in name_lower:
        return 'modulation'
    elif 'filter' in name_lower:
        return 'filter'
    elif 'synth' in name_lower:
        return 'instrument'
    else:
        return 'unknown'
        
def _format_parameter_value(value: float, param_type: str, unit: str) -> str:
    """Format parameter value for display"""
    if param_type == 'frequency':
        # Convert 0-1 to Hz range (20-20000)
        hz_value = 20 + (value * (20000 - 20))
        return f"{hz_value:.1f} Hz"
    elif param_type == 'gain' or param_type == 'threshold':
        # Convert 0-1 to dB range (-60 to +12)
        db_value = -60 + (value * (12 - (-60)))
        return f"{db_value:.1f} dB"
    elif param_type == 'ratio':
        # Convert 0-1 to ratio (1:1 to 20:1)
        ratio_value = 1 + (value * (20 - 1))
        return f"{ratio_value:.1f}:1"
    elif param_type == 'time':
        # Convert 0-1 to ms range (0.1 to 1000)
        ms_value = 0.1 + (value * (1000 - 0.1))
        return f"{ms_value:.1f} ms"
    elif unit:
        return f"{value:.2f} {unit}"
    else:
        return f"{value:.2f}"