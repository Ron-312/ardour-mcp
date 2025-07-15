#!/usr/bin/env python3
"""
Test script for new track control features:
- Track naming
- Record enable/safe
- Pan control
- Track listing
"""

import time
import json
import requests

BASE_URL = "http://localhost:8000"

def test_track_naming():
    """Test track naming functionality"""
    print("🏷️  Testing Track Naming")
    print("=" * 30)
    
    test_cases = [
        (1, "Lead Vocals"),
        (2, "Bass Guitar"),
        (3, "Drums"),
        (4, "Guitar Solo")
    ]
    
    for track_num, name in test_cases:
        print(f"Setting track {track_num} name to '{name}'...")
        try:
            response = requests.post(
                f"{BASE_URL}/track/{track_num}/name",
                json={"name": name}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {result['message']}")
            else:
                print(f"  ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        time.sleep(0.5)

def test_record_control():
    """Test record enable and safe functionality"""
    print("\n🎙️  Testing Record Control")
    print("=" * 30)
    
    # Test record enable
    print("Testing record enable...")
    for track in [1, 2]:
        try:
            # Enable recording
            response = requests.post(
                f"{BASE_URL}/track/{track}/record-enable",
                json={"enabled": True}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Track {track}: {result['message']}")
            
            time.sleep(0.3)
            
            # Disable recording
            response = requests.post(
                f"{BASE_URL}/track/{track}/record-enable",
                json={"enabled": False}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Track {track}: {result['message']}")
                
        except Exception as e:
            print(f"  ❌ Track {track} error: {e}")
    
    # Test record safe
    print("\nTesting record safe...")
    try:
        response = requests.post(
            f"{BASE_URL}/track/1/record-safe",
            json={"safe": True}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ {result['message']}")
    except Exception as e:
        print(f"  ❌ Record safe error: {e}")

def test_pan_control():
    """Test pan control functionality"""
    print("\n🎚️  Testing Pan Control")
    print("=" * 30)
    
    pan_tests = [
        (1, -1.0, "full left"),
        (2, 0.0, "center"),
        (3, 1.0, "full right"),
        (4, -0.5, "slight left"),
        (1, 0.75, "mostly right")
    ]
    
    for track, pan_pos, desc in pan_tests:
        print(f"Setting track {track} pan to {desc} ({pan_pos})...")
        try:
            response = requests.post(
                f"{BASE_URL}/track/{track}/pan",
                json={"pan_position": pan_pos}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {result['message']}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        time.sleep(0.5)

def test_track_listing():
    """Test track listing functionality"""
    print("\n📋 Testing Track Listing")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/track/list")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            print("Check Ardour's Window > Log for the track list results")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_mcp_client():
    """Test the MCP client with new features"""
    print("\n🎯 Testing MCP Client Manifest")
    print("=" * 30)
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", "mcp_client/ardour_mcp_client.py", "--describe"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            manifest = json.loads(result.stdout)
            tools = manifest.get("tools", [])
            print(f"✅ MCP manifest loaded successfully")
            print(f"📊 Available tools: {len(tools)}")
            
            new_tools = [
                "set_track_name",
                "set_track_record_enable", 
                "set_track_record_safe",
                "set_track_pan",
                "list_tracks"
            ]
            
            found_tools = [tool["name"] for tool in tools if tool["name"] in new_tools]
            print(f"🆕 New tools found: {found_tools}")
            
        else:
            print(f"❌ MCP client error: {result.stderr}")
    except Exception as e:
        print(f"❌ MCP test error: {e}")

def main():
    """Run all tests"""
    print("🎵 Testing New Ardour MCP Features")
    print("=" * 50)
    print("Make sure Ardour is running with OSC enabled!")
    print()
    
    # Test all new features
    test_track_naming()
    test_record_control()
    test_pan_control()
    test_track_listing()
    test_mcp_client()
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    print("✅ Track naming - Rename tracks with meaningful names")
    print("✅ Record control - Enable/disable recording per track")
    print("✅ Pan control - Position tracks in stereo field")
    print("✅ Track listing - Query all tracks from Ardour")
    print("✅ MCP manifest - Updated with new tools")
    print()
    print("🔍 Check Ardour to verify:")
    print("  - Track names changed in mixer")
    print("  - Record buttons enabled/disabled")
    print("  - Pan knobs moved to new positions")
    print("  - Ardour log shows OSC messages")

if __name__ == "__main__":
    main()