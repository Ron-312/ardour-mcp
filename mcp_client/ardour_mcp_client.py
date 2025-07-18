#!/usr/bin/env python3
"""
Ardour MCP Client - Full MCP protocol implementation for Cursor integration
"""

import argparse
import json
import sys
import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# MCP Server configuration
MCP_SERVER_URL = "http://localhost:8000"

def load_manifest():
    """Load the MCP manifest from JSON file"""
    manifest_path = Path(__file__).parent / "mcp_ardour.json"
    
    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "error": "Manifest file not found",
            "path": str(manifest_path)
        }
    except json.JSONDecodeError as e:
        return {
            "error": "Invalid JSON in manifest",
            "details": str(e)
        }

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by calling the MCP server API"""
    try:
        # Map tool names to API endpoints - using the ardour_ prefixed names
        endpoint_map = {
            # Transport controls
            "ardour_transport_play": ("POST", "/transport/play"),
            "ardour_transport_stop": ("POST", "/transport/stop"),
            "ardour_transport_rewind": ("POST", "/transport/rewind"),
            "ardour_transport_fast_forward": ("POST", "/transport/fast-forward"),
            "ardour_transport_goto_start": ("POST", "/transport/goto-start"),
            "ardour_transport_goto_end": ("POST", "/transport/goto-end"),
            "ardour_transport_toggle_roll": ("POST", "/transport/toggle-roll"),
            "ardour_transport_toggle_loop": ("POST", "/transport/toggle-loop"),
            "ardour_transport_set_speed": ("POST", "/transport/speed"),
            "ardour_transport_add_marker": ("POST", "/transport/add-marker"),
            "ardour_transport_next_marker": ("POST", "/transport/next-marker"),
            "ardour_transport_prev_marker": ("POST", "/transport/prev-marker"),
            
            # Track controls
            "ardour_track_set_fader": ("POST", "/track/{track_number}/fader"),
            "ardour_track_set_mute": ("POST", "/track/{track_number}/mute"),
            "ardour_track_set_solo": ("POST", "/track/{track_number}/solo"),
            "ardour_track_set_name": ("POST", "/track/{track_number}/name"),
            "ardour_track_set_record_enable": ("POST", "/track/{track_number}/record-enable"),
            "ardour_track_set_record_safe": ("POST", "/track/{track_number}/record-safe"),
            "ardour_track_set_pan": ("POST", "/track/{track_number}/pan"),
            "ardour_track_list": ("GET", "/track/list"),
            
            # Session controls
            "ardour_session_open_add_track_dialog": ("POST", "/session/add-track-dialog"),
            "ardour_session_save": ("POST", "/session/save"),
            "ardour_session_save_as": ("POST", "/session/save-as"),
            "ardour_session_create_snapshot": ("POST", "/session/snapshot"),
            "ardour_session_undo": ("POST", "/session/undo"),
            "ardour_session_redo": ("POST", "/session/redo"),
            
            # Selection controls (the working features)
            "ardour_select_strip": ("POST", "/selection/strip/select"),
            "ardour_expand_strip": ("POST", "/selection/strip/expand"),
            "ardour_set_expansion_mode": ("POST", "/selection/expand"),
            "ardour_hide_strip": ("POST", "/selection/hide"),
            "ardour_set_strip_name": ("POST", "/selection/name"),
            "ardour_set_strip_comment": ("POST", "/selection/comment"),
            "ardour_set_strip_group": ("POST", "/selection/group"),
            "ardour_set_group_enable": ("POST", "/selection/group/enable"),
            "ardour_set_group_gain": ("POST", "/selection/group/gain"),
            "ardour_set_group_relative": ("POST", "/selection/group/relative"),
            "ardour_set_group_mute": ("POST", "/selection/group/mute"),
            "ardour_set_group_solo": ("POST", "/selection/group/solo"),
            "ardour_set_group_recenable": ("POST", "/selection/group/recenable"),
            "ardour_set_group_select": ("POST", "/selection/group/select"),
            "ardour_set_group_active": ("POST", "/selection/group/active"),
            "ardour_set_group_color": ("POST", "/selection/group/color"),
            "ardour_set_group_monitoring": ("POST", "/selection/group/monitoring"),
            
            # Selected strip controls
            "ardour_set_recenable": ("POST", "/selection/recenable"),
            "ardour_set_record_safe": ("POST", "/selection/record_safe"),
            "ardour_set_mute": ("POST", "/selection/mute"),
            "ardour_set_solo": ("POST", "/selection/solo"),
            "ardour_set_solo_iso": ("POST", "/selection/solo_iso"),
            "ardour_set_solo_safe": ("POST", "/selection/solo_safe"),
            "ardour_set_monitor_input": ("POST", "/selection/monitor_input"),
            "ardour_set_monitor_disk": ("POST", "/selection/monitor_disk"),
            "ardour_set_polarity": ("POST", "/selection/polarity"),
            "ardour_set_gain": ("POST", "/selection/gain"),
            "ardour_set_fader": ("POST", "/selection/fader"),
            "ardour_set_db_delta": ("POST", "/selection/db_delta"),
            "ardour_set_trim": ("POST", "/selection/trim"),
            
            # Pan controls
            "ardour_set_pan_stereo_position": ("POST", "/selection/pan_stereo_position"),
            "ardour_set_pan_stereo_width": ("POST", "/selection/pan_stereo_width"),
            "ardour_set_pan_elevation_position": ("POST", "/selection/pan_elevation_position"),
            "ardour_set_pan_frontback_position": ("POST", "/selection/pan_frontback_position"),
            "ardour_set_pan_lfe_control": ("POST", "/selection/pan_lfe_control"),
            
            # Send controls
            "ardour_set_send_gain": ("POST", "/selection/send_gain"),
            "ardour_set_send_fader": ("POST", "/selection/send_fader"),
            "ardour_set_send_enable": ("POST", "/selection/send_enable"),
            
            # Plugin controls
            "ardour_select_plugin": ("POST", "/selection/plugin"),
            "ardour_set_plugin_page": ("POST", "/selection/plugin_page"),
            "ardour_set_plugin_activate": ("POST", "/selection/plugin/activate"),
            "ardour_set_plugin_parameter": ("POST", "/selection/plugin/parameter"),
            
            # VCA controls
            "ardour_set_vca": ("POST", "/selection/vca"),
            "ardour_toggle_vca": ("POST", "/selection/vca/toggle"),
            "ardour_spill_strips": ("POST", "/selection/spill"),
            
            # Automation and touch
            "ardour_set_automation": ("POST", "/selection/automation/{control_name}"),
            "ardour_set_touch": ("POST", "/selection/touch/{control_name}"),
            
            # Utility
            "ardour_get_current_selection": ("GET", "/selection/current"),
            "ardour_clear_selection": ("DELETE", "/selection/clear"),
        }
        
        if tool_name not in endpoint_map:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(endpoint_map.keys())
            }
        
        method, endpoint = endpoint_map[tool_name]
        url = f"{MCP_SERVER_URL}{endpoint}"
        
        # Handle path parameters
        if "{track_number}" in endpoint:
            track_number = arguments.get("track_number")
            if track_number is None:
                return {"error": "track_number is required for this tool"}
            url = url.replace("{track_number}", str(track_number))
        
        if "{control_name}" in endpoint:
            control_name = arguments.get("control_name")
            if control_name is None:
                return {"error": "control_name is required for this tool"}
            url = url.replace("{control_name}", control_name)
        
        # Make the request
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:  # POST
            response = requests.post(url, json=arguments, timeout=10)
        
        if response.status_code == 200:
            return {
                "success": True,
                "result": response.json(),
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "detail": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "detail": f"Cannot connect to MCP server at {MCP_SERVER_URL}. Make sure the server is running."
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Execution failed",
            "detail": str(e)
        }

def print_manifest():
    """Print the JSON manifest to stdout"""
    manifest = load_manifest()
    print(json.dumps(manifest, indent=2))

def get_tool_info(tool_name):
    """Get information about a specific tool"""
    manifest = load_manifest()
    
    if "error" in manifest:
        return manifest
    
    for tool in manifest.get("tools", []):
        if tool["name"] == tool_name:
            return tool
    
    return {"error": f"Tool '{tool_name}' not found"}

def list_tools():
    """List all available tools"""
    manifest = load_manifest()
    
    if "error" in manifest:
        return manifest
    
    tools = []
    for tool in manifest.get("tools", []):
        tools.append({
            "name": tool["name"],
            "description": tool["description"]
        })
    
    return {"tools": tools}

def validate_tool_input(tool_name, input_data):
    """Validate input data against tool schema"""
    tool_info = get_tool_info(tool_name)
    
    if "error" in tool_info:
        return tool_info
    
    schema = tool_info.get("inputSchema", {})
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Check required fields
    for field in required:
        if field not in input_data:
            return {
                "error": f"Missing required field: {field}",
                "tool": tool_name
            }
    
    # Basic type validation
    for field, value in input_data.items():
        if field in properties:
            prop_type = properties[field].get("type")
            
            if prop_type == "integer" and not isinstance(value, int):
                return {
                    "error": f"Field '{field}' must be an integer",
                    "tool": tool_name
                }
            elif prop_type == "number" and not isinstance(value, (int, float)):
                return {
                    "error": f"Field '{field}' must be a number",
                    "tool": tool_name
                }
            elif prop_type == "boolean" and not isinstance(value, bool):
                return {
                    "error": f"Field '{field}' must be a boolean",
                    "tool": tool_name
                }
    
    return {"valid": True}

def handle_mcp_protocol():
    """Handle MCP protocol communication via stdin/stdout"""
    try:
        while True:
            # Read input from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            # Handle different request types
            if request.get("method") == "tools/list":
                # List available tools
                manifest = load_manifest()
                if "error" in manifest:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": manifest["error"]
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "tools": manifest.get("tools", [])
                        }
                    }
                
            elif request.get("method") == "tools/call":
                # Execute a tool
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32602,
                            "message": "Missing tool name"
                        }
                    }
                else:
                    result = execute_tool(tool_name, arguments)
                    
                    if result.get("success"):
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result["result"], indent=2)
                                    }
                                ]
                            }
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "error": {
                                "code": -32603,
                                "message": result.get("error", "Unknown error"),
                                "data": result.get("detail", "")
                            }
                        }
            
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
            
            # Send response to stdout
            print(json.dumps(response), flush=True)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response), flush=True)

def main():
    """Main entry point for the MCP client"""
    parser = argparse.ArgumentParser(
        description="Ardour MCP Client - Control Ardour DAW via MCP protocol"
    )
    
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print JSON manifest and exit"
    )
    
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools"
    )
    
    parser.add_argument(
        "--tool-info",
        help="Get information about a specific tool"
    )
    
    parser.add_argument(
        "--validate",
        nargs=2,
        metavar=("TOOL", "JSON_INPUT"),
        help="Validate input for a tool"
    )
    
    parser.add_argument(
        "--execute",
        nargs=2,
        metavar=("TOOL", "JSON_INPUT"),
        help="Execute a tool with JSON input"
    )
    
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Run in MCP protocol mode (for Cursor integration)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Ardour MCP Client 1.0.0"
    )
    
    args = parser.parse_args()
    
    # If --mcp flag is used, run in MCP protocol mode
    if args.mcp:
        handle_mcp_protocol()
        return 0
    
    if args.describe:
        print_manifest()
        return 0
    
    if args.list_tools:
        result = list_tools()
        print(json.dumps(result, indent=2))
        return 0
    
    if args.tool_info:
        result = get_tool_info(args.tool_info)
        print(json.dumps(result, indent=2))
        return 0
    
    if args.validate:
        tool_name, json_input = args.validate
        try:
            input_data = json.loads(json_input)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "error": "Invalid JSON input",
                "details": str(e)
            }, indent=2))
            return 1
        
        result = validate_tool_input(tool_name, input_data)
        print(json.dumps(result, indent=2))
        return 0 if result.get("valid") else 1
    
    if args.execute:
        tool_name, json_input = args.execute
        try:
            input_data = json.loads(json_input)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "error": "Invalid JSON input",
                "details": str(e)
            }, indent=2))
            return 1
        
        result = execute_tool(tool_name, input_data)
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 1
    
    # If no arguments provided, show help
    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())