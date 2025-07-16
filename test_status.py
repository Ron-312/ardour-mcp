#!/usr/bin/env python3
"""
Quick Test Status Checker for Ardour MCP Server

Shows available tests and their status without running them.
"""

import os
import sys
import requests
from typing import List, Dict

def check_test_files() -> List[Dict[str, str]]:
    """Check which test files are available"""
    
    expected_tests = [
        {
            "name": "Transport & Basic Controls",
            "file": "tests/test_transport_api.py",
            "description": "Basic transport control and OSC connection"
        },
        {
            "name": "Track Control",
            "file": "tests/test_phase2_features.py", 
            "description": "Track fader, mute, solo, pan control"
        },
        {
            "name": "Send/Aux Control",
            "file": "tests/test_phase3_sends.py",
            "description": "Send levels and aux routing"
        },
        {
            "name": "Recording Controls",
            "file": "tests/test_recording_controls.py",
            "description": "Master and track recording controls"
        },
        {
            "name": "Plugin Discovery",
            "file": "tests/test_plugin_discovery.py",
            "description": "Basic plugin discovery and listing"
        },
        {
            "name": "Real Plugin Discovery",
            "file": "tests/test_real_plugin_discovery.py",
            "description": "Real plugin discovery with OSC feedback"
        },
        {
            "name": "Dynamic Parameter Mapping",
            "file": "tests/test_dynamic_parameter_mapping.py",
            "description": "Dynamic plugin parameter mapping system"
        },
        {
            "name": "Smart Parameter Control",
            "file": "tests/test_smart_parameters.py",
            "description": "Smart parameter value conversion"
        },
        {
            "name": "Plugin Control",
            "file": "tests/test_plugin_control.py",
            "description": "Plugin enable/disable and parameter control"
        },
        {
            "name": "Comprehensive Plugin Tests",
            "file": "tests/test_comprehensive_plugins.py",
            "description": "Complete plugin system validation"
        },
        {
            "name": "Full Plugin Workflow",
            "file": "tests/test_full_plugin_workflow.py", 
            "description": "End-to-end plugin workflow testing"
        }
    ]
    
    # Check which files exist
    for test in expected_tests:
        test["exists"] = os.path.exists(test["file"])
        
    return expected_tests

def check_server_status() -> Dict[str, str]:
    """Check MCP server status"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            return {"status": "RUNNING", "message": "Server is healthy"}
        else:
            return {"status": "ERROR", "message": f"Server returned {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "OFFLINE", "message": "Server is not running"}
    except Exception as e:
        return {"status": "ERROR", "message": f"Error: {str(e)}"}

def check_ardour_connection() -> Dict[str, str]:
    """Check Ardour OSC connection"""
    try:
        response = requests.post("http://localhost:8000/transport/play", timeout=3)
        if response.status_code == 200:
            # Try to stop as well
            requests.post("http://localhost:8000/transport/stop", timeout=3)
            return {"status": "CONNECTED", "message": "OSC commands successful"}
        else:
            return {"status": "ERROR", "message": f"Transport failed: {response.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "message": f"OSC test failed: {str(e)}"}

def main():
    """Main status check"""
    print("🎵 ARDOUR MCP SERVER - TEST STATUS CHECK")
    print("=" * 60)
    
    # Check server status
    print("\n🖥️  SERVER STATUS:")
    server_status = check_server_status()
    status_emoji = {"RUNNING": "✅", "OFFLINE": "❌", "ERROR": "⚠️"}
    print(f"   {status_emoji.get(server_status['status'], '❓')} {server_status['message']}")
    
    if server_status['status'] == "RUNNING":
        # Check Ardour connection
        print("\n📡 ARDOUR CONNECTION:")
        ardour_status = check_ardour_connection()
        print(f"   {status_emoji.get(ardour_status['status'], '❓')} {ardour_status['message']}")
    
    # Check test files
    print("\n📋 AVAILABLE TESTS:")
    tests = check_test_files()
    
    available_count = sum(1 for test in tests if test["exists"])
    total_count = len(tests)
    
    print(f"   📊 {available_count}/{total_count} test files available")
    print()
    
    for i, test in enumerate(tests, 1):
        status_icon = "✅" if test["exists"] else "❌"
        print(f"   {i:2d}. {status_icon} {test['name']}")
        print(f"       📁 {test['file']}")
        print(f"       📝 {test['description']}")
        if not test["exists"]:
            print(f"       ⚠️  File missing!")
        print()
    
    # Quick setup guide
    print("🚀 QUICK START GUIDE:")
    
    if server_status['status'] != "RUNNING":
        print("   1. Start MCP Server:")
        print("      python -m mcp_server.main")
        print()
    
    if server_status['status'] == "RUNNING" and ardour_status['status'] != "CONNECTED":
        print("   1. Start Ardour with OSC enabled:")
        print("      Edit → Preferences → Control Surfaces → OSC")
        print("      Set port to 3819")
        print()
    
    print("   2. Run individual tests:")
    for test in tests[:3]:  # Show first 3 as examples
        if test["exists"]:
            print(f"      python {test['file']}")
    print("      ...")
    print()
    
    print("   3. Run all tests:")
    print("      python run_all_tests.py")
    print()
    
    # System readiness assessment
    print("🎯 SYSTEM READINESS:")
    
    readiness_score = 0
    max_score = 3
    
    if server_status['status'] == "RUNNING":
        readiness_score += 1
        print("   ✅ MCP Server is running")
    else:
        print("   ❌ MCP Server is not running")
    
    if server_status['status'] == "RUNNING" and ardour_status.get('status') == "CONNECTED":
        readiness_score += 1
        print("   ✅ Ardour OSC connection working")
    else:
        print("   ❌ Ardour OSC connection not working")
    
    if available_count == total_count:
        readiness_score += 1
        print("   ✅ All test files available")
    else:
        print(f"   ⚠️  {total_count - available_count} test files missing")
    
    readiness_percentage = (readiness_score / max_score) * 100
    
    print(f"\n   📊 Readiness: {readiness_score}/{max_score} ({readiness_percentage:.0f}%)")
    
    if readiness_percentage == 100:
        print("   🎉 System ready for comprehensive testing!")
    elif readiness_percentage >= 66:
        print("   ✅ System mostly ready - some tests may fail")
    else:
        print("   ⚠️  System needs setup before testing")

if __name__ == "__main__":
    main()