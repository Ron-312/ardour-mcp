#!/usr/bin/env python3
"""
Ardour MCP Client - Single-file client for MCP protocol communication
"""

import argparse
import json
import sys
import os
from pathlib import Path

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
        "--version",
        action="version",
        version="Ardour MCP Client 1.0.0"
    )
    
    args = parser.parse_args()
    
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
    
    # If no arguments provided, show help
    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())